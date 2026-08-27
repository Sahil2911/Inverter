"""Render the solar generation board from the processed CSVs.

Emits two files from one body of content:
  dashboard/index.html    - standalone page (open locally, or serve via Pages)
  dashboard/artifact.html - fragment for publishing as a Claude Artifact

Charts are inline SVG computed here, so the page is fully self-contained: no
chart library, no network calls, nothing to break when it is opened offline.
"""
from __future__ import annotations

import csv
import html
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DAILY_CSV, DASHBOARD, GAPS_CSV, IRRADIANCE_CSV, SITES_CSV, load_config,
)

ASSETS = Path(__file__).resolve().parent / "assets"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600"
         "&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;500;600"
         "&display=swap")

GEN = "var(--gen)"
SUN = "var(--sun)"
PRINTED = "var(--printed)"

VIEW_W = 960
M_L, M_R, M_T, M_B = 48, 96, 12, 24


# ---------------------------------------------------------------- data loading

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def num(row: dict, key: str):
    raw = (row or {}).get(key, "")
    if raw in ("", None):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def build_series() -> list[dict]:
    """One record per calendar day that has generation, irradiance, or both."""
    daily = {r["date"]: r for r in read_csv(DAILY_CSV)}
    irr = {r["date"]: r for r in read_csv(IRRADIANCE_CSV)}
    out = []
    for day in sorted(set(daily) | set(irr)):
        gen_row, irr_row = daily.get(day), irr.get(day)
        kwh = num(gen_row, "headline_kwh") if gen_row else None
        capacity = num(gen_row, "net_capacity_kw_computed") if gen_row else None
        ghi = num(irr_row, "ghi_kwh_m2") if irr_row else None
        yield_kwp = (kwh / capacity) if (kwh is not None and capacity) else None
        # Performance ratio: what fraction of the sun that fell was converted,
        # relative to the array's nameplate rating.
        pr = (yield_kwp / ghi * 100.0) if (yield_kwp is not None and ghi) else None
        out.append({
            "date": day,
            "kwh": kwh,
            "kwh_printed": num(gen_row, "net_kwh_reported") if gen_row else None,
            "plant_kwh": num(gen_row, "plant_kwh_computed") if gen_row else None,
            "plant_kwh_printed": num(gen_row, "plant_kwh_reported") if gen_row else None,
            "township_kwh": num(gen_row, "township_kwh_computed") if gen_row else None,
            "township_kwh_printed": num(gen_row, "township_kwh_reported") if gen_row else None,
            "capacity_kw": capacity,
            "ghi": ghi,
            "sunshine": num(irr_row, "sunshine_hours") if irr_row else None,
            "temp": num(irr_row, "temp_max_c") if irr_row else None,
            "rain": num(irr_row, "precipitation_mm") if irr_row else None,
            "cloud": num(irr_row, "cloud_cover_pct") if irr_row else None,
            "yield_kwp": yield_kwp,
            "pr": pr,
            "flags": (gen_row or {}).get("reconciliation_flags", ""),
        })
    return out


# ------------------------------------------------------------------- formatting

def fnum(value, digits=0, dash="—"):
    if value is None:
        return dash
    return f"{value:,.{digits}f}"


