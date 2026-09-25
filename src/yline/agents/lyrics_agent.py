"""Lyrics agent — fetches synced lyrics from LRCLIB, falls back to Genius.

Takes song metadata and returns timestamped lyric lines for video assembly.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq

from yline.state import PipelineState, LyricLine
from yline.tools.lyrics import (
    FETCH_LYRICS_TOOL,
    fetch_synced_lyrics,
    fetch_plain_lyrics,
)
from yline.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a lyrics retrieval agent. Your job is to fetch synced (timestamped) lyrics 
for a given song.

Use the fetch_lyrics tool with the artist and title. The tool will try LRCLIB first for synced lyrics,
then fall back to Genius for plain lyrics.

If you get synced lyrics, return them as-is. If you only get plain lyrics, split them into lines
and estimate timing based on a typical song duration of 3-4 minutes, spacing lines evenly.

Respond with the lyrics data in JSON format.
"""

TOOL_MAP = {
    "fetch_lyrics": None,  # We handle this specially
}


async def lyrics_agent_node(state: PipelineState) -> dict[str, Any]:
    """LangGraph node: fetch synced lyrics for the resolved song.

    Args:
        state: Current pipeline state with song_metadata

    Returns:
        State update with lyrics list or error
    """
    metadata = state.get("song_metadata")
    errors = list(state.get("errors", []))

    if not metadata:
        errors.append("Lyrics agent: no song metadata available")
        return {"errors": errors}

    artist = metadata["artist"]
    title = metadata["title"]
    logger.info(f"Fetching lyrics for: {artist} - {title}")

    # Step 1: Try LRCLIB for synced lyrics (no LLM needed for this)
    try:
        synced = await fetch_synced_lyrics(artist, title)
        if synced:
            # Filter out empty lines
            lyrics = [line for line in synced if line["text"].strip()]
            
            # TEST MODE: Truncate to first 5 lines
            if state.get("test_mode"):
                lyrics = lyrics[:5]
                logger.info(f"TEST MODE: Truncated to {len(lyrics)} lines")
                
            logger.info(f"Got {len(lyrics)} synced lyric lines from LRCLIB")
            return {"lyrics": lyrics}
    except Exception as e:
        logger.warning(f"LRCLIB fetch failed: {e}")

    # Step 2: Try Genius for plain lyrics
    try:
        loop = asyncio.get_running_loop()
        plain = await loop.run_in_executor(None, fetch_plain_lyrics, artist, title)
        if plain:
            logger.info("Got plain lyrics from Genius, estimating timing")
            lyrics = _estimate_timing(plain)
            return {"lyrics": lyrics}
    except Exception as e:
        logger.warning(f"Genius fetch failed: {e}")

    # Step 3: Use LLM to try alternative search terms
    await rate_limiter.acquire(estimated_tokens=200)

    try:
        llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=300)
        response = await llm.ainvoke([
            SystemMessage(content="Suggest 2 alternative artist/title combinations to search for lyrics. Return JSON array of {artist, title} objects."),
            HumanMessage(content=f"Original: {artist} - {title}"),
        ])

        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            rate_limiter.record_usage(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

        # Try alternatives
        try:
            content = response.content
            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                alternatives = json.loads(content[start:end])
                for alt in alternatives:
                    try:
                        synced = await fetch_synced_lyrics(alt["artist"], alt["title"])
                        if synced:
                            lyrics = [l for l in synced if l["text"].strip()]
                            logger.info(f"Found lyrics via alternative: {alt['artist']} - {alt['title']}")
                            return {"lyrics": lyrics}
                    except Exception:
                        continue
        except (json.JSONDecodeError, KeyError):
            pass
    except Exception as e:
        logger.warning(f"LLM alternative search failed: {e}")

    errors.append(f"No lyrics found for: {artist} - {title}")
    return {"errors": errors}


def _estimate_timing(plain_lyrics: str, total_duration_ms: int = 210_000) -> list[dict]:
    """Split plain lyrics into timed lines with estimated timestamps.

    Args:
        plain_lyrics: Plain text lyrics
        total_duration_ms: Estimated song duration in ms (default 3:30)

    Returns:
        List of lyric line dicts with text, start_ms, end_ms
    """
    lines = [line.strip() for line in plain_lyrics.split("\n") if line.strip()]
    if not lines:
        return []

    interval_ms = total_duration_ms // len(lines)
    result = []
    for i, text in enumerate(lines):
        start = i * interval_ms
        end = (i + 1) * interval_ms
        result.append({
            "text": text,
            "start_ms": start,
            "end_ms": end,
        })
    return result
