#pragma once

#include "font.h"

// (hp * 13) >> 5 approximates (hp * 8) / 20
void drawHealthBar(short x, short y, short width, short hp, short maxHp) {
    short fillWidth;
    short hp3, maxHp2;
    byte barColor;

    if (hp < 0)
        hp = 0;
    fillWidth = (hp * 13) >> 5;
    if (fillWidth > width)
        fillWidth = width;

    hp3 = (hp << 1) + hp;
    maxHp2 = maxHp << 1;
    if (hp3 > maxHp2) {
        barColor = COL_HP_GREEN;
    } else if (hp3 > maxHp) {
        barColor = COL_YELLOW;
    } else {
        barColor = COL_HP_RED;
    }

    fillRect(x, y, x + width - 1, y + 2, COL_UI_BORDER);

    if (fillWidth > 0) {
        fillRect(x, y, x + fillWidth - 1, y + 2, barColor);
    }
}

void render_overworld(void) {
    short px, py;

    clearFB(COL_GRASS_L);
    drawMap();

    px = (player_x << 3) + 1;
    py = player_y << 3;
    drawPlayer(px, py);
}

void render_battle(void) {
    clearFB(COL_UI_BG);

    if (battle_message >= 3) {
        if ((flash_counter & 0x01) == 0) {
            if (battle_message == 3) {
                drawWIN(18, 14, COL_HP_GREEN);
            } else if (battle_message == 4) {
                drawLOSE(16, 14, COL_HP_RED);
            } else {
                drawRAN(18, 14, COL_BLACK);
            }
        }
        return;
    }

    drawPikachu(32, 0);
    drawHP(32, 15, COL_BLACK);
    drawHealthBar(40, 15, 8, enemy_hp, enemy_max_hp);

    drawVoltorb(0, 8);
    drawHP(0, 2, COL_BLACK);
    drawHealthBar(10, 2, 8, player_hp, player_max_hp);

    fillRect(0, 24, 47, 31, COL_WHITE);
    drawRect(0, 24, 47, 31, COL_BLACK);

    if (menu_selection == MENU_FIGHT) {
        drawArrow(2, 26, COL_BLACK);
        drawFIGHT(5, 26, COL_BLACK);
        drawRUN(28, 26, COL_UI_BORDER);
    } else {
        drawFIGHT(5, 26, COL_UI_BORDER);
        drawArrow(25, 26, COL_BLACK);
        drawRUN(28, 26, COL_BLACK);
    }
}

void render_game(void) {
    if (game_state == STATE_OVERWORLD) {
        render_overworld();
    } else {
        render_battle();
    }
}
