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
            
    # Calculate end_ms:
    # 1. Estimate natural vocal duration based on word count (~400ms/word + 1500ms baseline padding).
    #    Bounded between 3000ms (3.0s minimum read time) and 6500ms.
    # 2. For natural vocal pauses (gap <= 5500ms), hold the subtitle continuously until the next line starts.
    # 3. For long instrumental breaks (> 5500ms, e.g. guitar solo / bridge), display for natural vocal duration
    #    and leave the remaining duration as a clean instrumental gap without freezing subtitles.
    for i in range(len(parsed_lines)):
        text_words = len(parsed_lines[i]["text"].split())
        vocal_duration = max(3000, min(text_words * 400 + 1500, 6500))
        
        if i < len(parsed_lines) - 1:
            next_start = parsed_lines[i + 1]["start_ms"]
            gap_to_next = next_start - parsed_lines[i]["start_ms"]
            if gap_to_next <= 5500:
                parsed_lines[i]["end_ms"] = next_start
            else:
                display_dur = min(vocal_duration, gap_to_next - 2000)
                parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + max(2500, display_dur)
        else:
            parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + vocal_duration
            
    return parsed_lines

@traceable
async def fetch_synced_lyrics(
    artist: str,
    title: str,
    target_duration_sec: float | None = None,
    album: str | None = None,
) -> list[dict[str, Any]] | None:
    """Fetch synced lyrics from LRCLIB with retries and timeout.
    
    Args:
        artist: Artist name
        title: Track name
        target_duration_sec: Optional expected duration in seconds
        album: Optional expected album name
        
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
                        valid_tracks = [t for t in results if t.get("syncedLyrics")]
                        if valid_tracks:
                            clean_t = title.lower().strip()
                            clean_a = artist.lower().strip()
                            clean_alb = album.lower().strip() if album else ""

                            unwanted_keywords = [
                                "demo", "demos", "early demo", "work in progress", "wip",
                                "unreleased", "live", "acoustic", "instrumental", "karaoke",
                                "remix", "cover", "preview", "snippet"
                            ]

                            def track_rank(t: dict) -> tuple[float, float]:
                                t_name = t.get("trackName", "").lower().strip()
                                a_name = t.get("artistName", "").lower().strip()
                                alb_name = t.get("albumName", "").lower().strip()
                                dur = float(t.get("duration") or 210.0)

                                penalty = 0.0

                                # Penalize instrumental flag
                                if t.get("instrumental") is True:
                                    penalty += 100.0

                                # Penalize unwanted keywords (demo, live, acoustic, etc.) unless requested
                                for kw in unwanted_keywords:
                                    if kw in t_name and kw not in clean_t:
                                        penalty += 55.0
                                    if kw in alb_name and kw not in clean_alb:
                                        penalty += 45.0

                                # Exact / substring title match
                                if t_name == clean_t:
                                    penalty -= 50.0
                                elif clean_t in t_name or t_name in clean_t:
                                    penalty -= 25.0
                                else:
                                    penalty += 40.0

                                # Artist match
                                if clean_a == a_name:
                                    penalty -= 40.0
                                elif clean_a in a_name or a_name in clean_a:
                                    penalty -= 25.0
                                elif any(w in a_name for w in clean_a.split() if len(w) > 3):
                                    penalty -= 15.0
                                else:
                                    penalty += 35.0

                                # Album match bonus
                                if clean_alb and clean_alb in alb_name:
                                    penalty -= 20.0

                                # Duration scoring
                                if target_duration_sec is not None and target_duration_sec > 0:
                                    dur_diff = abs(dur - target_duration_sec)
                                    if dur_diff <= 3.0:
                                        penalty -= 35.0
                                    elif dur_diff <= 8.0:
                                        penalty -= 20.0
                                    elif dur_diff > 30.0:
                                        penalty += 35.0
                                    dur_dist = dur_diff
                                else:
                                    # Sensible default commercial song range: 75s to 480s
                                    if dur < 45.0:
                                        penalty += 80.0
                                    elif dur < 75.0:
                                        penalty += 40.0
                                    elif dur > 600.0:
                                        penalty += 40.0
                                    dur_dist = abs(dur - 215.0)

                                return (penalty, dur_dist)

                            best_track = min(valid_tracks, key=track_rank)
                            return parse_lrc(best_track["syncedLyrics"])
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
