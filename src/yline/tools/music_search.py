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

    import re

    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def _token_similarity(candidate_text: str, expected_text: str) -> float:
        c_tokens = _tokenize(candidate_text)
        e_tokens = _tokenize(expected_text)
        if not e_tokens:
            return 1.0 if not c_tokens else 0.0
        if not c_tokens:
            return 0.0
        overlap = len(c_tokens.intersection(e_tokens))
        if overlap == 0:
            return 0.0
        p = overlap / len(c_tokens)
        r = overlap / len(e_tokens)
        return 2.0 * (p * r) / (p + r)

    def _select_canonical_release(releases: list[dict[str, Any]]) -> tuple[str | None, int | None, bool]:
        """Pick the best official studio release and return (album_title, release_year, is_clean_studio)."""
        if not releases:
            return None, None, False

        def release_sort_key(rel: dict[str, Any]):
            rg = rel.get("release-group", {})
            is_official = 1 if rel.get("status") == "Official" else 0
            is_primary_album = 1 if rg.get("primary-type") in ("Album", "EP", "Single") else 0
            has_no_secondary = 1 if not rg.get("secondary-types") else 0
            return (has_no_secondary, is_primary_album, is_official)

        best_rel = max(releases, key=release_sort_key)
        album_title = best_rel.get("title")
        year = None
        if best_rel.get("date"):
            try:
                year = int(best_rel["date"][:4])
            except (ValueError, IndexError):
                pass
        rg_best = best_rel.get("release-group", {})
        is_clean_studio = (
            best_rel.get("status") == "Official"
            and rg_best.get("primary-type") in ("Album", "EP", "Single")
            and not rg_best.get("secondary-types")
        )
        return album_title, year, is_clean_studio

    def recording_rank(rec: dict[str, Any]) -> float:
        ac_list = rec.get("artist-credit", [])
        if ac_list and isinstance(ac_list[0], dict):
            rec_artist = "".join(ac.get("name", "") + ac.get("joinphrase", "") for ac in ac_list).strip()
        else:
            rec_artist = ""
        rec_title = rec.get("title", "")

        t_sim = _token_similarity(rec_title, title or query)
        a_sim = _token_similarity(rec_artist, artist or query)

        releases = rec.get("releases", [])
        _, _, is_clean_studio = _select_canonical_release(releases)
        studio_score = 1.0 if is_clean_studio else 0.0
        rel_count_score = min(1.0, len(releases) / 6.0)

        return 0.40 * t_sim + 0.30 * a_sim + 0.20 * studio_score + 0.10 * rel_count_score

    recordings = sorted(recordings, key=recording_rank, reverse=True)

    # Extract results
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
        album, year, _ = _select_canonical_release(releases)

        length_ms = rec.get("length")
        duration_sec = round(length_ms / 1000.0, 1) if length_ms else None

        results.append({
            "artist": artist_name,
            "title": rec_title,
            "album": album,
            "year": year,
            "duration_sec": duration_sec,
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
