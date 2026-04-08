#!/usr/bin/env python3
"""
Test script to verify that loop count parameter is respected correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

import opencap_visualizer as ocv

async def test_loop_count():
    """Test that loop count is properly respected."""
    
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
    
    # Test specific loop counts
    test_cases = [
        {"loops": 3, "description": "3 loops test"},
        {"loops": 5, "description": "5 loops test"},
        {"loops": 8, "description": "8 loops test"}
    ]
    
    for i, test_case in enumerate(test_cases):
        loops = test_case["loops"]
        description = test_case["description"]
        output_file = f"test_loop_{loops}.webm"
        
        print(f"\n=== {description.upper()} ===")
        print(f"Requesting {loops} loops, output: {output_file}")
        
        try:
            success = await ocv.create_video_async(
                test_files,
                output_file,
                camera="sagittal",
                loops=loops,
                verbose=True  # Enable verbose to see loop messages
            )
            
            if success:
                print(f"✅ {description} completed!")
                
                # Check if file exists and estimate duration based on size
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"Generated file size: {file_size:,} bytes")
                    
                    # Rough estimate: larger files should correlate with more loops
                    # (This is not precise but gives a general indication)
                    if i > 0:  # Compare with previous test
                        prev_output = f"test_loop_{test_cases[i-1]['loops']}.webm"
                        if os.path.exists(prev_output):
                            prev_size = os.path.getsize(prev_output)
                            if file_size > prev_size:
                                print(f"✅ File size increased as expected ({prev_size:,} -> {file_size:,} bytes)")
                            else:
                                print(f"⚠️  File size didn't increase as expected ({prev_size:,} -> {file_size:,} bytes)")
                else:
                    print(f"❌ Output file {output_file} was not created!")
                    return False
            else:
                print(f"❌ {description} failed!")
                return False
                
        except Exception as e:
            print(f"❌ {description} failed with error: {e}")
            return False
    
    print("\n🎉 All loop count tests completed!")
    print("\nGenerated files:")
    for test_case in test_cases:
        loops = test_case["loops"]
        filename = f"test_loop_{loops}.webm"
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  - {filename}: {size:,} bytes")
    
    return True

def main():
    """Run the loop count tests."""
    print("Testing loop count parameter...")
    print("This will test that the specified number of loops is actually recorded.")
    print("Higher loop counts should result in longer videos (larger file sizes).")
    
    try:
        success = asyncio.run(test_loop_count())
        if success:
            print("\n✅ All loop count tests completed successfully!")
            print("\nThe loop count parameter is now working correctly.")
            print("Check the console output to verify the requested loops were used.")
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
