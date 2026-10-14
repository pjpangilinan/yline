from __future__ import annotations
from langsmith import traceable

import asyncio
import hashlib
import html
import io
import json
import logging
import os
import re
import ssl
from typing import Any
import certifi
import httpx
from PIL import Image

Image.MAX_IMAGE_PIXELS = 200_000_000

logger = logging.getLogger(__name__)

# Standard browser headers to avoid 403 Forbidden / bot detection
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Domain-specific rate limiter with automatic exponential backoff on 429
class ImageRateLimiter:
    def __init__(self):
        # Default minimum delay per domain
        self._min_delays: dict[str, float] = {
            "wikimedia.org": 1.5,
            "bing.com": 0.8,
            "duckduckgo.com": 1.2,
            "default": 0.5,
        }
        self._last_call: dict[str, float] = {}
        self._backoff_until: dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _get_domain_key(self, host_or_url: str) -> str:
        h = host_or_url.lower()
        for d in ["wikimedia.org", "bing.com", "duckduckgo.com"]:
            if d in h:
                return d
        return "default"

    async def wait(self, target: str = "default"):
        key = self._get_domain_key(target)
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            # If domain is in backoff (e.g., from 429 response), pause
            until = self._backoff_until.get(key, 0.0)
            if until > now:
                wait_sec = until - now
                logger.info(f"Rate limiter backing off for {key}: waiting {wait_sec:.1f}s")
                await asyncio.sleep(wait_sec)
                now = asyncio.get_event_loop().time()

            last = self._last_call.get(key, 0.0)
            delay = self._min_delays.get(key, 0.5)
            elapsed = now - last
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)
            self._last_call[key] = asyncio.get_event_loop().time()

    async def notify_rate_limit(self, target: str, backoff_seconds: float = 5.0):
        """Called when a 429 or rate limit warning is received."""
        key = self._get_domain_key(target)
        async with self._lock:
            now = asyncio.get_event_loop().time()
            self._backoff_until[key] = max(self._backoff_until.get(key, 0.0), now + backoff_seconds)
            logger.warning(f"Domain {key} triggered rate limit (429). Pausing requests for {backoff_seconds}s")


_image_rate_limiter = ImageRateLimiter()

# Domains that host generic watermarked stock photography, video thumbnails, or retail products
STOCK_DOMAINS = [
    "shutterstock.com",
    "istockphoto.com",
    "alamy.com",
    "gettyimages.com",
    "dreamstime.com",
    "depositphotos.com",
    "123rf.com",
    "freepik.com",
    "vecteezy.com",
    "stock.adobe.com",
    "canva.com",
    "clipart",
    "pond5.com",
    "walmart.com",
    "amazon.com",
    "ebay.com",
    "target.com",
    "etsy.com",
    "displate.com",
    "movieposterdb.com",
    "redbubble.com",
    "aliexpress.com",
    "ytimg.com",
    "youtube.com",
    "vimeo.com",
    "dailymotion.com",
    "prcdn.co",
    "pinimg.com",
    "tiktok.com",
]

# Editorial, military PR, political, library archival scans, and shopping terms to exclude
EDITORIAL_EXCLUDE = {
    "obama", "trump", "biden", "bush", "clinton", "president", "congress", "senate",
    "white house", "politician", "politics", "military", "army", "navy", "air force",
    "national guard", "dvids", "dod", "soldier", "troops", "police", "patrol",
    "atmis", "somalia", "ambassador", "diplomatic", "ministry", "minister",
    "delegation", "peacekeeping", "summit", "parliament", "zebra", "wildlife",
    "taxidermy", "species", "subspecies", "genus",
    "library of congress", "boston public library", "internet archive", "book images",
    "trade card", "disaster", "outlet", "outlets", "mall", "shopping center",
    "specimen", "serpentinite", "geological", "mineral", "conference", "convention",
    "award", "ceremony", "protest", "rally", "diagram", "chart", "map", "blueprint",
    "1908", "1910", "1915", "1920", "1930", "1940", "1839", "1850", "1860", "1880",
}


def is_stock_url(url: str) -> bool:
    """Return True if URL is from a known stock photo, video thumbnail, or retail provider."""
    u = url.lower()
    return any(domain in u for domain in STOCK_DOMAINS)


