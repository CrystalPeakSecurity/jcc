#!/usr/bin/env python3
"""
midi_encode.py - Convert MIDI to monophonic music.h for Music Video player.

Usage:
    python midi_encode.py input.mid -o ../music.h

Makes MIDI monophonic by keeping the highest note when multiple notes overlap.

Requirements:
    pip install mido
"""

import argparse
import sys
from pathlib import Path

try:
    import mido
except ImportError:
    sys.exit("Install mido: pip install mido")


SAMPLE_RATE = 8000  # Match audio sample rate


def midi_to_events(
    midi_path: str, track_num: int = None, transpose: int = 0, skip_notes: int = 0
) -> list[tuple[int, int, bool]]:
    """Convert MIDI to (delta_samples, note, is_on) events."""
    mid = mido.MidiFile(midi_path)

    print(f"MIDI file: {midi_path}")
    print(f"  Type: {mid.type}")
    print(f"  Tracks: {len(mid.tracks)}")
    print(f"  Ticks per beat: {mid.ticks_per_beat}")

    for i, track in enumerate(mid.tracks):
        note_count = sum(1 for msg in track if msg.type == "note_on")
        print(f"  Track {i}: {track.name!r} ({note_count} note_ons)")

    # Collect note events directly (assumes monophonic input)
    mono_events = []
    note_on_count = 0

    for track_idx, track in enumerate(mid.tracks):
        if track_num is not None and track_idx != track_num:
            continue

        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if msg.type == "note_on":
                is_on = msg.velocity > 0
                if is_on:
                    note_on_count += 1
                    if note_on_count <= skip_notes:
                        continue
                out_note = max(0, min(127, msg.note + transpose))
                mono_events.append((abs_time, out_note, is_on))
            elif msg.type == "note_off":
                out_note = max(0, min(127, msg.note + transpose))
                mono_events.append((abs_time, out_note, False))

    # Sort by time (note_off before note_on at same time for clean transitions)
    mono_events.sort(key=lambda e: (e[0], e[2]))

    print(f"\nTotal events: {len(mono_events)}")

    tempo = 500000  # us/beat (120 BPM default)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                tempo = msg.tempo
                break

    ticks_per_second = mid.ticks_per_beat * (1000000 / tempo)
    samples_per_tick = SAMPLE_RATE / ticks_per_second

    print(f"Tempo: {60000000 / tempo:.1f} BPM")
    print(f"Samples per tick: {samples_per_tick:.4f}")

    result = []
    prev_tick = 0

    for tick, note, is_on in mono_events:
        delta_ticks = tick - prev_tick
        delta_samples = int(delta_ticks * samples_per_tick)
        result.append((delta_samples, note, is_on))
        prev_tick = tick

    total_samples = sum(e[0] for e in result)
    duration_sec = total_samples / SAMPLE_RATE
    print(f"Duration: {duration_sec:.1f}s ({total_samples} samples)")

    return result


def generate_header(events: list[tuple[int, int, bool]], output_path: str, source_name: str):
    with open(output_path, "w") as f:
        f.write(f"// music.h - Music Video music data\n")
        f.write(f"// Auto-generated from {source_name}\n")
        f.write(f"//\n")
        f.write(f"// Format: 3 bytes per event\n")
        f.write(f"//   Byte 0-1: delta time in samples (big-endian, {SAMPLE_RATE}Hz)\n")
        f.write(f"//   Byte 2: note number | (note_on << 7)\n\n")
        f.write("#ifndef MUSIC_H\n")
        f.write("#define MUSIC_H\n\n")
        f.write(f"#define MUSIC_EVENT_COUNT {len(events)}\n\n")
        f.write("static const byte MUSIC_DATA[] = {\n")

        for i, (delta, note, is_on) in enumerate(events):
            if delta > 65535:
                delta = 65535

            hi = (delta >> 8) & 0xFF
            lo = delta & 0xFF
            note_byte = note | (0x80 if is_on else 0x00)

            if i % 8 == 0:
                f.write("    ")
            f.write(f"0x{hi:02X}, 0x{lo:02X}, 0x{note_byte:02X}")
            if i < len(events) - 1:
                f.write(", ")
            if (i + 1) % 8 == 0:
                f.write("\n")

        if len(events) % 8 != 0:
            f.write("\n")
        f.write("};\n\n")
        f.write("#endif // MUSIC_H\n")

    total_samples = sum(e[0] for e in events)
    duration = total_samples / SAMPLE_RATE
    size = len(events) * 3

    print(f"\nWritten to {output_path}")
    print(f"  Events: {len(events)}")
    print(f"  Size: {size} bytes")
    print(f"  Duration: {duration:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Convert MIDI to Music Video music.h")
    parser.add_argument("midi", help="Input MIDI file")
    parser.add_argument("-o", "--output", default="music.h", help="Output header file")
    parser.add_argument("--track", type=int, default=None, help="Only use specific track number")
    parser.add_argument(
        "--transpose", type=int, default=0, help="Transpose notes by N semitones (e.g., -12 for one octave down)"
    )
    parser.add_argument("--skip", type=int, default=0, help="Skip first N note-on events")
    parser.add_argument("--list", action="store_true", help="List tracks and exit")
    args = parser.parse_args()

    if args.list:
        mid = mido.MidiFile(args.midi)
        print(f"Tracks in {args.midi}:")
        for i, track in enumerate(mid.tracks):
            notes = [msg.note for msg in track if msg.type == "note_on" and msg.velocity > 0]
            if notes:
                print(f"  {i}: {track.name!r} - {len(notes)} notes, range {min(notes)}-{max(notes)}")
            else:
                print(f"  {i}: {track.name!r} - no notes")
        return

    events = midi_to_events(args.midi, args.track, args.transpose, args.skip)
    generate_header(events, args.output, Path(args.midi).name)


if __name__ == "__main__":
    main()
