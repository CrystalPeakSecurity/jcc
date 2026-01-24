"""Tests for the ProjectConfig class."""

import pytest
from pathlib import Path

from jcc.aid import AID
from jcc.config import AnalysisConfig, ProjectConfig, PackageConfig, AppletConfig, ConfigError


class TestProjectConfigFromToml:
    def test_basic_config(self):
        toml = """
        [package]
        name = "com/test/counter"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "CounterApplet"
        """
        config = ProjectConfig.from_toml_string(toml)

        assert config.package.name == "com/test/counter"
        assert config.package.aid.to_hex() == "A000000062030105"
        assert config.package.version == "1.0"
        assert config.applet.aid.to_hex() == "A0000000620301050501"
        assert config.applet.class_name == "CounterApplet"

    def test_config_with_version(self):
        toml = """
        [package]
        name = "com/test/app"
        aid = "A000000062030105"
        version = "2.1"

        [applet]
        aid = "A0000000620301050501"
        class = "MyApplet"
        """
        config = ProjectConfig.from_toml_string(toml)
        assert config.package.version == "2.1"

    def test_missing_package_name(self):
        toml = """
        [package]
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "MyApplet"
        """
        with pytest.raises(ConfigError, match="package.name is required"):
            ProjectConfig.from_toml_string(toml)

    def test_missing_package_aid(self):
        toml = """
        [package]
        name = "com/test/app"

        [applet]
        aid = "A0000000620301050501"
        class = "MyApplet"
        """
        with pytest.raises(ConfigError, match="package.aid is required"):
            ProjectConfig.from_toml_string(toml)

    def test_missing_applet_aid(self):
        toml = """
        [package]
        name = "com/test/app"
        aid = "A000000062030105"

        [applet]
        class = "MyApplet"
        """
        with pytest.raises(ConfigError, match="applet.aid is required"):
            ProjectConfig.from_toml_string(toml)

    def test_missing_applet_class(self):
        toml = """
        [package]
        name = "com/test/app"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        """
        with pytest.raises(ConfigError, match="applet.class is required"):
            ProjectConfig.from_toml_string(toml)

    def test_invalid_package_aid(self):
        toml = """
        [package]
        name = "com/test/app"
        aid = "INVALID"

        [applet]
        aid = "A0000000620301050501"
        class = "MyApplet"
        """
        with pytest.raises(ConfigError, match="Invalid package.aid"):
            ProjectConfig.from_toml_string(toml)

    def test_invalid_applet_aid(self):
        toml = """
        [package]
        name = "com/test/app"
        aid = "A000000062030105"

        [applet]
        aid = "NOT_VALID"
        class = "MyApplet"
        """
        with pytest.raises(ConfigError, match="Invalid applet.aid"):
            ProjectConfig.from_toml_string(toml)

    def test_invalid_toml_syntax(self):
        toml = """
        [package
        name = "bad syntax"
        """
        with pytest.raises(ConfigError, match="Invalid TOML"):
            ProjectConfig.from_toml_string(toml)


class TestProjectConfigFromFile:
    def test_load_from_file(self, tmp_path: Path):
        config_file = tmp_path / "jcc.toml"
        config_file.write_text("""
        [package]
        name = "com/test/file"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "FileApplet"
        """)

        config = ProjectConfig.from_toml(config_file)

        assert config.package.name == "com/test/file"
        assert config.applet.class_name == "FileApplet"

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ConfigError, match="Config file not found"):
            ProjectConfig.from_toml(tmp_path / "nonexistent.toml")


class TestProjectConfigDefaults:
    def test_minimal_defaults(self):
        config = ProjectConfig.with_defaults()

        assert config.package.name == "com/example/applet"
        assert config.package.aid.to_hex() == "A000000062030101"
        assert config.package.version == "1.0"
        assert config.applet.aid.to_hex() == "A00000006203010101"
        assert config.applet.class_name == "Applet"

    def test_custom_package_name(self):
        config = ProjectConfig.with_defaults(package_name="com/my/app")
        assert config.package.name == "com/my/app"

    def test_custom_aids_as_strings(self):
        config = ProjectConfig.with_defaults(
            package_aid="A000000062030105",
            applet_aid="A0000000620301050501",
        )
        assert config.package.aid.to_hex() == "A000000062030105"
        assert config.applet.aid.to_hex() == "A0000000620301050501"

    def test_custom_aids_as_aid_objects(self):
        pkg_aid = AID.parse("A000000062030105")
        app_aid = AID.parse("A0000000620301050501")

        config = ProjectConfig.with_defaults(
            package_aid=pkg_aid,
            applet_aid=app_aid,
        )
        assert config.package.aid == pkg_aid
        assert config.applet.aid == app_aid

    def test_auto_applet_aid(self):
        config = ProjectConfig.with_defaults(package_aid="A000000062030105")
        assert config.applet.aid.to_hex() == "A00000006203010501"

    def test_custom_class_name(self):
        config = ProjectConfig.with_defaults(applet_class="MyCustomApplet")
        assert config.applet.class_name == "MyCustomApplet"

    def test_custom_version(self):
        config = ProjectConfig.with_defaults(version="3.0")
        assert config.package.version == "3.0"


class TestConfigImmutability:
    def test_project_config_frozen(self):
        config = ProjectConfig.with_defaults()
        with pytest.raises(AttributeError):
            config.package = None  # type: ignore

    def test_package_config_frozen(self):
        pkg = PackageConfig(name="com/test", aid=AID.parse("A000000062030105"))
        with pytest.raises(AttributeError):
            pkg.name = "modified"  # type: ignore

    def test_applet_config_frozen(self):
        applet = AppletConfig(aid=AID.parse("A0000000620301050501"), class_name="Test")
        with pytest.raises(AttributeError):
            applet.class_name = "modified"  # type: ignore


class TestExtendedApduConfig:
    def test_extended_apdu_defaults_to_false(self):
        config = ProjectConfig.with_defaults()
        assert config.analysis.extended_apdu is False

    def test_extended_apdu_from_toml_true(self):
        toml = """
        [package]
        name = "com/test/extended"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "ExtendedApplet"

        [analysis]
        extended_apdu = true
        """
        config = ProjectConfig.from_toml_string(toml)
        assert config.analysis.extended_apdu is True

    def test_extended_apdu_from_toml_false(self):
        toml = """
        [package]
        name = "com/test/standard"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "StandardApplet"

        [analysis]
        extended_apdu = false
        """
        config = ProjectConfig.from_toml_string(toml)
        assert config.analysis.extended_apdu is False

    def test_extended_apdu_not_specified_defaults_false(self):
        toml = """
        [package]
        name = "com/test/noext"
        aid = "A000000062030105"

        [applet]
        aid = "A0000000620301050501"
        class = "NoExtApplet"
        """
        config = ProjectConfig.from_toml_string(toml)
        assert config.analysis.extended_apdu is False

    def test_analysis_config_frozen(self):
        analysis = AnalysisConfig(extended_apdu=True)
        with pytest.raises(AttributeError):
            analysis.extended_apdu = False  # type: ignore
