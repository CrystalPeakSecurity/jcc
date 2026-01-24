// weapon.h - Player Weapons (simplified - no weapon sprites/states)

#pragma once

#include "combat.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "movement.h"

// =============================================================================
// Weapon damage constants
// JDOOM: game/player/Weapon.java, game/info/Info.java
// =============================================================================

#define PISTOL_DAMAGE 5   // Per bullet (base) - JDOOM: Weapon.java:223
#define SHOTGUN_DAMAGE 5  // Per pellet (7 pellets) - JDOOM: Weapon.java:223
#define SHOTGUN_PELLETS 7 // JDOOM: Weapon.java:257

// Fire delay in tics (35 tics = 1 second)
// DIVERGENCE: JDOOM uses weapon state tics, not a delay constant
// JDOOM: State tics defined in Info.java for each weapon state
#define PISTOL_DELAY 8   // ~4 shots/sec (approximates JDOOM pistol state tics)
#define SHOTGUN_DELAY 30 // ~1 shot/sec (approximates JDOOM shotgun state tics)

// =============================================================================
// Weapon ammo usage
// JDOOM: Weapon.java:52-96 P_CheckAmmo determines count per weapon
// =============================================================================

#define PISTOL_AMMOUSE                                                         \
    1 // JDOOM: Weapon.java:64 - count = 1 for regular weapons
#define SHOTGUN_AMMOUSE 1 // JDOOM: Weapon.java:64 - count = 1

// =============================================================================
// Weapon state for player
// DIVERGENCE: JDOOM uses pspdef_t with state pointer, tics, sx, sy
// JDOOM: PlayerSprite.java:31-37 pspdef_t
// We just track a cooldown since we don't have weapon sprites
// =============================================================================

short weapon_cooldown; // Tics until can fire again

// =============================================================================
// P_CheckAmmo - Check if player has enough ammo for current weapon
// JDOOM: Weapon.java:52-96 P_CheckAmmo
//
// Returns 1 if can fire, 0 if no ammo
// =============================================================================

short P_CheckAmmo(void) {
    // JDOOM: Weapon.java:52-96
    // JDOOM signature: public static boolean P_CheckAmmo(player_t player)

    // JDOOM: Weapon.java:53-54
    // int ammo;  // ammotype_t
    // int count;

    // JDOOM: Weapon.java:56
    // ammo = weaponinfo[player.readyweapon].ammo;
    // DIVERGENCE: We don't use weaponinfo table, switch on readyweapon directly

    // JDOOM: Weapon.java:59-64 - Determine ammo count needed
    // if (player.readyweapon == wp_bfg) count = BFGCELLS;
    // else if (player.readyweapon == wp_supershotgun) count = 2;
    // else count = 1;
    // DIVERGENCE: We only support count=1 weapons (no BFG/SSG)

    // JDOOM: Weapon.java:68 - am_noammo check
    // if (ammo == am_noammo || player.ammo[ammo] >= count) return true;
    switch (player.readyweapon) {
    case WP_FIST:
        return 1; // JDOOM: Weapon.java:68 - am_noammo always returns true
    case WP_PISTOL:
    case WP_CHAINGUN:
        // JDOOM: Weapon.java:68 - player.ammo[ammo] >= count (ammo=am_clip)
        if (player.ammo_clip >= PISTOL_AMMOUSE) {
            return 1;
        }
        break;
    case WP_SHOTGUN:
        // JDOOM: Weapon.java:68 - player.ammo[ammo] >= count (ammo=am_shell)
        if (player.ammo_shell >= SHOTGUN_AMMOUSE) {
            return 1;
        }
        break;
    }

    // JDOOM: Weapon.java:71-93 - Auto-switch weapon priority
    // Out of ammo, pick a weapon to change to.
    // E1M1 simplified priority (no plasma/chainsaw/missile/BFG):
    //   1. chaingun (if owned && clip > 0)
    //   2. shotgun (if owned && shell > 0)
    //   3. pistol (if clip > 0)
    //   4. fist (fallback - always owned)

    // JDOOM: Weapon.java:75-76
    if (player.weaponowned_chaingun != 0 && player.ammo_clip > 0) {
        player.readyweapon = WP_CHAINGUN;
        // JDOOM: Weapon.java:77-78
    } else if (player.weaponowned_shotgun != 0 && player.ammo_shell > 0) {
        player.readyweapon = WP_SHOTGUN;
        // JDOOM: Weapon.java:79-80
    } else if (player.ammo_clip > 0) {
        player.readyweapon = WP_PISTOL;
        // JDOOM: Weapon.java:88-89
    } else {
        // If everything fails - fist (always owned)
        player.readyweapon = WP_FIST;
    }

    // DIVERGENCE: Weapon.java:93
    // JDOOM: P_SetPsprite(player, ps_weapon,
    // weaponinfo[player.readyweapon].downstate); This starts weapon lowering
    // animation We switch instantly (no animation), so we just set readyweapon
    // directly above

    return 0;
}

