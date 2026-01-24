#!/usr/bin/env python3
"""MIDI Player for JavaCard FM Synth."""

import sys
import numpy as np
import sounddevice as sd
import mido
from driver import SynthSession, build_apdu, INS_GENERATE, BUFFER_BYTES, SAMPLE_RATE


def play_midi(midi_path: str, tempo_scale: float = 1.0):
    print(f"Loading {midi_path}...")
    mid = mido.MidiFile(midi_path)

    print(f"  Type: {mid.type}")
    print(f"  Tracks: {len(mid.tracks)}")
    print(f"  Ticks per beat: {mid.ticks_per_beat}")

    events = []
    tempo = 500000  # 120 BPM default

    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            # Convert ticks to seconds
            time_sec = mido.tick2second(abs_time, mid.ticks_per_beat, tempo)
            events.append((time_sec, msg))
            if msg.type == "set_tempo":
                tempo = msg.tempo

    events.sort(key=lambda x: x[0])
    total_duration = max(t for t, _ in events) if events else 0
    print(f"  Duration: {total_duration:.1f} seconds")

    note_events = []
    for time_sec, msg in events:
        if msg.type == "note_on" and msg.velocity > 0:
            note_events.append((time_sec / tempo_scale, "on", msg.channel, msg.note, msg.velocity))
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            note_events.append((time_sec / tempo_scale, "off", msg.channel, msg.note, 0))

    print(f"  Note events: {len(note_events)}")

    if not note_events:
        print("No notes found in MIDI file!")
        return

    print("\nPlaying...")
    with SynthSession() as synth:
        synth.set_param(0x01, 2)  # Modulator mult
        synth.set_param(0x03, 1)  # Feedback
        synth.set_param(0x06, 64)  # Attack
        synth.set_param(0x07, 8)  # Release

        all_samples = []
        current_time = 0.0
        event_idx = 0
        channel_notes = {0: 0, 1: 0}
        total_adjusted_duration = total_duration / tempo_scale
        while current_time < total_adjusted_duration + 1.0:
            while event_idx < len(note_events) and note_events[event_idx][0] <= current_time:
                time_sec, event_type, midi_ch, note, velocity = note_events[event_idx]
                synth_ch = 0 if midi_ch < 8 else 1

                if event_type == "on":
                    if channel_notes[synth_ch] != 0:
                        synth_ch = 1 - synth_ch
                    if channel_notes[synth_ch] != 0:
                        synth.note_off(synth_ch)

                    synth.note_on(synth_ch, note, min(velocity, 127))
                    channel_notes[synth_ch] = note

                elif event_type == "off":
                    for ch in [0, 1]:
                        if channel_notes[ch] == note:
                            synth.note_off(ch)
                            channel_notes[ch] = 0
                            break

                event_idx += 1

            data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
            samples = np.frombuffer(data, dtype=">i2")
            all_samples.append(samples)
            current_time += len(samples) / SAMPLE_RATE

            if len(all_samples) % 100 == 0:
                pct = min(100, int(current_time / (total_adjusted_duration + 1) * 100))
                print(f"\r  Progress: {pct}%", end="", flush=True)

        synth.note_off(0)
        synth.note_off(1)
        for _ in range(10):
            data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
            samples = np.frombuffer(data, dtype=">i2")
            all_samples.append(samples)

    print("\r  Progress: 100%")
    audio = np.concatenate(all_samples).astype(np.float32) / 32768.0
    print(f"\nPlaying {len(audio) / SAMPLE_RATE:.1f} seconds of audio...")
    sd.play(audio, SAMPLE_RATE)
    sd.wait()
    print("Done!")


def main():
    if len(sys.argv) < 2:
        print("Usage: midi_player.py <midi_file> [tempo_scale]")
        print("  tempo_scale: 1.0 = normal, 0.5 = half speed, 2.0 = double speed")
        sys.exit(1)

    midi_path = sys.argv[1]
    tempo_scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    play_midi(midi_path, tempo_scale)


if __name__ == "__main__":
    main()
