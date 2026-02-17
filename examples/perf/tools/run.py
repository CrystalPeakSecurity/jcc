#!/usr/bin/env python3
"""JavaCard performance benchmark runner.

Runs benchmarks on a loaded applet and measures timing.
The applet must already be loaded (use `just load examples/perf`).

Usage:
    python run.py              # Run all benchmarks on simulator
    python run.py --card       # Run on real card
    python run.py -f mul       # Filter by name
    python run.py -n 5000      # 5000 iterations per benchmark
"""

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from jcc.driver import BaseDriver
from jcc.driver.session import get_session
from jcc.driver.config import load_config

# Benchmark definitions: (name, INS code, description)
BENCHMARKS = [
    # Baseline
    ("noop", 0x00, "No-op (APDU overhead)"),

    # Variable access
    ("local_short", 0x10, "Local variable (short)"),
    ("local_int", 0x11, "Local variable (int)"),
    ("static_short", 0x12, "Static local (short)"),
    ("static_int", 0x13, "Static local (int)"),
    ("global_short", 0x14, "Global/offheap (short)"),
    ("global_int", 0x15, "Global/offheap (int)"),
    ("array_short", 0x16, "Array element (short)"),
    ("array_int", 0x17, "Array element (int)"),

    # Arithmetic
    ("add_short", 0x20, "Addition (short)"),
    ("add_int", 0x21, "Addition (int)"),
    ("sub_short", 0x22, "Subtraction (short)"),
    ("sub_int", 0x23, "Subtraction (int)"),
    ("mul_short", 0x24, "Multiply (short)"),
    ("mul_int", 0x25, "Multiply (int)"),
    ("div_short", 0x26, "Divide (short)"),
    ("div_int", 0x27, "Divide (int)"),
    ("mod_short", 0x28, "Modulo (short)"),
    ("mod_int", 0x29, "Modulo (int)"),
    ("and_int", 0x2A, "Bitwise AND (int)"),
    ("or_int", 0x2B, "Bitwise OR (int)"),
    ("xor_int", 0x2C, "Bitwise XOR (int)"),
    ("shl_int", 0x2D, "Shift left (int)"),
    ("shr_int", 0x2E, "Arith shift right (int)"),
    ("ushr_int", 0x2F, "Logic shift right (int)"),

    # Control flow
    ("loop_empty", 0x30, "Empty loop"),
    ("loop_work", 0x31, "Loop with work"),
    ("call_void", 0x32, "Function call (void)"),
    ("call_params", 0x33, "Function call (3 params)"),
    ("call_return", 0x34, "Function call (return)"),
    ("if_else", 0x35, "If/else branch"),

    # DOOM-specific
    ("fixed_mul", 0x50, "FixedMul (16.16)"),
    ("fixed_div", 0x51, "FixedDiv (16.16)"),
    ("trig_sine", 0x52, "Sine lookup"),
    ("point_to_angle", 0x54, "PointToAngle"),

    # Memory
    ("memset_loop", 0x60, "memset via loop (64B)"),
    ("memset_native", 0x61, "memset native (64B)"),

    # I/O
    ("io_send_200", 0x40, "Card sends 200B"),
    ("io_recv_200", 0x41, "Card recvs 200B"),
]


@dataclass
class BenchmarkResult:
    name: str
    description: str
    iterations: int
    runs: int
    times_ms: list

    @property
    def avg_ms(self) -> float:
        return sum(self.times_ms) / len(self.times_ms) if self.times_ms else 0

    @property
    def min_ms(self) -> float:
        return min(self.times_ms) if self.times_ms else 0

    @property
    def max_ms(self) -> float:
        return max(self.times_ms) if self.times_ms else 0


def build_apdu(ins: int, iterations: int, extra_data: bytes = b"") -> str:
    """Build APDU hex string."""
    iter_hi = (iterations >> 8) & 0xFF
    iter_lo = iterations & 0xFF
    data = bytes([iter_hi, iter_lo]) + extra_data
    lc = len(data)
    return f"00{ins:02X}0000{lc:02X}" + data.hex().upper()


def run_benchmark(session, name, ins, description, iterations, runs):
    """Run a single benchmark and return results."""
    times = []

    if name == "io_recv_200":
        extra_data = bytes(range(200))
        apdu = build_apdu(ins, iterations, extra_data)
    else:
        apdu = build_apdu(ins, iterations)

    for _ in range(runs):
        start = time.perf_counter()
        data, sw = session.send(apdu)
        elapsed = time.perf_counter() - start

        if sw != 0x9000:
            print(f"  Warning: {name} returned SW={sw:04X}")

        times.append(elapsed * 1000)

    return BenchmarkResult(
        name=name,
        description=description,
        iterations=iterations,
        runs=runs,
        times_ms=times,
    )


def print_results(results, baseline_ms):
    """Print benchmark results in a table."""
    print()
    print("=" * 85)
    print("BENCHMARK RESULTS")
    print("=" * 85)
    print()
    print(f"{'Benchmark':<20} {'Avg (ms)':<10} {'Adj (ms)':<10} {'us/op':<10} {'ops/sec':<12} Description")
    print("-" * 85)

    for r in results:
        adj_ms = max(0, r.avg_ms - baseline_ms)
        adj_us_per_op = (adj_ms * 1000) / r.iterations if r.iterations > 0 else 0
        adj_ops_per_sec = (r.iterations * 1000) / adj_ms if adj_ms > 0 else float("inf")

        ops_str = f"{adj_ops_per_sec:,.0f}" if adj_ops_per_sec < 1e9 else "inf"

        print(f"{r.name:<20} {r.avg_ms:>8.2f}  {adj_ms:>8.2f}  {adj_us_per_op:>8.2f}  {ops_str:>10}  {r.description}")

    print()


def main():
    parser = argparse.ArgumentParser(description="JavaCard Performance Benchmarks")
    parser.add_argument("--iterations", "-n", type=int, default=10000,
                        help="Iterations per benchmark")
    parser.add_argument("--runs", "-r", type=int, default=5,
                        help="Runs per benchmark for averaging")
    parser.add_argument("--card", action="store_true",
                        help="Use real card instead of simulator")
    parser.add_argument("--filter", "-f", type=str, default=None,
                        help="Only run benchmarks matching pattern")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    config = load_config(root_dir)
    backend = "card" if args.card else None

    print(f"Backend: {'card' if args.card else 'simulator'}")
    print(f"Iterations: {args.iterations}, Runs: {args.runs}")

    benchmarks = BENCHMARKS.copy()
    if args.filter:
        benchmarks = [(n, i, d) for n, i, d in benchmarks if args.filter in n]

    results = []
    baseline_ms = 0

    with get_session(config.applet_aid, backend=backend) as session:
        # Warmup: send a few noop APDUs to stabilize JVM/simulator timing
        warmup_apdu = build_apdu(0x00, 1)
        for _ in range(3):
            session.send(warmup_apdu)

        for name, ins, desc in benchmarks:
            print(f"Running {name}...", end=" ", flush=True)
            try:
                result = run_benchmark(session, name, ins, desc, args.iterations, args.runs)
                results.append(result)
                print(f"{result.avg_ms:.2f} ms")

                if name == "noop":
                    baseline_ms = result.avg_ms
            except Exception as e:
                print(f"ERROR: {e}")

    if results:
        print_results(results, baseline_ms)
        print("NOTES:")
        print(f"  - Baseline (APDU overhead): {baseline_ms:.2f} ms")
        print(f"  - 'Adj (ms)' = time - baseline")
        print(f"  - 'us/op' = microseconds per operation (adjusted)")
        print()


if __name__ == "__main__":
    main()
