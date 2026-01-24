# JavaCard Performance Benchmarks

Micro-benchmarks for understanding JavaCard operation costs.

## Quick Start

```bash
# Compile benchmarks
just bench-compile

# Run on simulator (start sim first with `just _sim_start`)
just sim load tools/perf/bench.cap A0000000620300D002 A0000000620300D00201 A0000000620300D00201
just bench

# Run on real card
just card-install tools/perf/bench.c
just bench-card
```

## Benchmarks

### Variable Access (0x10-0x17)
| INS | Name | Description |
|-----|------|-------------|
| 0x10 | local_short | Local variable (short) - stack-based |
| 0x11 | local_int | Local variable (int) - stack-based |
| 0x12 | static_short | Static local (short) - MEM_S heap |
| 0x13 | static_int | Static local (int) - MEM_S heap |
| 0x14 | global_short | Global variable (short) - MEM_S heap |
| 0x15 | global_int | Global variable (int) - MEM_S heap |
| 0x16 | array_short | Array element (short) - bounds-checked |
| 0x17 | array_int | Array element (int) - bounds-checked |

### Arithmetic (0x20-0x2F)
| INS | Name | Description |
|-----|------|-------------|
| 0x20 | add_short | Addition (short) |
| 0x21 | add_int | Addition (int) |
| 0x22 | sub_short | Subtraction (short) |
| 0x23 | sub_int | Subtraction (int) |
| 0x24 | mul_short | Multiply by 7 (short) |
| 0x25 | mul_int | Multiply by 7 (int) |
| 0x26 | div_short | Divide by 7 (short) |
| 0x27 | div_int | Divide by 7 (int) |
| 0x28 | mod_short | Modulo by 7 (short) |
| 0x29 | mod_int | Modulo by 7 (int) |
| 0x2A | and_int | Bitwise AND (int) |
| 0x2B | or_int | Bitwise OR (int) |
| 0x2C | xor_int | Bitwise XOR (int) |
| 0x2D | shl_int | Shift left (int) |
| 0x2E | shr_int | Arithmetic shift right (int) |
| 0x2F | ushr_int | Logical shift right (int) |

### Control Flow (0x30-0x35)
| INS | Name | Description |
|-----|------|-------------|
| 0x30 | loop_empty | Empty loop (loop overhead) |
| 0x31 | loop_work | Loop with work (sum) |
| 0x32 | call_void | Function call (no params) |
| 0x33 | call_params | Function call (3 int params) |
| 0x34 | call_return | Function call (with return) |
| 0x35 | if_else | If/else branching |

### I/O (0x40-0x41)
| INS | Name | Description |
|-----|------|-------------|
| 0x40 | io_send_large | Send 200 bytes, recv 1 |
| 0x41 | io_recv_large | Recv 200 bytes, send 1 |

### DOOM Operations (0x50-0x54)
| INS | Name | Description |
|-----|------|-------------|
| 0x50 | fixed_mul | FixedMul (16.16 fixed-point) |
| 0x51 | fixed_div | FixedDiv (16.16 fixed-point) |
| 0x52 | trig_sine | Sine table lookup |
| 0x54 | point_to_angle | PointToAngle calculation |

### Memory (0x60-0x61)
| INS | Name | Description |
|-----|------|-------------|
| 0x60 | memset_loop | memset via loop (64 bytes) |
| 0x61 | memset_native | memset via Util.arrayFillNonAtomic |

## Usage

```bash
# Run all benchmarks with defaults (1000 iterations, 5 runs)
just bench

# More iterations for accuracy
just bench -n 5000

# Filter to specific benchmarks
just bench -f mul
just bench -f fixed

# Include I/O benchmarks
just bench --io

# Run on real card
just bench-card -n 100
```

## Output

```
================================================================================
BENCHMARK RESULTS
================================================================================

Benchmark            Avg (ms)   Adj (ms)   us/op      ops/sec      Description
--------------------------------------------------------------------------------
noop                     5.23       0.00      0.00         inf      No-op (APDU overhead)
local_short             12.45       7.22      7.22     138,504      Local variable (short)
local_int               18.67      13.44     13.44      74,404      Local variable (int)
...
```

- **Avg (ms)**: Total time including APDU overhead
- **Adj (ms)**: Time minus baseline (pure computation)
- **us/op**: Microseconds per operation (adjusted)
- **ops/sec**: Operations per second (adjusted)

## Notes

- Simulator results are useful for relative comparisons
- Real card results will differ significantly (slower, but more consistent)
- Run multiple times to check for variance
- For DOOM, FixedMul and FixedDiv are critical hot-path operations
