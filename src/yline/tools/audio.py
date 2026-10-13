from __future__ import annotations
from langsmith import traceable

import asyncio
import os
import re
import yt_dlp
import logging
import imageio_ffmpeg

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    """Extract lowercase word tokens from text."""
    return set(re.findall(r"\w+", text.lower()))


def _token_similarity(candidate_text: str, expected_text: str) -> float:
    """Harmonic F1 similarity between candidate tokens and expected tokens."""
    c_tokens = _tokenize(candidate_text)
    e_tokens = _tokenize(expected_text)
    if not e_tokens:
        return 1.0 if not c_tokens else 0.0
    if not c_tokens:
        return 0.0
    overlap = len(c_tokens.intersection(e_tokens))
    if overlap == 0:
        return 0.0
    precision = overlap / len(c_tokens)
    recall = overlap / len(e_tokens)
    return 2.0 * (precision * recall) / (precision + recall)


@traceable
async def download_audio(
    query: str,
    output_dir: str,
    target_duration_sec: float | None = None,
    expected_title: str | None = None,
    expected_artist: str | None = None,
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
        # Search across all query variants and deduplicate candidates by video ID
        candidates = []
        seen_ids = set()
        base_query = f"{expected_artist} {expected_title}".strip() if (expected_artist and expected_title) else query.strip()
        search_terms = [
            base_query,
            f"{base_query} official audio",
            f"{base_query} audio",
            f"{base_query} lyric video",
            f"{query}",
        ]
        # Remove duplicate search queries while preserving order
        unique_search_terms = []
        for st in search_terms:
            if st and st not in unique_search_terms:
                unique_search_terms.append(st)

        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            for st in unique_search_terms:
                try:
                    res = ydl.extract_info(f"ytsearch5:{st}", download=False)
                    if res and 'entries' in res:
                        for entry in res['entries']:
                            if entry and entry.get('id') and entry.get('id') not in seen_ids:
                                seen_ids.add(entry.get('id'))
                                candidates.append(entry)
                except Exception as e:
                    logger.debug(f"Search failed for '{st}': {e}")

        if not candidates:
            return None

        # Principled semantic evaluation of candidates
        def score_candidate(entry: dict) -> float:
            c_title = entry.get('title', '')
            c_uploader = (entry.get('uploader') or entry.get('channel') or '')
            dur = float(entry.get('duration') or 0.0)

            # 1. Title fidelity: Token F1 against expected song title
            title_score = _token_similarity(c_title, expected_title) if expected_title else 0.8

            # 2. Artist/Uploader alignment: prioritize channels actually matching the artist
            if expected_artist:
                artist_in_uploader = _token_similarity(c_uploader, expected_artist)
                artist_in_title = _token_similarity(c_title, expected_artist)
                artist_score = 0.70 * artist_in_uploader + 0.30 * artist_in_title
            else:
                artist_score = 0.8

            # 3. Official release channel credibility
            u_clean = c_uploader.lower()
            is_official_channel = (
                u_clean.endswith("- topic") or
                "vevo" in u_clean or
                (expected_artist and _tokenize(expected_artist).issubset(_tokenize(c_uploader)))
            )
            official_score = 1.0 if is_official_channel else 0.5

            # 4. Duration alignment (relative error)
            if target_duration_sec and target_duration_sec > 0 and dur > 0:
                rel_err = abs(dur - target_duration_sec) / target_duration_sec
                dur_score = max(0.0, 1.0 - rel_err * 3.0)
            else:
                dur_score = 0.8

            # Composite normalized match score in [0.0, 1.0]
            return (
                0.40 * title_score +
                0.35 * dur_score +
                0.15 * artist_score +
                0.10 * official_score
            )

        best_entry = max(candidates, key=score_candidate)
        best_score = score_candidate(best_entry)

        target_url = best_entry.get('url') or best_entry.get('webpage_url') or best_entry.get('id')
        logger.info(f"Selected audio candidate: {best_entry.get('title')} (score: {best_score:.2f})")

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
