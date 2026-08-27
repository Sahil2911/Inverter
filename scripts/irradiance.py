"""Fetch daily solar irradiance for IFFCO Kalol from Open-Meteo.

`shortwave_radiation_sum` is daily global horizontal irradiation (GHI) in MJ/m2.
Divided by 3.6 it becomes kWh/m2, which is also "peak sun hours" - the number the
plant's specific yield (kWh/kWp) is compared against to get a performance ratio.

The reanalysis archive lags real time by a few days, so recent dates fall back to
the forecast endpoint, which serves the same variables for the recent past.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    IRRADIANCE_CSV, MJ_PER_KWH, PROCESSED, load_config,
)

DAILY_VARS = [
    "shortwave_radiation_sum",
    "sunshine_duration",
    "temperature_2m_max",
    "precipitation_sum",
    "cloud_cover_mean",
]
FIELDS = [
    "date", "ghi_kwh_m2", "ghi_mj_m2", "sunshine_hours",
    "temp_max_c", "precipitation_mm", "cloud_cover_pct", "source",
]


def fetch(url: str, params: dict, retries: int = 4) -> dict:
    query = urllib.parse.urlencode(params, doseq=True)
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(f"{url}?{query}", timeout=45) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            if attempt < retries - 1:
                delay = 2 ** (attempt + 1)
                print(f"    request failed ({exc}); retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
    raise RuntimeError(f"Open-Meteo request failed after {retries} attempts: {last}")


def blank_if_none(value):
    """CSV wants an empty cell, not the string 'None', for a missing reading."""
    return "" if value is None else value


def rows_from_payload(payload: dict, source: str) -> list[dict]:
    daily = payload.get("daily") or {}
    times = daily.get("time") or []
    rows = []
    for i, day in enumerate(times):
        def get(name):
            series = daily.get(name) or []
            return series[i] if i < len(series) else None

        ghi_mj = get("shortwave_radiation_sum")
        if ghi_mj is None:
            continue  # a day with no radiation value carries no usable signal
        sunshine = get("sunshine_duration")
        rows.append({
            "date": day,
            "ghi_kwh_m2": round(ghi_mj / MJ_PER_KWH, 4),
            "ghi_mj_m2": round(ghi_mj, 3),
            "sunshine_hours": round(sunshine / 3600.0, 3) if sunshine is not None else "",
            "temp_max_c": blank_if_none(get("temperature_2m_max")),
            "precipitation_mm": blank_if_none(get("precipitation_sum")),
            "cloud_cover_pct": blank_if_none(get("cloud_cover_mean")),
            "source": source,
        })
    return rows


def fetch_archive(cfg: dict, start: date, end: date) -> list[dict]:
    loc = cfg["location"]
    payload = fetch(cfg["irradiance_source"]["archive_endpoint"], {
        "latitude": loc["latitude"], "longitude": loc["longitude"],
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "daily": ",".join(DAILY_VARS), "timezone": loc["timezone"],
    })
    return rows_from_payload(payload, "open-meteo-archive")


def fetch_recent(cfg: dict, past_days: int) -> list[dict]:
    loc = cfg["location"]
    payload = fetch(cfg["irradiance_source"]["forecast_endpoint"], {
        "latitude": loc["latitude"], "longitude": loc["longitude"],
        "past_days": min(max(past_days, 1), 92), "forecast_days": 1,
        "daily": ",".join(DAILY_VARS), "timezone": loc["timezone"],
    })
    return rows_from_payload(payload, "open-meteo-forecast")


def read_existing() -> dict:
    if not IRRADIANCE_CSV.exists():
        return {}
    with IRRADIANCE_CSV.open(newline="") as fh:
        return {r["date"]: r for r in csv.DictReader(fh)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=date.fromisoformat,
                    help="first date to fetch (default: history_start from config)")
    ap.add_argument("--end", type=date.fromisoformat, default=date.today(),
                    help="last date to fetch (default: today)")
    ap.add_argument("--refresh-tail", type=int, default=10,
                    help="re-fetch this many recent days so forecast values are "
                         "replaced by reanalysis once the archive catches up")
    args = ap.parse_args()

    cfg = load_config()
    start = args.start or date.fromisoformat(cfg["history_start"])
    end = args.end
    if start > end:
        print(f"start {start} is after end {end}; nothing to do", file=sys.stderr)
        return 1

    existing = read_existing()
    # Anything older than the refresh tail and already stored is settled reanalysis.
    tail_cutoff = end - timedelta(days=args.refresh_tail)
    wanted = {
        (start + timedelta(days=i)).isoformat()
        for i in range((end - start).days + 1)
    }
    missing = {d for d in wanted if d not in existing or d >= tail_cutoff.isoformat()}

    if not missing:
        print(f"Irradiance up to date ({len(existing)} days through {max(existing)}).")
        return 0

    print(f"Fetching irradiance for {len(missing)} day(s) "
          f"({min(missing)} .. {max(missing)}) at {cfg['location']['label']}")

    fetched: dict[str, dict] = {}
    try:
        for row in fetch_archive(cfg, date.fromisoformat(min(missing)), end):
            fetched[row["date"]] = row
        print(f"  archive returned {len(fetched)} day(s)")
    except RuntimeError as exc:
        print(f"  archive unavailable: {exc}", file=sys.stderr)

    still_missing = sorted(d for d in missing if d not in fetched)
    if still_missing:
        gap = (end - date.fromisoformat(min(still_missing))).days + 2
        print(f"  {len(still_missing)} day(s) not in archive; trying forecast endpoint")
        try:
            for row in fetch_recent(cfg, gap):
                fetched.setdefault(row["date"], row)
        except RuntimeError as exc:
            print(f"  forecast endpoint unavailable: {exc}", file=sys.stderr)

    if not fetched:
        print("No irradiance data retrieved; leaving existing file untouched.",
              file=sys.stderr)
        return 1

    existing.update({d: r for d, r in fetched.items() if d in wanted})
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with IRRADIANCE_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for day in sorted(existing):
            writer.writerow({k: existing[day].get(k, "") for k in FIELDS})

    still = sorted(d for d in wanted if d not in existing)
    print(f"Wrote {len(existing)} day(s) to {IRRADIANCE_CSV.name}"
          + (f"; {len(still)} still missing (earliest {still[0]})" if still else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
