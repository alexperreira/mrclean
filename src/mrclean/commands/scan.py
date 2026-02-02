from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from mrclean.paths import NormalizedPath, normalize_input_path


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("scan", help="Scan paths and emit a report.")
    parser.add_argument("paths", nargs="+", help="Paths to scan.")
    parser.add_argument("--out", default="scan_report.json", help="Output report path.")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude paths matching this glob (can be repeated).",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symlinks while scanning.",
    )


def _utc_iso_from_ts(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _matches_any_glob(path: Path, globs: Iterable[str]) -> bool:
    return any(path.match(pattern) for pattern in globs)


def _walk_files(root: NormalizedPath, excludes: list[str], follow_symlinks: bool) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root.os_path, followlinks=follow_symlinks):
        dir_path = Path(dirpath)
        if excludes and _matches_any_glob(dir_path, excludes):
            continue
        for name in filenames:
            file_path = dir_path / name
            if excludes and _matches_any_glob(file_path, excludes):
                continue
            yield file_path


def run(args: argparse.Namespace) -> int:
    normalized = [normalize_input_path(p) for p in args.paths]
    report = {
        "version": 1,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "roots": [
            {
                "input": n.original,
                "os_path": n.os_path.as_posix(),
                "style": n.style,
            }
            for n in normalized
        ],
        "files": [],
        "errors": [],
        "summary": {"files": 0, "errors": 0},
    }

    for root in normalized:
        if not root.os_path.exists():
            report["errors"].append(
                {
                    "input": root.original,
                    "os_path": root.os_path.as_posix(),
                    "error": "path does not exist",
                }
            )
            continue
        for file_path in _walk_files(root, args.exclude, args.follow_symlinks):
            try:
                stat = file_path.stat() if args.follow_symlinks else file_path.lstat()
            except OSError as exc:
                report["errors"].append(
                    {
                        "path": root.display_for(file_path),
                        "os_path": file_path.as_posix(),
                        "error": str(exc),
                    }
                )
                continue
            report["files"].append(
                {
                    "path": root.display_for(file_path),
                    "os_path": file_path.as_posix(),
                    "size_bytes": stat.st_size,
                    "mtime": _utc_iso_from_ts(stat.st_mtime),
                    "atime": _utc_iso_from_ts(stat.st_atime),
                    "ctime": _utc_iso_from_ts(stat.st_ctime),
                }
            )

    report["summary"]["files"] = len(report["files"])
    report["summary"]["errors"] = len(report["errors"])

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True))
    print(f"Wrote scan report: {out_path}")
    return 0
