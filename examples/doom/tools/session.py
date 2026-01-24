#!/usr/bin/env python3
"""
session.py - Persistent session daemon for JavaCard applet

Holds a single CardSession open and accepts commands via Unix socket.
This prevents card resets between commands.

Usage:
    session.py start <instance-aid>  - Start daemon (blocks)
    session.py stop                  - Stop running daemon
    session.py status                - Check if daemon is running
"""

import json
import os
import socket
import sys
from pathlib import Path

# Import from driver.py (same directory)
sys.path.insert(0, str(Path(__file__).parent))
from driver import CardSession, build_apdu, parse_log, format_log_entry, INS_READ_LOG

SOCKET_PATH = "/tmp/jcc-doom-session.sock"
PID_PATH = "/tmp/jcc-doom-session.pid"


def handle_command(session: CardSession, cmd: dict) -> dict:
    """Handle a command from a client."""
    try:
        action = cmd.get("action")

        if action == "ping":
            return {"ok": True}

        elif action == "quit":
            return {"ok": True, "quit": True}

        elif action == "apdu":
            # Raw APDU send
            apdu_hex = cmd.get("apdu")
            if not apdu_hex:
                return {"error": "Missing 'apdu' field"}
            data, sw = session.send(apdu_hex)
            return {"data": data.hex().upper(), "sw": sw}

        elif action == "apdu_ok":
            # APDU send, expect SW=9000
            apdu_hex = cmd.get("apdu")
            if not apdu_hex:
                return {"error": "Missing 'apdu' field"}
            try:
                data = session.send_ok(apdu_hex)
                return {"data": data.hex().upper()}
            except RuntimeError as e:
                return {"error": str(e)}

        elif action == "read-log":
            data = session.send_ok(build_apdu(INS_READ_LOG))
            entries = parse_log(data) if data else []
            return {"entries": [format_log_entry(e) for e in entries]}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        return {"error": str(e)}


def run_daemon(instance_aid: str):
    """Run the session daemon."""
    # Clean up old socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    # Write PID file
    with open(PID_PATH, "w") as f:
        f.write(str(os.getpid()))

    # Create socket
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    print(f"Session daemon started, listening on {SOCKET_PATH}", file=sys.stderr)

    try:
        # Create the persistent session
        with CardSession(instance_aid) as session:
            print("Card session established", file=sys.stderr)

            while True:
                conn, _ = server.accept()
                try:
                    data = conn.recv(4096).decode("utf-8").strip()
                    if not data:
                        continue

                    cmd = json.loads(data)
                    response = handle_command(session, cmd)

                    conn.sendall((json.dumps(response) + "\n").encode("utf-8"))

                    if response.get("quit"):
                        print("Quit command received", file=sys.stderr)
                        break

                except json.JSONDecodeError as e:
                    conn.sendall((json.dumps({"error": f"Invalid JSON: {e}"}) + "\n").encode("utf-8"))
                except Exception as e:
                    conn.sendall((json.dumps({"error": str(e)}) + "\n").encode("utf-8"))
                finally:
                    conn.close()

    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        if os.path.exists(PID_PATH):
            os.unlink(PID_PATH)
        print("Session daemon stopped", file=sys.stderr)


def send_command(cmd: dict) -> dict:
    """Send a command to the running daemon."""
    if not os.path.exists(SOCKET_PATH):
        raise RuntimeError("Session daemon not running")

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    try:
        client.sendall((json.dumps(cmd) + "\n").encode("utf-8"))
        response = client.recv(65536).decode("utf-8").strip()
        return json.loads(response)
    finally:
        client.close()


def stop_daemon():
    """Stop the running daemon."""
    try:
        response = send_command({"action": "quit"})
        if response.get("ok"):
            print("Daemon stopped")
        else:
            print(f"Error: {response.get('error')}", file=sys.stderr)
    except RuntimeError as e:
        print(f"Daemon not running: {e}", file=sys.stderr)


def check_status():
    """Check if daemon is running."""
    try:
        response = send_command({"action": "ping"})
        if response.get("ok"):
            print("Daemon is running")
            return True
    except:
        pass
    print("Daemon is not running")
    return False


def is_running() -> bool:
    """Check if daemon is running (for use by driver.py)."""
    if not os.path.exists(SOCKET_PATH):
        return False
    try:
        response = send_command({"action": "ping"})
        return response.get("ok", False)
    except:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: session.py <start|stop|status> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "start":
        if len(sys.argv) < 3:
            print("Usage: session.py start <instance-aid>", file=sys.stderr)
            sys.exit(1)
        run_daemon(sys.argv[2])

    elif cmd == "stop":
        stop_daemon()

    elif cmd == "status":
        sys.exit(0 if check_status() else 1)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
