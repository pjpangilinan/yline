from __future__ import annotations
from langsmith import traceable

import httpx
from typing import Any

@traceable
async def search_music(query: str) -> dict[str, Any]:
    """Search MusicBrainz for song metadata with rate limiting and retries.
    
    Args:
        query: Song name, optionally with artist
    Returns:
        dict with artist, title, album, year, musicbrainz_id, status
    """
    import asyncio
    url = "https://musicbrainz.org/ws/2/recording"
    params = {
        "query": query,
        "fmt": "json",
        "limit": 5,
    }
    headers = {"User-Agent": "YLine/0.1.0 (https://github.com/pjpangilinan/yline)"}
    
    for attempt in range(3):
        try:
            await asyncio.sleep(1.0)  # MusicBrainz 1 req/sec policy
            async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    break
                elif resp.status_code == 503 or resp.status_code == 429:
                    await asyncio.sleep(2.0 * (attempt + 1))
                    continue
        except Exception:
            await asyncio.sleep(1.0 * (attempt + 1))
    else:
        return {"status": "not_found", "message": f"Service unavailable for '{query}'"}
        
    recordings = data.get("recordings", [])
    if not recordings:
        return {"status": "not_found", "message": f"No results for '{query}'"}
    
    results = []
    for rec in recordings[:3]:
        artist = rec.get("artist-credit", [{}])[0].get("name", "Unknown")
        title = rec.get("title", query)
        releases = rec.get("releases", [])
        album = releases[0].get("title") if releases else None
        year = None
        if releases and releases[0].get("date"):
            try:
                year = int(releases[0]["date"][:4])
            except (ValueError, IndexError):
                pass
        
        results.append({
            "artist": artist,
            "title": title,
            "album": album,
            "year": year,
            "musicbrainz_id": rec.get("id"),
        })
        
    return {
        "status": "found",
        "results": results
    }

SEARCH_MUSIC_TOOL = {
    "type": "function",
    "function": {
        "name": "search_music",
        "description": "Search MusicBrainz for song metadata (artist, title, album, year). Use when you need to resolve a song query into structured metadata.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Song name and optionally artist, e.g. 'Bohemian Rhapsody Queen'",
                }
            },
            "required": ["query"],
        },
    },
}
