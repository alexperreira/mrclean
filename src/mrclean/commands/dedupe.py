from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from mrclean.hashing import sha256_file
from mrclean.paths import NormalizedPath, normalize_input_path
from mrclean.reports import write_json


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("dedupe", help="Find duplicate files by hash.")
    parser.add_argument("paths", nargs="+", help="Paths to scan.")
    parser.add_argument("--out", default="duplicates_report.json", help="Output report path.")
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
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        help="Ignore files smaller than this size (bytes).",
    )


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


def _build_report(roots: list[NormalizedPath]) -> dict:
    return {
        "version": 1,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "roots": [
            {"input": n.original, "os_path": n.os_path.as_posix(), "style": n.style}
            for n in roots
        ],
        "duplicates": [],
        "errors": [],
        "summary": {
            "files": 0,
            "candidates": 0,
            "duplicate_groups": 0,
            "duplicates": 0,
            "errors": 0,
        },
    }


def run(args: argparse.Namespace) -> int:
    normalized = [normalize_input_path(p) for p in args.paths]
    report = _build_report(normalized)

    size_map: dict[int, list[tuple[NormalizedPath, Path]]] = {}
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
            report["summary"]["files"] += 1
            if stat.st_size < args.min_size:
                continue
            size_map.setdefault(stat.st_size, []).append((root, file_path))

    candidate_groups = {size: files for size, files in size_map.items() if len(files) > 1}
    report["summary"]["candidates"] = sum(len(files) for files in candidate_groups.values())

    for size, entries in sorted(candidate_groups.items()):
        hash_map: dict[str, list[tuple[NormalizedPath, Path]]] = {}
        for root, file_path in entries:
            try:
                file_hash = sha256_file(file_path)
            except OSError as exc:
                report["errors"].append(
                    {
                        "path": root.display_for(file_path),
                        "os_path": file_path.as_posix(),
                        "error": str(exc),
                    }
                )
                continue
            hash_map.setdefault(file_hash, []).append((root, file_path))

        for file_hash, files in hash_map.items():
            if len(files) < 2:
                continue
            group = {
                "size_bytes": size,
                "hash": file_hash,
                "files": [
                    {
                        "path": root.display_for(path),
                        "os_path": path.as_posix(),
                    }
                    for root, path in files
                ],
            }
            report["duplicates"].append(group)
            report["summary"]["duplicate_groups"] += 1
            report["summary"]["duplicates"] += len(files)

    report["summary"]["errors"] = len(report["errors"])

    out_path = Path(args.out)
    write_json(report, out_path)
    print(f"Wrote duplicates report: {out_path}")
    return 0
