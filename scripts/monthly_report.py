"""Write one Excel workbook per month: date against net generation.

Every calendar day of the month gets a row, so a day the report never arrived
shows as a blank rather than being quietly closed up - the gap is part of what
the month tells you.

Both readings are carried. "As printed" is the sheet's own TOTAL NET GENERATION
cell, which is the figure the plant circulates; "summed" adds up the site
columns beneath it. They disagree every day for two known reasons, set out in
the notes on each sheet.

Totals are written as formulas, not as numbers computed here, so the workbook
still adds up if a cell is edited.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DAILY_CSV, ROOT, load_config  # noqa: E402

REPORTS = ROOT / "reports"
FONT = "Arial"

HEAD_FILL = PatternFill("solid", fgColor="1F3864")
TOTAL_FILL = PatternFill("solid", fgColor="E8EDF5")
MISSING_FILL = PatternFill("solid", fgColor="FBE9E7")
THIN = Side(style="thin", color="BFBFBF")
MED = Side(style="medium", color="1F3864")

COLUMNS = [
    ("Date", 13),
    ("Day", 7),
    ("Net kWh (as printed in report)", 28),
    ("Net kWh (sum of site columns)", 28),
    ("Difference", 13),
]


def read_daily() -> dict:
    rows = {}
    if not DAILY_CSV.exists():
        return rows
    with DAILY_CSV.open(newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["date"]] = r
    return rows


def num(row, key):
    raw = (row or {}).get(key, "")
    if raw in ("", None):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def build_sheet(wb, year: int, month: int, daily: dict, cfg: dict,
                first_day: date, last_day: date):
    title = date(year, month, 1).strftime("%B %Y")
    ws = wb.create_sheet(date(year, month, 1).strftime("%b %Y"))
    loc = cfg["location"]["label"]

    ws["A1"] = f"{cfg.get('site_name', 'Plant')} — Daily Net Generation"
    ws["A1"].font = Font(name=FONT, size=14, bold=True, color="1F3864")
    ws["A2"] = f"{title} · {loc} · plant and township"
    ws["A2"].font = Font(name=FONT, size=10, color="595959")

    header_row = 4
    for i, (label, width) in enumerate(COLUMNS, start=1):
        c = ws.cell(header_row, i, label)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = Border(bottom=MED)
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[header_row].height = 30

    first = header_row + 1
    days_in_month = calendar.monthrange(year, month)[1]
    missing = []

    for d in range(1, days_in_month + 1):
        day = date(year, month, d)
        r = first + d - 1
        row = daily.get(day.isoformat())
        printed, summed = num(row, "net_kwh_reported"), num(row, "net_kwh_computed")

        cd = ws.cell(r, 1, day)
        cd.number_format = "dd-mmm-yyyy"
        cw = ws.cell(r, 2, day.strftime("%a"))
        cw.alignment = Alignment(horizontal="center")

        ws.cell(r, 3, printed)
        ws.cell(r, 4, summed)
        # difference as a formula so the sheet stays live if a figure is edited
        ws.cell(r, 5, f"=IF(COUNT(C{r},D{r})=2,D{r}-C{r},\"\")")

        for col in range(1, 6):
            cell = ws.cell(r, col)
            cell.font = Font(name=FONT, size=10)
            cell.border = Border(bottom=THIN)
            if col >= 3:
                cell.number_format = "#,##0.00;-#,##0.00;–"
        if row is None and first_day <= day <= last_day:
            # only a day whose report was actually due counts as missed; a day
            # still to come is simply blank
            missing.append(day)
            note = ws.cell(r, 3, "no report")
            note.font = Font(name=FONT, size=9, italic=True, color="C0392B")
            note.alignment = Alignment(horizontal="center")
            for col in range(1, 6):
                ws.cell(r, col).fill = MISSING_FILL
        elif row is None:
            note = ws.cell(r, 3,
                           "before records" if day < first_day else "not due yet")
            note.font = Font(name=FONT, size=9, italic=True, color="A6A6A6")
            note.alignment = Alignment(horizontal="center")

    last = first + days_in_month - 1
    tr = last + 1
    ws.cell(tr, 1, "Month total").font = Font(name=FONT, size=10, bold=True)
    ws.cell(tr, 2, "").font = Font(name=FONT, size=10)
    for col, letter in ((3, "C"), (4, "D"), (5, "E")):
        c = ws.cell(tr, col, f"=SUM({letter}{first}:{letter}{last})")
        c.font = Font(name=FONT, size=10, bold=True)
        c.number_format = "#,##0.00;-#,##0.00;–"
    due = sum(1 for d in range(1, days_in_month + 1)
              if first_day <= date(year, month, d) <= last_day)
    cnt = ws.cell(tr + 1, 1, "Days reported")
    cnt.font = Font(name=FONT, size=10, bold=True)
    c = ws.cell(tr + 1, 3, f"=COUNT(C{first}:C{last}) & \" of {due} due\"")
    c.font = Font(name=FONT, size=10, bold=True)
    c.alignment = Alignment(horizontal="center")
    for col in range(1, 6):
        ws.cell(tr, col).fill = TOTAL_FILL
        ws.cell(tr, col).border = Border(top=MED)
        ws.cell(tr + 1, col).fill = TOTAL_FILL

    n = tr + 3
    notes = [
        "Notes",
        "• “As printed” is the TOTAL NET GENERATION cell of the daily "
        "inverter report, i.e. the figure the plant circulates.",
        "• “Sum of site columns” adds the individual site readings in "
        "the same sheet.",
        "• The two disagree every day. The printed plant total leaves out the "
        "MPSS & MCC 13-16 column, and the printed net total adds a flat "
        "387.60 kWh that does not come from any column.",
        "• Figures are reproduced exactly as the daily report gave them; "
        "nothing is corrected here.",
    ]
    if missing:
        shown = ", ".join(d.strftime("%d %b") for d in missing[:10])
        notes.append(f"• No report arrived on {len(missing)} day(s): {shown}"
                     + ("…" if len(missing) > 10 else "") + ".")
    notes.append(f"• Generated from data/processed/generation_daily.csv.")
    for i, text in enumerate(notes):
        c = ws.cell(n + i, 1, text)
        c.font = Font(name=FONT, size=9,
                      bold=(i == 0), color="1F3864" if i == 0 else "595959")

    ws.freeze_panes = ws.cell(first, 1)
    ws.sheet_view.showGridLines = False
    return len(missing)


def months_in(daily: dict):
    seen = sorted({(int(d[:4]), int(d[5:7])) for d in daily})
    return seen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--month", help="YYYY-MM; default: every month with data")
    ap.add_argument("--no-recalc", action="store_true",
                    help="skip the LibreOffice pass that caches formula results")
    args = ap.parse_args()

    cfg = load_config()
    daily = read_daily()
    if not daily:
        print("No daily data yet; nothing to report.")
        return 0

    first_day = min(date.fromisoformat(d) for d in daily)
    last_day = max(date.fromisoformat(d) for d in daily)
    wanted = ([(int(args.month[:4]), int(args.month[5:7]))] if args.month
              else months_in(daily))
    REPORTS.mkdir(parents=True, exist_ok=True)
    written = []
    for year, month in wanted:
        in_month = [date.fromisoformat(d) for d in daily
                    if d.startswith(f'{year}-{month:02d}')]
        stamp = max(in_month) if in_month else date(year, month, 1)
        wb = Workbook()
        wb.remove(wb.active)
        missing = build_sheet(wb, year, month, daily, cfg,
                              first_day, last_day)
        path = REPORTS / f"{year}-{month:02d}_net_generation.xlsx"
        wb.save(path)
        written.append((path, missing, stamp))

    for path, missing, stamp in written:
        if not args.no_recalc:
            recalc(path)
        normalise(path, stamp)
        rel = path.relative_to(ROOT)
        print(f"  {rel}" + (f"  ({missing} day(s) with no report)" if missing else ""))
    print(f"\n{len(written)} monthly report(s) in {REPORTS.relative_to(ROOT)}/")
    return 0



def normalise(path: Path, stamp: date) -> None:
    """Make the file byte-identical for identical data.

    A workbook carries the moment it was written, in the zip entry headers and
    in docProps, so regenerating it every morning would produce a different file
    every morning and commit five of them a day. Both are pinned to the last
    reading the sheet covers, so the file changes only when the data does.
    """
    import re
    import shutil
    import zipfile

    fixed = (stamp.year, stamp.month, stamp.day, 0, 0, 0)
    iso = f"{stamp.isoformat()}T00:00:00Z"
    tmp = path.with_suffix(".tmp.xlsx")
    with zipfile.ZipFile(path) as src, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in sorted(src.infolist(), key=lambda i: i.filename):
            data = src.read(item.filename)
            if item.filename == "docProps/core.xml":
                text = data.decode("utf-8")
                text = re.sub(r"(<dcterms:(?:created|modified)[^>]*>)[^<]+(<)",
                              rf"\g<1>{iso}\g<2>", text)
                data = text.encode("utf-8")
            info = zipfile.ZipInfo(item.filename, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = item.external_attr
            dst.writestr(info, data)
    shutil.move(str(tmp), str(path))


def recalc(path: Path) -> None:
    """Cache formula results so previewers show totals without opening Excel.

    LibreOffice will not convert a file onto itself, so the conversion goes to a
    scratch directory and the result is moved back.
    """
    import shutil
    import tempfile
    if not shutil.which("soffice"):
        return
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "xlsx",
                 "--outdir", tmp, str(path)],
                check=True, capture_output=True, timeout=180,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            print(f"    (could not cache formula values for {path.name}: {exc})",
                  file=sys.stderr)
            return
        produced = Path(tmp) / path.name
        if produced.exists():
            shutil.move(str(produced), str(path))


if __name__ == "__main__":
    raise SystemExit(main())