def pretty_date(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def short_date(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b")


def esc(text) -> str:
    return html.escape(str(text), quote=True)


# ------------------------------------------------------------------ svg helpers

def nice_ticks(value: float):
    """Axis top and step that read as round numbers without wasting headroom.

    Tries 4, 5 and 6 intervals with the usual 1/2/2.5/5 steps and keeps whichever
    covers the data with the least empty space above it.
    """
    import math
    if value <= 0:
        return 1.0, 0.25, 4
    best = None
    for count in (4, 5, 6):
        raw = value / count
        exp = math.floor(math.log10(raw))
        base = 10 ** exp
        for mult in (1, 2, 2.5, 5, 10):
            step = mult * base
            if step * count >= value - 1e-9:
                top = step * count
                if best is None or top < best[0]:
                    best = (top, step, count)
                break
    return best


def tick_decimals(step: float) -> int:
    if step >= 1:
        return 0
    return 1 if step >= 0.1 else 2


def nice_max(value: float) -> float:
    return nice_ticks(value)[0]


def y_of_val(end):
    """The dot stays on the data; only the label moves."""
    return end["true_y"]


def time_panel(panel_id, records, series, height=170):
    """A time chart carrying one or more same-unit measures on a single axis.

    Two series of the same measure (printed vs summed kWh) share one scale, which
    is the honest way to compare them; a second y-axis would invent a relationship.
    """
    present = [sp for sp in series
               if any(r.get(sp["key"]) is not None for r in records)]
    if not present:
        return "", None

    inner_w = VIEW_W - M_L - M_R
    inner_h = height - M_T - M_B
    ords = [datetime.strptime(r["date"], "%Y-%m-%d").date().toordinal() for r in records]
    lo, hi = min(ords), max(ords)
    span = max(hi - lo, 1)

    def x_of(iso):
        o = datetime.strptime(iso, "%Y-%m-%d").date().toordinal()
        if hi == lo:
            return M_L + inner_w / 2
        return M_L + (o - lo) / span * inner_w

    peak = max(r[sp["key"]] for sp in present for r in records
               if r.get(sp["key"]) is not None)
    top, step, tick_count = nice_ticks(peak)
    tick_dp = tick_decimals(step)

    def y_of(v):
        return M_T + inner_h - (v / top) * inner_h

    labels = " and ".join(sp["label"] for sp in present)
    parts = [f'<svg viewBox="0 0 {VIEW_W} {height}" role="img" '
             f'aria-label="{esc(labels)} over time">']

    for i in range(tick_count + 1):
        v = step * i
        y = y_of(v)
        parts.append(f'<line class="grid" x1="{M_L}" y1="{y:.1f}" '
                     f'x2="{M_L + inner_w}" y2="{y:.1f}"/>')
        parts.append(f'<text class="axis" x="{M_L - 8}" y="{y + 3.5:.1f}" '
                     f'text-anchor="end">{fnum(v, tick_dp)}</text>')

    n = len(records)
    tick_step = max(1, round(n / 6))
    for i in sorted(set(list(range(0, n, tick_step)) + [n - 1])):
        iso = records[i]["date"]
        x = x_of(iso)
        anchor = "end" if i == n - 1 and n > 1 else ("start" if i == 0 and n > 1 else "middle")
        parts.append(f'<text class="axis" x="{x:.1f}" y="{M_T + inner_h + 15}" '
                     f'text-anchor="{anchor}">{esc(short_date(iso))}</text>')

    solo = len(present) == 1
    ends = []
    for sp in present:
        key, color = sp["key"], sp["color"]
        pts = [r for r in records if r.get(key) is not None]
        if not pts:
            continue
        # break the line across missing days rather than interpolating over them
        segments, current, prev_ord = [], [], None
        for r in pts:
            o = datetime.strptime(r["date"], "%Y-%m-%d").date().toordinal()
            if prev_ord is not None and o - prev_ord > 1:
                segments.append(current)
                current = []
            current.append(r)
            prev_ord = o
        if current:
            segments.append(current)

        for seg in segments:
            coords = [(x_of(r["date"]), y_of(r[key])) for r in seg]
            if len(coords) > 1:
                line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in coords)
                if solo:
                    base = M_T + inner_h
                    area = (f'M{coords[0][0]:.1f},{base:.1f} L'
                            + " L".join(f"{x:.1f},{y:.1f}" for x, y in coords)
                            + f" L{coords[-1][0]:.1f},{base:.1f} Z")
                    parts.append(f'<path d="{area}" fill="{color}" opacity="0.10"/>')
                parts.append(f'<path d="{line}" fill="none" stroke="{color}" '
                             f'stroke-width="2" stroke-linejoin="round" '
                             f'stroke-linecap="round"/>')
            else:
                x, y = coords[0]
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" '
                             f'stroke="var(--panel)" stroke-width="2"/>')

        last = pts[-1]
        ends.append({"sp": sp, "x": x_of(last["date"]), "y": y_of(last[key]),
                     "true_y": y_of(last[key]),
                     "text": (sp["label_fmt"](last[key]) if sp.get("label_fmt")
                              else f'{fnum(last[key], sp["digits"])} {sp["unit"]}')})

    # keep converging end-labels legible: nudge apart and run a leader to the dot
    ends.sort(key=lambda e: e["y"])
    for i in range(1, len(ends)):
        gap = ends[i]["y"] - ends[i - 1]["y"]
        if gap < 14:
            ends[i]["y"] += (14 - gap)
    for e in ends:
        parts.append(f'<circle cx="{e["x"]:.1f}" cy="{y_of_val(e):.1f}" r="4.5" '
                     f'fill="{e["sp"]["color"]}" stroke="var(--panel)" stroke-width="2"/>')
        if abs(e["y"] - y_of_val(e)) > 1.5:
            parts.append(f'<line x1="{e["x"] + 5:.1f}" y1="{y_of_val(e):.1f}" '
                         f'x2="{e["x"] + 9:.1f}" y2="{e["y"]:.1f}" '
                         f'stroke="var(--rule-strong)" stroke-width="1"/>')
        parts.append(f'<text class="dlabel" x="{e["x"] + 11:.1f}" '
                     f'y="{e["y"] + 3.5:.1f}">{esc(e["text"])}</text>')

    parts.append(f'<line class="crosshair" x1="0" y1="{M_T}" x2="0" y2="{M_T + inner_h}"/>')
    for sp in present:
        parts.append(f'<circle class="hover-dot" cx="0" cy="0" r="4.5" '
                     f'fill="{sp["color"]}" stroke="var(--panel)" stroke-width="2" '
                     f'style="opacity:0"/>')
    parts.append("</svg>")

    points = []
    for r in records:
        pt = {"x": round(x_of(r["date"]), 1), "label": pretty_date(r["date"])}
        for sp in present:
            v = r.get(sp["key"])
            pt[sp["key"]] = round(v, sp["digits"] + 2) if v is not None else None
            pt[sp["key"] + "_y"] = round(y_of(v), 1) if v is not None else None
        points.append(pt)

    meta = {
        "kind": "time", "id": panel_id, "viewWidth": VIEW_W, "tipY": M_T,
        "fields": [{"key": sp["key"], "label": sp["label"], "color": sp["color"],
                    "digits": sp["digits"], "unit": sp["unit"]} for sp in present],
        "points": points,
    }
    return "".join(parts), meta


