"""JavaCard Development Kit path resolution.

Provides unified path resolution for JCDK tools and export files,
used by both api/ (for loading API registry) and output/ (for capgen).
"""

import os
import platform
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


class JCDKError(Exception):
    """JavaCard SDK not found or misconfigured."""


def config_dir() -> Path:
    """Return the jcc configuration directory (~/.config/jcc)."""
    return Path.home() / ".config" / "jcc"


def sim_client_dir() -> Path:
    """Return the path to the bundled simulator client (JCCClient)."""
    return Path(__file__).parent / "data" / "sim-client"


def sim_client_cmd(*args: str) -> list[str]:
    """Build a JCCClient command with the correct classpath."""
    sim_dir = config_dir() / "jcdk-sim"
    cp = os.pathsep.join([
        str(sim_dir / "client" / "COMService" / "socketprovider.jar"),
        str(sim_dir / "client" / "AMService" / "amservice.jar"),
        str(sim_client_dir()),
    ])
    return ["java", "-cp", cp, "JCCClient", *args]


@dataclass(frozen=True)
class JCDKPaths:
    """Resolved paths to JavaCard SDK tools and files."""

    jc_home: Path
    java_home: Path
    capgen: Path
    verifycap: Path
    exp2text: Path
    export_dir: Path

    def get_env(self) -> dict[str, str]:
        """Get environment dict with JC_HOME and JAVA_HOME set."""
        env = os.environ.copy()
        env["JC_HOME"] = str(self.jc_home)
        env["JAVA_HOME"] = str(self.java_home)
        return env

    def has_package(self, package: str) -> bool:
        """Check if an API package exists in the export files.

        Args:
            package: Dotted package name (e.g., "javacardx.framework.util.intx").

        Returns:
            True if the package directory exists.
        """
        parts = package.replace(".", "/").split("/")
        return (self.export_dir / "/".join(parts)).exists()


def get_jcdk(javacard_version: str) -> JCDKPaths:
    """Resolve JCDK paths for the specified JavaCard version.

    Checks JC_HOME environment variable, falls back to ~/.config/jcc/jcdk.
    Requires exact version match for export files.

    Args:
        javacard_version: Version string like "3.2.0" or "3_2_0".

    Returns:
        JCDKPaths with all resolved paths.

    Raises:
        JCDKError: If SDK or required tools/files not found.
    """
    jc_home = _find_jc_home()
    java_home = _find_java_home()

    # Tools
    exp2text = _find_tool(jc_home, "exp2text")
    capgen = _find_tool(jc_home, "capgen")
    verifycap = _find_tool(jc_home, "verifycap")

    # Export files - extract from tools.jar into jc_home/versions/
    export_dir = _ensure_export_files(jc_home, javacard_version)

    return JCDKPaths(
        jc_home=jc_home,
        java_home=java_home,
        capgen=capgen,
        verifycap=verifycap,
        exp2text=exp2text,
        export_dir=export_dir,
    )


def _find_jc_home() -> Path:
    """Find JavaCard SDK installation directory.

    Returns:
        Path to SDK root.

    Raises:
        JCDKError: If SDK not found.
    """
    # Check environment variable first
    jc_home_env = os.environ.get("JC_HOME")
    if jc_home_env:
        path = Path(jc_home_env)
        if path.exists():
            return path
        raise JCDKError(f"JC_HOME set to {jc_home_env} but path does not exist")

    # Check ~/.config/jcc/jcdk
    config_jcdk = config_dir() / "jcdk"
    if config_jcdk.exists():
        return config_jcdk

    raise JCDKError(
        "JavaCard SDK not found. Set JC_HOME or run `just setup` to install."
    )


def _find_java_home() -> Path:
    """Find Java installation directory.

    Returns:
        Path to Java home.

    Raises:
        JCDKError: If Java not found.
    """
    # Check environment variable first
    java_home_env = os.environ.get("JAVA_HOME")
    if java_home_env:
        path = Path(java_home_env)
        if path.exists():
            return path
        raise JCDKError(f"JAVA_HOME set to {java_home_env} but path does not exist")

    # macOS: try Homebrew OpenJDK
    if platform.system() == "Darwin":
        homebrew_java = Path("/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home")
        if homebrew_java.exists():
            return homebrew_java

    # Try to find java in PATH and derive JAVA_HOME
    java_path = shutil.which("java")
    if java_path:
        # java is typically at $JAVA_HOME/bin/java
        java_home = Path(java_path).parent.parent
        if (java_home / "bin" / "java").exists():
            return java_home

    raise JCDKError("Java not found. Set JAVA_HOME environment variable or install Java 17.")


def _find_tool(jc_home: Path, tool_name: str) -> Path:
    """Find a tool in the SDK bin directory.

    Tries both .sh (Unix) and plain (Windows) variants.

    Args:
        jc_home: SDK root directory.
        tool_name: Tool name without extension.

    Returns:
        Path to the tool.

    Raises:
        JCDKError: If tool not found.
    """
    bin_dir = jc_home / "bin"

    # Try .sh extension first (Unix)
    sh_path = bin_dir / f"{tool_name}.sh"
    if sh_path.exists():
        return sh_path

    # Try without extension (Windows or direct executable)
    plain_path = bin_dir / tool_name
    if plain_path.exists():
        return plain_path

    raise JCDKError(f"{tool_name} not found in {bin_dir}")


def _ensure_export_files(jc_home: Path, javacard_version: str) -> Path:
    """Ensure export files are extracted from tools.jar.

    Extracts all api_export_files_* entries from lib/tools.jar into
    jc_home/versions/ on first use. Subsequent calls find the files
    already on disk and skip extraction.

    Args:
        jc_home: SDK root directory.
        javacard_version: Version string like "3.2.0".

    Returns:
        Path to the version-specific export files directory.

    Raises:
        JCDKError: If tools.jar not found or version not available.
    """
    versions_dir = jc_home / "versions"

    # Try exact version, then with .0 suffix (e.g. "3.2" -> "3.2.0")
    for suffix in [javacard_version, f"{javacard_version}.0"]:
        export_dir = versions_dir / f"api_export_files_{suffix}"
        if export_dir.exists():
            return export_dir

    # Not on disk yet — extract everything from tools.jar
    tools_jar = jc_home / "lib" / "tools.jar"
    if not tools_jar.exists():
        raise JCDKError(f"tools.jar not found at {tools_jar}")

    versions_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(tools_jar) as zf:
        members = [n for n in zf.namelist() if n.startswith("api_export_files_")]
        if not members:
            raise JCDKError(f"No export files found in {tools_jar}")
        for member in members:
            zf.extract(member, versions_dir)

    # Now look up the requested version
    for suffix in [javacard_version, f"{javacard_version}.0"]:
        export_dir = versions_dir / f"api_export_files_{suffix}"
        if export_dir.exists():
            return export_dir

    raise JCDKError(
        f"Export files for JavaCard {javacard_version} not found in {tools_jar}"
    )
