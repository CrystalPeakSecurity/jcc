#pragma once

#define SCREEN_WIDTH 32
#define SCREEN_HEIGHT 20
#define FB_SIZE 80

// Must be first global for APDU_sendBytesLong offset 0
byte framebuffer[FB_SIZE];

void clearFB(void) { memset_bytes(framebuffer, 0, FB_SIZE); }
