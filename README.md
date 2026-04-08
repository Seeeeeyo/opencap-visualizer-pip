# OpenCap Visualizer

Generate videos from OpenCap biomechanics data files with both command-line interface and Python API.

This tool uses the deployed [OpenCap Visualizer](https://opencap-visualizer.onrender.com/) to create videos from biomechanics data files (.json, .osim/.mot pairs) using headless browser automation.

## Features

- **Dual Interface**: Both command-line tool and Python API
- **No Local Setup Required**: Uses deployed web application by default
- **Multiple Data Formats**: Supports JSON files and OpenSim .osim/.mot pairs
- **Subject Comparison**: Generate videos with multiple subjects
- **Anatomical Camera Views**: Use biomechanics-friendly camera angles
- **Customizable**: Colors, zoom, centering, loops, and dimensions
- **Geometry model selection**: Choose the S3 geometry set used for visualization (`LaiArnold` or `Hu_ISB_shoulder`), matching the web app’s model picker
- **Automatic 3D Geometry**: Loads realistic human models from cloud storage
- **Realtime live IK WebSocket API**: Build and send `init` / `frame` messages from Python (`build_live_init_dict`, `send_live_frame`, etc.) without a precomputed full-motion JSON

## Installation

```bash
pip install opencap-visualizer
```

**Note**: After installation, you'll need to install browser dependencies:
```bash
playwright install chromium
```

### Live IK streaming (WebSocket server)

Install the optional dependency:

```bash
pip install opencap-visualizer[live]
```

#### Realtime streaming (Python API)

For **incremental** data (IK or any pipeline that produces one pose per timestep), run your own WebSocket server and use the same protocol as the visualizer’s **Live IK Stream** panel:

1. **`build_live_init_dict`** — skeleton metadata (`subjects` with per-body `attachedGeometries` / `scaleFactors`), `frameRate`, optional `camera` / `model` / styles (same options as file replay).
2. **`send_live_init(websocket, init_dict, mesh_load_delay=...)`** — send `init`; use **`mesh_load_delay=0`** for minimal latency after meshes load.
3. **`send_live_frame(websocket, streams)`** — send one timestep; `streams` is `{ subject_id: { "time": float, "bodies": { bone: { "rotation": [...], "translation": [...] } } } }`.
4. **`broadcast_live_frame(streams)`** — same as `send_live_frame` but to every connected client (like `send_notification`).
5. **`skeleton_bodies_from_visualizer_json(path)`** — load bone metadata from any exported visualizer JSON to avoid hand-copying geometry lists.

```python
import asyncio
import websockets
from opencap_visualizer import (
    build_live_init_dict,
    send_live_init,
    send_live_frame,
    skeleton_bodies_from_visualizer_json,
)

TEMPLATE_JSON = "/path/to/one_time_export.json"  # visualizer export with correct bodies/geometries

async def handler(websocket):
    bodies_meta = skeleton_bodies_from_visualizer_json(TEMPLATE_JSON)
    init_dict = build_live_init_dict(
        [{"id": "ik", "label": "Live", "bodies": bodies_meta, "model": "LaiArnold"}],
        frame_rate=60.0,
        camera="anterior",
    )
    await send_live_init(websocket, init_dict, mesh_load_delay=0.0)
    t = 0.0
    dt = 1.0 / 60.0
    while True:
        # Build bodies from your solver: each bone needs rotation [rx,ry,rz] and translation [x,y,z]
        bodies_pose = compute_pose_from_your_ik()  # dict[str, dict]
        await send_live_frame(
            websocket,
            {"ik": {"time": t, "bodies": bodies_pose}},
        )
        t += dt
        await asyncio.sleep(dt)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

# asyncio.run(main())
```

In the browser, connect to `ws://localhost:8765`, then press **Play** on the timeline so new frames update the pose (the client may start paused after `init`).

See **[TESTING.md](TESTING.md)** for smoke tests, `examples/realtime_live_server.py`, and a minimal WebSocket client check.

#### File replay (CLI / testing)

To replay a **full** visualizer JSON file (complete `time` series on disk):

```bash
opencap-visualizer-stream subject.json
# or: opencap-viz-stream subject1.json subject2.json 2.0
```

If **port 8765 is already in use**, use another port and the same port in the visualizer:

```bash
python -m opencap_visualizer.live_stream --port 8766 subject.json
```

Use a **real path** to your JSON (example asset: `opencap-visualizer/public/samples/walk/sample_mono.json` in the web app repo). `python -m opencap_visualizer.live_stream` matches the [main visualizer repo](https://github.com/utahmobl/opencap-visualizer)’s `live_stream_from_json.py`.

#### Live stream CLI reference (file replay)

| Positional | Description |
|------------|-------------|
| `FILE.json` | One or two visualizer JSON files. Subject IDs in the protocol are usually the file stems (e.g. `trial.json` → `trial`). |
| `speed` | Optional number after the JSON paths. Playback uses timestamps in the JSON; **1.0** ≈ real time, **2.0** ≈ 2× faster, **0.5** ≈ half speed. Default **1.0**. Parsed as the last non-`.json` argument that remains after flags. |

| Option | Description |
|--------|-------------|
| `--port N` | Listen port (default **8765**). Use if you see “address already in use”; set the same port in the visualizer WebSocket URL. |
| `--camera …` | Initial camera: anatomical preset (`anterior`, `posterior`, `sagittal_right`, `sagittal_left`, `superior`, `inferior`), axis / corner preset (`front`, `isometric`, `frontTopRight`, …), or inline JSON `{"position":[x,y,z],"target":[x,y,z]}`. |
| `--model …` | Geometry folder name(s) matching the web app (e.g. `LaiArnold`). One value for all subjects, or comma-separated per subject. |
| `--subject-colors` | Comma-separated hex colors, one per subject, e.g. `"#d3d3d3,#4995e0"`. Uniform color per subject (overrides per-bone color from `--body-style` for those subjects). |
| `--subject-opacity` | Comma-separated floats **0–1**, one per subject (whole-model transparency). |
| `--body-style` | Path to a JSON file, or inline JSON: a **single object** applies the same per-bone map to every subject; a **JSON array** gives one object per subject. Bones use `{ "color": "#rrggbb", "visible": true/false, … }` as in the visualizer. |

Flag order is flexible (`--port 8766 --camera anterior subject.json 50` is fine). The server binds to **0.0.0.0** (all interfaces) so other machines on the LAN can use `ws://<your-ip>:<port>`.

**Interactive stdin** (terminal where the server runs; skipped if stdin is not available):

| Command | Effect |
|---------|--------|
| `notify …` / `notify success …` | Banner on connected clients (`info` / `success` / `warning` / `error`). |
| `camera …` | Update camera without reloading subjects (same forms as `--camera`). |
| `scores n1 … n5 …` | Trial scores overlay; optional labels, `colors: g o r …`, `title: …`. |
| `hidescores` | Hide scores overlay. |
| `hide SUBJECT_ID` / `show SUBJECT_ID` | Subject visibility (IDs printed at connect, e.g. file stem). |
| `help` | List commands. |

## Command Line Usage

### Basic Examples

```bash
# Single subject
opencap-visualizer data.json -o output.mp4

# Multiple subjects comparison
opencap-visualizer subject1.json subject2.json -o comparison.mp4

# With custom settings
opencap-visualizer data.json --camera anterior --colors red --loops 2 -o front_view.mp4

# OpenSim files
opencap-visualizer model.osim motion.mot -o simulation.mp4

# Geometry model (must match the visualizer web app options)
opencap-visualizer data.json --model Hu_ISB_shoulder -o shoulder_model.mp4
```

### Advanced Examples

```bash
# Multiple subjects with different colors
opencap-visualizer s1.json s2.json s3.json --colors red green blue --camera sagittal -o side_comparison.mp4

# High-resolution with custom zoom
opencap-visualizer data.json --width 3840 --height 2160 --zoom 0.8 --camera superior -o 4k_top_view.mp4

# Interactive mode for manual exploration
opencap-visualizer data.json --interactive --camera anterior
```

### Camera Views

#### Anatomical Views (Recommended)
- `anterior` / `frontal` / `coronal` - Front-facing view
- `posterior` - Back view  
- `sagittal` / `lateral` - Side profile view
- `superior` - Top-down view
- `inferior` - Bottom-up view

#### Technical Views
- `top`, `bottom`, `front`, `back`, `left`, `right`
- `isometric`, `default`
- Corner views: `frontTopRight`, `backBottomLeft`, etc.

### Geometry model (`--model`)

The web visualizer resolves mesh geometry from named folders on cloud storage. In headless mode, pick the model **before** loading data (same choices as the app’s “Select Model” dialog):

| Value | Description |
|-------|-------------|
| `LaiArnold` | Default Lai Arnold full-body model |
| `Hu_ISB_shoulder` | Hu ISB shoulder model |

```bash
opencap-visualizer trial.json --model LaiArnold -o out.mp4
opencap-visualizer model.osim motion.mot --model Hu_ISB_shoulder -o out.mp4
```

### Command Line Options

```
positional arguments:
  FILE                  Data files (.json, or .osim/.mot pairs)

optional arguments:
  -o, --output PATH     Output video file (default: animation_video.mp4)
  --camera VIEW         Camera preset (anatomical or technical; optional)
  --model MODEL         Geometry folder: LaiArnold (default) or Hu_ISB_shoulder
  --colors COLOR...     Subject colors (hex or names: red, blue, #ff0000)
  --loops N             Animation loops to record (default: 1)
  --width PX            Video width (default: 1920)
  --height PX           Video height (default: 1080)
  --zoom FACTOR         Zoom factor (>1.0 = zoom out, default: 1.5)
  --no-center           Disable auto-centering on subjects
  --timeout SEC         Loading timeout in seconds (default: 120)
  --interactive         Open browser for manual exploration
  --vue-app-path PATH   Custom Vue app index.html path
  --dev-server-url URL  Custom Vue development server URL
  -v, --verbose         Enable verbose output
```

## Python API Usage

### Basic Examples

```python
import opencap_visualizer as ocv

# Simple usage
success = ocv.create_video("data.json", "output.mp4")
if success:
    print("Video generated successfully!")

# Multiple subjects with settings
success = ocv.create_video(
    ["subject1.json", "subject2.json"],
    "comparison.mp4", 
    camera="anterior",
    model="LaiArnold",
    colors=["red", "blue"],
    loops=2,
    verbose=True
)
```

### Class-based Usage

```python
import opencap_visualizer as ocv

# Create visualizer instance
visualizer = ocv.OpenCapVisualizer(verbose=True)

# Generate video synchronously
success = visualizer.generate_video_sync(
    input_files=["subject1.json", "subject2.json"],
    output_path="comparison.mp4",
    camera="sagittal",
    model="Hu_ISB_shoulder",
    colors=["#ff0000", "#00ff00"],
    width=1920,
    height=1080,
    zoom=1.2
)

print(f"Success: {success}")
```

### Async Usage

```python
import asyncio
import opencap_visualizer as ocv

async def generate_videos():
    # Using convenience function
    success = await ocv.create_video_async(
        "data.json", 
        "output.mp4",
        camera="anterior",
        model="LaiArnold",
        colors=["blue"]
    )
    
    # Using class
    visualizer = ocv.OpenCapVisualizer(verbose=True)
    success = await visualizer.generate_video(
        ["s1.json", "s2.json", "s3.json"],
        "triple_comparison.mp4",
        camera="posterior",
        model="LaiArnold",
        colors=["red", "green", "blue"],
        center_subjects=True,
        zoom=1.5
    )
    
    return success

# Run async function
success = asyncio.run(generate_videos())
```

### Live stream control helpers (Python)

With `opencap-visualizer[live]` and clients registered on your WebSocket server (as with the packaged CLI), you can broadcast UI commands to every connected browser:

```python
import asyncio
from opencap_visualizer import send_notification, send_camera

async def ping_clients():
    await send_notification("Stream ready", level="success")
    await send_camera("anterior")

asyncio.run(ping_clients())
```

See **`opencap_visualizer.live_stream`** for `stream_from_json` (file replay), `send_trial_scores`, subject visibility, etc. Realtime **`init` / `frame`** helpers are documented under [Realtime streaming](#realtime-streaming-python-api) above.

### API Reference

#### `OpenCapVisualizer` Class

```python
class OpenCapVisualizer:
    def __init__(self, verbose: bool = False)
    
    async def generate_video(
        self,
        input_files: Union[str, List[str]],
        output_path: str = "animation_video.mp4",
        *,
        vue_app_path: Optional[str] = None,
        dev_server_url: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        timeout_seconds: int = 120,
        loops: int = 1,
        camera: Optional[str] = None,
        center_subjects: bool = True,
        zoom: float = 0.8,
        colors: Optional[List[str]] = None,
        model: str = "LaiArnold",
        interactive: bool = False
    ) -> bool
    
    def generate_video_sync(self, ...) -> bool  # Synchronous wrapper
```

#### Convenience Functions

```python
async def create_video_async(input_files, output_path, **kwargs) -> bool
def create_video(input_files, output_path, **kwargs) -> bool
```

## Data Formats

### JSON Files
The tool accepts biomechanics JSON files with the following structure:
```json
{
  "Data": {
    "ModelScalingVars": "path/to/model.osim",
    "Results": "path/to/motion.mot",
    "FrameTimesOG": [0.0, 0.033, 0.066, ...]
  }
}
```

### OpenSim Files  
Alternatively, provide `.osim` (model) and `.mot` (motion) file pairs:
```bash
opencap-visualizer model.osim motion.mot -o output.mp4
```

## Dependencies

The tool automatically detects the best available option:

1. **Deployed Version** (Recommended): `https://opencap-visualizer.onrender.com/`
   - No local setup required
   - Always up-to-date
   - Requires internet connection

2. **Local Development Server**: `http://localhost:3000`
   - Start with `npm run serve` in the Vue.js project
   - Faster for development/testing

3. **Built Files**: Local `dist/index.html`
   - Build with `npm run build` in the Vue.js project
   - Works offline

## Configuration

### Custom Servers
```bash
# Use local development server
opencap-visualizer data.json --dev-server-url http://localhost:3000

# Use custom built files
opencap-visualizer data.json --vue-app-path /path/to/dist/index.html
```

### Environment Variables
```bash
# Set default development server
export OPENCAP_DEV_SERVER=http://localhost:3000
```

## Troubleshooting

### Browser Installation
If you get browser-related errors:
```bash
playwright install chromium
```

### Connection Issues
- Check internet connection for deployed version
- For local development: `npm run serve` in Vue project
- For built files: `npm run build` in Vue project

### File Format Issues
- Ensure JSON files contain valid biomechanics data structure
- For OpenSim files, provide both `.osim` and `.mot` files
- Check file paths are correct and accessible

### Video Generation Issues
- Increase timeout: `--timeout 300`
- Enable verbose mode: `--verbose` or `verbose=True`
- Try interactive mode: `--interactive`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see the source repository for guidelines.

## Support

For issues and questions:
- GitHub Issues: [https://github.com/utahmobl/opencap-visualizer/issues](https://github.com/utahmobl/opencap-visualizer/issues)
- Web App: [https://opencap-visualizer.onrender.com/](https://opencap-visualizer.onrender.com/) 