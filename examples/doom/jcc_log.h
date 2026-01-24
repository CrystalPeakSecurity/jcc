// jcc_log.h - Debug log buffer (reading clears the buffer)

#pragma once

#include "jcc.h"

#define LOG_SIZE 48

byte log_buffer[LOG_SIZE];
short log_idx;
byte log_overflow;

void log_ensure(short n) {
    if (log_idx + n > LOG_SIZE) {
        log_overflow = 1;
        log_idx = 0;
    }
}

void log_write_B(byte b0) {
    log_ensure(1);
    log_buffer[log_idx++] = b0;
}

void log_trace(byte note) {
    log_ensure(2);
    log_buffer[log_idx++] = 0x10;
    log_buffer[log_idx++] = note;
}

void log_trace_B(byte note, byte val) {
    log_ensure(3);
    log_buffer[log_idx++] = 0x11;
    log_buffer[log_idx++] = note;
    log_buffer[log_idx++] = val;
}

void log_trace_S(byte note, short val) {
    log_ensure(4);
    log_buffer[log_idx++] = 0x12;
    log_buffer[log_idx++] = note;
    WRITE_SHORT(log_buffer, log_idx, val); // jcc:ignore-sign-extension
}

void log_trace_I(byte note, int val) {
    log_ensure(6);
    log_buffer[log_idx++] = 0x13;
    log_buffer[log_idx++] = note;
    WRITE_INT(log_buffer, log_idx, val);
}

short log_read_into(byte *buffer, short max_len) {
    short count = 1;
    short available = log_idx;
    short i = 0;

    buffer[0] = log_overflow;
    log_overflow = 0;

    if (available > max_len - 1)
        available = max_len - 1;

    while (i < available) {
        buffer[count++] = log_buffer[i++];
    }

    log_idx = 0;
    return count;
}
