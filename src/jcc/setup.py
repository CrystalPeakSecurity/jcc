#!/usr/bin/env python3
"""Interactive setup for jcc toolchain (JCDK, simulator, Rust, GlobalPlatformPro)."""

import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "jcc"
ORACLE_URL = "https://www.oracle.com/java/technologies/javacard-downloads.html"
GP_API = "https://api.github.com/repos/martinpaljak/GlobalPlatformPro/releases/latest"

SIMULATOR_DOCKERFILE = (
    "FROM --platform=linux/386 i386/busybox:glibc\n"
)

G = "\033[32m"
Y = "\033[33m"
R = "\033[31m"
B = "\033[1m"
Z = "\033[0m"


# --- IO ---


def ok(msg: str) -> None:
    print(f"  {G}OK{Z} {msg}")


def warn(msg: str) -> None:
    print(f"  {Y}--{Z} {msg}")


def fail(msg: str) -> None:
    print(f"  {R}FAIL{Z} {msg}")


def ask_yn(prompt: str) -> bool:
    resp = input(f"  {prompt} [Y/n] ").strip().lower()
    return resp != "n"


def ask_path(prompt: str) -> Path | None:
    """Prompt for a file path. Handles shell escapes and drag-and-drop quotes."""
    raw = input(f"  {prompt}: ").strip().strip("'\"")
    if not raw:
        return None
    # Unescape backslashes: My\ File -> My File, \( -> (
    out = []
    i = 0
    while i < len(raw):
        if raw[i] == "\\" and i + 1 < len(raw):
            out.append(raw[i + 1])
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return Path("".join(out)).expanduser()


def cmd_ok(*args: str) -> str | None:
    """Run a command, return its output or None if it failed/wasn't found."""
    try:
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode != 0:
            return None
        return r.stdout.strip() or r.stderr.strip() or ""
    except FileNotFoundError:
        return None


def run(*args: str) -> bool:
    """Run a command, return True on success."""
    return subprocess.run(args, capture_output=True).returncode == 0


# --- Archive extraction ---


def extract(archive: Path, dest: Path) -> None:
    """Extract zip or tar.gz to dest, stripping a single top-level wrapper dir."""
    dest.mkdir(parents=True, exist_ok=True)
    if tarfile.is_tarfile(archive):
        _extract_tar(archive, dest)
    elif zipfile.is_zipfile(archive):
        _extract_zip(archive, dest)
    else:
        raise ValueError(f"Not a zip or tar.gz: {archive.name}")
    # macOS quarantine blocks Docker volume mounts
    if platform.system() == "Darwin":
        subprocess.run(["xattr", "-r", "-d", "com.apple.provenance", str(dest)],
                       capture_output=True)


def _strip_prefix(names: list[str]) -> str:
    """If all paths share one top-level dir, return it + '/'. Else ''."""
    tops = {n.split("/")[0] for n in names if "/" in n}
    return (tops.pop() + "/") if len(tops) == 1 else ""


def _rebase(path: str, prefix: str) -> str:
    return path[len(prefix):] if prefix and path.startswith(prefix) else path


def _extract_tar(src: Path, dest: Path) -> None:
    with tarfile.open(src) as tf:
        prefix = _strip_prefix(tf.getnames())
        for m in tf.getmembers():
            if m.isdir():
                continue
            rel = _rebase(m.name, prefix)
            if not rel:
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            data = tf.extractfile(m)
            if data is None:
                continue
            out.write_bytes(data.read())
            if m.mode & 0o111:
                out.chmod(out.stat().st_mode | 0o111)


def _extract_zip(src: Path, dest: Path) -> None:
    with zipfile.ZipFile(src) as zf:
        prefix = _strip_prefix(zf.namelist())
        for m in zf.infolist():
            if m.is_dir():
                continue
            rel = _rebase(m.filename, prefix)
            if not rel:
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(m))
            if m.external_attr >> 16 & 0o111:
                out.chmod(out.stat().st_mode | 0o111)


