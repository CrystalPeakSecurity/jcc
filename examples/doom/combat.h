// combat.h - Combat System
//
// JDOOM Reference: game/interaction/Damage.java, game/physics/MapMovement.java
//
// Handles damage application, hitscan attacks, and line-of-fire tracing.
//
// DIVERGENCE: Simplified intercept system
// JDOOM: Full blockmap iteration with intercept list
// We use a simpler approach: check all mobjs within range
// Reason: Blockmap iteration is complex and stack-heavy

#pragma once

#include "data/e1m1.h"
#include "data/mobjinfo.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "mobj.h"
#include "movement.h"

// Note: MISSILERANGE and MELEERANGE are defined in data/mobjinfo.h

// =============================================================================
// Explosion Damage Queue
// Breaks recursion: A_Explode -> P_DamageMobj -> P_SetMobjState -> A_Explode
// Instead of calling P_DamageMobj directly, A_Explode queues damage.
// Queue is processed iteratively after thinker actions complete.
// =============================================================================

struct explosion_queue_entry {
    short target;
    short inflictor;
    short source;
    short damage;
};

struct explosion_queue_entry explosion_queue[MAX_EXPLOSION_QUEUE];
short explosion_queue_count;

void P_QueueExplosionDamage(short target, short inflictor, short source,
                            short damage) {
    if (explosion_queue_count >= MAX_EXPLOSION_QUEUE)
        return; // Drop if full
    explosion_queue[explosion_queue_count].target = target;
    explosion_queue[explosion_queue_count].inflictor = inflictor;
    explosion_queue[explosion_queue_count].source = source;
    explosion_queue[explosion_queue_count].damage = damage;
    explosion_queue_count++;
}

// P_ProcessExplosionQueue defined after P_DamageMobj (needs forward reference)

// =============================================================================
// P_DamageMobj - Apply damage to a mobj
// JDOOM: game/interaction/Damage.java:606-719 P_DamageMobj
//
// inflictor_idx: mobj that caused damage (-1 for none, e.g. environment)
// source_idx: mobj responsible (-1 for none)
// damage: amount of damage
// =============================================================================