// =============================================================================
// P_ConsumeAmmo - Consume ammo for current weapon
// DIVERGENCE: No direct JDOOM equivalent - ammo consumed inline in each fire
// function JDOOM: Weapon.java:236, 251, 268, 288, 299, 304, 309 JDOOM:
// player.ammo[weaponinfo[player.readyweapon].ammo]-- (or -= 2 for SSG, -= 40
// for BFG) We factor out ammo consumption for clarity
// =============================================================================

void P_ConsumeAmmo(void) {
    switch (player.readyweapon) {
    case WP_FIST:
        break; // No ammo needed - JDOOM: am_noammo
    case WP_PISTOL:
    case WP_CHAINGUN:
        // JDOOM: Weapon.java:236, 288 - player.ammo[am_clip]--
        player.ammo_clip = player.ammo_clip - PISTOL_AMMOUSE;
        break;
    case WP_SHOTGUN:
        // JDOOM: Weapon.java:251 - player.ammo[am_shell]--
        player.ammo_shell = player.ammo_shell - SHOTGUN_AMMOUSE;
        break;
    }
}

// =============================================================================
// A_Punch - Fist attack
// JDOOM: Weapon.java:157-177 A_Punch
// =============================================================================

void A_Punch(void) {
    // JDOOM: Weapon.java:157
    // public static void A_Punch(player_t player)
    // DIVERGENCE: We use global player instead of parameter

    int angle;
    short damage;
    short hit_idx;

    // JDOOM: Weapon.java:158-159
    // int angle;  // angle_t
    // int damage;
    // int slope;
    // DIVERGENCE: We don't track slope (no vertical autoaim)

    // JDOOM: Weapon.java:162
    // damage = (Random.P_Random() % 10 + 1) << 1;
    // Note: << 1 is * 2, so damage is 2-20
    damage = ((P_Random() % 10) + 1) * 2;

    // DIVERGENCE: Weapon.java:164-165 - Berserk check missing
    // JDOOM: if (player.powers[pw_strength] != 0) damage *= 10;
    // Berserk multiplies damage by 10 (20-200 damage!)
    // We don't track player.powers[] array

    // JDOOM: Weapon.java:167
    // angle = player.mo.angle;
    angle = player.angle;

    // JDOOM: Weapon.java:168
    // angle += (Random.P_Random() - Random.P_Random()) << 18;
    // Add random spread (triangular distribution - clusters toward center)
    angle = angle + ((P_Random() - P_Random()) << 18);

    // DIVERGENCE: Weapon.java:169 - Missing P_AimLineAttack for autoaim slope
    // JDOOM: slope = MapMovement.P_AimLineAttack(player.mo, angle, MELEERANGE);
    // JDOOM: P_AimLineAttack does vertical autoaim sweep to find target height
    // We don't do vertical autoaim

    // JDOOM: Weapon.java:170
    // MapMovement.P_LineAttack(player.mo, angle, MELEERANGE, slope, damage);
    // DIVERGENCE: We pass 0 for slope implicitly (no vertical autoaim)
    hit_idx = P_LineAttackPlayer(angle, MELEERANGE, damage);

    // DIVERGENCE: Weapon.java:173-176 - Missing turn-to-face-target
    // JDOOM:
    // if (linetarget != null) {
    //     player.mo.angle = Fixed.PointToAngle2(player.mo.x, player.mo.y,
    //         linetarget.x, linetarget.y);
    // }
    // This auto-turns player to face the enemy they just punched
    // We don't turn to face the target after a hit
}

// =============================================================================
// A_FirePistol - Fire pistol
// JDOOM: Weapon.java:232-244 A_FirePistol
// =============================================================================

