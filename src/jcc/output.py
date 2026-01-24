"""Rich console output for JCC CLI."""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console

console = Console()


@contextmanager
def phase(name: str) -> Generator[None, None, None]:
    """Show spinner during phase, checkmark when done.

    Usage:
        with phase("Parsing"):
            ast = parse(source)
        # prints "✓ Parsing" when done
    """
    with console.status(f"[bold blue]{name}..."):
        yield
    console.print(f"[green]✓[/green] {name}")


def error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def info(message: str) -> None:
    """Print an info message."""
    console.print(message)


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")
