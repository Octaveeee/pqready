import csv
from pathlib import Path

from pqready.models import Target


def read_targets(path: Path) -> list[Target]:
    """Read targets from a CSV file with a header row."""
    targets = []
    with path.open(newline="", encoding="utf-8") as file:
        for line, row in enumerate(csv.DictReader(file), start=2):
            try:
                targets.append(
                    Target(
                        host=row["host"].strip(),
                        port=int(row["port"]),
                        label=row["label"].strip(),
                        sensitivity=int(row["sensitivity"]),
                        confidentiality_years=int(row["confidentiality_years"]),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}:{line}: invalid target ({exc})") from exc
    return targets
