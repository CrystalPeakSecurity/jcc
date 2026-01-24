#!/usr/bin/env python3
"""
JavaCard Performance Benchmark Runner

Runs benchmarks on JavaCard simulator or real card and measures timing.

Usage:
    python run.py [--iterations N] [--runs R] [--card]
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Paths
ROOT = Path(__file__).parent.parent.parent  # tools/perf -> tools -> root
CLIENT_CP = f"{ROOT}/etc/jcdk-sim/client/COMService/socketprovider.jar:{ROOT}/etc/jcdk-sim/client/AMService/amservice.jar"
CLIENT_DIR = ROOT / "etc/jcdk-sim-client"

# AIDs for benchmark applet
PKG_AID = "A0000000620300D002"
APPLET_AID = "A0000000620300D00201"

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
    ("mul_short", 0x24, "Multiply by 7 (short)"),
    ("mul_int", 0x25, "Multiply by 7 (int)"),
    ("div_short", 0x26, "Divide by 7 (short)"),
    ("div_int", 0x27, "Divide by 7 (int)"),
    ("mod_short", 0x28, "Modulo by 7 (short)"),
    ("mod_int", 0x29, "Modulo by 7 (int)"),
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


class CardSession:
    """Persistent session with the JavaCard applet via JCCClient."""

    def __init__(self, aid=APPLET_AID):
        self.aid = aid
        self.process = None
        self._start()

    def _start(self):
        cmd = [
            "java", "-cp", f"{CLIENT_CP}:{CLIENT_DIR}",
            "JCCClient", "session", self.aid
        ]
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT
        )
        line = self.process.stdout.readline()
        if not line:
            stderr = self.process.stderr.read()
            raise RuntimeError(f"Session failed to start: {stderr}")
        resp = json.loads(line)
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed to start: {resp}")

    def send(self, apdu_hex: str) -> tuple:
        """Send APDU, return (data, sw)."""
        self.process.stdin.write(apdu_hex + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(resp["error"])
        data = bytes.fromhex(resp.get("data", ""))
        sw = resp.get("sw", 0)
        return data, sw

    def close(self):
        if self.process:
            self.process.stdin.write("quit\n")
            self.process.stdin.flush()
            self.process.wait()
            self.process = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class RealCardInterface:
    """Interface to real JavaCard via GlobalPlatformPro."""

    def __init__(self):
        self.gp_jar = ROOT / "etc/gp/gp.jar"

    def send(self, apdu_hex: str) -> tuple:
        """Send APDU via gp tool."""
        formatted = " ".join(apdu_hex[i:i+2] for i in range(0, len(apdu_hex), 2))
        cmd = ["java", "-jar", str(self.gp_jar), "-d", "--applet", APPLET_AID, "-a", formatted]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)

        # Parse GP output format: A<< (0001+2) (8ms) 00 9000
        # Find all A<< response lines, take the second one (first is SELECT response)
        responses = []
        for line in result.stdout.split('\n'):
            if line.startswith('A<<'):
                # Format: A<< (NNNN+2) (Xms) [DATA] SWSW
                parts = line.split(')')
                if len(parts) >= 3:
                    data_sw = parts[-1].strip().split()
                    if data_sw:
                        sw_hex = data_sw[-1]
                        if len(sw_hex) == 4:
                            try:
                                sw = int(sw_hex, 16)
                                data_parts = data_sw[:-1]
                                data_hex = ''.join(data_parts)
                                data = bytes.fromhex(data_hex) if data_hex else b""
                                responses.append((data, sw))
                            except ValueError:
                                pass

        # Second response is our command (first is SELECT)
        if len(responses) >= 2:
            return responses[1]
        elif len(responses) == 1:
            return responses[0]

        if result.returncode != 0:
            raise RuntimeError(f"GP failed: {result.stderr}")
        return b"", 0x9000

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def ensure_simulator_ready():
    """Ensure simulator is running and applet is loaded."""
    cap_file = ROOT / "tools/perf/bench.cap"

    # Check if CAP file exists, compile if not
    if not cap_file.exists():
        print("Compiling benchmark applet...")
        result = subprocess.run(
            ["just", "compile", "tools/perf/bench.c"],
            cwd=ROOT, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Compile failed: {result.stderr}")
            sys.exit(1)

    # Try to connect - if it fails, restart simulator and load applet
    try:
        with CardSession() as session:
            # Quick test - send noop
            session.send("0000000000")
            return  # Already working
    except:
        pass  # Need to set up

    print("Starting simulator...")
    subprocess.run(["just", "_sim_restart"], cwd=ROOT, capture_output=True)

    print("Loading benchmark applet...")
    result = subprocess.run(
        ["just", "sim", "load", str(cap_file), PKG_AID, APPLET_AID, APPLET_AID],
        cwd=ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Load failed: {result.stderr}")
        print(result.stdout)
        sys.exit(1)

    # Give it a moment
    time.sleep(0.5)


def build_apdu(ins: int, iterations: int, extra_data: bytes = b"") -> str:
    """Build APDU hex string with extended APDU support for data > 255 bytes."""
    iter_hi = (iterations >> 8) & 0xFF
    iter_lo = iterations & 0xFF
    data = bytes([iter_hi, iter_lo]) + extra_data
    lc = len(data)

    if lc <= 255:
        # Standard APDU: CLA INS P1 P2 Lc Data
        return f"00{ins:02X}0000{lc:02X}" + data.hex().upper()
    else:
        # Extended APDU: CLA INS P1 P2 00 Lc_hi Lc_lo Data
        lc_hi = (lc >> 8) & 0xFF
        lc_lo = lc & 0xFF
        return f"00{ins:02X}000000{lc_hi:02X}{lc_lo:02X}" + data.hex().upper()


def run_benchmark(card, name: str, ins: int, description: str,
                  iterations: int, runs: int) -> BenchmarkResult:
    """Run a single benchmark and return results."""
    times = []

    # Special handling for I/O recv benchmarks - send appropriate amount of data
    if name == "io_recv_200":
        extra_data = bytes(range(200))
        apdu = build_apdu(ins, iterations, extra_data)
    else:
        apdu = build_apdu(ins, iterations)

    for _ in range(runs):
        start = time.perf_counter()
        data, sw = card.send(apdu)
        elapsed = time.perf_counter() - start

        if sw != 0x9000:
            print(f"  Warning: {name} returned SW={sw:04X}")

        times.append(elapsed * 1000)  # ms

    return BenchmarkResult(
        name=name,
        description=description,
        iterations=iterations,
        runs=runs,
        times_ms=times
    )


def print_results(results: list, baseline_ms: float):
    """Print benchmark results in a nice table."""
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
        adj_ops_per_sec = (r.iterations * 1000) / adj_ms if adj_ms > 0 else float('inf')

        ops_str = f"{adj_ops_per_sec:,.0f}" if adj_ops_per_sec < 1e9 else "inf"

        print(f"{r.name:<20} {r.avg_ms:>8.2f}  {adj_ms:>8.2f}  {adj_us_per_op:>8.2f}  {ops_str:>10}  {r.description}")

    print()


def main():
    parser = argparse.ArgumentParser(description="JavaCard Performance Benchmarks")
    parser.add_argument("--iterations", "-n", type=int, default=1000,
                        help="Iterations per benchmark")
    parser.add_argument("--runs", "-r", type=int, default=5,
                        help="Runs per benchmark for averaging")
    parser.add_argument("--card", action="store_true",
                        help="Use real card instead of simulator")
    parser.add_argument("--filter", "-f", type=str, default=None,
                        help="Only run benchmarks matching pattern")
    args = parser.parse_args()

    # Select card interface
    if args.card:
        card_class = RealCardInterface
        print("Using real card")
    else:
        card_class = CardSession
        print("Using simulator")
        ensure_simulator_ready()

    print(f"Iterations: {args.iterations}, Runs: {args.runs}")
    print()

    # Filter benchmarks
    benchmarks = BENCHMARKS.copy()
    if args.filter:
        benchmarks = [(n, i, d) for n, i, d in benchmarks if args.filter in n]

    # Run benchmarks
    results = []
    baseline_ms = 0

    try:
        with card_class() as card:
            for name, ins, desc in benchmarks:
                print(f"Running {name}...", end=" ", flush=True)
                try:
                    result = run_benchmark(card, name, ins, desc, args.iterations, args.runs)
                    results.append(result)
                    print(f"{result.avg_ms:.2f} ms")

                    if name == "noop":
                        baseline_ms = result.avg_ms

                except Exception as e:
                    print(f"ERROR: {e}")

    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    # Print results
    if results:
        print_results(results, baseline_ms)

        print("NOTES:")
        print(f"  - Baseline (APDU overhead): {baseline_ms:.2f} ms")
        print(f"  - 'Adj (ms)' = time - baseline")
        print(f"  - 'us/op' = microseconds per operation (adjusted)")
        print()


if __name__ == "__main__":
    main()
