import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from pqready.models import ScanResult


def _json_default(value: object) -> str:
    """Serialize types json does not know (datetime -> ISO 8601)."""
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def write_results(results: list[ScanResult], path: Path) -> None:
    """Write scan results as a JSON list."""
    data = [asdict(result) for result in results]
    path.write_text(json.dumps(data, indent=2, default=_json_default), encoding="utf-8")