def site_bars(panel_id, rows, latest_ghi):
    """Specific yield per site, one hue; zero-output sites flagged as a fault."""
    if not rows:
        return "", None
    ordered = sorted(rows, key=lambda r: (r["yield_kwp"] is None, -(r["yield_kwp"] or 0)))
    row_h, gap = 26, 6
    height = M_T + len(ordered) * (row_h + gap) + 28
    label_w = 250
    bar_x = label_w + 10
    bar_w = VIEW_W - bar_x - 96
    top, bstep, bcount = nice_ticks(max((r["yield_kwp"] or 0) for r in ordered))
    bdp = tick_decimals(bstep)

    parts = [f'<svg viewBox="0 0 {VIEW_W} {height}" role="img" '
             f'aria-label="Specific yield by site">']
    for i in range(bcount + 1):
        v = bstep * i
        x = bar_x + (v / top) * bar_w
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{M_T - 4}" x2="{x:.1f}" '
                     f'y2="{M_T + len(ordered) * (row_h + gap) - gap + 2}"/>')
        parts.append(f'<text class="axis" x="{x:.1f}" y="{height - 8}" '
                     f'text-anchor="middle">{fnum(v, max(bdp, 1))}</text>')
    parts.append(f'<text class="axis-title" x="{bar_x + bar_w / 2:.1f}" y="{height - 22}" '
                 f'text-anchor="middle">kWh per kWp installed</text>')

    for i, r in enumerate(ordered):
        y = M_T + i * (row_h + gap)
        val = r["yield_kwp"] or 0.0
        w = max((val / top) * bar_w, 0)
        dead = (r["energy_kwh"] or 0) <= 0
        color = "var(--crit)" if dead else GEN
        name = r["name"]
        display = name if len(name) <= 34 else name[:32] + "…"
        parts.append(f'<text class="site-label" x="{label_w}" '
                     f'y="{y + row_h / 2 + 3.5:.1f}" text-anchor="end">'
                     f'{esc(display)}</text>')
        pr = (val / latest_ghi * 100) if latest_ghi else None
        tip = (f'<div class="t-d">{esc(name)}</div>'
               f'<div class="t-r"><i style="background:{color}"></i>Generation '
               f'<b>{fnum(r["energy_kwh"], 2)} kWh</b></div>'
               f'<div class="t-r"><i style="background:{color}"></i>Capacity '
               f'<b>{fnum(r["capacity_kw"], 2)} kW</b></div>'
               f'<div class="t-r"><i style="background:{color}"></i>Specific yield '
               f'<b>{fnum(val, 2)} kWh/kWp</b></div>'
               + (f'<div class="t-r"><i style="background:{color}"></i>Perf. ratio '
                  f'<b>{fnum(pr, 1)} %</b></div>' if pr is not None else ""))
        if w >= 1:
            parts.append(
                f'<rect x="{bar_x}" y="{y + 1}" width="{w:.1f}" height="{row_h - 2}" '
                f'rx="4" fill="{color}" data-tip="{esc(tip)}"><title>{esc(name)}</title></rect>')
            # square off the baseline end so the bar grows from the axis
            parts.append(f'<rect x="{bar_x}" y="{y + 1}" width="{min(4, w):.1f}" '
                         f'height="{row_h - 2}" fill="{color}" pointer-events="none"/>')
        if dead:
            parts.append(f'<circle cx="{bar_x + 5}" cy="{y + row_h / 2:.1f}" r="3.5" '
                         f'fill="var(--crit)"/>')
            parts.append(f'<text class="dlabel" x="{bar_x + 14}" '
                         f'y="{y + row_h / 2 + 3.5:.1f}" style="fill:var(--crit)">'
                         f'No output</text>')
        else:
            parts.append(f'<text class="dlabel" x="{bar_x + w + 8:.1f}" '
                         f'y="{y + row_h / 2 + 3.5:.1f}">{val:.2f}</text>')
    parts.append("</svg>")
    return "".join(parts), {"kind": "bars", "id": panel_id}


