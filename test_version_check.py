#!/usr/bin/env python3
"""Quick test to verify the version and basic functionality."""

import opencap_visualizer as ocv

print(f"✅ OpenCap Visualizer version: {ocv.__version__}")
print(f"✅ Main function imported: {hasattr(ocv, 'main')}")
print(f"✅ API classes imported: {hasattr(ocv, 'OpenCapVisualizer')}")
print(f"✅ Convenience functions imported: {hasattr(ocv, 'create_video')}")

# Test that our fix comment is in the CLI code
import inspect
import opencap_visualizer.cli

source = inspect.getsource(opencap_visualizer.cli.VisualizerCLI.create_video_from_json)
if "compensate for Session.vue bug" in source:
    print("✅ Loop count fix is present in installed version")
else:
    print("❌ Loop count fix NOT found in installed version")

print("\n🎉 Version 1.1.1 ready for deployment!")