void P_DamageMobj(short target_idx, short inflictor_idx, short source_idx,
                  short damage) {
    short health;

    // Bounds check (not in JDOOM - they use object references)
    if (target_idx < 0 || target_idx >= MAX_MOBJS) {
        return;
    }

    // Active check (not in JDOOM - they use object references)
    if (!mobjs[target_idx].active) {
        return;
    }

    // JDOOM: Damage.java:612-613 - Can't damage non-shootable
    // JDOOM: if ((target.flags & MF_SHOOTABLE) == 0) return;
    if ((mobjs[target_idx].flags & MF_SHOOTABLE) == 0) {
        return;
    }

    // JDOOM: Damage.java:615-616 - Already dead
    // JDOOM: if (target.health <= 0) return;
    if (mobjs[target_idx].health <= 0) {
        return;
    }

    // JDOOM: Damage.java:618-620 - Zero momentum if MF_SKULLFLY
    // JDOOM: if ((target.flags & MF_SKULLFLY) != 0) { target.momx = target.momy
    // = target.momz = 0; } DIVERGENCE: We have momx/momy/momz but skip this for
    // simplicity Impact: Lost Souls won't stop when hit mid-charge (minor
    // behavioral difference)

    // JDOOM: Damage.java:622-624 - Player-specific half damage on sk_baby
    // JDOOM: player = target.player;
    //        if (player != null && gameskill == sk_baby) damage >>= 1;
    // DIVERGENCE: Difficulty settings not implemented (we always use UV)
    // Impact: None - we don't have easy mode anyway

    // JDOOM: Damage.java:629-646 - Thrust/knockback calculation
    // JDOOM: if (inflictor != null && (target.flags & MF_NOCLIP) == 0 &&
    //            (source == null || source.player == null ||
    //            source.player.readyweapon != wp_chainsaw)) { ang =
    //            PointToAngle2(inflictor.x, inflictor.y, target.x, target.y);
    //            thrust = damage * (FRACUNIT >> 3) * 100 / target.info.mass;
    //            // make fall forwards sometimes
    //            if (damage < 40 && damage > target.health &&
    //                target.z - inflictor.z > 64 * FRACUNIT && (P_Random() & 1)
    //                != 0) { ang += ANG180; thrust *= 4;
    //            }
    //            ang >>>= ANGLETOFINESHIFT;
    //            target.momx += FixedMul(thrust, finecosine(ang));
    //            target.momy += FixedMul(thrust, finesine(ang));
    //        }
    // DIVERGENCE: Knockback not implemented
    // Impact: Enemies don't get pushed back when shot (minor visual difference)

    // JDOOM: Damage.java:649-691 - Player-specific damage handling
    // DIVERGENCE: Handled separately in P_DamagePlayer() below
    // JDOOM does it inline; we split for clarity

    // JDOOM: Damage.java:694 - Apply damage to target health
    // JDOOM: target.health -= damage;
    health = mobjs[target_idx].health - damage;
    mobjs[target_idx].health = health;

    // JDOOM: Damage.java:695-698 - Check for death
    // JDOOM: if (target.health <= 0) { P_KillMobj(source, target); return; }
    if (health <= 0) {
        // =========== P_KillMobj inlined ===========
        // JDOOM: Damage.java:538-604 P_KillMobj(source, target)

        // JDOOM: Damage.java:550-559 - Kill count handling
        // JDOOM: if (source != null && source.player != null) {
        //            if ((target.flags & MF_COUNTKILL) != 0)
        //            source.player.killcount++;
        //        } else if ((target.flags & MF_COUNTKILL) != 0) {
        //            players.killcount++;
        //        }
        // DIVERGENCE: We always increment player.killcount (simplified
        // single-player) Impact: None in single-player - count is correct
        // either way
        if ((mobjs[target_idx].flags & MF_COUNTKILL) != 0) {
            player.killcount++;
        }

        // JDOOM: Damage.java:542 - Clear movement flags
        // JDOOM: target.flags &= ~(MF_SHOOTABLE | MF_FLOAT | MF_SKULLFLY);
        mobjs[target_idx].flags &= ~(MF_SHOOTABLE | MF_FLOAT | MF_SKULLFLY);

        // JDOOM: Damage.java:544-545 - Clear NOGRAVITY except for skulls
        // JDOOM: if (target.type != MT_SKULL) target.flags &= ~MF_NOGRAVITY;
        // DIVERGENCE: We clear it for all types (no MT_SKULL check)
        // Impact: Lost Souls will fall when killed (matches original behavior
        // anyway)
        mobjs[target_idx].flags &= ~MF_NOGRAVITY;

        // JDOOM: Damage.java:547 - Add corpse flags
        // JDOOM: target.flags |= MF_CORPSE | MF_DROPOFF;
        // (MF_CORPSE = 0x100000, MF_DROPOFF = 0x400 per Mobj.java:95,120)
        // DIVERGENCE: MF_CORPSE, MF_DROPOFF not defined in doom.h
        // Impact: Corpses can't be walked over ledges by player pushing (minor)
        // TODO: Add MF_CORPSE and MF_DROPOFF to doom.h if needed

        // JDOOM: Damage.java:548 - Reduce height for walking over corpses
        // JDOOM: target.height >>= 2;
        mobjs[target_idx].height = mobjs[target_idx].height >> 2;

        // JDOOM: Damage.java:562-568 - Player death handling
        // JDOOM: if (target.player != null) {
        //            target.flags &= ~MF_SOLID;
        //            target.player.playerstate = PST_DEAD;
        //            Weapon.P_DropWeapon(target.player);
        //        }
        // DIVERGENCE: Player death handled via player.dead flag in
        // P_DamagePlayer Impact: None - player death works, just tracked
        // differently

        // JDOOM: Damage.java:571-575 - Enter death or xdeath state
        // JDOOM: if (target.health < -target.info.spawnhealth &&
        // target.info.xdeathstate != S_NULL) {
        //            Mobj.P_SetMobjState(target, target.info.xdeathstate);
        //        } else {
        //            Mobj.P_SetMobjState(target, target.info.deathstate);
        //        }
        // DIVERGENCE: We only use deathstate, never xdeathstate
        // Impact: No gib animations when enemy is overkilled (visual only)
        // DIVERGENCE: Use P_SetMobjStateRaw instead of P_SetMobjState
        // Reason: Stack depth constraint - P_SetMobjState calls
        // P_MobjThinkerAction which can dispatch to any action including
        // A_Chase (expensive collision checks) INVARIANT: Initial death states
        // must have ACT_NONE. The action for this state is SKIPPED (not
        // delayed) - subsequent state actions run normally via P_MobjThinker.
        // If you add an enemy where deathstate has a real action, it will be
        // silently skipped!
        P_SetMobjStateRaw(target_idx,
                          MOBJINFO_DEATHSTATE(mobjs[target_idx].type));

        // JDOOM: Damage.java:576-579 - Randomize tics for visual variety
        // JDOOM: target.tics -= Random.P_Random() & 3;
        //        if (target.tics < 1) target.tics = 1;
        if (mobjs[target_idx].tics > 0) {
            mobjs[target_idx].tics -= P_Random() & 3;
            if (mobjs[target_idx].tics < 1) {
                mobjs[target_idx].tics = 1;
            }
        }

        // JDOOM: Damage.java:581-603 - Drop items based on enemy type
        // JDOOM: switch (target.type) {
        //            case MT_WOLFSS: case MT_POSSESSED: item = MT_CLIP; break;
        //            case MT_SHOTGUY: item = MT_SHOTGUN; break;
        //            case MT_CHAINGUY: item = MT_CHAINGUN; break;
        //            default: return;
        //        }
        //        mo = P_SpawnMobj(target.x, target.y, ONFLOORZ, item);
        //        mo.flags |= MF_DROPPED;
        // DIVERGENCE: Item drops not implemented
        // Impact: No ammo/weapon pickups from killed enemies

        return;
    }

    // JDOOM: Damage.java:700-705 - Pain state transition
    // JDOOM: if ((Random.P_Random() & 0xFF) < target.info.painchance &&
    //            (target.flags & MF_SKULLFLY) == 0) {
    //            target.flags |= MF_JUSTHIT;
    //            P_SetMobjState(target, target.info.painstate);
    //        }
    // DIVERGENCE: JDOOM masks P_Random() with 0xFF; we don't need to
    // (P_Random already returns 0-255, so mask is redundant)
    if ((mobjs[target_idx].flags & MF_SKULLFLY) == 0) {
        if (P_Random() < MOBJINFO_PAINCHANCE(mobjs[target_idx].type)) {
            // JDOOM: Damage.java:702 - MF_JUSTHIT triggers immediate
            // counterattack JDOOM: target.flags |= MF_JUSTHIT;
            mobjs[target_idx].flags |= MF_JUSTHIT;
            // JDOOM: Damage.java:704 - Enter pain state
            // JDOOM: P_SetMobjState(target, target.info.painstate);
            // DIVERGENCE: Use P_SetMobjStateRaw instead of P_SetMobjState
            // Reason: Stack depth constraint - same as death state above
            // INVARIANT: Initial pain states must have ACT_NONE (see death
            // state comment)
            P_SetMobjStateRaw(target_idx,
                              MOBJINFO_PAINSTATE(mobjs[target_idx].type));
        }
    }

    // JDOOM: Damage.java:707 - Wake up enemy immediately
    // JDOOM: target.reactiontime = 0;
    mobjs[target_idx].reactiontime = 0;

    // JDOOM: Damage.java:709-718 - Infighting/target switching logic
    // JDOOM: if ((target.threshold == 0 || target.type == MT_VILE) && source !=
    // null &&
    //            source != target && source.type != MT_VILE) {
    //            target.target = source;
    //            target.threshold = BASETHRESHOLD;
    //            if (target.state == states[target.info.spawnstate] &&
    //            target.info.seestate != S_NULL)
    //                P_SetMobjState(target, target.info.seestate);
    //        }
    // DIVERGENCE: Simplified MT_VILE checks (Arch-vile not in E1M1)
    // We match JDOOM's threshold check but omit MT_VILE special cases
    // Impact: Target switching behavior matches JDOOM for E1M1 monsters
    if (mobjs[target_idx].threshold == 0 && source_idx >= 0 &&
        source_idx != target_idx) {
        mobjs[target_idx].target_idx = source_idx;
        // JDOOM: PLocal.java:34 - BASETHRESHOLD = 100
        mobjs[target_idx].threshold = 100;
    }

    // JDOOM: Damage.java:715-717 - If in spawnstate, switch to seestate
    // JDOOM: if (target.state == states[target.info.spawnstate] &&
    // target.info.seestate != S_NULL)
    //            P_SetMobjState(target, target.info.seestate);
    // DIVERGENCE: Not implemented
    // Impact: Enemies hit while idle won't immediately start chasing
    // (They'll start chasing on next tick via A_Look anyway)
}

