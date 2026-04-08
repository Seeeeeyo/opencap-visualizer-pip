# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-04-08

### Added

- **Realtime live streaming API** (same WebSocket protocol as the visualizer; no full precomputed JSON required for your own server):
  - `build_live_init_dict`, `build_live_frame_dict` — construct `init` / `frame` message dicts.
  - `send_live_init`, `send_live_frame`, `broadcast_live_frame` — async send helpers (`mesh_load_delay` on init, default 1.0s, use `0` for low latency).
  - `skeleton_bodies_metadata`, `skeleton_bodies_from_visualizer_json` — skeleton metadata from visualizer `bodies` or a template file.
- **Refactor**: file replay `stream_from_json` now uses the same builders so protocol output stays consistent.

## [1.4.1] - 2026-04-08

### Added

- **Live stream CLI**: `--port N` when the default **8765** is already in use; clearer error if bind fails (`EADDRINUSE`).

## [1.4.0] - 2026-04-08

### Added

- **Live IK WebSocket streaming** (same protocol as the OpenCap Visualizer “Live IK Stream” panel).
  - Optional dependency: `pip install opencap-visualizer[live]` (installs `websockets`).
  - CLI: `opencap-visualizer-stream` / `opencap-viz-stream` (same arguments as the repo’s `live_stream_from_json.py`).
  - Python API: `stream_from_json`, `send_notification`, `send_camera`, `send_trial_scores`, and related helpers are exported from `opencap_visualizer`.
  - Run as a module: `python -m opencap_visualizer.live_stream subject.json`.

## [1.3.0] - 2026-03-23

### ✨ Added
- **Geometry model selection**: Choose the visualization mesh set to match the web app’s “Select Model” dialog.
  - CLI: `--model LaiArnold` (default) or `--model Hu_ISB_shoulder`
  - Python API: `model="LaiArnold"` or `model="Hu_ISB_shoulder"` on `generate_video` / `create_video` / `create_video_async`
  - Headless runs avoid the interactive model dialog by applying the selected model before loading JSON or after OpenSim conversion.

### Notes
- Requires a visualizer build that exposes the same `modelChoices` folder names (`Session.vue`).

## [1.2.0] - 2026-01-13

### 🐛 Fixed
- **Smooth Video Recording**: Replaced MediaRecorder-based capture with frame-by-frame screenshot capture
  - Videos now render at consistent 30fps (was ~3fps due to headless browser throttling)
  - Guaranteed smooth motion in all generated videos
- **Multi-subject Camera Centering**: Added fallback when THREE.js is not globally accessible

### ✨ Added
- **Automatic Frame Rate Downsampling**: High frame rate animations (e.g., 100fps) are automatically downsampled to 30fps for optimal file size
- **Progress Reporting**: Real-time capture progress with ETA during frame-by-frame recording
- **Chrome Optimization Flags**: Additional headless browser flags for improved rendering performance

### 🔧 Changed
- Video generation now requires ffmpeg (was optional, now required for frame compilation)

## [1.1.2] - 2025-09-19

### ✨ Added
- **Version Flag**: Added `--version` flag to CLI for easy version checking
  - Standard CLI behavior: `opencap-visualizer --version`
  - Shows program name and version number

## [1.1.1] - 2025-09-19

### 🐛 Fixed
- **Loop Count Bug**: Fixed critical issue where requested loop count was ignored
  - Previously: Requesting 5 loops would only record ~2-3 loops
  - Now: Requesting 5 loops correctly records exactly 5 loops
  - Root cause: Session.vue loop counting logic had off-by-one error
  - Solution: Added automatic compensation in CLI/API layer
- **Video Recording Format**: Enhanced format detection and conversion
  - Better handling of MP4 vs WebM output based on file extension
  - Improved ffmpeg fallback logic for format conversion
  - More robust error handling for unsupported formats
- **Minimum Duration Logic**: Improved automatic loop adjustment for short animations
  - Short animations (<3 seconds) automatically get more loops for usable videos
  - Clear logging when automatic adjustments are made
  - Respects user intent while ensuring video quality

### ✨ Added
- **Version Flag**: Added `--version` flag to CLI for easy version checking
  - Standard CLI behavior: `opencap-visualizer --version`
  - Shows program name and version number

### 🔧 Enhanced
- **Debug Logging**: Added comprehensive logging for troubleshooting
  - Browser console integration for better debugging
  - Clear messages about format choices and loop adjustments
  - Verbose mode shows all recording parameters
- **Error Messages**: More informative error messages and warnings
- **Documentation**: Updated API documentation with loop behavior notes

## [1.1.0] - 2024-07-30

### 🚨 BREAKING CHANGES
- **Package renamed**: `opencap-visualizer-cli` → `opencap-visualizer`
  - Command-line interface remains the same: `opencap-visualizer` and `opencap-viz`
  - Python imports now use: `import opencap_visualizer`

### ✨ Added
- **Python API**: Full programmatic access to video generation functionality
  - `OpenCapVisualizer` class for object-oriented usage  
  - `create_video()` and `create_video_async()` convenience functions
  - Async and sync support for different use cases
  - Comprehensive type hints and documentation
- **Enhanced CLI**: Improved command-line interface
  - Better error messages and progress indicators
  - Verbose mode for debugging and development
  - More robust file handling and validation
- **Format Support**: Extended file format compatibility
  - JSON files (pre-processed motion data)
  - .osim + .mot pairs (OpenSim models with motion)
  - Better error handling for invalid formats

### 🔧 Improved
- **Performance**: Optimized video generation pipeline
- **Reliability**: Enhanced error handling and recovery
- **Documentation**: Comprehensive README and API documentation
- **Testing**: Added automated testing infrastructure

### 🏗️ Infrastructure
- **Build System**: Updated packaging and distribution
- **CI/CD**: Automated testing and deployment
- **Dependencies**: Updated to latest stable versions

## [1.0.0] - 2024-07-15

### ✨ Initial Release
- Command-line tool for generating videos from biomechanics data
- Support for JSON and OpenSim file formats
- Configurable camera angles and visualization options
- Web-based visualization engine
- Cross-platform compatibility (Windows, macOS, Linux)
