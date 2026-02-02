from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mrclean.reports import ScanReport, write_scan_csv, write_scan_json


class ReportsTestCase(unittest.TestCase):
    def test_scan_report_to_dict(self) -> None:
        report = ScanReport(
            roots=[{"input": "/tmp", "os_path": "/tmp", "style": "posix"}],
            files=[{"path": "/tmp/a", "os_path": "/tmp/a", "size_bytes": 1}],
            errors=[{"path": "/tmp/b", "error": "missing"}],
        )
        payload = report.to_dict()
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["summary"]["files"], 1)
        self.assertEqual(payload["summary"]["errors"], 1)

    def test_write_scan_json_and_csv(self) -> None:
        report = ScanReport(
            roots=[{"input": "/tmp", "os_path": "/tmp", "style": "posix"}],
            files=[
                {
                    "path": "/tmp/a",
                    "os_path": "/tmp/a",
                    "size_bytes": 2,
                    "mtime": "2020-01-01T00:00:00Z",
                    "atime": "2020-01-01T00:00:00Z",
                    "ctime": "2020-01-01T00:00:00Z",
                }
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "scan.json"
            csv_path = Path(tmpdir) / "scan.csv"
            write_scan_json(report, json_path)
            write_scan_csv(report.files, csv_path)

            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["summary"]["files"], 1)

            with csv_path.open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["path"], "/tmp/a")