void A_FirePistol(void) {
    // JDOOM: Weapon.java:232
    // public static void A_FirePistol(player_t player)
    // DIVERGENCE: We use global player instead of parameter

    int angle;
    short damage;

    // DIVERGENCE: Weapon.java:233
    // JDOOM: Mobj.P_SetMobjState(player.mo, S_PLAY_ATK2);
    // Sets player sprite to attack frame 2 (shooting animation)
    // We don't have player sprite states

    // JDOOM: Weapon.java:236
    // player.ammo[weaponinfo[player.readyweapon].ammo]--;
    P_ConsumeAmmo();

    // DIVERGENCE: Weapon.java:239
    // JDOOM: PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_flash,
    //            weaponinfo[player.readyweapon].flashstate);
    // Sets muzzle flash sprite state
    // We don't render weapon sprites or muzzle flash

    // DIVERGENCE: Weapon.java:242
    // JDOOM: P_BulletSlope(player.mo);
    // P_BulletSlope (Weapon.java:213-217) does:
    //   int[] angleRef = {mo.angle};
    //   bulletslope = MapMovement.P_AimLineAttackWithSweep(mo, angleRef,
    //   16*64*FRACUNIT);
    // Vertical autoaim sweep to find target height
    // We don't do vertical autoaim

    // JDOOM: Weapon.java:243
    // P_GunShot(player.mo, player.refire == 0);
    // P_GunShot is inlined here:

    // JDOOM: Weapon.java:223 (in P_GunShot)
    // damage = 5 * (Random.P_Random() % 3 + 1);
    // Damage is 5, 10, or 15 (5-15)
    damage = 5 * ((P_Random() % 3) + 1);

    // JDOOM: Weapon.java:224 (in P_GunShot)
    // angle = mo.angle;
    angle = player.angle;

    // JDOOM: Weapon.java:226-227 (in P_GunShot)
    // if (!accurate)
    //     angle += (Random.P_Random() - Random.P_Random()) << 18;
    // First shot is accurate (refire == 0), subsequent shots spread
    if (player.refire > 0) {
        angle = angle + ((P_Random() - P_Random()) << 18);
    }

    // JDOOM: Weapon.java:229 (in P_GunShot)
    // MapMovement.P_LineAttack(mo, angle, MISSILERANGE, bulletslope, damage);
    // DIVERGENCE: We don't pass bulletslope (no vertical autoaim)
    P_LineAttackPlayer(angle, MISSILERANGE, damage);

    weapon_cooldown = PISTOL_DELAY;
}

// =============================================================================
// A_FireShotgun - Fire shotgun
// JDOOM: Weapon.java:246-259 A_FireShotgun
// =============================================================================

void A_FireShotgun(void) {
    // JDOOM: Weapon.java:246
    // public static void A_FireShotgun(player_t player)
    // DIVERGENCE: We use global player instead of parameter

    int angle;
    int base_angle;
    short damage;
    short i;

    // JDOOM: Weapon.java:247
    // int i;
    // (we use static short i for jcc compatibility)

    // DIVERGENCE: Weapon.java:249
    // JDOOM: Mobj.P_SetMobjState(player.mo, S_PLAY_ATK2);
    // Sets player sprite to attack frame 2
    // We don't have player sprite states

    // JDOOM: Weapon.java:251
    // player.ammo[weaponinfo[player.readyweapon].ammo]--;
    P_ConsumeAmmo();

    // DIVERGENCE: Weapon.java:253
    // JDOOM: PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_flash,
    //            weaponinfo[player.readyweapon].flashstate);
    // Sets muzzle flash sprite state
    // We don't render weapon sprites

    // DIVERGENCE: Weapon.java:255
    // JDOOM: P_BulletSlope(player.mo);
    // Vertical autoaim sweep - see A_FirePistol for details
    // We don't do vertical autoaim

    base_angle = player.angle;

    // JDOOM: Weapon.java:257-258
    // for (i = 0; i < 7; i++)
    //     P_GunShot(player.mo, false);
    // Fire 7 pellets, all inaccurate (false)
    for (i = 0; i < SHOTGUN_PELLETS; i++) {
        // P_GunShot (Weapon.java:219-230) inlined:

        // JDOOM: Weapon.java:223
        // damage = 5 * (Random.P_Random() % 3 + 1);
        damage = 5 * ((P_Random() % 3) + 1);

        // JDOOM: Weapon.java:224
        // angle = mo.angle;
        // JDOOM: Weapon.java:227 (since accurate=false)
        // angle += (Random.P_Random() - Random.P_Random()) << 18;
        angle = base_angle + ((P_Random() - P_Random()) << 18);

        // JDOOM: Weapon.java:229
        // MapMovement.P_LineAttack(mo, angle, MISSILERANGE, bulletslope,
        // damage); DIVERGENCE: We don't pass bulletslope
        P_LineAttackPlayer(angle, MISSILERANGE, damage);
    }

    weapon_cooldown = SHOTGUN_DELAY;
}

