// test_object_pool.h - Object pool patterns from flappy's game.h
// INS 0x52: Tests struct array traversal with active flags, spawn/despawn patterns

#pragma once

#define POOL_SIZE 4

struct pool_obj_t {
    short x;
    short y;
    byte active;
    byte type;
};

struct pool_obj_t pool[POOL_SIZE];

// Reset pool to known state
void reset_pool(void) {
    short i;
    for (i = 0; i < POOL_SIZE; i = i + 1) {
        pool[i].x = 0;
        pool[i].y = 0;
        pool[i].active = 0;
        pool[i].type = 0;
    }
}

void test_object_pool(APDU apdu, byte* buffer, byte p1) {
    short i;
    short count;
    short found;
    short sum;
    short max_x;

    // Basic active flag operations
    if (p1 == 0) {
        reset_pool();
        pool[0].active = 1;
        sendResult(apdu, buffer, pool[0].active);                                 // 1
        return;
    }
    if (p1 == 1) {
        reset_pool();
        pool[2].active = 1;
        sendResult(apdu, buffer, pool[2].active);                                 // 1
        return;
    }
    if (p1 == 2) {
        reset_pool();
        pool[1].active = 1;
        pool[1].active = 0;
        sendResult(apdu, buffer, pool[1].active);                                 // 0
        return;
    }

    // Count active objects (loop with flag check)
    if (p1 == 3) {
        reset_pool();
        count = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active) {
                count = count + 1;
            }
        }
        sendResult(apdu, buffer, count);                                          // 0
        return;
    }
    if (p1 == 4) {
        reset_pool();
        pool[0].active = 1;
        pool[2].active = 1;
        count = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active) {
                count = count + 1;
            }
        }
        sendResult(apdu, buffer, count);                                          // 2
        return;
    }
    if (p1 == 5) {
        reset_pool();
        pool[0].active = 1;
        pool[1].active = 1;
        pool[2].active = 1;
        pool[3].active = 1;
        count = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active) {
                count = count + 1;
            }
        }
        sendResult(apdu, buffer, count);                                          // 4
        return;
    }

    // Find first inactive slot (spawn pattern)
    if (p1 == 6) {
        reset_pool();
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) {
                found = i;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 0
        return;
    }
    if (p1 == 7) {
        reset_pool();
        pool[0].active = 1;
        pool[1].active = 1;
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) {
                found = i;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 2
        return;
    }
    if (p1 == 8) {
        reset_pool();
        pool[0].active = 1;
        pool[1].active = 1;
        pool[2].active = 1;
        pool[3].active = 1;
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) {
                found = i;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // -1 (pool full)
        return;
    }

    // Spawn object (find slot + set fields)
    if (p1 == 9) {
        reset_pool();
        pool[0].active = 1;
        // Find first inactive
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) {
                found = i;
                break;
            }
        }
        // Spawn at found slot
        if (found >= 0) {
            pool[found].x = 100;
            pool[found].y = 50;
            pool[found].active = 1;
            pool[found].type = 2;
        }
        sendResult(apdu, buffer, pool[1].x);                                      // 100
        return;
    }
    if (p1 == 10) {
        reset_pool();
        pool[0].active = 1;
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) {
                found = i;
                break;
            }
        }
        if (found >= 0) {
            pool[found].x = 100;
            pool[found].y = 50;
            pool[found].active = 1;
            pool[found].type = 2;
        }
        sendResult(apdu, buffer, pool[1].type);                                   // 2
        return;
    }

    // Update all active (continue pattern)
    if (p1 == 11) {
        reset_pool();
        pool[0].x = 10; pool[0].active = 1;
        pool[1].x = 20; pool[1].active = 0;  // Inactive
        pool[2].x = 30; pool[2].active = 1;
        pool[3].x = 40; pool[3].active = 0;  // Inactive
        // Decrement x for all active
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            pool[i].x = pool[i].x - 1;
        }
        sendResult(apdu, buffer, pool[0].x + pool[2].x);                          // 9 + 29 = 38
        return;
    }
    if (p1 == 12) {
        reset_pool();
        pool[0].x = 10; pool[0].active = 1;
        pool[1].x = 20; pool[1].active = 0;
        pool[2].x = 30; pool[2].active = 1;
        pool[3].x = 40; pool[3].active = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            pool[i].x = pool[i].x - 1;
        }
        // Inactive should be unchanged
        sendResult(apdu, buffer, pool[1].x + pool[3].x);                          // 20 + 40 = 60
        return;
    }

    // Despawn by condition (like pipes moving off screen)
    if (p1 == 13) {
        reset_pool();
        pool[0].x = -5; pool[0].active = 1;  // Off screen
        pool[1].x = 10; pool[1].active = 1;
        pool[2].x = -2; pool[2].active = 1;  // Off screen
        pool[3].x = 20; pool[3].active = 1;
        // Despawn if x < 0
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].x < 0) {
                pool[i].active = 0;
            }
        }
        count = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active) count = count + 1;
        }
        sendResult(apdu, buffer, count);                                          // 2
        return;
    }

    // Find rightmost x (max search like find_rightmost_pipe_x)
    if (p1 == 14) {
        reset_pool();
        pool[0].x = 10; pool[0].active = 1;
        pool[1].x = 30; pool[1].active = 1;
        pool[2].x = 5;  pool[2].active = 1;
        pool[3].x = 25; pool[3].active = 0;  // Inactive, should be ignored
        max_x = -100;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active && pool[i].x > max_x) {
                max_x = pool[i].x;
            }
        }
        sendResult(apdu, buffer, max_x);                                          // 30
        return;
    }
    if (p1 == 15) {
        reset_pool();
        // All inactive
        max_x = -100;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (pool[i].active && pool[i].x > max_x) {
                max_x = pool[i].x;
            }
        }
        sendResult(apdu, buffer, max_x);                                          // -100 (no active)
        return;
    }

    // Sum all x values of active objects
    if (p1 == 16) {
        reset_pool();
        pool[0].x = 10; pool[0].active = 1;
        pool[1].x = 20; pool[1].active = 0;
        pool[2].x = 30; pool[2].active = 1;
        pool[3].x = 40; pool[3].active = 1;
        sum = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            sum = sum + pool[i].x;
        }
        sendResult(apdu, buffer, sum);                                            // 10 + 30 + 40 = 80
        return;
    }

    // Find first active by condition (scored check like pipes)
    if (p1 == 17) {
        reset_pool();
        pool[0].x = 5;  pool[0].type = 1; pool[0].active = 1;  // type=scored
        pool[1].x = 15; pool[1].type = 0; pool[1].active = 1;  // Not scored
        pool[2].x = 8;  pool[2].type = 1; pool[2].active = 1;  // type=scored
        // Find first active with type == 0
        found = -1;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].type == 0) {
                found = i;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 1
        return;
    }

    // Update multiple fields in loop
    if (p1 == 18) {
        reset_pool();
        pool[0].x = 100; pool[0].y = 50; pool[0].active = 1;
        pool[1].x = 200; pool[1].y = 60; pool[1].active = 1;
        // Move all active: x -= 5, y += 2
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            pool[i].x = pool[i].x - 5;
            pool[i].y = pool[i].y + 2;
        }
        sendResult(apdu, buffer, pool[0].x + pool[0].y);                          // 95 + 52 = 147
        return;
    }

    // Collision-style check (nested conditions)
    if (p1 == 19) {
        reset_pool();
        pool[0].x = 10; pool[0].y = 20; pool[0].active = 1;
        pool[1].x = 50; pool[1].y = 60; pool[1].active = 1;
        // Check if any object at x=10, y=20
        found = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].x == 10 && pool[i].y == 20) {
                found = 1;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 1
        return;
    }
    if (p1 == 20) {
        reset_pool();
        pool[0].x = 10; pool[0].y = 20; pool[0].active = 1;
        pool[1].x = 50; pool[1].y = 60; pool[1].active = 1;
        // Check if any object at x=30, y=40
        found = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].x == 30 && pool[i].y == 40) {
                found = 1;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 0
        return;
    }

    // Range check like collision detection
    if (p1 == 21) {
        reset_pool();
        pool[0].x = 10; pool[0].y = 20; pool[0].active = 1;
        // Check if any active object has 5 <= x <= 15 and 15 <= y <= 25
        found = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].x >= 5 && pool[i].x <= 15 &&
                pool[i].y >= 15 && pool[i].y <= 25) {
                found = 1;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 1
        return;
    }
    if (p1 == 22) {
        reset_pool();
        pool[0].x = 10; pool[0].y = 20; pool[0].active = 1;
        // Check range 0-5, 0-5 (no match)
        found = 0;
        for (i = 0; i < POOL_SIZE; i = i + 1) {
            if (!pool[i].active) continue;
            if (pool[i].x >= 0 && pool[i].x <= 5 &&
                pool[i].y >= 0 && pool[i].y <= 5) {
                found = 1;
                break;
            }
        }
        sendResult(apdu, buffer, found);                                          // 0
        return;
    }

    sendResult(apdu, buffer, -1);
}
