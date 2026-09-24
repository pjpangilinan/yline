from __future__ import annotations
from langsmith import traceable

import asyncio
import hashlib
import io
import json
import logging
import os
import re
from typing import Any
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


@traceable
async def _search_bing(query: str, max_results: int = 15) -> list[str]:
    """Fallback search using Bing Images with retries and timeouts."""
    for attempt in range(3):
        try:
            await _image_rate_limiter.wait()
            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"
            async with httpx.AsyncClient(
                headers=BROWSER_HEADERS, timeout=12.0, follow_redirects=True
            ) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    matches = [
                        m for m in re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
                        if not is_stock_url(m)
                    ]
                    if matches:
                        return matches[:max_results]
        except Exception as e:
            logger.debug(f"Bing search attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1.5 + attempt * 1.5)
    return []


@traceable
async def search_images(query: str, max_results: int = 15) -> list[str]:
    """Search DuckDuckGo (with Bing fallback) for images.
    
    Includes rate limiting, retries, and realistic browser headers.
    """
    urls = await _search_ddg(query, max_results=max_results)
    if not urls:
        logger.info(f"DDG yielded 0 images for '{query}', falling back to Bing...")
        urls = await _search_bing(query, max_results=max_results)
    return urls


@traceable
async def download_image(
    url: str,
    save_path: str,
    min_width: int = 400,
    min_height: int = 300,
    min_bytes: int = 15000,
    timeout: float = 12.0,
    seen_hashes: set[str] | None = None,
) -> str | None:
    """Download, validate, deduplicate, and convert an image with timeouts and retries.
    
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
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(
                headers=BROWSER_HEADERS, timeout=timeout, follow_redirects=True
            ) as client:
                res = await client.get(url)
                if res.status_code != 200 or len(res.content) < min_bytes:
                    continue

                # Load with Pillow to ensure it's a valid complete image
                img = Image.open(io.BytesIO(res.content))
                img.load()
                w, h = img.size
                if w < min_width or h < min_height:
                    continue

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
            logger.debug(f"Download attempt {attempt+1} failed for {url}: {e}")
            await asyncio.sleep(0.5 + attempt * 1.0)
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