// =============================================================================
// P_DamagePlayer - Apply damage to player
// JDOOM: Damage.java:649-691 (player-specific section of P_DamageMobj)
//
// DIVERGENCE: JDOOM handles player damage inline within P_DamageMobj
// We separate it for clarity and to handle our different player struct
// =============================================================================

void P_DamagePlayer(short source_idx, short damage) {
    // JDOOM: Damage.java:651-653 - End of game hell hack
    // JDOOM: if (target.subsector.sector.special == 11 && damage >=
    // target.health) {
    //            damage = target.health - 1;
    //        }
    // DIVERGENCE: Not implemented (sector.special == 11 is E1M8 ending room)
    // Impact: Player can die in E1M8 ending sequence (but we don't have E1M8)

    // JDOOM: Damage.java:656-659 - Invulnerability check
    // JDOOM: if (damage < 1000 && player.powers[pw_invulnerability] != 0)
    // return; DIVERGENCE: Powerups not implemented Impact: No invulnerability
    // sphere effect
    // TODO: if (damage < 1000 && player.powers[pw_invulnerability] != 0)
    // return;

    // JDOOM: Damage.java:662-675 - Armor absorption
    // JDOOM: if (player.armortype != 0) {
    //            if (player.armortype == 1) saved = damage / 3;
    //            else saved = damage / 2;
    //            if (player.armorpoints <= saved) {
    //                saved = player.armorpoints;
    //                player.armortype = 0;
    //            }
    //            player.armorpoints -= saved;
    //            damage -= saved;
    //        }
    if (player.armortype != 0) {
        static short saved;
        // JDOOM: Damage.java:663-666 - Armor type determines absorption rate
        if (player.armortype == 1) {
            saved = damage / 3; // Green armor: 33% absorption
        } else {
            saved = damage / 2; // Blue armor: 50% absorption
        }
        // JDOOM: Damage.java:668-671 - Armor used up
        if (saved > player.armor) {
            saved = player.armor;
            player.armortype = 0; // JDOOM: Damage.java:671
        }
        // JDOOM: Damage.java:673-674
        player.armor = player.armor - saved;
        damage = damage - saved;
    }

    // JDOOM: Damage.java:677-679 - Apply damage to player health
    // JDOOM: player.health -= damage;
    //        if (player.health < 0) player.health = 0;
    player.health = player.health - damage;

    if (player.health <= 0) {
        player.health = 0;
        // JDOOM: Damage.java:566 - player.playerstate = PST_DEAD
        // DIVERGENCE: We use player.dead flag instead of playerstate enum
        // Impact: None - death is handled correctly
        player.dead = 1;
    }

    // JDOOM: Damage.java:681 - Set attacker for status bar face direction
    // JDOOM: player.attacker = source;
    // DIVERGENCE: player.attacker not stored
    // Impact: Status bar face won't look toward attacker (no status bar anyway)

    // JDOOM: Damage.java:682-685 - Damage count for screen flash
    // JDOOM: player.damagecount += damage;
    //        if (player.damagecount > 100) player.damagecount = 100;
    // DIVERGENCE: player.damagecount not stored
    // Impact: No red screen flash when damaged (visual only)
}