def download_and_extract(dest: Path, check_file: str, label: str) -> bool:
    """Ask for archive path, extract, validate. Loops until success or skip."""
    while True:
        path = ask_path(f"Path to {label} (or Enter to skip)")
        if path is None:
            return False
        if not path.exists():
            fail(f"Not found: {path}")
            continue
        print("    Extracting...")
        try:
            extract(path, dest)
        except Exception as e:
            fail(str(e))
            shutil.rmtree(dest, ignore_errors=True)
            continue
        if not (dest / check_file).exists():
            fail(f"Bad archive — expected {check_file}")
            shutil.rmtree(dest, ignore_errors=True)
            continue
        return True


# --- Steps ---


def setup_jcdk() -> None:
    print(f"\n{B}JavaCard SDK{Z}")
    jcdk = CONFIG_DIR / "jcdk"
    if (jcdk / "lib" / "tools.jar").exists():
        ok(str(jcdk))
        return

    warn("Not found")
    print(f"    Download from: {B}{ORACLE_URL}{Z}")
    if not download_and_extract(jcdk, "lib/tools.jar", "SDK zip"):
        return

    for sh in (jcdk / "bin").glob("*.sh"):
        sh.chmod(sh.stat().st_mode | 0o755)
    ok(f"Installed to {jcdk}")


def _sim_ready(sim: Path) -> bool:
    """Check if simulator is fully set up (files, keys, docker image)."""
    if not (sim / "runtime" / "bin" / "jcsl").exists():
        return False
    r = subprocess.run(["docker", "image", "inspect", "jcdk-sim"],
                       capture_output=True)
    return r.returncode == 0


def setup_simulator() -> None:
    print(f"\n{B}JavaCard Simulator{Z}")
    sim = CONFIG_DIR / "jcdk-sim"

    if _sim_ready(sim):
        ok(str(sim))
        return

    print("    Runs in Docker (32-bit Linux binary).")
    if not ask_yn("Set up simulator?"):
        return

    if not shutil.which("docker"):
        fail("Docker not found")
        is_mac = platform.system() == "Darwin"
        print(f"    Run: {B}{'brew install --cask docker' if is_mac else 'sudo apt install docker.io'}{Z}")
        return

    ok("Docker available")

    if not (sim / "runtime" / "bin" / "jcsl").exists():
        warn("Simulator not found")
        print(f"    1. Go to {B}{ORACLE_URL}{Z}")
        print(f"    2. Click the {B}Simulator{Z} tab")
        print(f"    3. Download the {B}Linux{Z} binary")
        if not download_and_extract(sim, "runtime/bin/jcsl", "simulator archive"):
            return

    ok(str(sim))

    # Configure SCP keys if not already done
    jcsl = sim / "runtime" / "bin" / "jcsl"
    configurator = sim / "tools" / "Configurator.jar"
    if configurator.exists():
        r = subprocess.run(
            ["java", "-jar", str(configurator), "-binary", str(jcsl), "-check"],
            capture_output=True, text=True,
        )
        if "not configured" in (r.stdout + r.stderr).lower() or r.returncode != 0:
            print("    Configuring SCP keys...")
            key = "404142434445464748494A4B4C4D4E4F"
            r = subprocess.run(
                ["java", "-jar", str(configurator), "-binary", str(jcsl),
                 "-SCP-keyset", "01", key, key, key],
                capture_output=True, text=True,
            )
            if r.returncode == 0:
                ok("SCP keys configured")
            else:
                fail("Failed to configure SCP keys")
                print(f"    {r.stderr.strip()}")
        else:
            ok("SCP keys already configured")

    (sim / "Dockerfile").write_text(SIMULATOR_DOCKERFILE)
    print("    Building Docker image...")
    r = subprocess.run(["docker", "build", "-t", "jcdk-sim", str(sim)], capture_output=True, text=True)
    if r.returncode == 0:
        ok("Docker image built")
    else:
        if "permission denied" in r.stderr.lower():
            fail("Docker permission denied")
            print(f"    Run: {B}sudo usermod -aG docker $USER{Z}")
            print(f"    Then log out and back in.")
        else:
            fail("Docker build failed")
            for line in r.stderr.strip().split("\n")[-3:]:
                print(f"    {line}")


