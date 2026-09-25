"""LangGraph pipeline — orchestrates all agents into a directed graph.

Song Query → Song Resolver → Lyrics Agent → Image Agent → Audio Agent → Video Assembler → .mp4
"""
from __future__ import annotations

import logging
import json
import os
from typing import Any

from langgraph.graph import StateGraph, END

from yline.state import PipelineState
from yline.agents.song_resolver import song_resolver_node
from yline.agents.lyrics_agent import lyrics_agent_node
from yline.agents.image_agent import image_agent_node
from yline.agents.audio_agent import audio_agent_node
from yline.agents.video_assembler import video_assembler_node

logger = logging.getLogger(__name__)


def _should_continue_after_resolver(state: PipelineState) -> str:
    """Route after song resolver: continue or error."""
    if state.get("song_metadata"):
        return "lyrics_agent"
    retries = state.get("retry_counts", {}).get("song_resolver", 0)
    if retries < 3:
        return "song_resolver"  # Retry
    return "error"


def _should_continue_after_lyrics(state: PipelineState) -> str:
    """Route after lyrics agent: continue or error."""
    if state.get("lyrics"):
        return "image_agent"
    return "error"


def _should_continue_after_images(state: PipelineState) -> str:
    """Always continue to audio agent (images are best-effort)."""
    return "audio_agent"


def _should_continue_after_audio(state: PipelineState) -> str:
    """Route after audio agent: continue or retry or error."""
    if state.get("audio_path"):
        return "video_assembler"
    
    retry_counts = state.get("retry_counts", {})
    if retry_counts.get("audio_agent", 0) < 3:
        return "audio_agent"
        
    return "error"


async def error_node(state: PipelineState) -> dict[str, Any]:
    """Terminal error node — logs accumulated errors."""
    errors = state.get("errors", [])
    logger.error(f"Pipeline failed with {len(errors)} error(s):")
    for err in errors:
        logger.error(f"  - {err}")
    return {}


def route_start(state: PipelineState) -> str:
    """Route from start based on cached state."""
    if not state.get("song_metadata"): return "song_resolver"
    if not state.get("lyrics"): return "lyrics_agent"
    if not state.get("images"): return "image_agent"
    if not state.get("audio_path"): return "audio_agent"
    if not state.get("video_path"): return "video_assembler"
    return "video_assembler"


def build_graph() -> StateGraph:
    """Build the LangGraph pipeline.

    Returns:
        Compiled LangGraph StateGraph ready to invoke
    """
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("song_resolver", song_resolver_node)
    graph.add_node("lyrics_agent", lyrics_agent_node)
    graph.add_node("image_agent", image_agent_node)
    graph.add_node("audio_agent", audio_agent_node)
    graph.add_node("video_assembler", video_assembler_node)
    graph.add_node("error", error_node)

    # Set entry point
    graph.add_conditional_edges(
        "__start__",
        route_start,
        {
            "song_resolver": "song_resolver",
            "lyrics_agent": "lyrics_agent",
            "image_agent": "image_agent",
            "audio_agent": "audio_agent",
            "video_assembler": "video_assembler",
        },
    )

    # Add conditional edges
    graph.add_conditional_edges(
        "song_resolver",
        _should_continue_after_resolver,
        {
            "lyrics_agent": "lyrics_agent",
            "song_resolver": "song_resolver",
            "error": "error",
        },
    )

    graph.add_conditional_edges(
        "lyrics_agent",
        _should_continue_after_lyrics,
        {
            "image_agent": "image_agent",
            "error": "error",
        },
    )

    graph.add_edge("image_agent", "audio_agent")

    graph.add_conditional_edges(
        "audio_agent",
        _should_continue_after_audio,
        {
            "video_assembler": "video_assembler",
            "audio_agent": "audio_agent",
            "error": "error",
        },
    )

    # Terminal edges
    graph.add_edge("video_assembler", END)
    graph.add_edge("error", END)

    return graph.compile()


async def run_pipeline(
    song_query: str, test_mode: bool = False, force: bool = False
) -> PipelineState:
    """Run the full lyric video pipeline.

    Args:
        song_query: User's song query (can be vague)
        test_mode: Truncate processing to 15 seconds for rapid E2E testing
        force: Ignore cached state and run all nodes from scratch

    Returns:
        Final pipeline state with video_path or errors
    """
    graph = build_graph()
    
    safe_query = "".join(c if c.isalnum() else "_" for c in song_query).strip("_")
    state_file = f"output/{safe_query}_state.json"
    os.makedirs("output", exist_ok=True)
    
    if os.path.exists(state_file) and not force:
        with open(state_file, "r") as f:
            initial_state = json.load(f)
            # Ensure test_mode flag is updated even on cached loads
            initial_state["test_mode"] = test_mode
            logger.info(f"Loaded cached state from {state_file}")
    else:
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except Exception:
                pass
        initial_state = {
            "song_query": song_query,
            "test_mode": test_mode,
            "song_metadata": None,
            "lyrics": [],
            "images": [],
            "audio_path": None,
            "video_path": None,
            "errors": [],
            "retry_counts": {},
        }

    logger.info(f"Starting pipeline for: {song_query}")
    
    final_state = dict(initial_state) if initial_state else {}
    # Run graph node by node so we can cache progress
    async for event in graph.astream(initial_state):
        for node_name, state_update in event.items():
            if isinstance(state_update, dict):
                final_state.update(state_update)
            # Cache state after every node
            with open(state_file, "w") as f:
                json.dump(final_state, f, indent=2)
            logger.info(f"Saved state after {node_name}")

    logger.info(f"Pipeline complete. Video: {final_state.get('video_path', 'FAILED') if final_state else 'FAILED'}")

    return final_state
