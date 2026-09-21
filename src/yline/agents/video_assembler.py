"""Video assembler — combines lyrics, images, and audio into final .mp4.

This is a deterministic node (no LLM calls). Uses MoviePy to composite
each lyric line as text over its corresponding background image,
synced to the audio track.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from yline.state import PipelineState
from yline.tools.video import assemble_video

logger = logging.getLogger(__name__)


async def video_assembler_node(state: PipelineState) -> dict[str, Any]:
    """LangGraph node: assemble the final lyric video.

    Args:
        state: Current pipeline state with lyrics, images, audio_path

    Returns:
        State update with video_path or error
    """
    lyrics = state.get("lyrics", [])
    images = state.get("images", [])
    audio_path = state.get("audio_path")
    metadata = state.get("song_metadata", {})
    errors = list(state.get("errors", []))

    if not lyrics:
        errors.append("Video assembler: no lyrics available")
        return {"errors": errors}

    artist = metadata.get("artist", "Unknown")
    title = metadata.get("title", "Unknown")

    # Build output path
    output_dir = os.path.join("output", f"{artist} - {title}".replace("/", "_"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{artist} - {title}.mp4".replace("/", "_"))

    # Map images to lyric lines
    image_paths = []
    for i in range(len(lyrics)):
        # Find the image for this lyric index
        matching = [img for img in images if img.get("lyric_index") == i]
        if matching and matching[0].get("path"):
            image_paths.append(matching[0]["path"])
        else:
            image_paths.append("")  # Will use black background

    logger.info(
        f"Assembling video: {len(lyrics)} lines, "
        f"{sum(1 for p in image_paths if p)} images, "
        f"audio={'yes' if audio_path else 'no'}"
    )

    try:
        result_path = assemble_video(
            lyrics=lyrics,
            image_paths=image_paths,
            audio_path=audio_path,
            output_path=output_path,
            test_mode=state.get("test_mode", False),
        )
        logger.info(f"Video assembled: {result_path}")
        return {"video_path": result_path}
    except Exception as e:
        logger.error(f"Video assembly failed: {e}")
        errors.append(f"Video assembly error: {e}")
        return {"errors": errors}
