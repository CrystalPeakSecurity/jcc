#!/usr/bin/env python3
"""
benchmark.py - Measure DOOM card performance

Runs game frames for 10 seconds and reports frame time statistics.
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path to import driver
sys.path.insert(0, str(Path(__file__).parent))

from driver import get_session, build_apdu, INS_GAME_FRAME, _build_input_data


def load_recording(path):
    """Load a recording file, returning list of input records."""
    inputs = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            if "f" in record:  # Skip header, only include frame records
                inputs.append(record)
    return inputs


def main():
    recording_file = sys.argv[1] if len(sys.argv) > 1 else None

    # Load recording if provided
    replay_inputs = None
    if recording_file:
        replay_inputs = load_recording(recording_file)
        print(f"Running benchmark using recording: {recording_file}")
        print(f"Frames to process: {len(replay_inputs)}")
        print()
    else:
        duration_seconds = 10
        print(f"Running benchmark for {duration_seconds} seconds...")
        print("Sending frames with zero input (standing still)")
        print()

    frame_times = []
    replay_idx = 0

    try:
        with get_session() as session:
            start_time = time.time()
            frame_count = 0

            # Run until duration (no recording) or until all frames processed (recording)
            while True:
                # Check termination condition
                if replay_inputs:
                    if replay_idx >= len(replay_inputs):
                        break  # Finished all recording frames
                else:
                    if time.time() - start_time >= duration_seconds:
                        break  # Finished 10 second duration

                # Get input: either from replay or zero
                if replay_inputs:
                    inp = replay_inputs[replay_idx]
                    input_data = _build_input_data(inp["f"], inp["s"], inp["r"])
                    replay_idx += 1
                else:
                    input_data = _build_input_data(0, 0, 0)  # No movement

                frame_start = time.time()

                try:
                    session.send_ok(build_apdu(INS_GAME_FRAME, data=input_data))
                    frame_end = time.time()

                    frame_time_ms = (frame_end - frame_start) * 1000
                    frame_times.append(frame_time_ms)
                    frame_count += 1

                except Exception as e:
                    print(f"\nError at frame {frame_count}: {e}")
                    break

            end_time = time.time()
            total_time = end_time - start_time

    except Exception as e:
        print(f"Session error: {e}")
        return 1

    if not frame_times:
        print("No frames completed successfully")
        return 1

    # Calculate statistics
    avg_frame_time = sum(frame_times) / len(frame_times)
    min_frame_time = min(frame_times)
    max_frame_time = max(frame_times)
    avg_fps = 1000 / avg_frame_time if avg_frame_time > 0 else 0

    # Percentiles
    sorted_times = sorted(frame_times)
    p50 = sorted_times[len(sorted_times) * 50 // 100]
    p95 = sorted_times[len(sorted_times) * 95 // 100]
    p99 = sorted_times[len(sorted_times) * 99 // 100]

    # Display results
    print("=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    print(f"Total time:        {total_time:.2f}s")
    print(f"Frames completed:  {frame_count}")
    print(f"Actual FPS:        {frame_count / total_time:.2f}")
    print()
    print("Frame Time (ms):")
    print(f"  Average:         {avg_frame_time:.2f}")
    print(f"  Min:             {min_frame_time:.2f}")
    print(f"  Max:             {max_frame_time:.2f}")
    print(f"  P50 (median):    {p50:.2f}")
    print(f"  P95:             {p95:.2f}")
    print(f"  P99:             {p99:.2f}")
    print()
    print(f"Theoretical FPS:   {avg_fps:.2f}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
