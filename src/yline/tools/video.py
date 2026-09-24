from __future__ import annotations
from langsmith import traceable
"""Video assembly tool — builds lyric videos with MoviePy 2.x.

Composites text overlays on background images, synced to audio.
"""

import logging
import os
from typing import Any

from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
    ColorClip,
)

logger = logging.getLogger(__name__)


@traceable
def assemble_video(
    lyrics: list[dict[str, Any]],
    image_paths: list[str],
    audio_path: str | None,
    output_path: str,
    resolution: tuple[int, int] = (1920, 1080),
    test_mode: bool = False,
) -> str:
    """Assemble a synced lyric video using MoviePy 2.x.

    For each lyric line, creates a clip with:
    - Background: the corresponding image (resized to fill) or black
    - Foreground: white text with black outline, centered

    Args:
        lyrics: List of dicts with text, start_ms, end_ms
        image_paths: List of image file paths (1 per lyric line)
        audio_path: Path to audio file, or None for silent video
        output_path: Where to save the final .mp4
        resolution: Output resolution (width, height)

    Returns:
        The output file path
    """
    clips = []
    w, h = resolution

    # Validate images and maintain 1:1 mapping with lyrics
    mapped_images = []
    for p in image_paths:
        if p and os.path.isfile(p):
            try:
                _ = ImageClip(p)
                mapped_images.append(p)
            except Exception:
                mapped_images.append(None)
        else:
            mapped_images.append(None)
            
    # Find first valid image to use as ultimate fallback
    last_valid = None
    for p in mapped_images:
        if p is not None:
            last_valid = p
            break
            
    # Propagate last valid image forward to fill holes
    final_images = []
    for p in mapped_images:
        if p is not None:
            last_valid = p
        final_images.append(last_valid)

    def create_clip(img_path, text, duration):
        if duration <= 0:
            duration = 0.5
            
        # Background clip
        if img_path and os.path.isfile(img_path):
            try:
                bg = ImageClip(img_path).with_duration(duration)
                img_ratio = bg.w / bg.h
                target_ratio = w / h
                if img_ratio > target_ratio:
                    bg = bg.resized(height=h)
                else:
                    bg = bg.resized(width=w)
                
                # Center-crop
                x_center = bg.w / 2
                y_center = bg.h / 2
                bg = bg.cropped(
                    x1=x_center - w / 2,
                    y1=y_center - h / 2,
                    x2=x_center + w / 2,
                    y2=y_center + h / 2
                )
            except Exception as e:
                logger.warning(f"Failed to load image {img_path}: {e}")
                bg = ColorClip(size=(w, h), color=(0, 0, 0)).with_duration(duration)
        else:
            bg = ColorClip(size=(w, h), color=(0, 0, 0)).with_duration(duration)

        # Text overlay
        if text:
            try:
                txt = (
                    TextClip(
                        text=text,
                        font_size=50,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        size=(w - 200, 300),
                        method="caption",
                        text_align="center",
                    )
                    .with_position("center")
                    .with_duration(duration)
                )
                
                # Semi-transparent background box behind text (fixed height)
                txt_bg = (
                    ColorClip(size=(w, 300), color=(0, 0, 0))
                    .with_opacity(0.6)
                    .with_position("center")
                    .with_duration(duration)
                )
                
                composite = CompositeVideoClip([bg, txt_bg, txt], size=(w, h))
            except Exception as e:
                logger.warning(f"TextClip failed: {e}")
                composite = bg
        else:
            composite = bg
            
        return composite

    # Add Intro Clip if lyrics don't start at 0
    if lyrics and lyrics[0]["start_ms"] > 0:
        intro_duration = lyrics[0]["start_ms"] / 1000.0
        intro_img = final_images[0] if final_images else None
        
        # Get song title/artist from state or derive from output_path
        file_name = os.path.basename(output_path).replace(".mp4", "")
        intro_text = f"Now Playing\n\n{file_name}"
        
        intro_clip = create_clip(intro_img, intro_text, intro_duration)
        clips.append(intro_clip)

    for i, line in enumerate(lyrics):
        start_sec = line["start_ms"] / 1000.0
        end_sec = line["end_ms"] / 1000.0
        duration = end_sec - start_sec

        text = line.get("text", "")
        
        img_path = final_images[i] if i < len(final_images) else (final_images[-1] if final_images else None)
        
        clip = create_clip(img_path, text, duration)
        clips.append(clip)
        
        # Add gap clip if there is a delay before the NEXT line
        if i < len(lyrics) - 1:
            next_start_sec = lyrics[i+1]["start_ms"] / 1000.0
            gap_duration = next_start_sec - end_sec
            if gap_duration > 0.1:
                gap_clip = create_clip(img_path, "", gap_duration)
                clips.append(gap_clip)

    if not clips:
        clips = [ColorClip(size=(w, h), color=(0, 0, 0)).with_duration(5.0)]

    audio = None
    if audio_path and os.path.isfile(audio_path):
        try:
            audio = AudioFileClip(audio_path)
        except Exception as e:
            logger.warning(f"Failed to load audio {audio_path}: {e}")

    # Build clips list ...
    final = concatenate_videoclips(clips, method="compose")

    # Handle audio and padding
    if test_mode and audio:
        audio = audio.subclipped(0, min(audio.duration, final.duration))
        final = final.with_audio(audio)
    elif audio and audio.duration > final.duration:
        gap = audio.duration - final.duration
        # Use the last image for the outro if available, else black
        outro_img = final_images[-1] if final_images else None
        outro = create_clip(outro_img, "", gap)
        final = concatenate_videoclips([final, outro], method="compose")
        final = final.with_audio(audio)
    elif audio:
        # Visual is longer than audio (rare, but truncate visual)
        final = final.with_duration(audio.duration).with_audio(audio)

    # Write output (try GPU nvenc first, fallback to CPU libx264)
    try:
        final.write_videofile(
            output_path,
            fps=24,
            codec="h264_nvenc",
            audio_codec="aac",
            threads=16,
            ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart", "-preset", "p4", "-tune", "hq"],
            logger="bar",
        )
    except Exception as e:
        logger.warning(f"NVENC encoding failed ({e}), falling back to libx264 CPU encoder...")
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=8,
            ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart", "-preset", "medium"],
            logger="bar",
        )

    return output_path


ASSEMBLE_VIDEO_TOOL = {
    "type": "function",
    "function": {
        "name": "assemble_video",
        "description": "Assemble a synced lyric video from lyrics, images, and audio.",
        "parameters": {
            "type": "object",
            "properties": {
                "lyrics": {
                    "type": "array",
                    "description": "Synced lyrics with text, start_ms, end_ms",
                    "items": {"type": "object"},
                },
                "image_paths": {
                    "type": "array",
                    "description": "Background image paths (1 per line)",
                    "items": {"type": "string"},
                },
                "audio_path": {
                    "type": "string",
                    "description": "Path to audio file",
                },
                "output_path": {
                    "type": "string",
                    "description": "Output .mp4 path",
                },
            },
            "required": ["lyrics", "image_paths", "output_path"],
        },
    },
}
