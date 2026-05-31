from __future__ import annotations

from pathlib import Path
from typing import Iterable


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_text_file(path: str | Path, content: str) -> Path:
    target = Path(path)
    ensure_directory(target.parent)
    target.write_text(content, encoding="utf-8")
    return target


def write_lines(path: str | Path, lines: Iterable[str]) -> Path:
    target = Path(path)
    ensure_directory(target.parent)
    target.write_text("".join(lines), encoding="utf-8")
    return target

