from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from mrclean.paths import normalize_input_path


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("clean", help="Apply a cleanup plan.")
    parser.add_argument("plan", help="Path to a cleanup plan JSON file.")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify files.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the plan (overrides --dry-run).",
    )
    parser.add_argument(
        "--log",
        default="mrclean.log",
        help="Path to write a cleanup log.",
    )


def _timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    for idx in range(1, 1000):
        candidate = parent / f"{stem}-{idx}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique destination for {destination}")


def _load_plan(plan_path: Path) -> dict:
    return json.loads(plan_path.read_text())


def run(args: argparse.Namespace) -> int:
    if args.apply and args.dry_run:
        raise SystemExit("Use either --apply or --dry-run, not both.")
    dry_run = not args.apply

    plan_path = Path(args.plan)
    payload = _load_plan(plan_path)
    actions = payload.get("actions", [])

    log_entries: list[dict] = []
    for entry in actions:
        action = entry.get("action")
        raw_path = entry.get("path")
        if not action or not raw_path:
            log_entries.append(
                {
                    "time": _timestamp(),
                    "status": "error",
                    "error": "missing action or path",
                    "entry": entry,
                }
            )
            continue
        normalized = normalize_input_path(raw_path)
        target = normalized.os_path
        display_path = normalized.original

        try:
            if action == "delete":
                if dry_run:
                    log_entries.append(
                        {
                            "time": _timestamp(),
                            "status": "dry-run",
                            "action": "delete",
                            "path": display_path,
                            "os_path": target.as_posix(),
                        }
                    )
                else:
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                    log_entries.append(
                        {
                            "time": _timestamp(),
                            "status": "deleted",
                            "action": "delete",
                            "path": display_path,
                            "os_path": target.as_posix(),
                        }
                    )
            elif action in {"move", "archive"}:
                destination_raw = entry.get("destination")
                if not destination_raw:
                    raise ValueError("missing destination for move/archive")
                destination_norm = normalize_input_path(destination_raw)
                destination = destination_norm.os_path
                if destination.is_dir() or action == "archive":
                    destination = destination / target.name
                destination = _unique_destination(destination)
                if dry_run:
                    log_entries.append(
                        {
                            "time": _timestamp(),
                            "status": "dry-run",
                            "action": action,
                            "path": display_path,
                            "destination": destination_norm.original,
                            "resolved_destination": destination.as_posix(),
                        }
                    )
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(destination))
                    log_entries.append(
                        {
                            "time": _timestamp(),
                            "status": "moved",
                            "action": action,
                            "path": display_path,
                            "destination": destination_norm.original,
                            "resolved_destination": destination.as_posix(),
                        }
                    )
            else:
                log_entries.append(
                    {
                        "time": _timestamp(),
                        "status": "error",
                        "error": f"unknown action '{action}'",
                        "path": display_path,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            log_entries.append(
                {
                    "time": _timestamp(),
                    "status": "error",
                    "action": action,
                    "path": display_path,
                    "error": str(exc),
                }
            )

    log_path = Path(args.log)
    log_path.write_text(json.dumps({"entries": log_entries}, indent=2, ensure_ascii=True))

    summary = {
        "total": len(log_entries),
        "errors": sum(1 for entry in log_entries if entry.get("status") == "error"),
        "dry_run": dry_run,
    }
    print(f"Wrote cleanup log: {log_path}")
    print(
        f"Cleanup summary: {summary['total']} entries,"
        f" {summary['errors']} errors, dry-run={summary['dry_run']}"
    )
    return 0