// =============================================================================
// P_LineAttack - Trace a hitscan attack
// JDOOM: game/physics/MapMovement.java P_LineAttack
//
// DIVERGENCE: Simplified - no blockmap traversal
// JDOOM: Uses P_PathTraverse with blockmap iteration and intercept sorting
// We iterate all active mobjs and check if they're in the line of fire
// This is less efficient but much simpler and uses less stack
//
// shooter_idx: attacking mobj (-1 for player)
// angle: attack direction (BAM)
// distance: maximum range
// damage: damage to deal
//
// Returns: index of hit mobj, or -1 if hit wall/nothing
// =============================================================================

short P_LineAttack(short shooter_idx, int angle, int distance, short damage) {
    int shootx;
    int shooty;
    int shootz;
    int aimx;
    int aimy;
    int dx;
    int dy;
    int dist;
    int cos_angle;
    int sin_angle;
    short i;
    short best_idx;
    int best_dist;
    int mo_dx;
    int mo_dy;
    int mo_dist;
    int cross;
    int perp_dist;
    int mo_radius;

    // Get shooter position
    if (shooter_idx < 0) {
        // Player is shooting
        shootx = player.x;
        shooty = player.y;
        shootz = player.z + (41 << FRACBITS); // Player eye height
    } else {
        shootx = mobjs[shooter_idx].x;
        shooty = mobjs[shooter_idx].y;
        shootz = mobjs[shooter_idx].z + (mobjs[shooter_idx].height >> 1);
    }

    // Calculate aim direction
    // CRITICAL: Use ANGLE_TO_FINE for unsigned shift, not >> which
    // sign-extends!
    cos_angle = finecosine(ANGLE_TO_FINE(angle));
    sin_angle = finesine(ANGLE_TO_FINE(angle));

    // Aim endpoint
    aimx = shootx + FixedMul(distance, cos_angle);
    aimy = shooty + FixedMul(distance, sin_angle);

    dx = aimx - shootx;
    dy = aimy - shooty;

    // Find closest mobj in line of fire
    best_idx = -1;
    best_dist = distance + 1;

    for (i = 0; i < MAX_MOBJS; i++) {
        if (!mobjs[i].active) {
            continue;
        }

        // Can't shoot yourself
        if (i == shooter_idx) {
            continue;
        }

        // Must be shootable
        if ((mobjs[i].flags & MF_SHOOTABLE) == 0) {
            continue;
        }

        // Vector from shooter to mobj
        mo_dx = mobjs[i].x - shootx;
        mo_dy = mobjs[i].y - shooty;

        // Project onto aim line: dot product / distance
        // frac = (mo_dx * dx + mo_dy * dy) / (distance^2)
        // Simplified: use dot product to check if in front
        mo_dist = FixedMul(mo_dx >> 8, dx >> 8) + FixedMul(mo_dy >> 8, dy >> 8);

        if (mo_dist <= 0) {
            continue; // Behind shooter
        }

        // Perpendicular distance: cross product / distance
        // cross = mo_dx * dy - mo_dy * dx
        cross = FixedMul(mo_dx >> 8, dy >> 8) - FixedMul(mo_dy >> 8, dx >> 8);
        if (cross < 0) {
            cross = -cross;
        }

        // Normalize by distance to get perpendicular distance
        dist = P_AproxDistance(dx, dy);
        if (dist > 0) {
            perp_dist = FixedDiv(cross << 8, dist >> 8);
        } else {
            perp_dist = cross;
        }

        // Check if within mobj radius
        mo_radius = mobjs[i].radius;
        if (perp_dist > mo_radius) {
            continue; // Missed
        }

        // Check actual distance to mobj
        mo_dist = P_AproxDistance(mo_dx, mo_dy);
        if (mo_dist > distance) {
            continue; // Out of range
        }

        // TODO: Check for blocking walls between shooter and target
        // For now, assume clear line of sight (already checked in AI)

        // Is this the closest hit?
        if (mo_dist < best_dist) {
            best_dist = mo_dist;
            best_idx = i;
        }
    }

    // Apply damage to hit target
    if (best_idx >= 0) {
        P_DamageMobj(best_idx, shooter_idx, shooter_idx, damage);
    }

    return best_idx;
}

