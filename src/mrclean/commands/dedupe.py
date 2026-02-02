from __future__ import annotations

import argparse


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("dedupe", help="Find duplicate files by hash.")
    parser.add_argument("paths", nargs="+", help="Paths to scan.")
    parser.add_argument("--out", default="duplicates_report.json", help="Output report path.")


def run(args: argparse.Namespace) -> int:
    # TODO: Implement duplicate detection
    print(f"dedupe not implemented yet; would scan: {args.paths} -> {args.out}")
    return 0
