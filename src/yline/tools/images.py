from __future__ import annotations

import httpx
import re
import json
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

async def search_images(query: str, max_results: int = 15) -> list[str]:
    """Search DuckDuckGo for images.
    
    Args:
        query: Search query
        max_results: Max number of image URLs to return
        
    Returns:
        List of image URLs.
    """
    import asyncio
    try:
        # Prevent IP block by spacing out requests
        await asyncio.sleep(1.5)
        async with httpx.AsyncClient() as client:
            # 1. Get vqd token
            res = await client.get(
                "https://duckduckgo.com/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=10.0
            )
            vqd_match = re.search(r'vqd=([\d-]+)', res.text)
            if not vqd_match:
                logger.error("Could not find vqd token")
                return []
            vqd = vqd_match.group(1)
            
            # 2. Search images
            params = {
                "l": "us-en",
                "o": "json",
                "q": query,
                "vqd": vqd,
                "f": ",,,",
                "p": "1",
                "v7exp": "a"
            }
            res_img = await client.get(
                "https://duckduckgo.com/i.js",
                params=params,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10.0
            )
            data = res_img.json()
            results = data.get("results", [])
            urls = [r["image"] for r in results[:max_results]]
            return urls
    except Exception as e:
        logger.error(f"Error searching images: {e}")
        return []

async def download_image(url: str, save_path: str) -> str | None:
    """Download and validate an image.
    
    Args:
        url: Image URL
        save_path: File path to save
        
    Returns:
        The save_path if successful, None otherwise.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            res = await client.get(url, timeout=10.0)
            res.raise_for_status()
            
            # Load with Pillow to ensure it's fully valid and convert to RGB
            img = Image.open(io.BytesIO(res.content))
            img.load()  # Force loading the actual image data (verify() only checks headers)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Save strictly as JPEG to guarantee MoviePy compatibility
            img.save(save_path, format="JPEG", quality=95)
            return save_path
    except Exception as e:
        logger.error(f"Error downloading image {url}: {e}")
        return None

SEARCH_IMAGES_TOOL = {
    "type": "function",
    "function": {
        "name": "search_images",
        "description": "Search DuckDuckGo for images.",
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
                }
            },
            "required": ["query"],
        },
    },
}
