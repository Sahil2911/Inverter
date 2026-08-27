# Kalol Solar Generation Board

Tidy dataset and daily dashboard for the rooftop inverter fleet at the **IFFCO
Kalol** complex — plant and township — with the solar resource at site plotted
alongside it.

## How it fits together

```
Generation/MM/DD/'YYYY HH:MM.xlsx'   <- Power Automate files each day's workbook here
data/processed/                      <- the tidy dataset built from those workbooks
dashboard/index.html                 <- the board (open in any browser)
dashboard/artifact.html              <- same board, as a publishable fragment
```

`Generation/` is the archive and belongs to Power Automate — the pipeline only
ever **reads** it. Nothing is moved, renamed or deleted.

Each day is keyed on the **reading date inside the sheet**, not the folder it
landed in. That matters: the off-schedule deliveries (30 Jun 17:17 and 9 Jul
11:28) carry the *previous* day's figures, and keying on the sheet date files
them correctly instead of overwriting the day they arrived on.

### The processed dataset

| File | One row per | Holds |
|---|---|---|
| `generation_sites.csv` | site × day | capacity kW, generation kWh |
| `generation_daily.csv` | day | section and net totals, both **as printed** and **as summed**, plus reconciliation deltas |
| `report_gaps.csv` | failed delivery | date, why it was unusable, which file |
| `irradiance_kalol.csv` | day | GHI kWh/m², sunshine hours, max temp, rain, cloud cover |

## Running it

```bash
pip install -r requirements.txt
python scripts/daily_update.py      # ingest -> irradiance -> dashboard
```

Individual stages:

```bash
python scripts/ingest.py [FILE ...]   # default: every workbook under Generation/
python scripts/irradiance.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]
python scripts/build_dashboard.py
```

Re-running is safe and produces byte-identical output.

**The dataset outlives its source files.** Ingest *merges* into
`data/processed/` rather than replacing it, so once a day is recorded it stays
recorded even if its workbook is later tidied out of `Generation/`. Dropping an
old month to keep the repo small therefore costs you nothing on the dashboard.
Re-adding a corrected workbook still overwrites that day. To deliberately
rebuild from only the workbooks present right now:

```bash
python scripts/ingest.py --rebuild
```

## Irradiance

Daily global horizontal irradiation for 23.2456°N, 72.4986°E from the
[Open-Meteo](https://open-meteo.com/) reanalysis archive — no API key, no
account. Published in MJ/m² and converted at **3.6 MJ = 1 kWh**.

That gives the two metrics the board leads with:

- **Specific yield** = generation ÷ installed kW (kWh/kWp) — array size divided out
- **Performance ratio** = specific yield ÷ irradiation — the share of available
  sun actually converted, which is what makes one day comparable to another

The last 10 days are re-fetched each run so provisional forecast values are
replaced by settled reanalysis.

## Two defects in the source workbook

Across **51 of 51** days ingested, the printed totals disagree with the columns
above them. The pattern is consistent enough to name the cause:

**1. The plant total leaves out the MPSS & MCC 13-16 column.** The gap matches
that site's daily output on 49 of 51 days, and the printed plant capacity
(925.26 kW) is short of the columns (995.26 kW) by exactly its 70 kW.

**2. The total net cell adds a flat 387.60 kWh.** Every single day, `TOTAL NET
GENERATION` = printed plant + township + 387.60. A real array never returns an
identical figure two days running, let alone 51. The printed net *capacity*
(1,472.515 kW) likewise exceeds the itemised columns (1,164.845 kW) by 307.67 kW,
so this looks like a hard-coded stand-in for an array that is not itemised
anywhere in the sheet.

Township reconciles exactly, so the site columns themselves are sound.

The dashboard **shows both readings side by side** — in the headline, as two
series on the generation trend, and in a *Printed totals vs column sums* panel
that names the gap per section. Derived metrics (specific yield, performance
ratio) use the column sums, since those are the figures that reconcile.

## Data coverage

51 of the 60 days between 29 Jun and 27 Aug 2026 have usable generation data:

- **4 deliveries arrived blank** (27–30 Jul) — the file was committed on time but
  its plant reading row never populated. These are recorded in `report_gaps.csv`
  rather than dropped, so a silent Power Automate failure stays visible.
- **5 days never arrived** (30 Jun, 5–7 Jul, 27 Aug).

Missing days are drawn as breaks in the trend, never as zero.

## Automation

`.github/workflows/daily-dashboard.yml` runs the pipeline when Power Automate
pushes a workbook to `Generation/`, plus a 16:00 UTC (21:30 IST) backstop and a
manual trigger. It commits the refreshed dataset and dashboard — never
`Generation/` itself.