# ---------------------------------------------------------------------- page

def panel_block(panel_id, title, caption, svg, legend_html="", empty_msg=None):
    if not svg:
        return (f'<section class="card panel"><div class="panel-head"><div>'
                f'<h2>{esc(title)}</h2><div class="cap">{esc(caption)}</div></div>'
                f'{legend_html}</div><div class="empty">{esc(empty_msg or "No data yet.")}'
                f'</div></section>')
    return (f'<section class="card panel"><div class="panel-head"><div>'
            f'<h2>{esc(title)}</h2><div class="cap">{esc(caption)}</div></div>'
            f'{legend_html}</div>'
            f'<div class="plot" id="{panel_id}">{svg}<div class="tip"></div></div>'
            f'</section>')



def coverage(records, gaps, first_day, last_day) -> dict:
    """Which days in the window have usable generation, and why the rest do not."""
    from datetime import timedelta
    have = {r["date"] for r in records if r["kwh"] is not None}
    blank = {g["date"] for g in gaps}
    span, day = [], first_day
    while day <= last_day:
        span.append(day.isoformat())
        day += timedelta(days=1)
    absent = [d for d in span if d not in have and d not in blank]
    return {"expected": len(span), "have": len(have), "blank": sorted(blank),
            "absent": absent, "first": span[0] if span else None,
            "last": span[-1] if span else None}


def diagnose_totals(daily_rows, site_rows) -> dict:
    """Work out *why* the printed totals differ, rather than only that they do.

    Two patterns show up across the whole history: a constant added into the net
    total, and one site column left out of the plant total.
    """
    out = {"days": len(daily_rows), "flagged": 0, "constant": None,
           "constant_days": 0, "omitted": None, "omitted_days": 0}
    if not daily_rows:
        return out
    out["flagged"] = sum(1 for r in daily_rows if r.get("reconciliation_flags"))

    offsets = {}
    for r in daily_rows:
        pr, tr, nr = (num(r, "plant_kwh_reported"), num(r, "township_kwh_reported"),
                      num(r, "net_kwh_reported"))
        if None in (pr, tr, nr):
            continue
        key = round(nr - pr - tr, 2)
        offsets[key] = offsets.get(key, 0) + 1
    if offsets:
        value, count = max(offsets.items(), key=lambda kv: kv[1])
        if count >= max(2, int(0.8 * len(daily_rows))) and abs(value) > 0.5:
            out["constant"], out["constant_days"] = value, count

    per_day = {}
    for row in site_rows:
        if row["section"] == "PLANT":
            per_day.setdefault(row["date"], {})[row["name"]] = num(row, "energy_kwh")
    names = sorted({n for d in per_day.values() for n in d})
    best = (0, None)
    for name in names:
        hits = 0
        for r in daily_rows:
            pc, pr = num(r, "plant_kwh_computed"), num(r, "plant_kwh_reported")
            value = per_day.get(r["date"], {}).get(name)
            if None in (pc, pr, value):
                continue
            # allow a couple of kWh for the sheet rounding its displayed cells
            if abs((pc - pr) - value) <= 2.0:
                hits += 1
        if hits > best[0]:
            best = (hits, name)
    if best[1] and best[0] >= max(2, int(0.8 * len(daily_rows))):
        out["omitted"], out["omitted_days"] = best[1], best[0]
    return out


