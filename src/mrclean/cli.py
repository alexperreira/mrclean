from __future__ import annotations

import argparse
import sys

from .commands import clean, dedupe, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mrclean",
        description="Scan for unused files and duplicates, then safely clean up.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan.add_parser(subparsers)
    dedupe.add_parser(subparsers)
    clean.add_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return scan.run(args)
    if args.command == "dedupe":
        return dedupe.run(args)
    if args.command == "clean":
        return clean.run(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
