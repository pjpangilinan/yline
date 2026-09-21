"""Pipeline state models for the yline lyric video generation pipeline.

Defines Pydantic models for structured entities (song metadata, timed lyric lines,
image assets) and the LangGraph TypedDict state used across pipeline nodes.
"""
from __future__ import annotations

from typing import TypedDict
from pydantic import BaseModel, Field


class SongMetadata(BaseModel):
    """Structured metadata resolved for a song.

    Attributes:
        artist: Primary artist or band name.
        title: Title of the song/recording.
        album: Optional release or album title.
        year: Optional release year.
        musicbrainz_id: Optional MusicBrainz recording identifier (UUID).
    """

    artist: str = Field(description="Primary artist or band name")
    title: str = Field(description="Song or recording title")
    album: str | None = Field(default=None, description="Album or release title")
    year: int | None = Field(default=None, description="Release year")
    musicbrainz_id: str | None = Field(
        default=None, description="MusicBrainz recording identifier UUID"
    )


class LyricLine(BaseModel):
    """A single line of lyrics with millisecond-precision timing.

    Attributes:
        text: Plain text content of the lyric line.
        start_ms: Timestamp in milliseconds when the line begins in the audio.
        end_ms: Timestamp in milliseconds when the line ends in the audio.
    """

    text: str = Field(description="Plain text content of the lyric line")
    start_ms: int = Field(description="Start time in milliseconds from audio onset")
    end_ms: int = Field(description="End time in milliseconds from audio onset")


class ImageAsset(BaseModel):
    """Visual asset associated with a specific lyric line.

    Attributes:
        path: Absolute or relative local filesystem path to the saved image.
        lyric_index: 0-based index of the corresponding LyricLine.
        search_query: Search query used to discover or retrieve the image.
    """

    path: str = Field(description="Local path to downloaded image file")
    lyric_index: int = Field(
        description="0-based index of the corresponding lyric line"
    )
    search_query: str = Field(
        description="Search query used to discover or retrieve the image"
    )


class PipelineState(TypedDict, total=False):
    """LangGraph pipeline execution state.

    Serialized dictionaries are used for Pydantic models to ensure compatibility
    with LangGraph state serialization and checkpointing.

    Attributes:
        song_query: Initial user query describing the song to resolve.
        test_mode: Whether the pipeline is running in test mode.
        song_metadata: Serialized SongMetadata dict (via .model_dump()) or None.
        lyrics: Serialized list of LyricLine dicts.
        images: Serialized list of ImageAsset dicts.
        audio_path: Local filesystem path to downloaded song audio, or None.
        video_path: Local filesystem path to assembled final video, or None.
        errors: Accumulated error and warning messages encountered during execution.
        retry_counts: Node retry counter map tracking attempt counts per node.
    """

    song_query: str
    test_mode: bool
    song_metadata: dict | None  # serialized SongMetadata
    lyrics: list[dict]  # serialized list[LyricLine]
    images: list[dict]  # serialized list[ImageAsset]
    audio_path: str | None
    video_path: str | None
    errors: list[str]
    retry_counts: dict[str, int]


__all__ = [
    "SongMetadata",
    "LyricLine",
    "ImageAsset",
    "PipelineState",
]
