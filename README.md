# MrClean

CLI-only tool to scan for old/unused files and duplicate content, with safe cleanup actions.

## Planned Commands
- `scan` - collect file metadata and emit a report
- `dedupe` - detect duplicates by hash
- `clean` - apply a reviewed cleanup plan (dry-run by default)

## Status
Scaffolded; implementation in progress.

## Scan Report (v1)
JSON fields: `path`, `os_path`, `size_bytes`, `mtime`, `atime`, `ctime`.
Optional CSV output via `--out-csv`.