// =============================================================================
// P_LineAttackPlayer - Player fires hitscan weapon
// Simplified wrapper for player attacks
// =============================================================================

short P_LineAttackPlayer(int angle, int distance, short damage) {
    return P_LineAttack(-1, angle, distance, damage);
}

// =============================================================================
// P_LineAttackMobj - Enemy fires hitscan at player
// JDOOM: Used by A_PosAttack, A_SPosAttack, etc.
//
// DIVERGENCE: Direct player hit check instead of full tracing
// JDOOM uses full P_LineAttack with blockmap traversal
// We check if player is in line of fire and apply damage directly
// =============================================================================

void P_LineAttackMobj(short shooter_idx, int angle, int distance,
                      short damage) {
    int shootx;
    int shooty;
    int dx;
    int dy;
    int px;
    int py;
    int dist_to_player;
    int mo_dx;
    int mo_dy;
    int cross;
    int perp_dist;
    int aim_dist;
    int cos_angle;
    int sin_angle;

    if (shooter_idx < 0 || !mobjs[shooter_idx].active) {
        return;
    }

    shootx = mobjs[shooter_idx].x;
    shooty = mobjs[shooter_idx].y;

    // Check distance to player (player is mobj[0])
    px = mobjs[PLAYER_MOBJ_IDX].x;
    py = mobjs[PLAYER_MOBJ_IDX].y;

    mo_dx = px - shootx;
    mo_dy = py - shooty;
    dist_to_player = P_AproxDistance(mo_dx, mo_dy);

    if (dist_to_player > distance) {
        return;
    }

    // Calculate aim direction
    // CRITICAL: Use ANGLE_TO_FINE for unsigned shift, not >> which
    // sign-extends!
    cos_angle = finecosine(ANGLE_TO_FINE(angle));
    sin_angle = finesine(ANGLE_TO_FINE(angle));

    dx = FixedMul(distance, cos_angle);
    dy = FixedMul(distance, sin_angle);
    aim_dist = P_AproxDistance(dx, dy);

    // Cross product: perpendicular distance to aim line
    cross = FixedMul(mo_dx >> 8, dy >> 8) - FixedMul(mo_dy >> 8, dx >> 8);
    if (cross < 0) {
        cross = -cross;
    }

    // Normalize
    if (aim_dist > 0) {
        perp_dist = FixedDiv(cross << 8, aim_dist >> 8);
    } else {
        perp_dist = cross;
    }

    // Player radius is 16 units
    if (perp_dist > (16 << FRACBITS)) {
        return;
    }

    // Check if player is in front (dot product positive)
    if (FixedMul(mo_dx >> 8, dx >> 8) + FixedMul(mo_dy >> 8, dy >> 8) <= 0) {
        return;
    }

    // TODO: Check for blocking walls

    // Hit! Apply damage to player
    P_DamagePlayer(shooter_idx, damage);
}

