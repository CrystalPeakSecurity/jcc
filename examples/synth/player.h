// player.h - Music player for baked-in MIDI data

#ifndef PLAYER_H
#define PLAYER_H

#include "music.h"

static short music_event_idx;
static short music_samples_left;
static byte music_playing;
static byte music_waiting;

void player_init(void) {
    music_event_idx = 0;
    music_samples_left = 0;
    music_playing = 0;
    music_waiting = 0;
}

void player_start(void) {
    music_event_idx = 0;
    music_samples_left = 0;
    music_playing = 1;
    music_waiting = 0;
}

void player_stop(void) {
    music_playing = 0;
    music_waiting = 0;
    synth_note_off(0);
    synth_note_off(1);
}

byte player_tick(void) {
    short event_off;
    short delta;
    byte note_flag;
    byte note;
    byte is_on;

    if (music_playing == 0) {
        return 0;
    }

    if (music_samples_left > 0) {
        music_samples_left = music_samples_left - 1;
        return 1;
    }

    while (music_event_idx < MUSIC_EVENT_COUNT) {
        event_off = music_event_idx * 3;
        delta = ((MUSIC_DATA[event_off] & 0xFF) << 8) |
                (MUSIC_DATA[event_off + 1] & 0xFF);
        note_flag = MUSIC_DATA[event_off + 2];

        if (music_waiting == 0 && delta > 0) {
            music_samples_left = delta - 1; // -1 because this tick counts
            music_waiting = 1;
            return 1;
        }

        note = note_flag & 0x7F;
        is_on = (note_flag >> 7) & 1; // jcc:ignore-sign-extension

        if (is_on != 0) {
            synth_note_on(0, note, 100);
        } else {
            synth_note_off(0);
        }

        music_event_idx = music_event_idx + 1;
        music_waiting = 0;
    }

    music_event_idx = 0;
    music_waiting = 0;

    return 1;
}

void player_advance(short samples) {
    short event_off;
    short delta;
    byte note_flag;
    byte note;
    byte is_on;

    if (music_playing == 0) {
        return;
    }

    while (samples > 0) {
        if (music_samples_left > 0) {
            if (music_samples_left >= samples) {
                music_samples_left = music_samples_left - samples;
                return;
            }
            samples = samples - music_samples_left;
            music_samples_left = 0;
        }

        while (music_event_idx < MUSIC_EVENT_COUNT) {
            event_off = music_event_idx * 3;
            delta = ((MUSIC_DATA[event_off] & 0xFF) << 8) |
                    (MUSIC_DATA[event_off + 1] & 0xFF);
            note_flag = MUSIC_DATA[event_off + 2];

            if (music_waiting == 0 && delta > 0) {
                music_samples_left = delta;
                music_waiting = 1;
                break;
            }

            note = note_flag & 0x7F;
            is_on = (note_flag >> 7) & 1; // jcc:ignore-sign-extension

            if (is_on != 0) {
                synth_note_on(0, note, 100);
            } else {
                synth_note_off(0);
            }

            music_event_idx = music_event_idx + 1;
            music_waiting = 0;
        }

        if (music_event_idx >= MUSIC_EVENT_COUNT) {
            music_event_idx = 0;
            music_waiting = 0;
        }
    }
}

#endif // PLAYER_H
