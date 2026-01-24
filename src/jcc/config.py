"""Project configuration for JCC."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

import tomllib

from jcc.aid import AID, AIDError

# =============================================================================
# Feature Flags
# =============================================================================

# memset_short uses javacardx.framework.util.ArrayLogic for fast short[] fills.
# Currently BROKEN: causes load failures on some cards. Needs investigation.
# Set to False to enable once the underlying issue is fixed.
DISABLE_MEMSET_SHORT = True


class ConfigError(Exception):
    """Configuration error."""


@dataclass(frozen=True, slots=True)
class AppletConfig:
    """Applet configuration."""

    aid: AID
    class_name: str


@dataclass(frozen=True, slots=True)
class PackageConfig:
    """Package configuration."""

    name: str
    aid: AID
    version: str = "1.0"


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    """Analysis configuration."""

    max_stack_slots: int = 64  # 16-bit words (JCVM native unit)
    extended_apdu: bool = False  # Enable extended APDU support (>255 bytes)
    javacard_version: str = "3.0.1"  # Target JavaCard version (3.0.1, 3.0.4, 3.0.5, 3.1, 3.2)
    has_intx: bool = False  # True only for cards with javacardx.framework.util.intx (3.0.4+)


@dataclass(frozen=True, slots=True)
class PatternRuleConfig:
    """Configuration for a pattern-based lint rule."""

    pattern: str
    message: str
    name: str | None = None


@dataclass(frozen=True, slots=True)
class LintConfig:
    """Lint configuration."""

    enabled: bool = True
    pattern_rules: tuple[PatternRuleConfig, ...] = ()
    death_pain_state: bool = False  # DOOM-specific structural rule
    paths: tuple[str, ...] = ("*.h", "*.c", "data/*.h", "data/*.c")  # Glob patterns for files to lint


# JavaCard version -> (javacard.framework version, java.lang version)
JAVACARD_IMPORT_VERSIONS: dict[str, tuple[str, str]] = {
    "2.2.2": ("1.3", "1.0"),
    "3.0.1": ("1.4", "1.0"),
    "3.0.4": ("1.5", "1.0"),
    "3.0.5": ("1.6", "1.0"),
    "3.1": ("1.8", "1.0"),
    "3.2": ("1.9", "1.0"),
}


def get_import_versions(javacard_version: str) -> tuple[str, str]:
    """Get import versions for a JavaCard target version.

    Args:
        javacard_version: Target JavaCard version (e.g., "3.0.5", "3.2")

    Returns:
        Tuple of (framework_version, lang_version)

    Raises:
        ConfigError: If the version is not supported
    """
    if javacard_version not in JAVACARD_IMPORT_VERSIONS:
        supported = ", ".join(sorted(JAVACARD_IMPORT_VERSIONS.keys()))
        raise ConfigError(f"Unsupported javacard_version '{javacard_version}'. Supported: {supported}")
    return JAVACARD_IMPORT_VERSIONS[javacard_version]


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Complete project configuration.

    Loaded from TOML config file or constructed programmatically.
    This is the main configuration class for JCC projects.
    """

    package: PackageConfig
    applet: AppletConfig
    analysis: AnalysisConfig = AnalysisConfig()
    lint: LintConfig = LintConfig()

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        """Load configuration from TOML file.

        Args:
            path: Path to the TOML configuration file

        Returns:
            ProjectConfig instance

        Raises:
            ConfigError: If the file doesn't exist or has invalid format
        """
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid TOML in {path}: {e}") from e

        return cls._from_dict(data, source=path)

    @classmethod
    def from_toml_string(cls, content: str) -> Self:
        """Load configuration from TOML string.

        Useful for testing and programmatic configuration.

        Args:
            content: TOML content as a string

        Returns:
            ProjectConfig instance

        Raises:
            ConfigError: If the content has invalid format
        """
        try:
            data = tomllib.loads(content)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid TOML: {e}") from e

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict, source: Path | None = None) -> Self:
        """Parse configuration from dictionary.

        Args:
            data: Dictionary with configuration data
            source: Optional source path for error messages

        Returns:
            ProjectConfig instance

        Raises:
            ConfigError: If required fields are missing or invalid
        """
        source_str = f" in {source}" if source else ""

        try:
            pkg_data = data.get("package", {})
            applet_data = data.get("applet", {})

            # Validate required fields
            if not pkg_data.get("name"):
                raise ConfigError(f"package.name is required{source_str}")
            if not pkg_data.get("aid"):
                raise ConfigError(f"package.aid is required{source_str}")
            if not applet_data.get("aid"):
                raise ConfigError(f"applet.aid is required{source_str}")
            if not applet_data.get("class"):
                raise ConfigError(f"applet.class is required{source_str}")

            # Parse AIDs
            try:
                pkg_aid = AID.parse(pkg_data["aid"])
            except AIDError as e:
                raise ConfigError(f"Invalid package.aid{source_str}: {e}") from e

            try:
                applet_aid = AID.parse(applet_data["aid"])
            except AIDError as e:
                raise ConfigError(f"Invalid applet.aid{source_str}: {e}") from e

            package = PackageConfig(
                name=pkg_data["name"],
                aid=pkg_aid,
                version=pkg_data.get("version", "1.0"),
            )

            applet = AppletConfig(
                aid=applet_aid,
                class_name=applet_data["class"],
            )

            # Parse optional analysis config
            analysis_data = data.get("analysis", {})
            javacard_version = analysis_data.get("javacard_version", "3.2")
            # Validate javacard_version early
            if javacard_version not in JAVACARD_IMPORT_VERSIONS:
                supported = ", ".join(sorted(JAVACARD_IMPORT_VERSIONS.keys()))
                raise ConfigError(
                    f"Unsupported javacard_version '{javacard_version}'{source_str}. Supported: {supported}"
                )
            analysis = AnalysisConfig(
                max_stack_slots=analysis_data.get("max_stack_slots", 64),
                extended_apdu=analysis_data.get("extended_apdu", False),
                javacard_version=javacard_version,
                has_intx=analysis_data.get("has_intx", False),
            )

            # Parse optional lint config
            lint_data = data.get("lint", {})
            pattern_rules: list[PatternRuleConfig] = []
            for rule_data in lint_data.get("pattern_rules", []):
                if "pattern" not in rule_data or "message" not in rule_data:
                    raise ConfigError(f"lint.pattern_rules entries require 'pattern' and 'message'{source_str}")
                pattern_rules.append(
                    PatternRuleConfig(
                        pattern=rule_data["pattern"],
                        message=rule_data["message"],
                        name=rule_data.get("name"),
                    )
                )
            # Parse lint paths (default to common C patterns)
            lint_paths = lint_data.get("paths", ["*.h", "*.c", "data/*.h", "data/*.c"])
            if isinstance(lint_paths, str):
                lint_paths = [lint_paths]

            lint = LintConfig(
                enabled=lint_data.get("enabled", True),
                pattern_rules=tuple(pattern_rules),
                death_pain_state=lint_data.get("death_pain_state", False),
                paths=tuple(lint_paths),
            )

            return cls(package=package, applet=applet, analysis=analysis, lint=lint)

        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Error parsing config{source_str}: {e}") from e

    @classmethod
    def with_defaults(
        cls,
        package_name: str = "com/example/applet",
        package_aid: str | AID | None = None,
        applet_aid: str | AID | None = None,
        applet_class: str = "Applet",
        version: str = "1.0",
    ) -> Self:
        """Create config with defaults, generating AIDs if not provided.

        Useful for quick testing or when AIDs are not important.

        Args:
            package_name: Package name (default: "com/example/applet")
            package_aid: Package AID (default: auto-generated)
            applet_aid: Applet AID (default: package_aid + 0x01)
            applet_class: Applet class name (default: "Applet")
            version: Package version (default: "1.0")

        Returns:
            ProjectConfig instance
        """
        # Default package AID (testing range per GlobalPlatform)
        if package_aid is None:
            pkg_aid = AID.parse("A000000062030101")
        elif isinstance(package_aid, str):
            pkg_aid = AID.parse(package_aid)
        else:
            pkg_aid = package_aid

        # Default applet AID (package AID + 01)
        if applet_aid is None:
            app_aid = pkg_aid + 0x01
        elif isinstance(applet_aid, str):
            app_aid = AID.parse(applet_aid)
        else:
            app_aid = applet_aid

        return cls(
            package=PackageConfig(name=package_name, aid=pkg_aid, version=version),
            applet=AppletConfig(aid=app_aid, class_name=applet_class),
        )
