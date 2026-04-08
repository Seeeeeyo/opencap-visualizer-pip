#!/usr/bin/env python3
"""
Minimal realtime WebSocket server for testing the visualizer **Live IK Stream** panel.

Requires: pip install opencap-visualizer[live]

Example::

    python examples/realtime_live_server.py /path/to/visualizer_export.json
    python examples/realtime_live_server.py /path/to/export.json --port 8766

In the browser: connect to ws://localhost:8765 (or your host/port), then press **Play**
on the timeline so frames update the pose.
"""

from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Test OpenCap Visualizer live WebSocket stream")
    parser.add_argument(
        "template_json",
        help="Any visualizer JSON with a non-empty bodies map (attachedGeometries / scaleFactors)",
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--subject-id", default="ik", dest="subject_id")
    parser.add_argument("--model", default="LaiArnold")
    parser.add_argument("--camera", default="anterior")
    parser.add_argument("--fps", type=float, default=30.0)
    args = parser.parse_args()

    try:
        import websockets
    except ImportError:
        print("Install websockets: pip install opencap-visualizer[live]", file=sys.stderr)
        sys.exit(1)

    from opencap_visualizer import (
        build_live_init_dict,
        send_live_init,
        send_live_frame,
        skeleton_bodies_from_visualizer_json,
    )

    meta = skeleton_bodies_from_visualizer_json(args.template_json)
    init_dict = build_live_init_dict(
        [
            {
                "id": args.subject_id,
                "label": "Realtime test",
                "bodies": meta,
                "model": args.model,
            }
        ],
        frame_rate=args.fps,
        camera=args.camera,
    )
    dt = 1.0 / args.fps

    async def handler(websocket: object) -> None:
        await send_live_init(websocket, init_dict, mesh_load_delay=0.5)
        t = 0.0
        while True:
            bodies = {
                name: {"rotation": [0.0, 0.0, 0.0], "translation": [0.0, 1.0, 0.0]}
                for name in meta
            }
            await send_live_frame(
                websocket,
                {args.subject_id: {"time": t, "bodies": bodies}},
            )
            t += dt
            await asyncio.sleep(dt)

    async def run() -> None:
        async with websockets.serve(handler, args.host, args.port):
            print(
                f"Listening ws://{args.host}:{args.port} — "
                "open Live IK Stream in the visualizer, connect, then press Play."
            )
            await asyncio.Future()

    asyncio.run(run())


if __name__ == "__main__":
    main()
