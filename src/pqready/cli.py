import time
from pathlib import Path
from typing import Annotated

import typer

from pqready.results import write_results
from pqready.scanner.scan import scan_target
from pqready.targets import read_targets

app = typer.Typer(help="Quantum readiness scanner for TLS endpoints.")


@app.command()
def scan(
    targets: Annotated[Path, typer.Argument(help="CSV file of targets.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="JSON results file.")],
    timeout: Annotated[float, typer.Option(help="Timeout per handshake, in seconds.")] = 10.0,
    delay: Annotated[float, typer.Option(help="Pause between targets, in seconds.")] = 1.0,
) -> None:
    """Scan TLS endpoints listed in a CSV file."""
    try:
        target_list = read_targets(targets)
    except (OSError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    results = []
    for index, target in enumerate(target_list, start=1):
        if index > 1:
            time.sleep(delay)
        result = scan_target(target, timeout)
        results.append(result)
        typer.echo(f"[{index}/{len(target_list)}] {target.host}:{target.port} {result.status}")
    write_results(results, output)
    typer.echo(f"{len(results)} results written to {output}")


@app.command()
def report(
    results: Annotated[Path, typer.Argument(help="JSON results file from 'scan'.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="HTML report file.")],
) -> None:
    """Generate an HTML report from scan results."""
    typer.echo(f"TODO: report {results} -> {output}")
