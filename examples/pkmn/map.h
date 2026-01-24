#pragma once

#define MAP_W 6
#define MAP_H 4
#define TILE_SIZE 8

#define TILE_PATH 0
#define TILE_GRASS_S 1
#define TILE_GRASS_T 2

const byte tilemap[24] = {
    TILE_GRASS_S, TILE_GRASS_S, TILE_PATH,    TILE_PATH,    TILE_GRASS_T,
    TILE_GRASS_T, TILE_GRASS_S, TILE_PATH,    TILE_PATH,    TILE_GRASS_T,
    TILE_GRASS_T, TILE_GRASS_T, TILE_GRASS_S, TILE_PATH,    TILE_PATH,
    TILE_GRASS_T, TILE_GRASS_T, TILE_GRASS_T, TILE_GRASS_S, TILE_GRASS_S,
    TILE_PATH,    TILE_PATH,    TILE_GRASS_T, TILE_GRASS_T,
};

void drawTile(short tx, short ty) {
    byte tileType = tilemap[(ty << 2) + (ty << 1) + tx];
    short px = tx << 3;
    short py = ty << 3;

    switch (tileType) {
    case TILE_PATH:
        fillTile8(px, py, COL_PATH);
        break;

    case TILE_GRASS_S:
        fillTile8(px, py, COL_GRASS_L);
        setPixel(px + 1, py + 2, COL_GRASS_D);
        setPixel(px + 4, py + 1, COL_GRASS_D);
        setPixel(px + 6, py + 4, COL_GRASS_D);
        setPixel(px + 2, py + 5, COL_GRASS_D);
        setPixel(px + 5, py + 6, COL_GRASS_D);
        break;

    case TILE_GRASS_T:
        fillTile8(px, py, COL_TALL_L);
        setPixel(px + 1, py, COL_TALL_D);
        setPixel(px + 5, py, COL_TALL_D);
        setPixel(px + 3, py + 1, COL_TALL_D);
        setPixel(px + 7, py + 1, COL_TALL_D);
        setPixel(px + 1, py + 2, COL_TALL_D);
        setPixel(px + 5, py + 2, COL_TALL_D);
        setPixel(px + 3, py + 3, COL_TALL_D);
        setPixel(px + 7, py + 3, COL_TALL_D);
        setPixel(px + 1, py + 4, COL_TALL_D);
        setPixel(px + 5, py + 4, COL_TALL_D);
        setPixel(px + 3, py + 5, COL_TALL_D);
        setPixel(px + 7, py + 5, COL_TALL_D);
        setPixel(px + 1, py + 6, COL_TALL_D);
        setPixel(px + 5, py + 6, COL_TALL_D);
        setPixel(px + 3, py + 7, COL_TALL_D);
        setPixel(px + 7, py + 7, COL_TALL_D);
        break;
    }
}

void drawMap(void) {
    short tx, ty;
    for (ty = 0; ty < MAP_H; ty++) {
        for (tx = 0; tx < MAP_W; tx++) {
            drawTile(tx, ty);
        }
    }
}
