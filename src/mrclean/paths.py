from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_WSL_MNT_RE = re.compile(r"^/mnt/([A-Za-z])(/|$)")


def is_windows_path(raw: str) -> bool:
    return bool(_WINDOWS_DRIVE_RE.match(raw))


def is_wsl_mnt_path(raw: str) -> bool:
    return bool(_WSL_MNT_RE.match(raw))


def windows_to_wsl(raw: str) -> str:
    drive = raw[0].lower()
    remainder = raw[2:].lstrip("\\/").replace("\\", "/")
    if remainder:
        return f"/mnt/{drive}/{remainder}"
    return f"/mnt/{drive}"


def wsl_to_windows(raw: str) -> str:
    match = _WSL_MNT_RE.match(raw)
    if not match:
        return raw
    drive = match.group(1).upper()
    remainder = raw[5 + 1 :]  # len("/mnt/") + drive
    remainder = remainder.lstrip("/").replace("/", "\\")
    if remainder:
        return f"{drive}:\\{remainder}"
    return f"{drive}:\\"


@dataclass(frozen=True)
class NormalizedPath:
    original: str
    os_path: Path
    style: str  # "windows" or "posix"

    def display_for(self, os_path: Path) -> str:
        as_posix = os_path.as_posix()
        if self.style == "windows":
            return wsl_to_windows(as_posix)
        return as_posix


def normalize_input_path(raw: str) -> NormalizedPath:
    cleaned = raw.strip()
    if is_windows_path(cleaned):
        return NormalizedPath(
            original=cleaned,
            os_path=Path(windows_to_wsl(cleaned)),
            style="windows",
        )
    expanded = Path(cleaned).expanduser()
    return NormalizedPath(original=cleaned, os_path=expanded, style="posix")
