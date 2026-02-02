from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCAN_REPORT_VERSION = 1
SCAN_CSV_FIELDS = (
    "path",
    "os_path",
    "size_bytes",
    "mtime",
    "atime",
    "ctime",
)


@dataclass
class ScanReport:
    roots: list[dict]
    files: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "version": SCAN_REPORT_VERSION,
            "generated_at": self.generated_at,
            "roots": self.roots,
            "files": self.files,
            "errors": self.errors,
            "summary": {"files": len(self.files), "errors": len(self.errors)},
        }


def write_json(payload: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def write_scan_json(report: ScanReport, out_path: Path) -> None:
    write_json(report.to_dict(), out_path)


def write_scan_csv(files: Iterable[dict], out_path: Path) -> None:
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCAN_CSV_FIELDS)
        writer.writeheader()
        for row in files:
            writer.writerow({key: row.get(key, "") for key in SCAN_CSV_FIELDS})
