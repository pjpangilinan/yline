"""Song resolver agent — interprets user queries and finds song metadata.

Takes a potentially vague query like "that queen song about real life"
and resolves it to structured metadata via MusicBrainz.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq

from yline.state import PipelineState, SongMetadata
from yline.tools.music_search import SEARCH_MUSIC_TOOL, search_music
from yline.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a music expert agent. Your job is to resolve a user's song query to exact metadata.

Instructions:
1. Call search_music to look up recordings on MusicBrainz. Pass 'query', and optionally 'artist' and 'title' if recognized.
2. When query results are returned, select the best matching recording and call return_song with the artist, title, album, and release year.
3. If search_music results are ambiguous or after searching, call return_song with the known artist, title, album, and year. Never fail to call return_song.
4. Call the tools directly without extra conversational text.
"""

TOOL_MAP = {
    "search_music": search_music,
}


async def song_resolver_node(state: PipelineState) -> dict[str, Any]:
    """LangGraph node: resolve a song query to structured metadata.

    Args:
        state: Current pipeline state with song_query

    Returns:
        State update with song_metadata or error
    """
    query = state["song_query"]
    errors = list(state.get("errors", []))
    retry_counts = dict(state.get("retry_counts", {}))

    logger.info(f"Resolving song query: {query}")

    # Fast-path: Normalize dashes and check for clear "Artist - Title" or "Title by Artist"
    norm_query = query.replace("–", "-").replace("—", "-").strip()
    direct_match = None
    if " - " in norm_query:
        parts = norm_query.split(" - ", 1)
        artist_cand, title_cand = parts[0].strip().strip('"\''), parts[1].strip().strip('"\'')
        try:
            search_res = await search_music(norm_query, artist=artist_cand, title=title_cand)
            if search_res.get("status") == "found" and search_res.get("results"):
                direct_match = search_res["results"][0]
        except Exception:
            pass
    elif " by " in norm_query.lower():
        import re
        parts = re.split(r"\s+by\s+", norm_query, maxsplit=1, flags=re.IGNORECASE)
        title_cand, artist_cand = parts[0].strip().strip('"\''), parts[1].strip().strip('"\'')
        try:
            search_res = await search_music(norm_query, artist=artist_cand, title=title_cand)
            if search_res.get("status") == "found" and search_res.get("results"):
                direct_match = search_res["results"][0]
        except Exception:
            pass

    if direct_match and direct_match.get("artist") and direct_match.get("title"):
        logger.info(f"Direct match found: {direct_match['artist']} - {direct_match['title']}")
        metadata = SongMetadata(
            artist=direct_match["artist"],
            title=direct_match["title"],
            album=direct_match.get("album"),
            year=direct_match.get("year"),
            duration_sec=direct_match.get("duration_sec"),
            musicbrainz_id=direct_match.get("musicbrainz_id"),
        )
        return {
            "song_metadata": metadata.model_dump(),
            "retry_counts": retry_counts,
        }

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=500,
    )

    messages: list = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Find the song: {norm_query}"),
    ]

    # Tools definition
    RETURN_SONG_TOOL = {
        "type": "function",
        "function": {
            "name": "return_song",
            "description": "Call this tool when you have found the correct song metadata to return it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist": {"type": "string"},
                    "title": {"type": "string"},
                    "album": {"type": "string"},
                    "year": {"type": "integer"},
                    "duration_sec": {"type": "number"},
                    "musicbrainz_id": {"type": "string"}
                },
                "required": ["artist", "title"]
            }
        }
    }
    
    tools = [SEARCH_MUSIC_TOOL, RETURN_SONG_TOOL]
    max_iterations = 4

    for iteration in range(max_iterations):
        await rate_limiter.acquire(estimated_tokens=300)

        try:
            response = await llm.ainvoke(messages, tools=tools)
        except Exception as e:
            logger.warning(f"LLM call failed: {e}. Falling back to direct MusicBrainz search.")
            try:
                search_res = await search_music(norm_query)
                if search_res.get("status") == "found" and search_res.get("results"):
                    best = search_res["results"][0]
                    metadata = SongMetadata(
                        artist=best["artist"],
                        title=best["title"],
                        album=best.get("album"),
                        year=best.get("year"),
                        duration_sec=best.get("duration_sec"),
                        musicbrainz_id=best.get("musicbrainz_id"),
                    )
                    return {
                        "song_metadata": metadata.model_dump(),
                        "retry_counts": retry_counts,
                    }
            except Exception:
                pass
            errors.append(f"Song resolver LLM error: {e}")
            return {"errors": errors}

        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            rate_limiter.record_usage(
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            )

        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                func_name = tool_call["name"]
                func_args = tool_call["args"]

                if func_name == "return_song":
                    logger.info(f"Resolved from LLM tool: {func_args.get('artist')} - {func_args.get('title')}")
                    metadata = SongMetadata(
                        artist=func_args.get("artist", "Unknown"),
                        title=func_args.get("title", "Unknown"),
                        album=func_args.get("album"),
                        year=func_args.get("year"),
                        duration_sec=func_args.get("duration_sec"),
                        musicbrainz_id=func_args.get("musicbrainz_id")
                    )
                    return {
                        "song_metadata": metadata.model_dump(),
                        "retry_counts": retry_counts,
                    }

                logger.info(f"Tool call: {func_name}({func_args})")
                if func_name == "search_music":
                    try:
                        result = await search_music(**func_args)
                    except Exception as e:
                        result = {"status": "error", "message": str(e)}
                else:
                    result = {"status": "error", "message": f"Unknown tool: {func_name}"}

                messages.append(
                    ToolMessage(
                        content=json.dumps(result),
                        tool_call_id=tool_call["id"],
                    )
                )
        else:
            if iteration < max_iterations - 1:
                messages.append(
                    HumanMessage(content="Please use the search_music tool to find the song, or return_song if you found it.")
                )

    # Fallback: if search iterations exhausted, prompt LLM to return best known metadata
    try:
        await rate_limiter.acquire(estimated_tokens=200)
        fallback_res = await llm.ainvoke(
            messages + [HumanMessage(content=f"Now call return_song directly with the known artist and title for: {query}")],
            tools=[RETURN_SONG_TOOL],
        )
        if fallback_res.tool_calls:
            for tc in fallback_res.tool_calls:
                if tc["name"] == "return_song":
                    args = tc["args"]
                    logger.info(f"Resolved from fallback: {args.get('artist')} - {args.get('title')}")
                    metadata = SongMetadata(
                        artist=args.get("artist", "Unknown"),
                        title=args.get("title", "Unknown"),
                        album=args.get("album"),
                        year=args.get("year"),
                        duration_sec=args.get("duration_sec"),
                        musicbrainz_id=args.get("musicbrainz_id")
                    )
                    return {
                        "song_metadata": metadata.model_dump(),
                        "retry_counts": retry_counts,
                    }
    except Exception as e:
        logger.debug(f"Fallback resolution failed: {e}")

    errors.append(f"Could not resolve song: {query}")
    retry_counts["song_resolver"] = retry_counts.get("song_resolver", 0) + 1
    return {"errors": errors, "retry_counts": retry_counts}
