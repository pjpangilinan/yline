from __future__ import annotations
from langsmith import traceable

import httpx
from typing import Any

@traceable
async def search_music(
    query: str,
    artist: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Search MusicBrainz for song metadata with rate limiting, retries, and fielded search.
    
    Args:
        query: Song name, optionally with artist
        artist: Optional specific artist name
        title: Optional specific track title
    Returns:
        dict with artist, title, album, year, musicbrainz_id, status
    """
    import asyncio
    url = "https://musicbrainz.org/ws/2/recording"
    headers = {"User-Agent": "YLine/0.1.0 (https://github.com/pjpangilinan/yline)"}

    # Generate candidate search queries, prioritizing fielded search
    candidate_queries: list[str] = []
    if artist and title:
        candidate_queries.append(f'recording:"{title}" AND artist:"{artist}"')
        candidate_queries.append(f'recording:{title} AND {artist}')
    elif " by " in query:
        parts = query.split(" by ", 1)
        t, a = parts[0].strip().strip('"\''), parts[1].strip().strip('"\'')
        candidate_queries.append(f'recording:"{t}" AND artist:"{a}"')
        candidate_queries.append(f'recording:{t} AND {a}')
    elif " - " in query:
        parts = query.split(" - ", 1)
        a, t = parts[0].strip().strip('"\''), parts[1].strip().strip('"\'')
        candidate_queries.append(f'recording:"{t}" AND artist:"{a}"')
        candidate_queries.append(f'recording:{t} AND {a}')

    clean_q = query.strip()
    if clean_q not in candidate_queries:
        candidate_queries.append(clean_q)

    recordings: list[dict[str, Any]] = []
    for cand in candidate_queries:
        params = {
            "query": cand,
            "fmt": "json",
            "limit": 15,
        }
        for attempt in range(2):
            try:
                await asyncio.sleep(1.0)  # MusicBrainz 1 req/sec policy
                async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        recs = data.get("recordings", [])
                        if recs:
                            recordings = recs
                            break
                    elif resp.status_code in (429, 503):
                        await asyncio.sleep(2.0 * (attempt + 1))
                        continue
            except Exception:
                await asyncio.sleep(1.0 * (attempt + 1))
        if recordings:
            break

    if not recordings:
        return {"status": "not_found", "message": f"No results for '{query}'"}

    # Rank and extract results
    results = []
    for rec in recordings:
        ac_list = rec.get("artist-credit", [])
        if ac_list and isinstance(ac_list[0], dict):
            artist_name = "".join(
                ac.get("name", "") + ac.get("joinphrase", "") for ac in ac_list
            ).strip()
        else:
            artist_name = "Unknown"

        rec_title = rec.get("title", query)
        releases = rec.get("releases", [])
        album = releases[0].get("title") if releases else None
        year = None
        if releases and releases[0].get("date"):
            try:
                year = int(releases[0]["date"][:4])
            except (ValueError, IndexError):
                pass

        results.append({
            "artist": artist_name,
            "title": rec_title,
            "album": album,
            "year": year,
            "musicbrainz_id": rec.get("id"),
        })

    return {
        "status": "found",
        "results": results[:5]
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
                },
                "artist": {
                    "type": "string",
                    "description": "Optional specific artist name for high-accuracy search",
                },
                "title": {
                    "type": "string",
                    "description": "Optional specific track title for high-accuracy search",
                },
            },
            "required": ["query"],
        },
    },
}
