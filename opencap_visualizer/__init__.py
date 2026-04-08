"""
OpenCap Visualizer - Generate videos from biomechanics data files

A tool for creating videos from OpenCap biomechanics data with both
command-line interface and Python API support. Optional live IK streaming
to the web visualizer is available via ``pip install opencap-visualizer[live]``
(``opencap-visualizer-stream`` CLI, realtime ``build_live_init_dict`` / ``send_live_frame``, and related helpers).

Basic Usage:
    Command Line:
        $ opencap-visualizer data.json -o output.mp4
        $ opencap-visualizer subject1.json subject2.json --camera anterior --colors red blue
        $ opencap-visualizer-stream subject.json   # requires [live] extra

    Python API:
        >>> import opencap_visualizer as ocv
        >>> success = ocv.create_video("data.json", "output.mp4")  # Synchronous
        >>> success = await ocv.create_video_async("data.json", "output.mp4")  # Async
        
        >>> visualizer = ocv.OpenCapVisualizer(verbose=True)
        >>> await visualizer.generate_video(
        ...     ["subject1.json", "subject2.json"], 
        ...     "comparison.mp4",
        ...     camera="anterior", 
        ...     colors=["red", "blue"]
        ... )
"""

__version__ = "1.5.0"
__author__ = "Selim Gilon"
__email__ = "selim.gilon@utah.edu"

# Import CLI main function
from .cli import main

# Import Python API
from .api import (
    OpenCapVisualizer,
    create_video,
    create_video_async,
    DEFAULT_OUTPUT_FILENAME,
    DEFAULT_VIEWPORT_SIZE,
    DEFAULT_TIMEOUT
)

_LIVE_STREAM_PUBLIC = (
    "skeleton_bodies_metadata",
    "skeleton_bodies_from_visualizer_json",
    "build_live_init_dict",
    "build_live_frame_dict",
    "send_live_init",
    "send_live_frame",
    "broadcast_live_frame",
    "stream_from_json",
    "send_notification",
    "send_camera",
    "send_subject_visibility",
    "hide_subject",
    "show_subject",
    "send_trial_scores",
    "send_hide_scores",
    "run_live_stream_cli",
)


def __getattr__(name: str):
    if name == "run_live_stream_cli":
        from . import live_stream

        return live_stream.main
    if name in _LIVE_STREAM_PUBLIC:
        from . import live_stream

        return getattr(live_stream, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_LIVE_STREAM_PUBLIC))


__all__ = [
    # CLI
    "main",
    
    # Python API - Main class
    "OpenCapVisualizer",
    
    # Python API - Convenience functions
    "create_video",
    "create_video_async",
    
    # Constants
    "DEFAULT_OUTPUT_FILENAME",
    "DEFAULT_VIEWPORT_SIZE",
    "DEFAULT_TIMEOUT",
    # Live IK streaming (requires pip install opencap-visualizer[live] for WebSocket runtime)
    "skeleton_bodies_metadata",
    "skeleton_bodies_from_visualizer_json",
    "build_live_init_dict",
    "build_live_frame_dict",
    "send_live_init",
    "send_live_frame",
    "broadcast_live_frame",
    "stream_from_json",
    "send_notification",
    "send_camera",
    "send_subject_visibility",
    "hide_subject",
    "show_subject",
    "send_trial_scores",
    "send_hide_scores",
    "run_live_stream_cli",
] 