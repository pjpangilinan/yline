from __future__ import annotations
from langsmith import traceable

import os
import yt_dlp
import logging
import imageio_ffmpeg

logger = logging.getLogger(__name__)

@traceable
async def download_audio(query: str, output_dir: str) -> str | None:
    """Download audio from YouTube using yt-dlp.
    
    Args:
        query: YouTube search query
        output_dir: Directory to save the audio file
    """
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
    }
    
    search_queries = [f"{query} topic", f"{query} audio", query]
    for sq in search_queries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{sq}", download=True)
                if not info or 'entries' not in info or not info['entries']:
                    continue
                    
                entry = info['entries'][0]
                expected_path = ydl.prepare_filename(entry).rsplit('.', 1)[0] + '.mp3'
                
                if os.path.exists(expected_path):
                    return expected_path
        except Exception as e:
            logger.warning(f"Audio download attempt for '{sq}' failed: {e}")
            continue
    return None

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
