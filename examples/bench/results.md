# JCVM Instruction Cost (Raw Measurements)

**Card:** J3R180 — 1000 iters × 5 runs × 7 suites (drop hi/lo) — empty-loop baseline subtracted

## 0 Push, 0 Pop

| Instruction | us | cost |
|---|--:|--:|
| `goto_w L; L:` | 3.1 | 1.1x |
| `sinc 3 1` | 4.2 | 1.5x |
| `iinc 3 1` | 4.3 | 1.5x |
| `nop` | 65.5 | 23.4x |
| `invokestatic (void)` | 21.7 | 3.9x |

## 1 Push, 1 Pop (short)

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `sconst 5; pop` | 5.7 | +0.0 | 1.0x |
| `bspush 5; pop` | 6.6 | +0.8 | 1.3x |
| `sspush 5; pop` | 6.8 | +1.1 | 1.4x |
| `sload; pop` | 5.9 | +0.2 | 1.1x |
| `aload; pop` | 6.1 | +0.4 | 1.2x |
| `getstatic_a; pop` | 10.7 | +5.0 | 2.8x |
| `getfield_a_this; pop` | 17.6 | +11.9 | 5.3x |
| `sconst 5; sstore` | 7.0 | +1.3 | 1.5x |
| `sconst 5; sneg; pop` | 9.1 | +3.4 | 1.3x |
| `sconst 5; s2b; pop` | 9.1 | +3.4 | 1.3x |
| `sconst 5; ifeq L; L:` | 7.2 | +1.5 | 1.6x |
| `sconst 5; ifne L; L:` | 8.0 | +2.3 | 1.9x |
| `sconst 1; slookupswitch L; L:` | 9.5 | +3.8 | 2.4x |
| `sconst 0; stableswitch L; L:` | 12.4 | +6.6 | 3.4x |
| `invokestatic (short); pop` | 29.3 | +23.6 | 4.2x |

## 1 Push, 1 Pop (int)

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `iconst 5; pop2` | 6.3 | +0.0 | 1.0x |
| `bipush 5; pop2` | 6.8 | +0.5 | 1.4x |
| `sipush 5; pop2` | 6.7 | +0.4 | 1.4x |
| `iipush 5; pop2` | 7.7 | +1.4 | 1.7x |
| `iload; pop2` | 6.4 | +0.1 | 1.3x |
| `iconst 5; istore` | 8.3 | +2.0 | 2.0x |
| `iconst 5; i2s; pop` | 8.5 | +2.2 | 1.0x |
| `iconst 5; i2b; pop` | 9.7 | +3.4 | 1.5x |
| `iconst 5; ineg; pop2` | 9.7 | +3.4 | 1.5x |
| `invokestatic (int); pop2` | 29.6 | +23.3 | 4.3x |

## 2 Push, 2 Pop (short)

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `sconst 5; sconst 3; pop2` | 9.3 | +0.0 | 1.0x |
| `sconst 5; sconst 3; pop; pop` | 11.7 | +2.4 | 1.0x |
| `sconst 5; dup; pop; pop` | 11.6 | +2.3 | 1.2x |
| `sconst 5; sconst 3; sadd; pop` | 12.5 | +3.2 | 1.5x |
| `sconst 5; sconst 3; ssub; pop` | 12.4 | +3.1 | 1.4x |
| `sconst 5; sconst 3; smul; pop` | 13.1 | +3.8 | 1.7x |
| `sconst 5; sconst 3; sdiv; pop` | 14.7 | +5.4 | 2.2x |
| `sconst 5; sconst 3; srem; pop` | 15.5 | +6.3 | 2.6x |
| `sconst 5; sconst 3; sand; pop` | 12.9 | +3.6 | 1.6x |
| `sconst 5; sconst 3; sor; pop` | 12.7 | +3.4 | 1.5x |
| `sconst 5; sconst 3; sxor; pop` | 12.6 | +3.3 | 1.5x |
| `sconst 5; sconst 3; sshl; pop` | 14.2 | +4.9 | 2.1x |
| `sconst 5; sconst 3; sshr; pop` | 14.0 | +4.7 | 2.0x |
| `sconst 5; sconst 3; sushr; pop` | 14.0 | +4.7 | 2.0x |
| `sconst 3; sconst 5; if_scmplt L; L:` | 11.4 | +2.1 | 2.1x |
| `sconst 5; sconst 5; if_scmpeq L; L:` | 11.5 | +2.2 | 2.1x |