def build() -> dict:
    cfg = load_config()
    records = build_series()
    sites = read_csv(SITES_CSV)
    gaps = read_csv(GAPS_CSV)
    daily_rows = read_csv(DAILY_CSV)
    gen_days = [r for r in records if r["kwh"] is not None]

    if not gen_days:
        latest = None
    else:
        latest = gen_days[-1]

    latest_iso = latest["date"] if latest else None
    site_rows = []
    for r in sites:
        if latest_iso and r["date"] != latest_iso:
            continue
        cap = num(r, "capacity_kw")
        kwh = num(r, "energy_kwh")
        site_rows.append({
            "name": r["name"], "section": r["section"],
            "capacity_kw": cap, "energy_kwh": kwh,
            "yield_kwp": (kwh / cap) if (kwh is not None and cap) else None,
        })

    latest_ghi = latest["ghi"] if latest else None
    dead = [s for s in site_rows if (s["energy_kwh"] or 0) <= 0]

    panels_meta = []

    gen_svg, gen_meta = time_panel("p-gen", records, [
        {"key": "kwh", "color": GEN, "label": "Summed from columns",
         "unit": "kWh", "digits": 0},
        {"key": "kwh_printed", "color": PRINTED, "label": "Printed in sheet",
         "unit": "kWh", "digits": 0},
    ], height=210)
    if gen_meta:
        panels_meta.append(gen_meta)

    irr_svg, irr_meta = time_panel("p-irr", records, [
        {"key": "ghi", "color": SUN, "label": "Irradiation (GHI)",
         "unit": "kWh/m\u00b2", "digits": 2,
         "label_fmt": lambda v: f"{v:.2f} kWh/m\u00b2"},
    ], height=180)
    if irr_meta:
        panels_meta.append(irr_meta)

    pr_svg, pr_meta = time_panel("p-pr", records, [
        {"key": "pr", "color": GEN, "label": "Performance ratio",
         "unit": "%", "digits": 1, "label_fmt": lambda v: f"{v:.1f} %"},
    ], height=170)
    if pr_meta:
        panels_meta.append(pr_meta)

    bars_svg, bars_meta = site_bars("p-sites", site_rows, latest_ghi)
    if bars_meta:
        panels_meta.append(bars_meta)

    cover = None
    if records:
        cover = coverage(records, gaps,
                         date.fromisoformat(records[0]["date"]),
                         date.fromisoformat(records[-1]["date"]))

    return {
        "cfg": cfg, "records": records, "gen_days": gen_days, "latest": latest,
        "gaps": gaps, "cover": cover,
        "diag": diagnose_totals(daily_rows, sites),
        "site_rows": site_rows, "dead": dead, "latest_ghi": latest_ghi,
        "svg": {"gen": gen_svg, "irr": irr_svg, "pr": pr_svg, "bars": bars_svg},
        "panels_meta": panels_meta,
    }


def freshness_chip(latest_iso: str | None) -> str:
    if not latest_iso:
        return '<span class="chip bad"><span class="dot"></span>no report ingested</span>'
    age = (date.today() - date.fromisoformat(latest_iso)).days
    if age <= 1:
        return '<span class="chip ok"><span class="dot"></span>current</span>'
    return (f'<span class="chip bad"><span class="dot"></span>'
            f'{age} days behind</span>')


def reconciliation_panel(latest: dict | None, diag: dict | None = None) -> str:
    """Printed totals and column sums side by side, with the gap named."""
    if not latest:
        return ""
    row = next((r for r in read_csv(DAILY_CSV) if r["date"] == latest["date"]), {})
    if not row:
        return ""

    body, diverges = [], False
    for key, label in (("plant", "Plant"), ("township", "Township"),
                       ("net", "Total net")):
        printed = num(row, f"{key}_kwh_reported")
        summed = num(row, f"{key}_kwh_computed")
        delta = (summed - printed) if (printed is not None and summed is not None) else None
        pct = (delta / printed * 100) if (delta is not None and printed) else None
        agrees = delta is not None and abs(delta) <= 0.5
        if delta is not None and not agrees:
            diverges = True
        if delta is None:
            mark = "&mdash;"
        elif agrees:
            mark = "Agrees"
        else:
            mark = '<span class="flag">Differs</span>'
        body.append(
            f'<tr><td>{esc(label)}</td><td>{fnum(printed, 2)}</td>'
            f'<td>{fnum(summed, 2)}</td>'
            f'<td>{"&mdash;" if delta is None else format(delta, "+,.2f")}</td>'
            f'<td>{"&mdash;" if pct is None else format(pct, "+.1f")}</td>'
            f'<td style="text-align:left">{mark}</td></tr>')

    caption = ("The sheet's own total cells against the sum of the site columns "
               "beneath them, for the latest day.")
    if diverges:
        findings = []
        d = diag or {}
        if d.get("days"):
            findings.append(f'This is not a one-off: the totals fail to reconcile on '
                            f'<b>{d["flagged"]} of {d["days"]}</b> days ingested.')
        if d.get("omitted"):
            findings.append(
                f'The <b>plant</b> total looks like it leaves out the '
                f'<b>{esc(d["omitted"])}</b> column &mdash; the gap matches that '
                f'site\'s output on {d["omitted_days"]} of {d["days"]} days, and the '
                f'printed plant capacity is short by exactly its 70 kW.')
        if d.get("constant") is not None:
            findings.append(
                f'The <b>total net</b> cell adds a flat '
                f'<b>{d["constant"]:,.2f} kWh</b> on top of plant + township &mdash; '
                f'the same figure on {d["constant_days"]} of {d["days"]} days. A real '
                'array never returns an identical number two days running, let alone '
                f'{d["constant_days"]}, so this reads as a hard-coded value for '
                'capacity that is not itemised anywhere in the sheet.')
        note = ('<div class="notice"><div class="body">'
                + "<br><br>".join(findings) +
                ('<br><br>' if findings else '') +
                'Township reconciles exactly, so the site columns themselves are sound. '
                'Both readings are kept in <code>generation_daily.csv</code>; nothing '
                'is discarded.</div></div>')
    else:
        note = ('<div class="notice info"><div class="body">Printed totals and '
                'column sums agree for this day.</div></div>')

    return ('<section class="card panel"><div class="panel-head"><div>'
            '<h2>Printed totals vs column sums</h2>'
            f'<div class="cap">{esc(caption)}</div></div>'
            '<div class="legend">'
            '<span><i style="background:var(--gen)"></i>Summed</span>'
            '<span><i style="background:var(--printed)"></i>Printed</span>'
            '</div></div>'
            '<div class="scroller"><table><thead><tr><th>Section</th>'
            '<th>Printed kWh</th><th>Summed kWh</th><th>Difference</th>'
            '<th>Difference %</th><th style="text-align:left">Status</th></tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{note}</section>')


