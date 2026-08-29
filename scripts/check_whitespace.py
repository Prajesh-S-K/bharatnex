"""Reject trailing whitespace in tracked text files where it is not intentional."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_SUFFIXES = {".md"}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / path.decode() for path in result.stdout.split(b"\0") if path]


def main() -> None:
    failures: list[str] = []

    for path in tracked_files():
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if line.rstrip(" \t") != line:
                failures.append(f"{path.relative_to(ROOT)}:{line_number}")

    if failures:
        locations = "\n".join(f"- {location}" for location in failures)
        raise SystemExit(f"Trailing whitespace found:\n{locations}")

    print("PASS tracked-file whitespace")


if __name__ == "__main__":
    main()
