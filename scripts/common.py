"""Shared helpers for the IFFCO Kalol solar generation pipeline."""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "plant.json"
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
DASHBOARD = ROOT / "dashboard"

SITES_CSV = PROCESSED / "generation_sites.csv"
DAILY_CSV = PROCESSED / "generation_daily.csv"
GAPS_CSV = PROCESSED / "report_gaps.csv"
IRRADIANCE_CSV = PROCESSED / "irradiance_kalol.csv"

MJ_PER_KWH = 3.6


def load_config() -> dict:
    with CONFIG_PATH.open() as fh:
        return json.load(fh)


def source_dirs(config: dict) -> list[Path]:
    """Where the workbooks live. Power Automate owns these; we only read."""
    return [ROOT / d for d in config.get("source_dirs", ["Generation"])]


def clean_text(value) -> str:
    """Collapse the newlines and padding the source workbook uses for layout."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def to_float(value):
    """Capacities arrive as strings, readings as numbers; blanks must stay None."""
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = clean_text(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = clean_text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def date_from_path(path: Path):
    """Recover the delivery date from Power Automate's MM/DD/'YYYY HH:MM.xlsx' tree.

    Used only as a fallback: a workbook that failed to populate carries no date
    inside, but we still want to record that a report arrived that day.
    """
    parts = path.parts
    if len(parts) < 3:
        return None
    month, day, name = parts[-3], parts[-2], parts[-1]
    year = re.match(r"\s*(\d{4})", name)
    if not (year and month.isdigit() and day.isdigit()):
        return None
    try:
        return date(int(year.group(1)), int(month), int(day))
    except ValueError:
        return None