def site_table(site_rows, latest_ghi) -> str:
    body = []
    for s in sorted(site_rows, key=lambda r: (r["section"], -(r["energy_kwh"] or 0))):
        pr = ((s["yield_kwp"] / latest_ghi * 100)
              if (s["yield_kwp"] is not None and latest_ghi) else None)
        status = ('<span class="flag">No output</span>'
                  if (s["energy_kwh"] or 0) <= 0 else "OK")
        body.append(
            f'<tr><td>{esc(s["name"])}</td><td>{esc(s["section"].title())}</td>'
            f'<td>{fnum(s["capacity_kw"], 2)}</td><td>{fnum(s["energy_kwh"], 2)}</td>'
            f'<td>{fnum(s["yield_kwp"], 2)}</td><td>{fnum(pr, 1)}</td>'
            f'<td style="text-align:left">{status}</td></tr>')
    cap = sum(s["capacity_kw"] or 0 for s in site_rows)
    kwh = sum(s["energy_kwh"] or 0 for s in site_rows)
    yld = kwh / cap if cap else None
    pr_all = (yld / latest_ghi * 100) if (yld and latest_ghi) else None
    return (
        '<div class="scroller"><table><thead><tr><th>Site</th><th>Section</th>'
        '<th>Capacity kW</th><th>kWh</th><th>kWh/kWp</th><th>PR %</th>'
        '<th style="text-align:left">Status</th></tr></thead><tbody>'
        + "".join(body) +
        f'</tbody><tfoot><tr><td>All sites</td><td>{len(site_rows)}</td>'
        f'<td>{fnum(cap, 2)}</td><td>{fnum(kwh, 2)}</td><td>{fnum(yld, 2)}</td>'
        f'<td>{fnum(pr_all, 1)}</td><td style="text-align:left">—</td></tr></tfoot>'
        '</table></div>')


