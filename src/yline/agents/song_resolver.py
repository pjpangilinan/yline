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

SYSTEM_PROMPT = """You are a music expert agent. Your job is to take a user's song query
and resolve it to an exact song using the search_music tool.

The query might be vague ("that sad Radiohead song"), a partial title ("bohemian"),
or exact ("Choosin' Texas by Ella Langley"). You must figure out what song they mean
and search for it.

Rules:
- Always use the search_music tool to look up the song
- If the first search doesn't find a good match, try alternative queries (different spelling, artist name, etc.)
- You have up to 3 search attempts
- Once you find the right song, respond with ONLY the JSON metadata, nothing else
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

    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        max_tokens=500,
    )

    messages: list = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Find the song: {query}"),
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
            logger.error(f"LLM call failed: {e}")
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

    errors.append(f"Could not resolve song: {query}")
    retry_counts["song_resolver"] = retry_counts.get("song_resolver", 0) + 1
    return {"errors": errors, "retry_counts": retry_counts}
