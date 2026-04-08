# Testing the live WebSocket API (v1.5+)

Requires `pip install -e ".[live]"` (or `pip install opencap-visualizer[live]`).

## 1. Smoke test (no browser)

Verifies builders and optional skeleton loader:

```bash
python -c "
from opencap_visualizer import build_live_init_dict, build_live_frame_dict, skeleton_bodies_metadata
b = {'pelvis': {'attachedGeometries': ['p.vtk'], 'scaleFactors': [1,1,1]}}
init = build_live_init_dict([{'id': 't', 'bodies': b}], frame_rate=30)
frame = build_live_frame_dict({'t': {'time': 0.0, 'bodies': {'pelvis': {'rotation':[0,0,0], 'translation':[0,1,0]}}}})
assert init['type'] == 'init' and frame['type'] == 'frame'
print('OK')
"
```

With a visualizer export on disk (paths relative to your machine):

```bash
python -c "
from pathlib import Path
from opencap_visualizer import skeleton_bodies_from_visualizer_json, build_live_init_dict
p = Path('path/to/visualizer_export.json')
meta = skeleton_bodies_from_visualizer_json(p)
d = build_live_init_dict([{'id': 'demo', 'bodies': meta, 'model': 'LaiArnold'}], frame_rate=30)
print(len(d['subjects'][0]['bodies']), 'bones')
"
```

## 2. Minimal server + visualizer UI

1. Copy `examples/realtime_live_server.py` (see below) or paste the README example from `README.md` (Realtime streaming section).
2. Set `TEMPLATE_JSON` to an absolute path to any visualizer JSON that includes a non-empty `bodies` map.
3. Run: `python examples/realtime_live_server.py`
4. Open the OpenCap Visualizer, **Live IK Stream**, connect to `ws://localhost:8765` (or your `--port`).
5. Press **Play** on the timeline so incoming frames update the pose.

## 3. Optional: raw WebSocket client

While the server runs:

```bash
python -c "
import asyncio, json, websockets
async def t():
    async with websockets.connect('ws://127.0.0.1:8765') as ws:
        print('init', json.loads(await ws.recv())['type'])
        print('frame', json.loads(await asyncio.wait_for(ws.recv(), timeout=5))['type'])
asyncio.run(t())
"
```

## File replay CLI (regression)

Still supported for full-motion JSON files:

```bash
opencap-visualizer-stream /path/to/trial.json 2.0
```

See `README.md` and `CHANGELOG.md` for flags and release notes.
