"""Load JavaCard API registry from SDK export files.

Uses the SDK's exp2text tool to convert binary .exp files to text,
then parses the output to build the API registry.
"""

import subprocess
import tempfile
from pathlib import Path

from jcc.api.parser import parse_exp_text
from jcc.api.types import APIRegistry, ClassInfo, PackageInfo
from jcc.jcdk import JCDKPaths, get_jcdk


def load_api_registry(
    jcdk: JCDKPaths,
    packages: list[str] | None = None,
) -> APIRegistry:
    """Load API registry by running exp2text and parsing output.

    Args:
        jcdk: Resolved JCDK paths from get_jcdk().
        packages: List of packages to load. Defaults to common packages.

    Returns:
        APIRegistry containing all classes and methods from specified packages.

    Raises:
        subprocess.CalledProcessError: If exp2text fails.
    """
    if packages is None:
        packages = [
            "javacard.framework",
            "java.lang",
        ]

    classes: dict[str, ClassInfo] = {}
    package_infos: dict[str, PackageInfo] = {}

    for package in packages:
        text = _run_exp2text(jcdk, package)
        result = parse_exp_text(text)
        for cls in result.classes:
            classes[cls.name] = cls
        if result.package is not None:
            package_infos[result.package.name] = result.package

    return APIRegistry(classes=classes, packages=package_infos)


def _run_exp2text(jcdk: JCDKPaths, package: str) -> str:
    """Run exp2text tool and return output.

    Args:
        jcdk: Resolved JCDK paths.
        package: Package name (e.g., "javacard.framework").

    Returns:
        Text output from exp2text.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run exp2text with output directory
        result = subprocess.run(
            [
                str(jcdk.exp2text),
                "-classdir",
                str(jcdk.export_dir),
                "-d",
                tmpdir,
                package,
            ],
            capture_output=True,
            text=True,
            check=True,
            env=jcdk.get_env(),
        )

        # Find the output .tex file (path structure varies by package)
        tex_files = list(Path(tmpdir).rglob("*_exp.tex"))

        if not tex_files:
            raise RuntimeError(
                f"exp2text did not produce any output for {package}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

        # Should only be one
        return tex_files[0].read_text()


def load_api_registry_from_version(
    javacard_version: str,
    packages: list[str] | None = None,
) -> APIRegistry:
    """Convenience function to load API registry by version.

    Args:
        javacard_version: Version string like "3.2.0".
        packages: List of packages to load. Defaults to common packages.

    Returns:
        APIRegistry for the specified version.
    """
    jcdk = get_jcdk(javacard_version)
    return load_api_registry(jcdk, packages)
