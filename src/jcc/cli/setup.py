"""Setup: interactive environment configuration."""


def run_setup() -> None:
    """Full setup: prerequisites + toolchain."""
    from jcc.setup import main

    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")


def run_setup_toolchain() -> None:
    """Interactive toolchain setup (JCDK, simulator, Rust, GlobalPlatformPro)."""
    from jcc.setup import main_toolchain

    try:
        main_toolchain()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