// =============================================================================
// P_FireWeapon - Fire current weapon
// JDOOM: Weapon.java:98-111 P_FireWeapon
// =============================================================================

void P_FireWeapon(void) {
    // JDOOM: Weapon.java:98
    // public static void P_FireWeapon(player_t player)
    // DIVERGENCE: We use global player instead of parameter

    // JDOOM: Weapon.java:99
    // int newstate;

    // DIVERGENCE: Weapon.java:98-111 - Cooldown check added
    // JDOOM: Fire rate controlled by weapon state tics, not a cooldown counter
    // JDOOM: P_MovePsprites (PlayerSprite.java:134-155) decrements psp.tics
    // each frame We use a simple cooldown counter instead
    if (weapon_cooldown > 0) {
        return;
    }

    // JDOOM: Weapon.java:102-103
    // Check ammo BEFORE firing, auto-switch if out
    if (!P_CheckAmmo()) {
        return;
    }

    // DIVERGENCE: Weapon.java:105
    // JDOOM: Mobj.P_SetMobjState(player.mo, S_PLAY_ATK1);
    // Sets player sprite to attack frame 1 (winding up)
    // We don't have player sprite states

    // DIVERGENCE: Weapon.java:107-108
    // JDOOM: newstate = weaponinfo[player.readyweapon].atkstate;
    // JDOOM: PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_weapon,
    // newstate); This sets the weapon to its attack state, which has an action
    // function The action function (e.g., A_FirePistol) is called by
    // P_SetPsprite We call the action functions directly below

    // DIVERGENCE: Weapon.java:110
    // JDOOM: EnemyAI.P_NoiseAlert(player.mo, player.mo);
    // Propagates noise through BSP to alert enemies
    // soundtarget on sectors gets set to player
    // We don't have enemy AI noise propagation

    switch (player.readyweapon) {
    case WP_FIST:
        A_Punch();
        // DIVERGENCE: JDOOM fist timing via state machine
        // JDOOM: S_PUNCH1 through S_PUNCH5 states with various tics
        weapon_cooldown = 10; // Approximates JDOOM fist state tics
        break;
    case WP_PISTOL:
        A_FirePistol();
        // weapon_cooldown set in A_FirePistol
        break;
    case WP_SHOTGUN:
        A_FireShotgun();
        // weapon_cooldown set in A_FireShotgun
        break;
    case WP_CHAINGUN:
        // JDOOM: Weapon.java:283-296 A_FireCGun
        // public static void A_FireCGun(player_t player, PlayerSprite.pspdef_t
        // psp)
        //
        // JDOOM: Weapon.java:284-285
        // if (player.ammo[weaponinfo[player.readyweapon].ammo] == 0)
        //     return;
        //
        // JDOOM: Weapon.java:287
        // Mobj.P_SetMobjState(player.mo, S_PLAY_ATK2);
        //
        // JDOOM: Weapon.java:288
        // player.ammo[weaponinfo[player.readyweapon].ammo]--;
        //
        // JDOOM: Weapon.java:290-291
        // PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_flash,
        //     weaponinfo[player.readyweapon].flashstate + psp.diverge_stnum -
        //     S_CHAIN1);
        // NOTE: This alternates between two flash states based on current state
        //
        // JDOOM: Weapon.java:293
        // P_BulletSlope(player.mo);
        //
        // JDOOM: Weapon.java:295
        // P_GunShot(player.mo, player.refire == 0);
        //
        // DIVERGENCE: We reuse A_FirePistol instead of implementing A_FireCGun
        // Same firing logic, just faster cooldown
        A_FirePistol();
        weapon_cooldown = 4; // Half pistol delay - approximates chaingun tics
        break;
    }
}

