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
    # 1. Estimate natural vocal duration based on word count (~500ms/word + 2000ms baseline padding).
    #    Bounded between 4500ms (4.5s minimum vocal sustain) and 8000ms.
    # 2. For natural musical transitions (gap <= 8000ms), hold the subtitle continuously until the next line starts.
    # 3. For substantial instrumental breaks (> 8000ms, e.g. guitar solo / bridge), display for natural vocal duration
    #    and leave the remaining duration as a clean instrumental break without freezing subtitles.
    for i in range(len(parsed_lines)):
        text_words = len(parsed_lines[i]["text"].split())
        vocal_duration = max(4500, min(text_words * 500 + 2000, 8000))
        
        if i < len(parsed_lines) - 1:
            next_start = parsed_lines[i + 1]["start_ms"]
            gap_to_next = next_start - parsed_lines[i]["start_ms"]
            if gap_to_next <= 8000:
                parsed_lines[i]["end_ms"] = next_start
            else:
                display_dur = min(vocal_duration, gap_to_next - 3000)
                parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + max(4000, display_dur)
        else:
            parsed_lines[i]["end_ms"] = parsed_lines[i]["start_ms"] + vocal_duration
            
    return parsed_lines

def _tokenize(text: str) -> set[str]:
    """Extract lowercase word tokens from text."""
    return set(re.findall(r"\w+", text.lower()))


def _token_similarity(candidate_text: str, expected_text: str) -> float:
    """Harmonic F1 similarity between candidate tokens and expected tokens.
    
    Naturally rewards exact title matches and penalizes unrequested edition modifiers
    (e.g. 'Demo', 'Live', 'Remix') without needing static keyword blacklists.
    """
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
                            def track_rank(t: dict) -> float:
                                t_name = t.get("trackName", "").strip()
                                a_name = t.get("artistName", "").strip()
                                alb_name = t.get("albumName", "").strip()
                                dur = float(t.get("duration") or 0.0)

                                title_score = _token_similarity(t_name, title)
                                artist_score = _token_similarity(a_name, artist)
                                album_score = _token_similarity(alb_name, album) if album else 1.0

                                if target_duration_sec and target_duration_sec > 0 and dur > 0:
                                    rel_err = abs(dur - target_duration_sec) / target_duration_sec
                                    dur_score = max(0.0, 1.0 - rel_err * 2.0)
                                else:
                                    dur_score = 1.0 if (60.0 <= dur <= 600.0) else 0.4

                                inst_penalty = 1.0 if t.get("instrumental") is True else 0.0

                                return (
                                    0.45 * title_score +
                                    0.25 * dur_score +
                                    0.20 * artist_score +
                                    0.10 * album_score -
                                    inst_penalty
                                )

                            best_track = max(valid_tracks, key=track_rank)
                            return parse_lrc(best_track["syncedLyrics"])
                    return None
                elif res.status_code in (429, 500, 502, 503, 504):
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
