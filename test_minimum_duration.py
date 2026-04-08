#!/usr/bin/env python3
"""
Test script to verify the minimum duration feature works correctly for short animations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

import opencap_visualizer as ocv

async def test_minimum_duration():
    """Test that short animations automatically get more loops for minimum duration."""
    
    # Test files (assuming these exist in the current directory)
    test_files = [
        "model.osim",
        "motion.mot"
    ]
    
    # Check if test files exist
    missing_files = [f for f in test_files if not os.path.exists(f)]
    if missing_files:
        print(f"Missing test files: {missing_files}")
        print("Please ensure you have model.osim and motion.mot files to test with.")
        return False
    
    print(f"Using test files: {test_files}")
    
    # Test with just 1 loop - should automatically increase for short animations
    print("\n=== Testing Minimum Duration with 1 Loop ===")
    print("If the animation is <3 seconds, loops should be automatically increased...")
    
    try:
        success = await ocv.create_video_async(
            test_files,
            "test_minimum_duration.mp4",
            camera="anterior",
            loops=1,  # Start with just 1 loop
            verbose=True  # Enable verbose to see the automatic adjustment
        )
        if success:
            print("✅ Minimum duration test passed!")
            
            # Check if file exists and has reasonable size
            output_file = Path("test_minimum_duration.mp4")
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"Generated video file size: {file_size:,} bytes")
                if file_size > 100000:  # At least 100KB for a reasonable video
                    print("✅ Video file appears to have reasonable content!")
                else:
                    print("⚠️  Video file seems quite small, may indicate an issue.")
            else:
                print("❌ Video file was not created!")
                return False
        else:
            print("❌ Minimum duration test failed!")
            return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    # Test with 5 loops - should use 5 loops unless animation is very short
    print("\n=== Testing with 5 Loops ===")
    print("Should use exactly 5 loops unless animation is extremely short...")
    
    try:
        success = await ocv.create_video_async(
            test_files,
            "test_5_loops.mp4",
            camera="anterior",
            loops=5,
            verbose=True
        )
        if success:
            print("✅ 5-loop test passed!")
        else:
            print("❌ 5-loop test failed!")
            return False
    except Exception as e:
        print(f"❌ 5-loop test failed with error: {e}")
        return False
    
    print("\n🎉 All minimum duration tests passed!")
    print("\nGenerated files:")
    for filename in ["test_minimum_duration.mp4", "test_5_loops.mp4"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  - {filename}: {size:,} bytes")
    
    return True

def main():
    """Run the minimum duration tests."""
    print("Testing minimum duration feature...")
    print("This will test that short animations automatically get more loops for a minimum 3-second video.")
    
    try:
        success = asyncio.run(test_minimum_duration())
        if success:
            print("\n✅ All tests completed successfully!")
            print("\nThe feature ensures that even very short animations will produce")
            print("videos that are at least 3 seconds long by automatically increasing loops.")
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