// =============================================================================
// P_SwitchWeapon - Switch to a new weapon
//
// DIVERGENCE: No direct JDOOM equivalent function
// JDOOM weapon switching is spread across multiple functions:
//
// 1. Something sets player.pendingweapon (input handling, pickup, ammo out)
//
// 2. A_WeaponReady (Weapon.java:127-135) detects pendingweapon change:
//    if (player.pendingweapon != wp_nochange || player.health == 0) {
//        newstate = weaponinfo[player.readyweapon].downstate;
//        PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_weapon, newstate);
//        return;
//    }
//
// 3. A_Lower (Weapon.java:377-404) gradually lowers weapon:
//    psp.sy += LOWERSPEED;  // 6*FRACUNIT per tic
//    if (psp.sy < WEAPONBOTTOM) return;  // Still lowering
//    // Weapon is down, now switch
//    player.readyweapon = player.pendingweapon;
//    PlayerSprite.P_BringUpWeapon(player);
//
// 4. P_BringUpWeapon (PlayerSprite.java:96-108) starts raise:
//    if (player.pendingweapon == wp_nochange)
//        player.pendingweapon = player.readyweapon;
//    newstate = weaponinfo[player.pendingweapon].upstate;
//    player.pendingweapon = wp_nochange;
//    player.psprites[ps_weapon].sy = WEAPONBOTTOM;
//    P_SetPsprite(player, ps_weapon, newstate);
//
// 5. A_Raise (Weapon.java:406-421) gradually raises weapon:
//    psp.sy -= RAISESPEED;  // 6*FRACUNIT per tic
//    if (psp.sy > WEAPONTOP) return;  // Still raising
//    psp.sy = WEAPONTOP;
//    newstate = weaponinfo[player.readyweapon].readystate;
//    PlayerSprite.P_SetPsprite(player, PlayerSprite.ps_weapon, newstate);
//
// We switch weapons instantly without animation states
// =============================================================================

void P_SwitchWeapon(short weapon) {
    // DIVERGENCE: JDOOM uses pendingweapon + state machine for animated switch
    // We just instantly set readyweapon

    // DIVERGENCE: JDOOM doesn't check ammo when switching
    // JDOOM: You can switch to empty weapon, then P_CheckAmmo will auto-switch
    // away We prevent switching to empty weapon for better UX

    switch (weapon) {
    case WP_FIST:
        // JDOOM: wp_fist (0) - no ammo needed
        player.readyweapon = WP_FIST;
        break;
    case WP_PISTOL:
        // JDOOM: wp_pistol (1) - uses am_clip
        if (player.ammo_clip > 0) {
            player.readyweapon = WP_PISTOL;
        }
        break;
    case WP_SHOTGUN:
        // JDOOM: wp_shotgun (2) - uses am_shell
        if (player.ammo_shell > 0) {
            player.readyweapon = WP_SHOTGUN;
        }
        break;
    case WP_CHAINGUN:
        // JDOOM: wp_chaingun (4) - uses am_clip
        if (player.ammo_clip > 0) {
            player.readyweapon = WP_CHAINGUN;
        }
        break;
    }
}

// =============================================================================
// P_WeaponTick - Called each game tic to update weapon state
//
// DIVERGENCE: No direct JDOOM equivalent
// JDOOM: P_MovePsprites (PlayerSprite.java:134-155) handles weapon timing:
//
// for (i = 0; i < NUMPSPRITES; i++) {
//     psp = player.psprites[i];
//     if (psp.state != null) {
//         // a -1 tic count never changes
//         if (psp.tics != -1) {
//             psp.tics--;
//             if (psp.tics == 0)
//                 P_SetPsprite(player, i, psp.state.nextstate);
//         }
//     }
// }
// // Sync flash position to weapon position
// player.psprites[ps_flash].sx = player.psprites[ps_weapon].sx;
// player.psprites[ps_flash].sy = player.psprites[ps_weapon].sy;
//
// JDOOM: Each state has a tics count, when it hits 0, advance to nextstate
// JDOOM: States can have action functions called on transition
// We use a simple cooldown counter instead of full state machine
// =============================================================================

void P_WeaponTick(void) {
    // Decrement cooldown each tic
    if (weapon_cooldown > 0) {
        weapon_cooldown = weapon_cooldown - 1;
    }
}
