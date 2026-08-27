"""Run the whole daily pipeline: ingest -> irradiance -> dashboard.

Safe to run repeatedly. Re-ingesting a date replaces that date's rows rather
than duplicating them, and irradiance days already stored are not re-fetched
unless they fall inside the refresh tail.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ("Ingesting workbooks from data/inbox", [sys.executable, str(HERE / "ingest.py")]),
    ("Updating irradiance for IFFCO Kalol", [sys.executable, str(HERE / "irradiance.py")]),
    ("Rebuilding dashboard", [sys.executable, str(HERE / "build_dashboard.py")]),
]


def main() -> int:
    failures = []
    for title, cmd in STEPS:
        print(f"\n=== {title} ===")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            # A missing workbook or an unreachable weather API must not stop the
            # dashboard from being rebuilt with whatever data is already on disk.
            print(f"    step exited {result.returncode}", file=sys.stderr)
            failures.append(title)
    if failures:
        print(f"\nCompleted with {len(failures)} failing step(s): "
              + "; ".join(failures), file=sys.stderr)
        return 1
    print("\nPipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
