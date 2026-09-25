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

# Image rate limiter to space out requests and avoid IP bans
class ImageRateLimiter:
    def __init__(self, min_delay: float = 1.0):
        self.min_delay = min_delay
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_call
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
            self._last_call = asyncio.get_event_loop().time()

_image_rate_limiter = ImageRateLimiter(min_delay=1.2)

# Domains that host generic watermarked stock photography
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
]

def is_stock_url(url: str) -> bool:
    """Return True if URL is from a known stock photo provider."""
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

# Titles/categories on Wikimedia that are unsuitable for lyric video backgrounds
WIKIMEDIA_EXCLUDE_TERMS = [
    "flag of", "coat of arms", "icon", "symbol", "map", "diagram", "chart",
    "logo", "screenshot", "signature", "seal of", "currency", "coin"
]


@traceable
async def _search_wikimedia(query: str, max_results: int = 15) -> list[str]:
    """Search Wikimedia Commons for high-resolution, relevant public domain photos."""
    for attempt in range(2):
        try:
            await _image_rate_limiter.wait()
            params = {
                "action": "query",
                "generator": "search",
                "gsrnamespace": "6",  # File namespace
                "gsrsearch": query,
                "gsrlimit": str(max_results + 5),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "format": "json",
            }
            async with httpx.AsyncClient(
                headers={"User-Agent": "YlineBot/1.0 (contact@yline.local)"},
                verify=_ssl_context,
                timeout=10.0,
            ) as client:
                res = await client.get("https://commons.wikimedia.org/w/api.php", params=params)
                if res.status_code == 200:
                    data = res.json()
                    pages = data.get("query", {}).get("pages", {})
                    results = []
                    for _, v in pages.items():
                        infos = v.get("imageinfo", [])
                        if not infos:
                            continue
                        info = infos[0]
                        mime = info.get("mime", "")
                        if mime not in ["image/jpeg", "image/png", "image/webp"]:
                            continue
                        title = v.get("title", "").lower()
                        if any(term in title for term in WIKIMEDIA_EXCLUDE_TERMS):
                            continue
                        w = info.get("width", 0)
                        h = info.get("height", 0)
                        if w < 500 or h < 400:
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

    for attempt in range(2):
        try:
            await _image_rate_limiter.wait()
            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"
            async with httpx.AsyncClient(
                headers=BROWSER_HEADERS, timeout=12.0, follow_redirects=True
            ) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    # Parse image JSON blobs: m="{...}"
                    raw_matches = re.findall(r'm="(\{[^"]+\})"', res.text)
                    relevant_matches = []
                    fallback_matches = []

                    for m in raw_matches:
                        try:
                            d = json.loads(html.unescape(m))
                            murl = d.get("murl")
                            if not murl or is_stock_url(murl):
                                continue
                            
                            title = d.get("t", "").lower()
                            title_words = set(re.findall(r"[a-zA-Z]{3,}", title))
                            overlap = query_keywords.intersection(title_words)
                            if query_keywords and len(overlap) > 0:
                                relevant_matches.append(murl)
                            else:
                                fallback_matches.append(murl)
                        except Exception:
                            continue

                    # If we found matches with keyword overlap in the title, use them
                    if len(relevant_matches) >= 2:
                        return relevant_matches[:max_results]
                    
                    # Otherwise, if Bing had multiple matches, take top relevant + fallback
                    combined = relevant_matches + fallback_matches
                    if len(combined) >= 3:
                        return combined[:max_results]
        except Exception as e:
            logger.debug(f"Bing search attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1.2 + attempt * 1.0)
    return []


@traceable
async def search_images(query: str, max_results: int = 15) -> list[str]:
    """Search across multiple providers with relevance fallback.
    
    1. First tries Wikimedia Commons (high relevance, curated CC/public domain images).
    2. Then tries Bing Images (with title keyword validation to avoid local filler).
    3. If query fails, simplifies query words and retries.
    """
    clean_q = " ".join(re.findall(r"[a-zA-Z0-9]+", query))
    if not clean_q:
        clean_q = query

    # 1. Wikimedia Commons
    urls = await _search_wikimedia(clean_q, max_results=max_results)
    if urls:
        return urls

    # 2. Bing Images
    urls = await _search_bing(clean_q, max_results=max_results)
    if urls:
        return urls

    # 3. If query has >2 words and returned 0 results, simplify to top 2 keywords
    words = [w for w in re.findall(r"[a-zA-Z]{3,}", clean_q) if w.lower() not in {"aesthetic", "scene", "view"}]
    if len(words) > 2:
        simplified = " ".join(words[:2])
        logger.info(f"Retrying image search with simplified query '{simplified}' (was '{clean_q}')")
        urls = await _search_wikimedia(simplified, max_results=max_results)
        if urls:
            return urls
        urls = await _search_bing(simplified, max_results=max_results)
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
        headers = BROWSER_HEADERS
        verify_arg: Any = True
        if "wikimedia.org" in url:
            headers = {"User-Agent": "YlineLyricVideoBot/1.0 (https://github.com/pjpangilinan/yline; mailto:contact@yline.local)"}
            verify_arg = _ssl_context

        async with httpx.AsyncClient(
            headers=headers, verify=verify_arg, timeout=timeout, follow_redirects=True
        ) as client:
            res = await client.get(url)
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
