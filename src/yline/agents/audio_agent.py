"""Audio agent — downloads song audio from YouTube via yt-dlp.

Simple agent: takes song metadata, searches YouTube, downloads audio.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from yline.state import PipelineState
from yline.tools.audio import download_audio

logger = logging.getLogger(__name__)


async def audio_agent_node(state: PipelineState) -> dict[str, Any]:
    """LangGraph node: download audio for the resolved song.

    Args:
        state: Current pipeline state with song_metadata

    Returns:
        State update with audio_path or error (non-fatal)
    """
    metadata = state.get("song_metadata")
    errors = list(state.get("errors", []))

    if not metadata:
        errors.append("Audio agent: no song metadata available")
        return {"audio_path": None, "errors": errors}

    artist = metadata["artist"]
    title = metadata["title"]
    output_dir = os.path.join("output", f"{artist} - {title}".replace("/", "_"))
    os.makedirs(output_dir, exist_ok=True)

    retry_counts = state.get("retry_counts", {})
    attempts = retry_counts.get("audio_agent", 0)

    suffixes = ["", "official audio", "lyric video", "audio"]
    suffix = suffixes[attempts % len(suffixes)]
    query = f"{artist} - {title} {suffix}".strip()

    # Calculate expected song duration: prioritize official metadata duration, fallback to lyrics bound
    meta_dur = metadata.get("duration_sec")
    lyrics = state.get("lyrics", [])
    lyric_dur = (lyrics[-1]["end_ms"] / 1000.0) if (lyrics and lyrics[-1].get("end_ms")) else None

    if meta_dur and float(meta_dur) > 0:
        target_duration_sec = float(meta_dur)
    elif lyric_dur:
        target_duration_sec = lyric_dur
    else:
        target_duration_sec = None

    logger.info(f"Downloading audio (attempt {attempts+1}): {query} (target dur: {target_duration_sec}s)")

    audio_path = await download_audio(
        query,
        output_dir,
        target_duration_sec=target_duration_sec,
        expected_title=title,
        expected_artist=artist,
    )
    if audio_path:
        logger.info(f"Audio downloaded: {audio_path}")
        return {"audio_path": audio_path}
        
    errors.append(f"Failed to download audio for {artist} - {title}")
    retry_counts = state.get("retry_counts", {})
    retry_counts["audio_agent"] = retry_counts.get("audio_agent", 0) + 1
    return {"audio_path": None, "errors": errors, "retry_counts": retry_counts}
