#!/usr/bin/env python3
"""Metal riff player for JavaCard FM synth."""

import numpy as np
import sounddevice as sd
from driver import SynthSession, build_apdu, INS_GENERATE, BUFFER_BYTES, SAMPLE_RATE

BPM = 140
BEAT = 60.0 / BPM

E2, G2, A2, B2 = 40, 43, 45, 47
E3, F3, G3, A3, Bb3, B3, C4, D4 = 52, 53, 55, 57, 58, 59, 60, 62
E4 = 64

METAL_RIFF = [
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.25),
    (G2, 0.25),
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.25),
    (0, 0.125),
    (E2, 0.125),
    (A2, 0.25),
    (G2, 0.25),
    (E3, 0.25),
    (E3, 0.25),
    (G3, 0.25),
    (E3, 0.25),
    (Bb3, 0.25),
    (A3, 0.25),
    (G3, 0.25),
    (E3, 0.25),
    (E3, 0.25),
    (E3, 0.25),
    (G3, 0.25),
    (E3, 0.25),
    (A3, 0.25),
    (G3, 0.25),
    (E3, 0.5),
    (E3, 0.25),
    (E3, 0.25),
    (G3, 0.25),
    (E3, 0.25),
    (Bb3, 0.25),
    (A3, 0.25),
    (G3, 0.25),
    (E3, 0.25),
    (E3, 0.25),
    (G3, 0.25),
    (A3, 0.25),
    (B3, 0.25),
    (C4, 0.25),
    (B3, 0.25),
    (A3, 0.25),
    (G3, 0.25),
    (E4, 0.25),
    (D4, 0.25),
    (C4, 0.25),
    (B3, 0.25),
    (A3, 0.25),
    (G3, 0.25),
    (E3, 0.5),
    (E2, 0.125),
    (E2, 0.125),
    (0, 0.125),
    (E2, 0.125),
    (E2, 0.125),
    (E2, 0.125),
    (0, 0.125),
    (E2, 0.125),
    (G2, 0.25),
    (A2, 0.25),
    (B2, 0.25),
    (A2, 0.25),
    (E3, 1.0),
]


def play_metal():
    print("Playing Metal Riff")

    with SynthSession() as synth:
        synth.set_param(0x01, 2)  # Modulator mult
        synth.set_param(0x03, 2)  # Feedback
        synth.set_param(0x06, 127)  # Attack
        synth.set_param(0x07, 16)  # Release

        all_samples = []
        current_note = 0

        for note, beats in METAL_RIFF:
            duration = beats * BEAT
            samples_needed = int(duration * SAMPLE_RATE)

            if note != current_note:
                if current_note != 0:
                    synth.note_off(0)
                if note != 0:
                    synth.note_on(0, note, 127)
                current_note = note

            samples_collected = 0
            while samples_collected < samples_needed:
                data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
                samples = np.frombuffer(data, dtype=">i2")
                all_samples.append(samples)
                samples_collected += len(samples)

        synth.note_off(0)
        for _ in range(20):
            data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
            samples = np.frombuffer(data, dtype=">i2")
            all_samples.append(samples)

    audio = np.concatenate(all_samples).astype(np.float32) / 32768.0
    print(f"Playing {len(audio) / SAMPLE_RATE:.1f} seconds of audio...")
    sd.play(audio, SAMPLE_RATE)
    sd.wait()
    print("Done!")


if __name__ == "__main__":
    play_metal()
