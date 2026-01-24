#pragma once

#include "map.h"
#include "sprites.h"

#define STATE_OVERWORLD 0
#define STATE_BATTLE 1

#define INPUT_NONE 0
#define INPUT_UP 1
#define INPUT_DOWN 2
#define INPUT_LEFT 3
#define INPUT_RIGHT 4
#define INPUT_A 5

#define MENU_FIGHT 0
#define MENU_RUN 1

byte game_state = STATE_OVERWORLD;

short player_x = 2;
short player_y = 1;
short player_hp = 20;
short player_max_hp = 20;

short enemy_hp = 0;
short enemy_max_hp = 0;

byte menu_selection = MENU_FIGHT;
byte battle_message = 0;
byte flash_counter = 0;

short rng_state = 12345;

byte anim_frame = 0;
byte anim_counter = 0;

short random_short(void) {
    rng_state = (short)((25173 * rng_state + 13849) & 0x7FFF);
    return rng_state;
}

byte can_walk(short x, short y) {
    if (x < 0 || x >= MAP_W || y < 0 || y >= MAP_H)
        return 0;
    return 1;
}

void check_encounter(void) {
    byte tile = tilemap[(player_y << 2) + (player_y << 1) + player_x];
    if (tile == TILE_GRASS_T) {
        if ((random_short() & 3) == 0) {
            game_state = STATE_BATTLE;
            enemy_hp = (short)(10 + (random_short() & 3));
            enemy_max_hp = enemy_hp;
            menu_selection = MENU_FIGHT;
            battle_message = 0;
        }
    }
}

void overworld_tick(byte input) {
    short new_x = player_x;
    short new_y = player_y;

    if (input == INPUT_UP)
        new_y--;
    else if (input == INPUT_DOWN)
        new_y++;
    else if (input == INPUT_LEFT)
        new_x--;
    else if (input == INPUT_RIGHT)
        new_x++;

    if (new_x != player_x || new_y != player_y) {
        if (can_walk(new_x, new_y)) {
            player_x = new_x;
            player_y = new_y;
            check_encounter();
        }
    }
}

short calc_damage(void) { return (short)(1 + (random_short() & 3)); }

void battle_tick(byte input) {
    short damage;

    if (battle_message >= 3) {
        flash_counter++;
        if (flash_counter >= 6) {
            if (battle_message == 3) {
                player_hp = player_hp + 5;
                if (player_hp > player_max_hp)
                    player_hp = player_max_hp;
            } else if (battle_message == 4) {
                player_hp = player_max_hp;
            }
            game_state = STATE_OVERWORLD;
            battle_message = 0;
            flash_counter = 0;
        }
        return;
    }

    if (input == INPUT_UP || input == INPUT_DOWN) {
        menu_selection = (menu_selection == MENU_FIGHT) ? MENU_RUN : MENU_FIGHT;
        battle_message = 0;
        return;
    }

    if (input == INPUT_A) {
        if (menu_selection == MENU_FIGHT) {
            damage = calc_damage();
            enemy_hp = enemy_hp - damage;
            if (enemy_hp <= 0) {
                enemy_hp = 0;
                battle_message = 3;
                flash_counter = 0;
                return;
            }

            damage = calc_damage();
            player_hp = player_hp - damage;
            if (player_hp <= 0) {
                player_hp = 1;
                battle_message = 4;
                flash_counter = 0;
                return;
            }

            battle_message = 1;
        } else {
            if ((random_short() & 1) == 0) {
                battle_message = 5;
                flash_counter = 0;
            } else {
                damage = calc_damage();
                player_hp = player_hp - damage;
                if (player_hp <= 0) {
                    player_hp = 1;
                    battle_message = 4;
                    flash_counter = 0;
                    return;
                }
                battle_message = 2;
            }
        }
    }
}

void game_tick(byte input) {
    anim_counter++;
    if (anim_counter >= 8) {
        anim_counter = 0;
        anim_frame = (anim_frame == 0) ? 1 : 0;
    }

    if (game_state == STATE_OVERWORLD) {
        overworld_tick(input);
    } else {
        battle_tick(input);
    }
}

void reset_game(void) {
    game_state = STATE_OVERWORLD;
    player_x = 2;
    player_y = 1;
    player_hp = 20;
    player_max_hp = 20;
    enemy_hp = 0;
    enemy_max_hp = 0;
    menu_selection = MENU_FIGHT;
    battle_message = 0;
    rng_state = 12345;
}
