#!/usr/bin/env python3
"""
Test script to verify the video recording fix works for both MP4 and WebM outputs.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

import opencap_visualizer as ocv

async def test_recording_formats():
    """Test recording in both MP4 and WebM formats."""
    
    # Test files (assuming these exist in the current directory)
    test_files = [
        "model.osim",
        "motion.mot"
    ]
    
    # Find an existing test file
    test_file = None
    for file in test_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("No test files found. Please ensure you have a JSON data file to test with.")
        return False
    
    print(f"Using test file: {test_file}")
    
    # Test 1: MP4 output
    print("\n=== Testing MP4 Output ===")
    try:
        success = await ocv.create_video_async(
            test_files,
            "test_output.mp4",
            camera="anterior",
            loops=5,
            verbose=True
        )
        if success:
            print("✅ MP4 recording test passed!")
        else:
            print("❌ MP4 recording test failed!")
            return False
    except Exception as e:
        print(f"❌ MP4 recording test failed with error: {e}")
        return False
    
    # Test 2: WebM output
    print("\n=== Testing WebM Output ===")
    try:
        success = await ocv.create_video_async(
            test_files,
            "test_output.webm",
            camera="anterior", 
            loops=5,
            verbose=True
        )
        if success:
            print("✅ WebM recording test passed!")
        else:
            print("❌ WebM recording test failed!")
            return False
    except Exception as e:
        print(f"❌ WebM recording test failed with error: {e}")
        return False
    
    print("\n🎉 All recording format tests passed!")
    return True

def main():
    """Run the recording format tests."""
    print("Testing video recording fixes...")
    print("This will test both MP4 and WebM output formats to ensure they work correctly.")
    
    try:
        success = asyncio.run(test_recording_formats())
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
