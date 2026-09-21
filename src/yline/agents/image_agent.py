"""Image agent — generates search queries per lyric line and downloads images.

Uses the LLM to create evocative image search queries based on lyric content,
then scrapes DuckDuckGo for matching images.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from yline.state import PipelineState
from yline.tools.images import search_images, download_image
from yline.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a visual artist agent. Given a song's lyrics, generate image search queries for each line.

Rules:
- The search query MUST use the EXACT WORDS from the lyric line itself.
- DO NOT hallucinate abstract moods, feelings, or new imagery (e.g., if the lyric is "river in a dry land", search for "river in a dry land", NOT "desolate landscape water").
- If the lyric is very long, extract the most important exact words from the line.
- Remove filler words (ooh, yeah, ah) and punctuation.
- DO NOT invent any new words that are not present in the original lyric text.

Respond with a JSON array of search queries, one per lyric line.
Example: For lyrics ["A river in a dry land", "The last ace in a lost hand"], respond with: ["river in a dry land", "last ace in a lost hand"]
"""

# Batch size for LLM calls (process lyrics in chunks to stay within token limits)
BATCH_SIZE = 15


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

    # Step 2: Download images for each query
    images = []
    for i, (lyric, query) in enumerate(zip(lyrics, all_queries)):
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
                        path = await download_image(url, save_path)
                        if not path:
                            raise ValueError("download_image returned None")
                        images.append({
                            "path": path,
                            "lyric_index": i,
                            "search_query": query,
                        })
                        break  # Got one valid image, break loop
                    except Exception as e:
                        logger.warning(f"Failed to download {url}: {e}")
                        continue
                else:
                    # All URLs failed — add placeholder
                    images.append({
                        "path": "",
                        "lyric_index": i,
                        "search_query": query,
                    })
            else:
                images.append({
                    "path": "",
                    "lyric_index": i,
                    "search_query": query,
                })
        except Exception as e:
            logger.warning(f"Image search failed for line {i}: {e}")
            images.append({
                "path": "",
                "lyric_index": i,
                "search_query": query,
            })

    logger.info(f"Downloaded {sum(1 for img in images if img['path'])} / {len(images)} images")
    return {"images": images}


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
            llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7, max_tokens=800)
            response = llm.invoke([
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
            content = response.content
            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                queries = json.loads(content[start:end])
                # Ensure we have the right number of queries
                while len(queries) < len(batch):
                    queries.append(f"{artist} aesthetic background")
                all_queries.extend(queries[: len(batch)])
            else:
                # Fallback: use generic queries
                all_queries.extend([f"{text[:30]} aesthetic" for text in batch])

        except Exception as e:
            logger.warning(f"LLM query generation failed: {e}")
            all_queries.extend([f"{text[:30]} aesthetic" for text in batch])

    return all_queries
