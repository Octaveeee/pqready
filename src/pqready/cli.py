from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Quantum readiness scanner for TLS endpoints.")


@app.command()
def scan(
    targets: Annotated[Path, typer.Argument(help="CSV file of targets.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="JSON results file.")],
) -> None:
    """Scan TLS endpoints listed in a CSV file."""
    typer.echo(f"TODO: scan {targets} -> {output}")


@app.command()
def report(
    results: Annotated[Path, typer.Argument(help="JSON results file from 'scan'.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="HTML report file.")],
) -> None:
    """Generate an HTML report from scan results."""
    typer.echo(f"TODO: report {results} -> {output}")
