"""Image agent — generates search queries per lyric line and downloads images.

Uses the LLM to create evocative image search queries based on lyric content,
then scrapes DuckDuckGo for matching images.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from yline.state import PipelineState
from yline.tools.images import search_images, download_image
from yline.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a creative visual art director agent. Given a song's lyrics, generate concise, concrete image search queries for each lyric line.

Rules:
- Generate 2 to 3 concrete visual words per line (maximum 4 words). Focus on physical objects, settings, lighting, or tangible actions.
  GOOD: "autumn leaves", "holding hands", "candlelight", "hospital corridor", "rainy window", "bicycle path", "pocket watch", "vintage car".
  BAD: "soft candlelight calming atmosphere", "scattered gold coins dark floor", "cracked spine fragile structure", "aesthetic pleasing scene".
- Search engines fail when given abstract metaphors or long phrases. Convert metaphors and feelings into simple, concrete physical scenes:
  - If a lyric is about heartbreak/loss -> "broken glass", "empty room", "solitary figure rain".
  - If a lyric is about joy/romance -> "holding hands", "golden sunset", "couple smiling".
  - If a lyric is about time/waiting -> "wall clock", "train platform", "hourglass".
- Never use generic filler terms: "aesthetic", "scene", "wallpaper", "photo", "moody", "vibes".
- Remove filler words (ooh, yeah, ah, etc.) and punctuation.

Respond with a JSON array of search query strings, exactly one per lyric line.
Example: For lyrics ["The calendar's hung", "You're a regular decorated emergency"], respond with: ["vintage calendar", "hospital hallway"]
"""

# Batch size for LLM calls (process lyrics in chunks to stay within token limits)
BATCH_SIZE = 10


async def image_agent_node(state: PipelineState) -> dict[str, Any]:
    """LangGraph node: generate search queries and download images for each lyric line.

    Args:
        state: Current pipeline state with lyrics and song_metadata

    Returns:
        State update with images list or error
    """
    lyrics = state.get("lyrics", [])
    metadata = state.get("song_metadata", {})
    errors = list(state.get("errors", []))

    if not lyrics:
        errors.append("Image agent: no lyrics available")
        return {"errors": errors}

    artist = metadata.get("artist", "Unknown")
    title = metadata.get("title", "Unknown")
    logger.info(f"Generating images for {len(lyrics)} lyric lines")

    # Create output directory
    output_dir = os.path.join("output", f"{artist} - {title}".replace("/", "_"), "images")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Generate search queries for all lyrics using LLM
    all_queries = await _generate_search_queries(lyrics, artist, title)

    # Step 2: Concurrently download unique images for each query
    # Concurrency bounded to 4 to prevent rate limiting while allowing concurrent download/search
    concurrency_sem = asyncio.Semaphore(4)
    seen_hashes: set[str] = set()
    hash_lock = asyncio.Lock()

    async def _fetch_for_line(i: int, query: str) -> dict[str, Any]:
        async with concurrency_sem:
            logger.info(f"  [{i+1}/{len(lyrics)}] Searching: {query}")
            try:
                urls = await search_images(query, max_results=15)
                if not urls:
                    # Fallback to generic search
                    urls = await search_images(f"{artist} {title} aesthetic", max_results=15)

                if urls:
                    save_path = os.path.join(output_dir, f"img_{i:03d}.jpg")
                    for url in urls:
                        try:
                            async with hash_lock:
                                current_seen = set(seen_hashes)
                            path = await download_image(url, save_path, seen_hashes=current_seen)
                            if not path:
                                continue
                            async with hash_lock:
                                seen_hashes.update(current_seen)
                            return {
                                "path": path,
                                "lyric_index": i,
                                "search_query": query,
                            }
                        except Exception as e:
                            logger.warning(f"Failed to download {url}: {e}")
                            continue
            except Exception as e:
                logger.warning(f"Image search failed for line {i}: {e}")

            return {
                "path": "",
                "lyric_index": i,
                "search_query": query,
            }

    tasks = [_fetch_for_line(i, query) for i, query in enumerate(all_queries)]
    images = await asyncio.gather(*tasks)

    logger.info(f"Downloaded {sum(1 for img in images if img['path'])} / {len(images)} images")
    return {"images": list(images)}


async def _generate_search_queries(
    lyrics: list[dict], artist: str, title: str
) -> list[str]:
    """Use LLM to generate image search queries for each lyric line.

    Processes in batches to stay within token limits.
    """
    all_queries: list[str] = []
    lyric_texts = [line["text"] for line in lyrics]

    for batch_start in range(0, len(lyric_texts), BATCH_SIZE):
        batch = lyric_texts[batch_start : batch_start + BATCH_SIZE]

        await rate_limiter.acquire(estimated_tokens=500)

        try:
            llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.5, max_tokens=1000)
            response = await llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Song: {artist} - {title}\n\nGenerate one image search query per line:\n"
                    + "\n".join(f"{i+1}. {text}" for i, text in enumerate(batch))
                ),
            ])

            if hasattr(response, "response_metadata"):
                usage = response.response_metadata.get("token_usage", {})
                rate_limiter.record_usage(
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0),
                )

            # Parse JSON array from response
            content = response.content or ""
            start = content.find("[")
            end = content.rfind("]") + 1
            parsed_queries = None
            if start >= 0 and end > start:
                try:
                    parsed_queries = json.loads(content[start:end])
                except Exception as e:
                    logger.debug(f"Failed to parse JSON brackets slice: {e}")

            if isinstance(parsed_queries, list) and parsed_queries:
                # Ensure queries are strings and pad if fewer than batch
                cleaned = [str(q).strip().strip('"\'') for q in parsed_queries if str(q).strip()]
                while len(cleaned) < len(batch):
                    cleaned.append(f"{title} scenery")
                all_queries.extend(cleaned[: len(batch)])
            else:
                logger.warning(f"Could not parse JSON query array from LLM, falling back to thematic queries")
                all_queries.extend([_clean_fallback_query(text, title) for text in batch])

        except Exception as e:
            logger.warning(f"LLM query generation failed: {e}")
            all_queries.extend([_clean_fallback_query(text, title) for text in batch])

    return all_queries


def _clean_fallback_query(text: str, title: str) -> str:
    """Produce a concise 2-3 word fallback query from lyric text."""
    words = re.findall(r"[a-zA-Z]{3,}", text)
    if len(words) >= 2:
        return " ".join(words[:3])
    return f"{title} scenery"