## 2 Push, 2 Pop (int)

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `iconst 5; iconst 3; pop2; pop2` | 12.5 | +0.0 | 1.0x |
| `iconst 5; iconst 3; iadd; pop2` | 13.9 | +1.4 | 2.0x |
| `iconst 5; iconst 3; isub; pop2` | 13.8 | +1.3 | 1.9x |
| `iconst 5; iconst 3; imul; pop2` | 15.5 | +3.0 | 2.6x |
| `iconst 5; iconst 3; idiv; pop2` | 16.6 | +4.1 | 2.9x |
| `iconst 5; iconst 3; irem; pop2` | 19.0 | +6.5 | 3.8x |
| `iconst 5; iconst 3; iand; pop2` | 13.8 | +1.3 | 1.9x |
| `iconst 5; iconst 3; ior; pop2` | 13.9 | +1.4 | 2.0x |
| `iconst 5; iconst 3; ixor; pop2` | 13.8 | +1.3 | 1.9x |
| `iconst 5; iconst 3; ishl; pop2` | 15.0 | +2.5 | 2.4x |
| `iconst 5; iconst 3; ishr; pop2` | 15.2 | +2.7 | 2.4x |
| `iconst 5; iconst 3; iushr; pop2` | 14.9 | +2.4 | 2.3x |
| `iconst 5; iconst 3; icmp; pop` | 14.2 | +1.7 | 2.1x |

## Array Access

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `getstatic_a; sconst 0; pop2` | 13.7 | +0.0 | 2.9x |
| `getstatic_a; sconst 0; pop; pop` | 16.2 | +2.5 | 2.8x |
| `getstatic_b; pop (direct field)` | 10.7 | -3.0 | 2.8x |
| `getstatic_a; sconst 0; baload; pop (array)` | 29.0 | +15.3 | 4.2x |
| `getstatic_s; pop (direct field)` | 10.8 | -2.9 | 2.9x |
| `getstatic_a; sconst 1; saload; pop (array)` | 30.7 | +17.0 | 4.5x |
| `sconst 5; putstatic_b (direct field)` | 11.9 | -1.8 | 3.3x |
| `getstatic_a; sconst 0; sconst 5; bastore (array)` | 29.2 | +15.5 | 4.2x |
| `sconst 5; putstatic_s (direct field)` | 12.0 | -1.7 | 3.3x |
| `getstatic_a; sconst 1; sconst 5; sastore (array)` | 33.6 | +19.9 | 5.0x |
| `getstatic_a; sconst 0; sconst 5; bastore; baload; pop` | 58.5 | +44.8 | 3.6x |
| `getstatic_a; sconst 1; sconst 5; sastore; saload; pop` | 64.3 | +50.6 | 4.0x |

## Exceptions

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `aconst_null; athrow (baseline)` | 50.2 | +0.0 | 15.9x |
| `sconst 5; aconst_null; athrow` | 55.2 | +5.0 | 16.7x |
| `iconst 5; aconst_null; athrow` | 57.4 | +7.2 | 17.5x |
| `sload 3; aconst_null; athrow` | 58.7 | +8.5 | 9.5x |

## Linear Array Access (1000 bytes)

| Instruction | us | Δ baseline | cost |
|---|--:|--:|--:|
| `getstatic_a; sload i; sconst 5; pop2; pop (baseline)` | 19.8 | +0.0 | 2.0x |
| `getstatic_a RAM; sload i; baload; pop` | 29.3 | +9.4 | 3.2x |
| `getstatic_a EEPROM; sload i; baload; pop` | 30.0 | +10.2 | 3.2x |
| `getstatic_a RAM; sload i; sconst 5; bastore` | 29.5 | +9.7 | 3.2x |
| `getstatic_a EEPROM; sload i; sconst 5; bastore` | 29.7 | +9.8 | 3.2x |
