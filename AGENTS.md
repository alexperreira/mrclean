# AGENTS.md

## Working Agreements
- Ask before executing any command.
- CLI-only project (no GUI/TUI) unless explicitly requested.
- Target Windows usage with WSL compatibility in mind.
- Default implementation language: Python.
- Prefer duplicate detection by hash.
- Maintain this file as a living rules document; add new explicit or implicit rules here.
- For tracked files: use `git commit -m "<scoped message>" -- path/to/file1 path/to/file2` (list each path explicitly).
- For brand-new files: use `git restore --staged :/ && git add "path/to/file1" "path/to/file2" && git commit -m "<scoped message>" -- path/to/file1 path/to/file2`.