def setup_rust() -> None:
    print(f"\n{B}Rust + wasm32{Z}")

    if shutil.which("rustc"):
        targets = cmd_ok("rustup", "target", "list", "--installed") or ""
        if "wasm32-unknown-unknown" in targets:
            ok(cmd_ok("rustc", "--version") or "rustc")
            ok("wasm32-unknown-unknown")
            return

    if not ask_yn("Set up Rust support?"):
        return

    if not shutil.which("rustc"):
        warn("rustc not found")
        if not ask_yn("Install via rustup?"):
            return
        subprocess.run(["sh", "-c", "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"])
        cargo_bin = str(Path.home() / ".cargo" / "bin")
        os.environ["PATH"] = cargo_bin + os.pathsep + os.environ["PATH"]
        if not shutil.which("rustc"):
            ok("Installed — restart your shell then re-run just setup")
            return

    ok(cmd_ok("rustc", "--version") or "rustc")

    targets = cmd_ok("rustup", "target", "list", "--installed") or ""
    if "wasm32-unknown-unknown" in targets:
        ok("wasm32-unknown-unknown")
    else:
        warn("wasm32 target missing")
        if ask_yn("Install it?"):
            if run("rustup", "target", "add", "wasm32-unknown-unknown"):
                ok("wasm32-unknown-unknown installed")
            else:
                fail("Failed to add target")


def setup_gp() -> None:
    print(f"\n{B}GlobalPlatformPro{Z}")
    gp_jar = CONFIG_DIR / "gp" / "gp.jar"
    if gp_jar.exists():
        ok(str(gp_jar))
        return
    if not ask_yn("Download for real card support?"):
        return

    print("    Downloading...")
    try:
        req = urllib.request.Request(GP_API, headers={"Accept": "application/vnd.github.v3+json"})
        release = json.loads(urllib.request.urlopen(req).read())
        url = next(a["browser_download_url"] for a in release["assets"] if a["name"] == "gp.jar")
        gp_jar.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, gp_jar)
        ok(f"{release['tag_name']} → {gp_jar}")
    except Exception as e:
        fail(str(e))


# --- Main ---


def setup_headers() -> None:
    """Generate versioned C headers from SDK export files."""
    print(f"\n{B}API Headers{Z}")
    jcdk = CONFIG_DIR / "jcdk"
    versions_dir = jcdk / "versions"
    if not versions_dir.exists():
        warn("JCDK not installed, skipping header generation")
        return

    from jcc.api.headergen import generate_all_headers
    from jcc.api.loader import load_api_registry
    from jcc.jcdk import get_jcdk

    include_dir = CONFIG_DIR / "include"
    include_dir.mkdir(parents=True, exist_ok=True)

    # Copy jcc.h from package data
    src_jcc_h = Path(__file__).parent / "data" / "include" / "jcc.h"
    dest_jcc_h = include_dir / "jcc.h"
    shutil.copy2(src_jcc_h, dest_jcc_h)

    for export_dir in sorted(versions_dir.glob("api_export_files_*")):
        version = export_dir.name.removeprefix("api_export_files_")
        try:
            jcdk_paths = get_jcdk(version)
        except Exception:
            warn(f"Could not resolve JCDK for {version}")
            continue

        # Load all available packages for this version
        packages: list[str] = []
        for exp_file in export_dir.rglob("*.exp"):
            # Path: <package_path>/javacard/<last>.exp
            # e.g., javacard/framework/javacard/framework.exp -> javacard.framework
            #        javacardx/framework/util/intx/javacard/intx.exp -> javacardx.framework.util.intx
            rel = exp_file.relative_to(export_dir)
            parts = rel.parts
            # 'javacard' sentinel dir is always second-to-last; package is everything before it
            package_parts = parts[:-2]
            packages.append(".".join(package_parts))

        if not packages:
            continue

        try:
            registry = load_api_registry(jcdk_paths, packages)
        except Exception as e:
            warn(f"Failed to load API for {version}: {e}")
            continue

        output_dir = include_dir / version
        generated = generate_all_headers(registry, output_dir)
        if generated:
            ok(f"{version}")
            for path in generated:
                print(f"    {path.relative_to(output_dir)}")
        else:
            warn(f"{version}: no headers generated")

    ok(f"Generated all C headers: {include_dir}")


def main_toolchain() -> None:
    print(f"{B}jcc setup-toolchain{Z}")
    setup_jcdk()
    setup_headers()
    setup_simulator()
    setup_rust()
    setup_gp()
    print()