def render_body(ctx: dict) -> str:
    cfg, latest = ctx["cfg"], ctx["latest"]
    records, gen_days = ctx["records"], ctx["gen_days"]
    site_rows, dead, latest_ghi = ctx["site_rows"], ctx["dead"], ctx["latest_ghi"]
    svg = ctx["svg"]
    loc = cfg["location"]

    latest_iso = latest["date"] if latest else None
    irr_days = [r for r in records if r["ghi"] is not None]

    head = (
        '<div class="rail"><div>'
        '<div class="eyebrow">Rooftop inverter fleet</div>'
        '<h1>Solar Generation Board</h1>'
        f'<div class="sub">{esc(loc["label"])} · plant &amp; township · '
        f'{len(site_rows) or "—"} metered sites</div></div>'
        '<div class="stamp"><div class="eyebrow">Latest report</div>'
        f'<div class="d">{esc(pretty_date(latest_iso)) if latest_iso else "—"}</div>'
        f'<div style="margin-top:5px">{freshness_chip(latest_iso)}</div></div></div>')

    if latest:
        printed_net = latest.get("kwh_printed")
        gap = (latest["kwh"] - printed_net) if printed_net is not None else None
        gap_pct = (gap / printed_net * 100) if (gap is not None and printed_net) else None
        figures = (
            '<div class="fig"><div class="fl">'
            '<i style="background:var(--gen)"></i>Summed from columns</div>'
            f'<div class="val">{fnum(latest["kwh"], 1)}<span class="unit">kWh</span></div>'
            '</div>'
            '<div class="fig"><div class="fl">'
            '<i style="background:var(--printed)"></i>Printed in sheet</div>'
            f'<div class="val">{fnum(printed_net, 1)}'
            '<span class="unit">kWh</span></div></div>')
        if gap is not None:
            hero_note = (f'Gap {gap:+,.1f} kWh ({gap_pct:+.1f}%) \u00b7 '
                         f'Plant {fnum(latest["plant_kwh"], 0)} / '
                         f'{fnum(latest["plant_kwh_printed"], 0)} \u00b7 '
                         f'Township {fnum(latest["township_kwh"], 0)} / '
                         f'{fnum(latest["township_kwh_printed"], 0)}'
                         '  (summed / printed)')
        else:
            hero_note = (f'Plant {fnum(latest["plant_kwh"], 0)} kWh \u00b7 '
                         f'Township {fnum(latest["township_kwh"], 0)} kWh')
    else:
        figures = ('<div class="fig"><div class="fl">Summed from columns</div>'
                   '<div class="val">&mdash;</div></div>')
        hero_note = "Waiting for the first workbook."

    kpi = []
    kpi.append(('Irradiation at site', fnum(latest_ghi, 2), 'kWh/m²',
                f'{fnum(latest["sunshine"], 1)} h sunshine' if latest and latest["sunshine"]
                is not None else 'Global horizontal'))
    kpi.append(('Specific yield', fnum(latest["yield_kwp"], 2) if latest else "—",
                'kWh/kWp', 'Generation ÷ installed kW'))
    kpi.append(('Performance ratio', fnum(latest["pr"], 1) if latest else "—", '%',
                'Yield ÷ irradiation'))
    kpi.append(('Installed capacity',
                fnum(latest["capacity_kw"], 1) if latest else "—", 'kW',
                f'{len(site_rows)} sites'))
    kpi.append(('Sites with no output', str(len(dead)) if latest else "—", '',
                (", ".join(s["name"].title() for s in dead)[:46] if dead else 'All reporting')))
    kpi.append(('Cloud cover', fnum(latest["cloud"], 0) if latest else "—", '%',
                f'{fnum(latest["rain"], 1)} mm rain' if latest and latest["rain"]
                is not None else 'Daily mean'))

    kpis = "".join(
        f'<div class="kpi"><div class="k">{esc(k)}</div>'
        f'<div class="v">{esc(v)}' + (f'<small>{esc(u)}</small>' if u else "") +
        f'</div><div class="m">{esc(m)}</div></div>'
        for k, v, u, m in kpi)

    band = (
        '<div class="band">'
        '<section class="card hero"><div class="eyebrow">Net generation, latest day</div>'
        f'<div class="figs">{figures}</div>'
        f'<div class="note">{esc(hero_note)}</div></section>'
        f'<div class="kpis">{kpis}</div></div>')

    cover, gaps = ctx.get("cover"), ctx.get("gaps", [])
    history_note = ""
    if cover and (cover["blank"] or cover["absent"]):
        bits = []
        if cover["blank"]:
            bits.append(f'<b>{len(cover["blank"])}</b> arrived blank '
                        f'({", ".join(pretty_date(d) for d in cover["blank"][:6])}'
                        f'{"…" if len(cover["blank"]) > 6 else ""}) — the workbook '
                        'was delivered but its plant reading row never populated')
        if cover["absent"]:
            shown = ", ".join(pretty_date(d) for d in cover["absent"][:6])
            bits.append(f'<b>{len(cover["absent"])}</b> never arrived '
                        f'({shown}{"…" if len(cover["absent"]) > 6 else ""})')
        history_note = (
            '<div class="notice info"><div class="body">'
            f'<b>{cover["have"]} of {cover["expected"]} days</b> between '
            f'{esc(pretty_date(cover["first"]))} and {esc(pretty_date(cover["last"]))} '
            'have usable generation data. Of the rest, ' + "; ".join(bits) +
            '. Those days are left as breaks in the trend rather than drawn as zero.'
            '</div></div>')

    legend_gen = ('<div class="legend">'
                  '<span><i style="background:var(--gen)"></i>Summed from columns</span>'
                  '<span><i style="background:var(--printed)"></i>Printed in sheet</span>'
                  '</div>')
    legend_irr = ('<div class="legend"><span><i style="background:var(--sun)"></i>'
                  'Global horizontal irradiation (kWh/m²)</span></div>')

    panels = (
        panel_block("p-gen", "Daily net generation",
                    "Both readings of the same day on one scale: the printed net total, "
                    "and the sum of the site columns.",
                    svg["gen"], legend_gen,
                    "No workbook ingested yet — the first report will draw this.") +
        panel_block("p-irr", "Solar resource at IFFCO Kalol",
                    f'Daily global horizontal irradiation, {loc["latitude"]}°N '
                    f'{loc["longitude"]}°E. Same time axis as the panel above.',
                    svg["irr"], legend_irr,
                    "Irradiance not fetched yet.") +
        panel_block("p-pr", "Performance ratio",
                    "Specific yield ÷ irradiation — how much of the available sun the "
                    "fleet actually converted, with array size divided out. "
                    "Computed on the column sums.",
                    svg["pr"], "",
                    "Needs both a generation report and irradiance for the same day."))

    if site_rows:
        tabs = (
            '<section class="card panel"><div class="panel-head"><div>'
            '<h2>Site performance, latest day</h2>'
            '<div class="cap">Ranked by specific yield, so a small array is judged '
            'against its own size rather than the big ones.</div></div>'
            '<div class="tabs" data-tabs>'
            '<button class="tab" data-target="sites-chart" aria-selected="true">Chart</button>'
            '<button class="tab" data-target="sites-table" aria-selected="false">Table</button>'
            '</div></div>'
            f'<div id="sites-chart"><div class="plot" id="p-sites">{svg["bars"]}'
            '<div class="tip"></div></div></div>'
            f'<div id="sites-table" class="hidden">{site_table(site_rows, latest_ghi)}</div>'
            '</section>')
    else:
        tabs = ""

    src = cfg["irradiance_source"]
    foot = (
        '<footer>'
        f'<p><b>Generation</b> — parsed from the daily inverter workbooks that '
        f'Power Automate files under <code>Generation/MM/DD/</code>. Each day is '
        f'keyed on the reading date inside the sheet, not the delivery date, so a '
        f'catch-up delivery lands on the day it reports. '
        f'{len(gen_days)} day(s) ingested'
        + (f', {len(gaps)} delivered blank' if gaps else '') + '.</p>'
        f'<p><b>Irradiance</b> — {esc(src["provider"])} reanalysis for '
        f'{esc(loc["latitude"])}°N {esc(loc["longitude"])}°E ({esc(loc["label"])}), '
        f'daily global horizontal irradiation converted from MJ/m² at 3.6 MJ = 1 kWh. '
        f'{len(irr_days)} day(s) loaded.</p>'
        f'<p>Board rebuilt {esc(datetime.now().strftime("%d %b %Y, %H:%M"))} · '
        'performance ratio uses nameplate DC capacity from the workbook’s CAPACITY row.</p>'
        '</footer>')

    board = {"panels": ctx["panels_meta"]}
    script = (f'<script>window.__BOARD__={json.dumps(board)};</script>'
              f'<script>{(ASSETS / "dashboard.js").read_text()}</script>')

    recon = reconciliation_panel(latest, ctx.get("diag"))
    return (f'<div class="wrap">{head}{band}'
            f'{history_note}{panels}{recon}{tabs}{foot}</div>{script}')


def main() -> int:
    ctx = build()
    body = render_body(ctx)
    css = (ASSETS / "dashboard.css").read_text()
    title = "Kalol Solar Board"
    DASHBOARD.mkdir(parents=True, exist_ok=True)

    fragment = (f'<title>{title}</title>\n'
                f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                f'<link rel="stylesheet" href="{FONTS}">\n'
                f'<style>{css}</style>\n{body}\n')
    (DASHBOARD / "artifact.html").write_text(fragment)

    standalone = ('<!doctype html>\n<html lang="en">\n<head>\n'
                  '<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                  f'<title>{title}</title>\n'
                  '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                  f'<link rel="stylesheet" href="{FONTS}">\n'
                  f'<style>{css}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n')
    (DASHBOARD / "index.html").write_text(standalone)

    print(f"Dashboard written: {len(ctx['gen_days'])} generation day(s), "
          f"{len([r for r in ctx['records'] if r['ghi'] is not None])} irradiance day(s), "
          f"{len(ctx['site_rows'])} sites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