@traceable
async def _search_ddg(query: str, max_results: int = 15) -> list[str]:
    """Search DuckDuckGo with retries, timeouts, and headers."""
    for attempt in range(3):
        try:
            await _image_rate_limiter.wait()
            async with httpx.AsyncClient(
                headers=BROWSER_HEADERS, timeout=12.0, follow_redirects=True
            ) as client:
                res = await client.get("https://duckduckgo.com/", params={"q": query})
                vqd_match = re.search(r'vqd=([\d-]+)', res.text)
                if not vqd_match:
                    await asyncio.sleep(1.0 + attempt * 1.5)
                    continue
                vqd = vqd_match.group(1)

                params = {
                    "l": "us-en",
                    "o": "json",
                    "q": query,
                    "vqd": vqd,
                    "f": ",,,",
                    "p": "1",
                }
                res_img = await client.get(
                    "https://duckduckgo.com/i.js",
                    params=params,
                    headers={"Referer": "https://duckduckgo.com/"},
                )
                if res_img.status_code == 200:
                    data = res_img.json()
                    results = data.get("results", [])
                    urls = [r["image"] for r in results if r.get("image") and not is_stock_url(r["image"])]
                    if urls:
                        return urls[:max_results]
        except Exception as e:
            logger.debug(f"DDG search attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1.5 + attempt * 1.5)
    return []


# Wikimedia SSL context using certifi bundle
_ssl_context = ssl.create_default_context(cafile=certifi.where())

@traceable
async def _search_wikimedia(query: str, max_results: int = 5) -> list[str]:
    """Search Wikimedia Commons for high-resolution, landscape-oriented public domain photos."""
    for attempt in range(2):
        try:
            await _image_rate_limiter.wait("wikimedia.org")
            params = {
                "action": "query",
                "generator": "search",
                "gsrnamespace": "6",  # File namespace
                "gsrsearch": f"{query} photo",
                "gsrlimit": str(min(max_results + 5, 15)),
                "prop": "imageinfo|categories",
                "iiprop": "url|size|mime",
                "cllimit": "25",
                "format": "json",
            }
            async with httpx.AsyncClient(
                headers={"User-Agent": "YlineLyricVideoBot/1.0 (https://github.com/pjpangilinan/yline; mailto:contact@yline.local)"},
                verify=_ssl_context,
                timeout=10.0,
            ) as client:
                res = await client.get("https://commons.wikimedia.org/w/api.php", params=params)
                if res.status_code == 429:
                    await _image_rate_limiter.notify_rate_limit("wikimedia.org", backoff_seconds=8.0)
                    continue
                if res.status_code == 200:
                    data = res.json()
                    pages = data.get("query", {}).get("pages", {})
                    results = []
                    for _, v in pages.items():
                        title = v.get("title", "")
                        infos = v.get("imageinfo", [])
                        if not infos:
                            continue
                        info = infos[0]
                        mime = info.get("mime", "")
                        if mime not in ["image/jpeg", "image/png", "image/webp"]:
                            continue
                        w = info.get("width", 0)
                        h = info.get("height", 0)
                        # Require landscape aspect ratio suitable for 16:9 video slides.
                        # Naturally filters out portrait book pages, stamps, vertical cards, and coins by geometry.
                        if w < 800 or h < 450 or (w / max(1, h)) < 1.15:
                            continue
                        cats = " ".join(c.get("title", "").lower() for c in v.get("categories", []))
                        t_low = title.lower()
                        if any(term in t_low or term in cats for term in EDITORIAL_EXCLUDE):
                            continue
                        url = info.get("url")
                        if url and not is_stock_url(url):
                            results.append(url)
                    if results:
                        return results[:max_results]
        except Exception as e:
            logger.debug(f"Wikimedia search attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1.0)
    return []


@traceable
async def _search_bing(query: str, max_results: int = 15) -> list[str]:
    """Search Bing Images with metadata extraction and relevance validation."""
    query_keywords = set(re.findall(r"[a-zA-Z]{3,}", query.lower())) - {
        "aesthetic", "scene", "view", "photo", "image", "wallpaper", "picture"
    }

    import urllib.parse
    enc_q = urllib.parse.quote_plus(f"{query} photography")

    for attempt in range(2):
        try:
            await _image_rate_limiter.wait("bing.com")
            url = f"https://www.bing.com/images/search?q={enc_q}&form=HDRSC2&first=1"
            async with httpx.AsyncClient(
                headers=BROWSER_HEADERS, timeout=12.0, follow_redirects=True
            ) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    raw_matches = re.findall(r'm="(\{[^"]+\})"', res.text)
                    relevant_matches = []

                    for m in raw_matches:
                        try:
                            d = json.loads(html.unescape(m))
                            murl = d.get("murl")
                            if not murl or is_stock_url(murl):
                                continue
                            
                            title = d.get("t", "").lower()
                            if any(term in title for term in EDITORIAL_EXCLUDE):
                                continue
                            title_words = set(re.findall(r"[a-zA-Z]{3,}", title))
                            overlap = query_keywords.intersection(title_words)
                            if query_keywords and len(overlap) > 0:
                                relevant_matches.append(murl)
                        except Exception:
                            continue

                    if relevant_matches:
                        return relevant_matches[:max_results]
        except Exception as e:
            logger.debug(f"Bing search attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1.2 + attempt * 1.0)
    return []


@traceable
async def search_images(query: str, max_results: int = 15) -> list[str]:
    """Search across multiple providers with relevance fallback.
    
    1. First tries Wikimedia Commons (high relevance, curated CC/public domain images).
    2. If multi-word, simplifies query to top 2 keywords and tries Wikimedia Commons.
    3. Then tries Bing Images (with title keyword validation to avoid local filler).
    4. Finally falls back to DuckDuckGo images.
    """
    clean_q = " ".join(re.findall(r"[a-zA-Z0-9]+", query))
    if not clean_q:
        clean_q = query

    # 1. Wikimedia Commons (primary)
    urls = await _search_wikimedia(clean_q, max_results=max_results)
    if urls:
        return urls

    # 1b. Simplified 2-word Wikimedia query
    words = [w for w in re.findall(r"[a-zA-Z]{3,}", clean_q) if w.lower() not in {"aesthetic", "scene", "view", "photo", "image", "wallpaper", "picture"}]
    if len(words) >= 2:
        two_word_q = " ".join(words[:2])
        if two_word_q.lower() != clean_q.lower():
            urls = await _search_wikimedia(two_word_q, max_results=max_results)
            if urls:
                return urls

    # 2. Bing Images (secondary with keyword overlap)
    urls = await _search_bing(clean_q, max_results=max_results)
    if urls:
        return urls

    # 3. DuckDuckGo fallback
    urls = await _search_ddg(clean_q, max_results=max_results)
    if urls:
        return urls

    return []


@traceable
async def download_image(
    url: str,
    save_path: str,
    min_width: int = 400,
    min_height: int = 300,
    min_bytes: int = 15000,
    timeout: float = 6.0,
    seen_hashes: set[str] | None = None,
) -> str | None:
    """Download, validate, deduplicate, and convert an image.
    
    Args:
        url: Image URL
        save_path: Destination path
        min_width: Minimum allowable width in px
        min_height: Minimum allowable height in px
        min_bytes: Minimum payload size
        timeout: HTTP download timeout
        seen_hashes: Optional set of MD5 hashes already seen for this song
        
    Returns:
        The save_path if successful, None otherwise.
    """
    if is_stock_url(url):
        return None
    try:
        await _image_rate_limiter.wait(url)
        headers = BROWSER_HEADERS
        verify_arg: Any = True
        if "wikimedia.org" in url:
            headers = {"User-Agent": "YlineLyricVideoBot/1.0 (https://github.com/pjpangilinan/yline; mailto:contact@yline.local)"}
            verify_arg = _ssl_context

        async with httpx.AsyncClient(
            headers=headers, verify=verify_arg, timeout=timeout, follow_redirects=True
        ) as client:
            res = await client.get(url)
            if res.status_code == 429:
                await _image_rate_limiter.notify_rate_limit(url, backoff_seconds=8.0)
                return None
            if res.status_code != 200 or len(res.content) < min_bytes:
                return None

            # Load with Pillow to ensure it's a valid complete image
            img = Image.open(io.BytesIO(res.content))
            img.load()
            w, h = img.size
            if w < min_width or h < min_height:
                return None

            if img.mode != "RGB":
                img = img.convert("RGB")

            # Downscale oversized images to 1080p to keep memory and encoding fast
            if w > 1920 or h > 1080:
                img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

            # Encode to JPEG and compute MD5 on the exact saved bytes
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            jpeg_bytes = buf.getvalue()
            img_hash = hashlib.md5(jpeg_bytes).hexdigest()

            if seen_hashes is not None and img_hash in seen_hashes:
                logger.debug(f"Skipping duplicate image hash {img_hash[:8]} for {url}")
                return None

            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(jpeg_bytes)
            if seen_hashes is not None:
                seen_hashes.add(img_hash)
            return save_path
    except Exception as e:
        logger.debug(f"Download failed for {url}: {e}")
    return None


@traceable
async def download_image_from_candidates(
    urls: list[str],
    save_path: str,
    min_width: int = 400,
    min_height: int = 300,
    min_bytes: int = 15000,
    seen_hashes: set[str] | None = None,
) -> str | None:
    """Try downloading from a list of candidate URLs until one succeeds and is non-duplicate."""
    for candidate_url in urls:
        result = await download_image(
            candidate_url,
            save_path,
            min_width=min_width,
            min_height=min_height,
            min_bytes=min_bytes,
            seen_hashes=seen_hashes,
        )
        if result:
            return result
    return None


SEARCH_IMAGES_TOOL = {
    "type": "function",
    "function": {
        "name": "search_images",
        "description": "Search DuckDuckGo and Bing for real images matching a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Image search query",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                },
            },
            "required": ["query"],
        },
    },
}
