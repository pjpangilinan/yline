from __future__ import annotations

import os
import re
import httpx
from typing import Any
import lyricsgenius

def parse_lrc(lrc_text: str) -> list[dict[str, Any]]:
    """Parse LRC format lyrics into structured data.
    
    Args:
        lrc_text: The LRC string, e.g., '[00:12.34] line text'
        
    Returns:
        List of dicts with text, start_ms, end_ms.
    """
    lines = []
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
    
    parsed_lines = []
    for line in lrc_text.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            mins, secs, text = match.groups()
            start_ms = int(int(mins) * 60000 + float(secs) * 1000)
            parsed_lines.append({
                "text": text.strip(),
                "start_ms": start_ms
            })
            
    # Calculate end_ms based on the start_ms of the next line
    for i in range(len(parsed_lines)):
        if i < len(parsed_lines) - 1:
            parsed_lines[i]["end_ms"] = parsed_lines[i + 1]["start_ms"]
        else:
            # For the last line, add 5 seconds
            parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + 5000
            
    return parsed_lines

async def fetch_synced_lyrics(artist: str, title: str) -> list[dict[str, Any]] | None:
    """Fetch synced lyrics from LRCLIB.
    
    Args:
        artist: Artist name
        title: Track name
        
    Returns:
        List of dicts with text, start_ms, end_ms, or None if not found.
    """
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://lrclib.net/api/search",
                params={"q": f"{artist} {title}"},
                timeout=10.0
            )
            res.raise_for_status()
            results = res.json()
            
            if not results:
                return None
                
            # Find the first result with synced lyrics
            for track in results:
                if track.get("syncedLyrics"):
                    return parse_lrc(track["syncedLyrics"])
                    
            return None
    except Exception:
        return None

def fetch_plain_lyrics(artist: str, title: str) -> str | None:
    """Fetch plain lyrics using lyricsgenius.
    
    Args:
        artist: Artist name
        title: Track name
        
    Returns:
        String of plain lyrics, or None if not found.
    """
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if not token:
        return None
        
    try:
        genius = lyricsgenius.Genius(token)
        genius.verbose = False
        song = genius.search_song(title, artist)
        if song:
            return song.lyrics
    except Exception:
        return None
    return None

FETCH_LYRICS_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_synced_lyrics",
        "description": "Fetch synced lyrics for a track.",
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
                }
            },
            "required": ["artist", "title"],
        },
    },
}
