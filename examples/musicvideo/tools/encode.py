#!/usr/bin/env python3
"""
encode.py - Convert video to RLE-compressed 2bpp C header for Music Video player.

Usage:
    python encode.py input.mp4 -o ../video.h --fps 4

Requirements:
    pip install opencv-python numpy
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


SCREEN_W = 32
SCREEN_H = 20
FB_SIZE = SCREEN_W * SCREEN_H // 4  # 160 bytes (2bpp = 4 pixels per byte)


def extract_frames(video_path: str, target_fps: float, max_frames: int = 0) -> list[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        sys.exit(f"Cannot open video: {video_path}")

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = source_fps / target_fps
    expected_frames = int(total_frames / frame_interval)
    if max_frames > 0:
        expected_frames = min(expected_frames, max_frames)

    print(f"Source: {source_fps:.1f} fps, {total_frames} frames")
    print(f"Target: {target_fps} fps, ~{expected_frames} frames")

    frames = []
    frame_idx = 0
    next_capture = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx >= next_capture:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (SCREEN_W, SCREEN_H), interpolation=cv2.INTER_AREA)

            frames.append(resized)
            next_capture += frame_interval

            if len(frames) % 100 == 0:
                print(f"\rExtracted {len(frames)} frames...", end="", flush=True)

            if max_frames > 0 and len(frames) >= max_frames:
                break

        frame_idx += 1

    cap.release()
    print(f"\rExtracted {len(frames)} frames total")
    return frames


def frame_to_bytes_2bpp(frame: np.ndarray) -> bytes:
    """2bpp: 4 pixels per byte, MSB first (pixel 0 in bits 7-6)."""
    result = bytearray(FB_SIZE)

    for y in range(SCREEN_H):
        for byte_idx in range(8):  # 8 bytes per row (32 pixels / 4)
            byte_val = 0
            for pix in range(4):  # 4 pixels per byte
                x = byte_idx * 4 + pix
                # Quantize 0-255 to 0-3
                gray = frame[y, x]
                level = gray // 64  # 0-63=0, 64-127=1, 128-191=2, 192-255=3
                if level > 3:
                    level = 3
                # Pack into byte (MSB first: pixel 0 at bits 7-6)
                byte_val |= level << (6 - pix * 2)
            result[y * 8 + byte_idx] = byte_val

    return bytes(result)


def rle_encode(data: bytes) -> bytes:
    """0x00-0x7F: literal, 0x80-0xFF: repeat (N & 0x7F) + 3 copies."""
    result = bytearray()
    i = 0

    while i < len(data):
        run_start = i
        run_value = data[i]
        while i < len(data) and data[i] == run_value and (i - run_start) < 130:
            i += 1
        run_length = i - run_start

        if run_length >= 3:
            result.append(0x80 | (run_length - 3))
            result.append(run_value)
        else:
            i = run_start
            literal_start = i

            while i < len(data) and (i - literal_start) < 127:
                if i + 2 < len(data) and data[i] == data[i + 1] == data[i + 2]:
                    break
                i += 1

            literal_length = i - literal_start
            if literal_length > 0:
                result.append(literal_length)
                result.extend(data[literal_start:i])

    return bytes(result)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def generate_header(frames: list[bytes], output_path: str, source_name: str, fps: float, use_delta: bool = True):
    print(f"Compressing frames {'(delta)' if use_delta else '(raw)'}...")
    compressed_frames = []
    prev_frame = bytes(FB_SIZE)  # Start with all zeros

    for i, f in enumerate(frames):
        if use_delta and i > 0:
            # Delta encode: XOR with previous frame
            delta = xor_bytes(f, prev_frame)
            compressed_frames.append(rle_encode(delta))
        else:
            # Keyframe (first frame or no delta)
            compressed_frames.append(rle_encode(f))
        prev_frame = f

        if (i + 1) % 100 == 0:
            print(f"\rCompressed {i + 1}/{len(frames)}...", end="", flush=True)
    print(f"\rCompressed {len(frames)} frames")

    offsets = [0]
    for cf in compressed_frames:
        offsets.append(offsets[-1] + len(cf))

    total_size = offsets[-1]
    total_uncompressed = len(frames) * FB_SIZE
    ratio = total_size / total_uncompressed * 100

    print(f"\nStatistics:")
    print(f"  Frames: {len(frames)}")
    print(f"  Uncompressed: {total_uncompressed:,} bytes")
    print(f"  Compressed: {total_size:,} bytes ({ratio:.1f}%)")
    print(f"  Offset table: {len(offsets) * 2:,} bytes")
    print(f"  Total: {total_size + len(offsets) * 2:,} bytes")

    if total_size > 25000:
        print(f"\nWARNING: Compressed size ({total_size:,}) may exceed budget!")
        print("Consider reducing FPS or using a shorter clip.")

    with open(output_path, "w") as f:
        f.write(f"// video.h - Music Video compressed frames (2bpp)\n")
        f.write(f"// Generated by encode.py\n")
        f.write(f"// Source: {source_name} @ {fps} fps, {SCREEN_W}x{SCREEN_H} @ 2bpp\n")
        f.write(f"// Compression: {ratio:.1f}%{' (delta encoded)' if use_delta else ''}\n\n")
        f.write("#pragma once\n\n")

        f.write(f"#define TOTAL_FRAMES {len(frames)}\n")
        f.write(f"#define TOTAL_COMPRESSED_SIZE {total_size}\n")
        f.write(f"#define USE_DELTA_ENCODING {1 if use_delta else 0}\n\n")

        f.write(f"const short frame_offsets[{len(frames) + 1}] = {{\n")
        for i, off in enumerate(offsets):
            if i % 16 == 0:
                f.write("    ")
            f.write(f"{off}")
            if i < len(offsets) - 1:
                f.write(", ")
            if (i + 1) % 16 == 0:
                f.write("\n")
        if len(offsets) % 16 != 0:
            f.write("\n")
        f.write("};\n\n")

        f.write(f"const byte frame_data[TOTAL_COMPRESSED_SIZE] = {{\n")
        all_data = b"".join(compressed_frames)
        for i, b in enumerate(all_data):
            if i % 16 == 0:
                f.write("    ")
            f.write(f"0x{b:02X}")
            if i < len(all_data) - 1:
                f.write(", ")
            if (i + 1) % 16 == 0:
                f.write("\n")
        if len(all_data) % 16 != 0:
            f.write("\n")
        f.write("};\n")

    print(f"\nWritten to {output_path}")


def preview_frames(frames: list[np.ndarray], count: int = 5):
    chars = " ░▒█"

    for i, frame in enumerate(frames[:count]):
        print(f"\n--- Frame {i} ---")
        for y in range(SCREEN_H):
            line = ""
            for x in range(SCREEN_W):
                level = frame[y, x] // 64
                if level > 3:
                    level = 3
                line += chars[level]
            print(line)


def main():
    parser = argparse.ArgumentParser(description="Convert video to Music Video 2bpp C header")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("-o", "--output", default="video.h", help="Output header file")
    parser.add_argument("--fps", type=float, default=4, help="Target FPS (default: 4)")
    parser.add_argument("--max-frames", type=int, default=0, help="Max frames to extract (0=all)")
    parser.add_argument("--duration", type=float, default=0, help="Max duration in seconds (0=all)")
    parser.add_argument("--preview", type=int, metavar="N", help="Preview first N frames")
    parser.add_argument("--no-delta", action="store_true", help="Disable delta encoding")
    args = parser.parse_args()

    max_frames = args.max_frames
    if args.duration > 0:
        max_frames = int(args.duration * args.fps)

    print(f"Extracting frames at {args.fps} fps...")
    frames = extract_frames(args.video, args.fps, max_frames)

    if args.preview:
        preview_frames(frames, args.preview)

    print("Converting frames to 2bpp bytes...")
    frame_bytes = [frame_to_bytes_2bpp(f) for f in frames]

    generate_header(frame_bytes, args.output, Path(args.video).name, args.fps, use_delta=not args.no_delta)


if __name__ == "__main__":
    main()
