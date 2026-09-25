from __future__ import annotations
from langsmith import traceable

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
    # Match standard LRC line: [mm:ss.xx] or [mm:ss.xxx] text
    pattern = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)')
    offset_pattern = re.compile(r'\[offset:\s*([+-]?\d+)\]', re.IGNORECASE)
    
    global_offset_ms = 0
    raw_lines = lrc_text.strip().split('\n')
    for raw in raw_lines:
        off_match = offset_pattern.match(raw.strip())
        if off_match:
            try:
                global_offset_ms = int(off_match.group(1))
            except ValueError:
                pass

    parsed_lines = []
    for line in raw_lines:
        match = pattern.match(line.strip())
        if match:
            mins, secs, text = match.groups()
            text_str = text.strip()
            if text_str:  # Filter out empty text lines / empty instrumental markers
                # Standard LRC offset: positive offset means lyrics play earlier (or later depending on spec, standard is track delay)
                start_ms = int(int(mins) * 60000 + float(secs) * 1000) + global_offset_ms
                start_ms = max(0, start_ms)
                parsed_lines.append({
                    "text": text_str,
                    "start_ms": start_ms
                })
            
    # Calculate end_ms: cap dialogue display during long instrumental breaks (>4.5s)
    # to avoid subtitles freezing across guitar solos / interludes.
    for i in range(len(parsed_lines)):
        if i < len(parsed_lines) - 1:
            next_start = parsed_lines[i + 1]["start_ms"]
            gap = next_start - parsed_lines[i]["start_ms"]
            if gap > 4500:
                parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + 4000
            else:
                parsed_lines[i]["end_ms"] = next_start
        else:
            # For the last line, display for up to 4 seconds
            parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + 4000
            
    return parsed_lines

@traceable
async def fetch_synced_lyrics(artist: str, title: str) -> list[dict[str, Any]] | None:
    """Fetch synced lyrics from LRCLIB with retries and timeout.
    
    Args:
        artist: Artist name
        title: Track name
        
    Returns:
        List of dicts with text, start_ms, end_ms, or None if not found.
    """
    import asyncio
    headers = {
        "User-Agent": "YLine/0.1.0 (https://github.com/pjpangilinan/yline)"
    }
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                res = await client.get(
                    "https://lrclib.net/api/search",
                    params={"q": f"{artist} {title}"},
                )
                if res.status_code == 200:
                    results = res.json()
                    if results:
                        for track in results:
                            if track.get("syncedLyrics"):
                                return parse_lrc(track["syncedLyrics"])
                    return None
                elif res.status_code == 429:
                    await asyncio.sleep(2.0 * (attempt + 1))
                    continue
        except Exception:
            await asyncio.sleep(1.0 * (attempt + 1))
    return None

@traceable
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
        if song and song.lyrics:
            text = song.lyrics
            # Strip Genius header lines e.g. "Song Name Lyrics"
            text = re.sub(r'^.*?[Ll]yrics\s*\n', '', text)
            # Strip section headers [Chorus], [Verse 1] etc.
            text = re.sub(r'\[.*?\]', '', text)
            # Strip trailing "123Embed" from Genius
            text = re.sub(r'\d*Embed$', '', text).strip()
            return text if text else None
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