// =============================================================================
// A_PosAttack - Zombieman attack action
// JDOOM: game/ai/EnemyAI.java A_PosAttack
//
// Fires a single hitscan bullet at target
// =============================================================================

void A_PosAttack(short mobj_idx) {
    int angle;
    short damage;

    if (!mobjs[mobj_idx].active) {
        return;
    }

    // JDOOM: EnemyAI.java - A_FaceTarget(actor)
    A_FacePlayer(mobj_idx);

    // JDOOM: EnemyAI.java - angle = actor.angle + ((P_Random() - P_Random()) <<
    // 20) Random spread: +/- ~5.6 degrees
    angle = mobjs[mobj_idx].angle;
    angle = angle + ((P_Random() - P_Random()) << 20);

    // JDOOM: EnemyAI.java - damage = ((P_Random() % 5) + 1) * 3
    // Range: 3-15 damage (1*3 to 5*3)
    damage = ((P_Random() % 5) + 1) * 3;

    // JDOOM: EnemyAI.java - P_LineAttack(actor, angle, MISSILERANGE, ...)
    P_LineAttackMobj(mobj_idx, angle, MISSILERANGE, damage);
}

// =============================================================================
// A_SPosAttack - Shotgun Guy attack action
// JDOOM: game/ai/EnemyAI.java A_SPosAttack
//
// Fires 3 hitscan pellets at target
// =============================================================================

