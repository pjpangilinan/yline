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

SYSTEM_PROMPT = """You are a visionary music video art director.
Your task: Deeply analyze the song's lyrics, theme, cultural setting, and emotional tone (translating non-English lyrics internally to grasp the true meaning), then generate evocative 2-to-3 word photography search queries for each lyric line.

RULES:
1. Context and cultural setting:
   - Understand what the song is actually about!
   - For urban, everyday life, or romance songs (e.g., OPM/indie songs about dating on a budget, city life, inflation): evoke relatable modern settings like "cozy coffee shop", "supermarket aisle", "street food night", "rainy city street", "dim kitchen table", "city skyline night", "sunset rooftop", "convenience store night", "starry sky".
   - For folk, melancholic, or acoustic songs: evoke atmospheric nature like "foggy forest path", "overcast mountain lake", "candlelit dark room", "autumn porch twilight".
   - For synthpop or energetic songs: evoke vibrant urban nightscapes like "neon rain street", "city lights dawn", "night highway traffic".
2. NEVER be hyper-literal or absurd:
   - Do NOT search for literal idioms, body parts, or props (e.g., NEVER search for "can of sardines", "bag of rice", "clown", "belt", "money", or human faces).
   - Do NOT produce nonsensical weather mismatches (e.g. NEVER search for snow or blizzards for tropical/urban settings, and NEVER search for wild animals or desert zebras).
3. Vocal filler lines (e.g. "Ooh", "Ah", "La la"):
   - When a lyric is just vocalizations or non-verbal syllables, generate beautiful cinematic transition scenery matching the song's atmosphere (e.g. "twilight city skyline", "soft bokeh streetlights", "sunset clouds horizon").
4. Concrete visual words:
   - Each query must consist of 2 to 3 concrete physical setting and lighting words (maximum 4 words).
   - Never use generic filler words like "aesthetic", "scene", "photo", "wallpaper", "vibes".

Respond strictly with a JSON array of query strings, exactly one per lyric line.
Example: For lyrics ["No one to wonder when I will be home", "One more night alone"], respond with: ["dim bedroom night", "foggy streetlamp rain"]
"""

# Batch size for LLM calls (process lyrics in chunks to stay within token limits)
BATCH_SIZE = 10


async def _generate_theme_palette(artist: str, title: str, sample_lyrics: list[str]) -> list[str]:
    """Dynamically generate a tailored visual search palette matching the song's aesthetic."""
    await rate_limiter.acquire(estimated_tokens=250)
    try:
        llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.6, max_tokens=250)
        lyrics_excerpt = " | ".join(sample_lyrics[:6])
        response = await llm.ainvoke([
            SystemMessage(content=(
                "You are a cinematic art director. Analyze the song's genre, language, and theme. "
                "Generate 6 to 8 diverse, evocative 2-to-3-word physical setting and lighting photography queries "
                "that capture this song's specific visual world, aesthetic, and mood. Respond strictly with a JSON array of query strings. "
                "Example: [\"cozy coffee shop\", \"rainy city street\", \"supermarket aisle\", \"city skyline night\", \"warm kitchen table\"]"
            )),
            HumanMessage(content=f"Song: {artist} - {title}\nLyrics: {lyrics_excerpt}"),
        ])
        content = response.content or ""
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end])
            if isinstance(parsed, list) and parsed:
                return [str(q).strip().strip('"\'') for q in parsed if str(q).strip()]
    except Exception as e:
        logger.debug(f"Dynamic theme palette generation failed: {e}")

    return [
        "city street night",
        "coffee shop window",
        "starry night sky",
        "sunset horizon",
        "rainy window evening",
        "quiet park twilight",
    ]


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

    # Step 1: Dynamically generate song-specific visual theme palette
    sample_texts = [line.get("text", "") for line in lyrics if line.get("text")]
    theme_palette = await _generate_theme_palette(artist, title, sample_texts)

    # Step 2: Generate search queries for all lyrics using LLM
    all_queries = await _generate_search_queries(lyrics, artist, title, theme_palette)

    # Step 3: Concurrently download unique images for each query
    # Concurrency bounded to 2 to respect Wikimedia / Bing rate limit policies
    concurrency_sem = asyncio.Semaphore(2)
    seen_hashes: set[str] = set()

    async def _fetch_for_line(i: int, query: str) -> dict[str, Any]:
        async with concurrency_sem:
            save_path = os.path.join(output_dir, f"img_{i:03d}.jpg")

            candidate_queries = [
                query,
                theme_palette[i % len(theme_palette)],
                f"{title} landscape scenery",
                "city night street",
            ]

            for tier_idx, q in enumerate(candidate_queries):
                if not q:
                    continue
                try:
                    urls = await search_images(q, max_results=15)
                    if not urls:
                        continue

                    for url in urls:
                        try:
                            path = await download_image(url, save_path, seen_hashes=seen_hashes)
                            if path:
                                return {
                                    "path": path,
                                    "lyric_index": i,
                                    "search_query": q,
                                }
                        except Exception as e:
                            logger.debug(f"Failed to download {url}: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Image search tier {tier_idx+1} failed for line {i}: {e}")
                    continue

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
    lyrics: list[dict], artist: str, title: str, theme_palette: list[str] | None = None
) -> list[str]:
    """Use LLM to generate image search queries for each lyric line.

    Processes in batches to stay within token limits.
    """
    all_queries: list[str] = []
    lyric_texts = [line["text"] for line in lyrics]
    palette = theme_palette or [f"{title} scenery"]

    for batch_start in range(0, len(lyric_texts), BATCH_SIZE):
        batch = lyric_texts[batch_start : batch_start + BATCH_SIZE]

        await rate_limiter.acquire(estimated_tokens=500)

        try:
            llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5, max_tokens=2000)
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
            content = str(response.content or "")
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
                    fallback_q = palette[len(cleaned) % len(palette)]
                    cleaned.append(fallback_q)
                all_queries.extend(cleaned[: len(batch)])
            else:
                logger.warning("Could not parse JSON query array from LLM, falling back to thematic palette")
                all_queries.extend([
                    palette[idx % len(palette)]
                    for idx in range(len(all_queries), len(all_queries) + len(batch))
                ])

        except Exception as e:
            logger.warning(f"LLM query generation failed: {e}")
            all_queries.extend([
                palette[idx % len(palette)]
                for idx in range(len(all_queries), len(all_queries) + len(batch))
            ])

    return all_queries
