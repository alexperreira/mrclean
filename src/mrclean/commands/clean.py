from __future__ import annotations

import argparse


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("clean", help="Apply a cleanup plan.")
    parser.add_argument("plan", help="Path to a cleanup plan JSON file.")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify files.")


def run(args: argparse.Namespace) -> int:
    # TODO: Implement cleanup actions
    mode = "dry-run" if args.dry_run else "apply"
    print(f"clean not implemented yet; would {mode} plan: {args.plan}")
    return 0
