#!/usr/bin/env python3
"""Quick stack probe using direct JCCClient session."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
CLIENT_CP = (
    f"{ROOT}/etc/jcdk-sim/client/COMService/socketprovider.jar:{ROOT}/etc/jcdk-sim/client/AMService/amservice.jar"
)
CLIENT_DIR = ROOT / "etc/jcdk-sim-client"
AID = "DA43B630ED9302AABB0101"

SLOTS = [1, 2, 3, 5, 7, 11, 15, 23, 31, 47, 63, 95, 127, 191, 255]


class Session:
    def __init__(self):
        cmd = ["java", "-cp", f"{CLIENT_CP}:{CLIENT_DIR}", "JCCClient", "session", AID]
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT
        )
        line = self.proc.stdout.readline()
        resp = json.loads(line)
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed: {resp}")

    def send(self, apdu_hex):
        self.proc.stdin.write(apdu_hex + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            return None, 0
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def close(self):
        self.proc.stdin.write("quit\n")
        self.proc.stdin.flush()
        self.proc.wait()


def probe(session, slots):
    p1 = (slots >> 8) & 0xFF
    p2 = slots & 0xFF
    _, sw = session.send(f"8001{p1:02X}{p2:02X}")
    return sw == 0x9000


print("=" * 50)
print("JavaCard Stack Probe (simulator)")
print("=" * 50)

s = Session()

# Binary search
low, high = 0, len(SLOTS) - 1
last_ok, first_fail = 0, SLOTS[-1] + 1

while low <= high:
    mid = (low + high) // 2
    n = SLOTS[mid]
    ok = probe(s, n)
    print(f"  {n:4d} slots: {'OK' if ok else 'OVERFLOW'}")
    if ok:
        last_ok = n
        low = mid + 1
    else:
        first_fail = n
        high = mid - 1

print()
print(f"RESULT: Max slots = {last_ok} (fails at {first_fail})")
print("=" * 50)

s.close()