void A_SPosAttack(short mobj_idx) {
    int angle;
    int base_angle;
    short damage;
    short i;

    if (!mobjs[mobj_idx].active) {
        return;
    }

    // JDOOM: EnemyAI.java - A_FaceTarget(actor)
    A_FacePlayer(mobj_idx);

    base_angle = mobjs[mobj_idx].angle;

    // JDOOM: EnemyAI.java - for (int i = 0; i < 3; i++)
    // Fire 3 pellets with spread
    for (i = 0; i < 3; i++) {
        // JDOOM: angle = actor.angle + ((P_Random() - P_Random()) << 20)
        angle = base_angle + ((P_Random() - P_Random()) << 20);
        // JDOOM: damage = ((P_Random() % 5) + 1) * 3
        damage = ((P_Random() % 5) + 1) * 3; // 3-15 per pellet
        P_LineAttackMobj(mobj_idx, angle, MISSILERANGE, damage);
    }
}

// =============================================================================
// A_TroopAttack - Imp attack action
// JDOOM: game/ai/EnemyAI.java A_TroopAttack
//
// DIVERGENCE: Hitscan instead of fireball at range
// JDOOM: At melee range, does claw attack (3-24 damage)
// JDOOM: At range, spawns fireball projectile (MT_TROOPSHOT)
// We use hitscan at range instead (projectiles deferred)
// Impact: Imp attacks are instant-hit instead of dodgeable fireballs
// =============================================================================

void A_TroopAttack(short mobj_idx) {
    int dist;
    int angle;
    short damage;

    if (!mobjs[mobj_idx].active) {
        return;
    }

    // JDOOM: EnemyAI.java - A_FaceTarget(actor)
    A_FacePlayer(mobj_idx);

    // Check for melee range
    dist = P_AproxDistance(mobjs[PLAYER_MOBJ_IDX].x - mobjs[mobj_idx].x,
                           mobjs[PLAYER_MOBJ_IDX].y - mobjs[mobj_idx].y);

    // JDOOM: EnemyAI.java - P_CheckMeleeRange checks:
    // dist < MELEERANGE - 20*FRACUNIT + target.info.radius
    // MELEERANGE = 64*FRACUNIT, player radius = 16*FRACUNIT
    if (dist < MELEERANGE - (20 << FRACBITS) + PLAYER_RADIUS) {
        // JDOOM: EnemyAI.java - damage = (P_Random() % 8 + 1) * 3
        // Melee attack: 3-24 damage
        damage = ((P_Random() % 8) + 1) * 3;
        P_DamagePlayer(mobj_idx, damage);
        return;
    }

    // JDOOM: EnemyAI.java - P_SpawnMissile(actor, target, MT_TROOPSHOT)
    // DIVERGENCE: Hitscan instead of fireball projectile
    // Fireball does 3-24 damage on impact, we use same range
    angle = mobjs[mobj_idx].angle;
    angle = angle + ((P_Random() - 128) << 20); // Random spread
    damage = ((P_Random() % 8) + 1) * 3;

    P_LineAttackMobj(mobj_idx, angle, MISSILERANGE, damage);
}

// =============================================================================
// P_ProcessExplosionQueue - Process queued explosion damage iteratively
// Called after thinker actions complete to break recursion cycle.
// Queue can grow during processing (chain reactions), but we iterate not
// recurse.
// =============================================================================

void P_ProcessExplosionQueue(void) {
    short i;
    // Use index loop since queue can grow during processing
    for (i = 0; i < explosion_queue_count; i++) {
        P_DamageMobj(explosion_queue[i].target, explosion_queue[i].inflictor,
                     explosion_queue[i].source, explosion_queue[i].damage);
    }
    explosion_queue_count = 0;
}
