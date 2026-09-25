from __future__ import annotations
from langsmith import traceable

import asyncio
import os
import yt_dlp
import logging
import imageio_ffmpeg

logger = logging.getLogger(__name__)

@traceable
async def download_audio(
    query: str,
    output_dir: str,
    target_duration_sec: float | None = None,
) -> str | None:
    """Download studio audio from YouTube using yt-dlp.

    Filters out live versions, concert recordings, slowed/reverb, and remixes
    to ensure perfect audio-to-lyric synchronization.

    Args:
        query: YouTube search query
        output_dir: Directory to save the audio file
        target_duration_sec: Target duration in seconds (from synced lyrics) if known
    """
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'socket_timeout': 15,
        'extract_audio': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    loop = asyncio.get_running_loop()

    def _sync_find_and_download() -> str | None:
        # Search for candidates
        candidates = []
        search_terms = [
            f"{query} official audio",
            f"{query} lyric video",
            f"{query}",
        ]

        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            for st in search_terms:
                try:
                    res = ydl.extract_info(f"ytsearch5:{st}", download=False)
                    if res and 'entries' in res:
                        candidates.extend(res['entries'])
                except Exception as e:
                    logger.debug(f"Search failed for '{st}': {e}")
                if len(candidates) >= 5:
                    break

        if not candidates:
            return None

        # Score and rank candidates: penalize live/concert/remix/slowed
        best_entry = None
        best_score = float('inf')

        for entry in candidates:
            title = entry.get('title', '').lower()
            uploader = (entry.get('uploader') or entry.get('channel') or '').lower()
            dur = entry.get('duration') or 0

            # Penalty for live or altered versions
            penalty = 0.0
            live_keywords = ['live', 'concert', 'festival', 'tour', 'acoustic live', 'live at', 'session']
            if any(k in title for k in live_keywords):
                penalty += 150.0

            altered_keywords = ['remix', 'slowed', 'reverb', 'speed up', 'nightcore', 'instrumental', 'karaoke', 'cover']
            if any(k in title for k in altered_keywords):
                penalty += 150.0

            # Bonus for studio/official tags
            if 'official audio' in title or 'lyric' in title or 'audio' in title or 'topic' in uploader:
                penalty -= 10.0

            # Duration delta if target duration known
            dur_diff = abs(dur - target_duration_sec) if target_duration_sec and dur > 0 else 0.0
            # If duration is wildly off (>45s mismatch), heavy penalty
            if target_duration_sec and dur > 0 and abs(dur - target_duration_sec) > 45:
                penalty += 100.0

            score = penalty + dur_diff
            if score < best_score:
                best_score = score
                best_entry = entry

        if not best_entry:
            best_entry = candidates[0]

        target_url = best_entry.get('url') or best_entry.get('webpage_url') or best_entry.get('id')
        logger.info(f"Selected audio candidate: {best_entry.get('title')} (score: {best_score:.1f})")

        # Download the best candidate
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                if not info:
                    return None
                expected_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                if os.path.exists(expected_path) and os.path.getsize(expected_path) > 0:
                    return expected_path

                # Fallback: check output_dir for newest mp3
                mp3_files = [
                    os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.lower().endswith(".mp3")
                ]
                if mp3_files:
                    return max(mp3_files, key=os.path.getmtime)
        except Exception as e:
            logger.warning(f"Audio download execution failed: {e}")

        return None

    return await loop.run_in_executor(None, _sync_find_and_download)

DOWNLOAD_AUDIO_TOOL = {
    "type": "function",
    "function": {
        "name": "download_audio",
        "description": "Download audio from YouTube.",
        "parameters": {
            "type": "object",
            "properties": {
                "artist": {
                    "type": "string",
                    "description": "Artist name",
                },
                "title": {
                    "type": "string",
                    "description": "Track title",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save the output file",
                }
            },
            "required": ["artist", "title", "output_dir"],
        },
    },
}
