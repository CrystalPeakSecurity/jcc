// jcc_fb.h - 2bpp Framebuffer for Music Video
//
// 32x20 @ 2bpp, row-major layout
// Video is stored in response_buffer[0:160]
// NOTE: response_buffer must be declared before including this file

#ifndef JCC_FB_H
#define JCC_FB_H

// Screen configuration
#define SCREEN_W 32
#define SCREEN_H 20
#define FB_SIZE 160 // SCREEN_W * SCREEN_H / 4 (2bpp = 4 pixels per byte)
#define FB_OFFSET 0 // Offset in response_buffer (video first)

// Row-major: 8 bytes per row (32 pixels / 4 pixels per byte)
#define ROW_BYTES 8

// 2-bit color palette (grayscale)
#define COLOR_BLACK 0 // 00
#define COLOR_DARK 1  // 01
#define COLOR_LIGHT 2 // 10
#define COLOR_WHITE 3 // 11

void clearFB(void) { memset_at(response_buffer, FB_OFFSET, 0, FB_SIZE); }

#endif // JCC_FB_H
