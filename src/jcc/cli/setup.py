"""Setup: interactive environment configuration."""


def run_setup() -> None:
    """Interactive setup of JCDK, simulator, and Java."""
    from jcc.setup import main

    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
