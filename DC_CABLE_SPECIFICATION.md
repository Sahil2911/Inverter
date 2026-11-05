# Solar DC Cable — Technical Specification & Procurement Sheet

Rooftop PV plant, Ahmedabad (Gujarat). DC cabling from PV modules to inverter
DC input. Prepared 05 Nov 2026.

**Site:** IFFCO Kalol complex (plant + township), 23.2456 N / 72.4986 E —
**1164.85 kW** total across **18 arrays** (13 plant, 5 township), per
`config/plant.json` and `data/processed/generation_sites.csv` in this repo.

> **Scope note.** This covers the **DC side only** — module interconnection,
> string cable to inverter MPPT inputs, and (if used) array-to-combiner runs.
> AC-side cable, earthing/bonding conductors and LA/earth pits are a separate
> specification.

---

## 0. THE ONE NON-NEGOTIABLE

Solar DC cable sold in India is under a **Quality Control Order**. It must
carry the **ISI mark against IS 17293:2020** under a valid BIS licence.

- Order: *Solar DC Cable and Fire Survival Cable (Quality Control) Order, 2023*,
  DPIIT S.O. 3807(E) dated **24 August 2023**, mandatory from **~24/25 February 2024**.
- Standard: **IS 17293:2020** — *Electric cables for photovoltaic systems for
  rated voltage 1500 V DC*. (Endorsement No. 1 dated 22 May 2025 applies.)
- Non-compliance is a cognizable offence under the BIS Act 2016 — fine from
  ₹2 lakh, imprisonment up to 2 years.

**Practical consequence:** unmarked cable, "EN 50618 only" cable, or imported
cable without an Indian BIS licence is **not legally usable** and will be a
problem at DISCOM inspection. Reject any quote that cannot produce a
**CM/L licence number** you can verify on the BIS portal.

Exemption: goods manufactured in India purely for export. Not applicable here.

---

## 1. Technical specification (tender-ready)

| # | Parameter | Requirement |
|---|---|---|
| 1 | Standard | **IS 17293:2020** with valid BIS licence + ISI mark. IEC 62930 / EN 50618 (H1Z2Z2-K) compliance to be stated additionally |
| 2 | Type designation | H1Z2Z2-K (single core, flexible, PV) |
| 3 | Rated voltage | **1.5 kV DC** (1500 V DC) |
| 4 | Max permitted DC voltage | **1.8 kV DC** |
| 5 | Max permitted AC voltage | 1.0 kV AC |
| 6 | Conductor | Flexible **electrolytic-grade annealed TINNED copper**, fine stranded, **Class 5 to IEC 60228 / IS 8130**. Bare (untinned) copper NOT acceptable |
| 7 | Insulation | **Electron-beam cross-linked polyolefin (XLPO)**, halogen-free, flame retardant. **PVC and XLPE are NOT acceptable** |
| 8 | Outer sheath | **Electron-beam cross-linked polyolefin (XLPO)**, halogen-free, flame retardant, **UV- and ozone-resistant** |
| 9 | Cores | Single core |
| 10 | Colour | **Red = positive, Black = negative.** Sheath black-with-red-stripe acceptable for positive if consistently applied |
| 11 | Ambient / operating temp | **−40 °C to +90 °C** continuous |
| 12 | Max conductor temp | **120 °C for 20,000 h** (thermal endurance to EN 60216-2, temp index +120 °C) |
| 13 | Short-circuit temp | **200 °C min, 5 s** at conductor (250 °C/5 s preferred) |
| 14 | Voltage withstand | **6.5 kV AC and 15 kV DC**, 5 min |
| 15 | Spark test | 6000 V AC (8400 V DC) |
| 16 | Flame retardance | EN 50618 Table 2; single-cable flame test **IEC/EN 60332-1-2** |
| 17 | Smoke | Low smoke, light transmittance **>70 %** per IEC/EN 61034-2 |
| 18 | Halogen-free | Per IEC 60754 / EN 50525-1 Annex B. **Zero halogen required** |
| 19 | UV / weathering | UV resistant, suitable for outdoor exposed installation. Test standard to be declared |
| 20 | Ozone resistance | EN 50396 cl. 8.1.3 Method B |
| 21 | Acid & alkali resistance | EN 60811-2-1 (oxalic acid, sodium hydroxide) |
| 22 | Oil / chemical resistance | EN 60811-2-1 |
| 23 | Ammonia resistance | Required (rooftop / agricultural exposure) |
| 24 | Damp heat & hydrolysis | Required per IS 17293 / EN 50618 |
| 25 | Min bending radius | **6 × OD** fixed installation; **15 × OD** occasional flexing |
| 26 | Elongation | ≥125 % insulation and sheath (EN 60811) |
| 27 | Shrinkage | ≤2 % at 120 °C (EN 60811-1-3) |
| 28 | Design service life | **25 years minimum** outdoor |
| 29 | RoHS / REACH | Compliant |
| 30 | Marking (embossed, every 1 m) | Manufacturer name/brand, **ISI mark + CM/L licence no.**, `IS 17293`, size in mm², `1.5 kV DC`, H1Z2Z2-K, year, sequential metre marking |
| 31 | Packing | Wooden drums 500 m / 1000 m; coils 90 m / 100 m. Both ends sealed, drum legend as cl. 30 |

---

## 2. Sizing

### 2.1 Design rules applied

- **Current:** cable rating ≥ **1.25 × I_sc(module)** per IEC 62548.
- **Voltage:** cable rating ≥ 1.2 × V_oc(array) at minimum site temperature.
  At 1.5 kV DC rating against a ~1000–1100 V system, this is satisfied with
  very large margin — **voltage never drives the size here.**
- **Voltage drop:** target **≤1 %** per string run; **2 % absolute maximum**
  for total DC side. Computed at **70 °C** conductor temperature, not 90 °C —
  see §2.4 for why. **This is what actually drives the size.**
- **Ambient:** Kalol rooftop. Ratings below are quoted at **60 °C ambient**;
  apply the derating factors in §2.3 for cable in conduit/tray on a hot roof.

### 2.2 Current carrying capacity (60 °C ambient, EN 50618 / IS 17293 basis)

| Size | Approx OD | Single cable **in air** | Single cable **on surface** | **2 cables touching** on surface | R max @20 °C | Weight |
|---|---|---|---|---|---|---|
| 1.5 mm² | 4.9 mm | 30 A | 29 A | 24 A | 13.70 Ω/km | 39 kg/km |
| 2.5 mm² | 5.3 mm | 41 A | 39 A | 33 A | 8.21 Ω/km | 51 kg/km |
| **4 mm²** | 5.9 mm | **55 A** | 52 A | 44 A | 5.09 Ω/km | 65 kg/km |
| **6 mm²** | 6.5 mm | **70 A** | 67 A | 57 A | 3.39 Ω/km | 87 kg/km |
| 10 mm² | 7.4 mm | 98 A | 93 A | 79 A | 1.95 Ω/km | 132 kg/km |
| 16 mm² | 8.8 mm | 132 A | 125 A | 107 A | 1.24 Ω/km | 198 kg/km |
| 25 mm² | 10.5 mm | 176 A | 167 A | 142 A | 0.795 Ω/km | 301 kg/km |
| 35 mm² | 12.0 mm | 218 A | 207 A | 176 A | 0.565 Ω/km | 405 kg/km |

Resistances are IEC 60228 Class 5 **tinned** copper maxima. Larger sizes to
185 mm² (and 240 mm² on request) are catalogued.

### 2.3 Ambient derating factors

| Ambient | ≤60 °C | 70 °C | 80 °C | 90 °C |
|---|---|---|---|---|
| Factor | 1.00 | 0.92 | 0.84 | 0.75 |

Use **0.92 or 0.84** for cable in closed conduit or metal tray on an exposed
Ahmedabad roof in May–June. Even so, current is not the binding constraint for
string cable — see §2.4.

### 2.4 Maximum run length for voltage drop — THIS drives the size

**Conductor temperature matters, and 90 °C is the wrong basis here.** At
~13 A in a 55 A-rated cable, I²R heating is only **5.8 %** of rated loss, so
the conductor sits essentially at ambient — not at its 90 °C limit. 90 °C is
correct for *thermal* sizing; for *voltage drop* it overstates resistance by
~7 %. The tables below use **70 °C**, a realistic hot-roof figure for Kalol.

| Temp | R (4 mm²) |
|---|---|
| 20 °C | 5.09 Ω/km |
| 60 °C | 5.89 Ω/km |
| **70 °C (design)** | **6.09 Ω/km** |
| 90 °C (thermal limit) | 6.49 Ω/km |

#### Max one-way run at 70 °C

| Size | ≤1 % | ≤1.5 % | ≤2 % |
|---|---|---|---|
| 2.5 mm² | 27 m | 40 m | 53 m |
| **4 mm²** | **43 m** | **64 m** | **86 m** |
| **6 mm²** | 65 m | 97 m | 129 m |
| 10 mm² | 112 m | 168 m | 224 m |
| 16 mm² | 176 m | 264 m | 353 m |

*(at I_mpp = 13.3 A, V_mpp = 696 V — a modern 16 × 580 Wp string)*

#### The decisive variable is YOUR module current

% drop ∝ (L × I_mpp) / V_mpp. For **4 mm² at 60 m one-way, 70 °C**:

| Module class | I_mpp | Modules/str | V_mpp | Drop @60 m | Verdict |
|---|---|---|---|---|---|
| ~330 Wp poly (M50A-era) | 8.8 A | 22 | 825 V | **0.78 %** | ✅ under 1 % |
| ~330 Wp poly | 8.8 A | 20 | 750 V | **0.86 %** | ✅ under 1 % |
| ~360 Wp mono/poly | 9.3 A | 20 | 760 V | **0.89 %** | ✅ under 1 % |
| ~450 Wp mono | 11.0 A | 20 | 800 V | **1.00 %** | ✅ at 1 % |
| 580 Wp TOPCon | 13.3 A | 18 | 783 V | 1.24 % | ⚠️ under 2 %, over 1 % |
| 580 Wp TOPCon | 13.3 A | 16 | 696 V | 1.40 % | ⚠️ under 2 %, over 1 % |

**Conclusion: 4 mm² at 60 m is sound provided I_mpp ≲ 11 A.** For a plant of
M50A vintage — typically 320–400 Wp modules at 8.8–9.3 A — 60 m of 4 mm²
lands at **0.78–0.89 %**, comfortably inside 1 %. Only high-current modern
modules (13 A+) push past 1 %, and even those stay under 2 %.

Formula to re-run with your actuals:

    ΔV   = 2 × L(m) × I_mpp(A) × R₇₀(Ω/m)      [×2 for go + return]
    R₇₀  = R₂₀ × 1.197                          (4 mm²: 0.00609 Ω/m)
    %drop = ΔV / V_mpp(string) × 100

> **Caveat.** This assumes **individual string runs**, which is what the 4–6
> MPPT replacement inverters give you. If strings are paralleled *before* the
> run — the old M50A combiner architecture — current multiplies and 4 mm²
> fails. Do not apply this to a combined run.

### 2.5 Recommended selection

| Application | Size | Note |
|---|---|---|
| Module-to-module interconnection | 4 mm² | **Factory-fitted leads with MC4** — nothing to buy |
| String cable, run **≤70 m**, I_mpp ≤9.3 A | **4 mm²** | **Default for this plant.** Holds 1 % to 70 m at 8.8 A |
| String cable, run ≤45 m, I_mpp 13 A+ | 4 mm² | Holds 1 % only to ~43 m at 13.3 A |
| String cable, run **60–105 m** | **6 mm²** | Holds 1 % to 105 m at 8.8 A — see §2.5.1 |
| String cable, run >105 m | 10 mm² | Or relocate the inverter — usually cheaper than copper |
| Array JB / combiner → inverter (only if SCB retained) | 16–25 mm² | Size on **combined** string current × 1.25 |

**Standardise on 4 mm² for the bulk of the string-cable BOQ**, with 6 mm²
for identified runs beyond ~70 m (see §2.5.1). Beyond the electrical
case, two practical arguments reinforce it:

1. **Single crimp size.** One MC4 barrel, one die, one spares holding. Mixed
   4/6 mm² invites mis-crimped connectors, which are the single most common
   cause of DC-side hot joints.
2. **Module leads are 4 mm² anyway.** Each module's factory tail is 4 mm², so
   a 6 mm² run is already in series with ~2 m of 4 mm² per module pair. The
   upgrade buys less than the cross-section ratio suggests.

Do not let a supplier push **2.5 mm²** — it holds only 27 m at 1 %.

#### 2.5.1 Long runs (~100 m) — use 6 mm²

Thresholds at **I_mpp 8.8 A, V_mpp 750 V, 70 °C** (i.e. your likely modules):

| Size | Holds ≤1 % to | Holds ≤2 % to |
|---|---|---|
| **4 mm²** | **70 m** | 140 m |
| **6 mm²** | **105 m** | 210 m |
| 10 mm² | 183 m | 365 m |

So **4 mm² is good to ~70 m, not 100 m.** At 100 m one-way:

| Module | 4 mm² | 6 mm² | 10 mm² |
|---|---|---|---|
| ~330 Wp, 20/str (750 V) | 1.43 % | **0.95 %** | 0.55 % |
| ~330 Wp, 22/str (825 V) | 1.30 % | 0.87 % | 0.50 % |
| ~360 Wp, 20/str (760 V) | 1.49 % | **0.99 %** | 0.57 % |
| ~450 Wp, 20/str (800 V) | 1.67 % | 1.12 % | 0.64 % |
| **580 Wp, 16/str — future re-power** | **2.33 % ✗** | 1.55 % | 0.89 % |

Add ~0.11 % for module interconnect leads (~8 m of 4 mm² in series along a
20-module string): 4 mm² at 100 m is effectively **1.54 %**, 6 mm² **1.07 %**.

**Energy alone does not justify the upgrade.** For 3 strings at 100 m
(600 m of cable, 19.8 kWp, 30,690 kWh/yr):

| Upgrade | Drop | Saving | 25-yr NPV | Cost | |
|---|---|---|---|---|---|
| 4 → 6 mm² | 1.43 → 0.95 % | 146 kWh/yr (₹732) | ₹7,819 | ₹13,200 | no payback |
| 4 → 10 mm² | 1.43 → 0.55 % | 271 kWh/yr (₹1,353) | ₹14,442 | ₹39,000 | no payback |

**Specify 6 mm² anyway, for two reasons that are not about today's energy:**

1. **Re-powering headroom — the decisive one.** This cable has a 25-year life;
   modules get replaced at 12–15 years, and 320–400 Wp modules are already
   discontinued. Any replacement will be 550 Wp+ at **13–14 A**, which puts
   4 mm² at 100 m at **2.33 % — outside the 2 % limit**. 6 mm² stays at 1.55 %
   and survives the swap. Re-pulling 600 m through existing conduit in year 13,
   with access and shutdown costs, will far exceed ₹13,200 spent now.
2. **It restores the 1 % budget.** 1.54 % on a string cable consumes most of a
   2 % whole-DC-side allowance, leaving nothing for leads, JBs and ageing.

**Also do this, free:** group the long strings onto **their own MPPT**. If a
100 m string shares an MPPT with a 30 m string, the tracker settles on a
compromise voltage and you lose more than the resistive drop. The 4–6 MPPT
replacement inverters make this cost nothing.

**And check first whether 100 m is unavoidable** — at that distance, moving the
inverter closer, or routing those strings to a nearer inverter, is often cheaper
than any cable size. Lengthening the string (20 → 22 modules) also helps
slightly, but **only after checking V_oc at minimum site temperature** against
the inverter's 1000/1100 V ceiling — 22 × 330 Wp is already near it.

> **Two sizes, handled deliberately.** This does mean a second crimp size
> alongside the 4 mm² bulk. Keep the 6 mm² as a clearly labelled sub-lot for
> the identified long runs only, with its own crimp die, and mark those strings
> on the SLD. That is manageable; mixing sizes at random across the plant is not.

#### Economics check, 50 kW block, 12 runs × 60 m = 720 m

| Module | 4 mm² drop | 6 mm² drop | Loss saved | 25-yr NPV of saving | 6 mm² upgrade cost | Verdict |
|---|---|---|---|---|---|---|
| 8.8 A (older) | 0.86 % | 0.57 % | 0.29 % | ≈₹11,800 | ≈₹15,800 | **4 mm² wins** |
| 13.3 A (modern) | 1.40 % | 0.93 % | 0.47 % | ≈₹19,300 | ≈₹15,800 | 6 mm² marginally pays |

*(1,550 kWh/kW/yr, ₹5/kWh, 8 % discount, ₹22/m premium for 6 mm². Indicative —
re-run with your actual tariff and quoted rates.)*

For older modules the saving does not recover the copper. **Your judgement is
the economically correct one.**

## 3. Impact of the inverter change — read this before fixing quantities

The old **Delta RPI M50A has 2 MPPTs** with 10–12 paralleled string inputs.
Every replacement shortlisted (Delta M50A_260 = 6 MPPT, Sungrow SG50CX = 5,
Solis S5-GC50K = 5, Growatt MID 50KTL3-X2 = 4) accepts only **~2 strings per
MPPT at ~30 A**.

Consequences for this cable order:

1. **Quantity goes UP, not flat.** Strings that were previously combined in an
   array junction box and carried to the inverter on one fat pair will now run
   **individually, full length, to the inverter**. More metres of 4 mm².
2. **You may be able to delete the combiner boxes entirely** — with 4–6 MPPTs
   and direct string termination, SCBs and their 16–25 mm² main runs often
   become unnecessary. That offsets some of the added 4 mm².
3. **Decide the inverter first, then buy cable.** The MPPT count sets the string
   routing, which sets the length. Ordering cable before the inverter is
   selected risks a 20–30 % quantity error either way.

---

## 4. Preferred makes — status against IS 17293

You named KEI, Polycab, Gloster and Universal. Verification result:

| Make | Solar DC range | IS 17293 status | Assessment |
|---|---|---|---|
| **KEI Industries** | Yes — full range 1.5–185 mm² (240 on request). Tinned Cu Class 5, XLPO HFFR, 1.5/1.8 kV DC, −40/+90 °C, 120 °C/20,000 h, 200 °C/5 s, claimed 30-yr life | Public product page cites only **EN 50618 / 2PfG 1169 — does NOT display IS 17293**. Third-party listings do claim IS 17293 | **Technically strongest and best documented.** Its web catalogue predates the QCO — **demand the current CM/L licence in writing** |
| **Polycab** | Yes — electron-beam cross-linked, EN 50618 / H1Z2Z2-K. Commonly stocked 2.5 / 4 / 6 mm² | Trade press reports compliance with IS 17293, IEC 62930, UL 4703, TÜV 2PfG 1169, RoHS, REACH | **Credible. Strong Gujarat availability.** Verify CM/L licence |
| **Gloster Cables** (Secunderabad; plants in Medak, Telangana) | **No confirmed IS 17293 solar range found.** One trade listing shows a "PV" cable at **1000 V with XLPE insulation** | Unconfirmed | **Caution.** 1000 V and XLPE both **fail** this spec (needs 1500 V DC and XLPO). Do not accept against cl. 3/7 without a licence and datasheet |
| **Universal Cables** (Satna, MP) | **No solar PV DC range found.** Catalogue shows PVC/flexible/power cables, capacitors, MV/EHV | Unconfirmed | **Unlikely to be a supplier for this item.** Ask, but do not plan around it |

### Recommendation

- **Enquire to KEI and Polycab as your primary two.** Both are credible, both
  have Gujarat distribution.
- **Keep Gloster and Universal in the enquiry list** but make the ISI/IS 17293
  licence a pass/fail qualification — do not relax the spec to fit them.
- **Add one more BIS-licensed make for competitive tension.** Finolex, RR Kabel
  and Apar all publish IS 17293-marked solar DC cable. Three live quotes beats
  two on a copper-priced commodity.

---

## 5. Documents to demand with the quote

Make these a condition of order, not an afterthought:

1. **BIS licence certificate for IS 17293:2020** with **CM/L number** — and
   verify it yourself on the BIS portal. Non-negotiable.
2. **Type test certificate** from a NABL-accredited lab against IS 17293.
3. **Batch / routine test certificate per drum** — conductor resistance,
   voltage withstand, spark test, dimensions.
4. Manufacturer datasheet confirming every clause in §1.
5. **25-year product warranty** on paper, with the warranty holder named.
6. IEC 62930 / EN 50618 / TÜV 2PfG 1169 certificate (secondary, but a good
   signal of genuine solar-grade compound).
7. RoHS / REACH declaration.
8. Confirmation of **drum/coil metre marking** and sequential length print.

### Inspection on receipt

- Check ISI mark and CM/L number are **physically embossed on the cable**, not
  only printed on the drum label.
- Scratch test: XLPO is tough and rubbery; PVC is glossy and dents easily.
- Measure OD against §2.2 — undersized OD usually means thin insulation.
- Measure conductor resistance on a sample against the §2.2 column. This is the
  single most effective check against under-sized or non-tinned conductor.

---

## 6. Indicative quantity basis

Per **50 kW inverter block** (DC:AC 1.1–1.2, i.e. 55–60 kWp):

| Module | Modules | Strings @16/str | Cable runs (±) | Avg run 25 m | Avg run 40 m |
|---|---|---|---|---|---|
| 540 Wp | ~105 | 6–7 | 12–14 | **300–350 m** | 480–560 m |
| 580 Wp | ~100 | 6–7 | 12–14 | **300–350 m** | 480–560 m |
| 620 Wp | ~95 | 6 | 12 | **300 m** | 480 m |

**Rule of thumb: 7–12 m of 4 mm² per kW of DC capacity** (4 mm² throughout — see §2.5), depending on how far
the array sits from the inverter. Add **10 % wastage** plus allowance for
terminations and dressing loops.

String count comfortably fits every shortlisted inverter (Sungrow and Solis
give 10 string inputs; Growatt has 4 MPPTs — verify its input count against
6–7 strings).

### Candidate M50A locations at Kalol

The arrays large enough to plausibly carry 50 kW-class inverters:

| Array | Capacity | Likely 50 kW units |
|---|---|---|
| NARMADA | 236.0 kW | up to 4 |
| PUMP HOUSE, TRAFFIC & CANTEEN | 229.36 kW | up to 4 |
| BAGGING | 113.4 kW | up to 2 |
| ADMIN CLUSTER | 70.0 kW | 1 |
| MPSS & MCC 13-16 | 70.0 kW | 1 |
| MCC-2 | 60.0 kW | 1 |

**This is inference from array capacity, not an inventory.** Confirm which
arrays actually have M50A units before costing.

---

## 7. What I still need to finalise the BOQ

The specification above is complete and can go out to vendors as-is. Site
capacity and the array breakdown I have taken from this repo. Still needed:

1. **Module I_mpp and modules per string** — the single figure that settles
   the 4 mm² question. If I_mpp ≤ 11 A, 4 mm² at 60 m is confirmed.
2. **Which arrays have M50A inverters, and how many** — the repo gives array
   capacities but not inverter make/model per array.
3. **Module make/model** — specifically **I_sc, I_mpp, V_oc, V_mpp** and Wp.
4. **Total strings** per affected array.
5. **Which replacement inverter you select** (sets MPPT count → string routing).
6. **Longest and shortest string route length**, roof to inverter, following the
   actual tray/conduit path — not straight-line distance.
7. Whether array junction / combiner boxes are retained or deleted.
8. Mounting: conduit, cable tray, or open-clipped (affects §2.3 derating).

Give me items 1–6 and I will produce the sized BOQ with per-string lengths, a
voltage-drop check per string, and a drum-wise ordering schedule.

---

## Sources

- IS 17293:2020 and QCO — DPIIT S.O. 3807(E) 24 Aug 2023; BIS; compliance
  summaries (Aleph India, EVTL India, BL-India, Vincular, worldtradescanner)
- EN 50618 / H1Z2Z2-K rating basis — Lapp (EN 50618 Table A.3), Top Cable
- Current ratings, resistances, dimensions, derating — KEI Industries solar
  cable catalogue page
- Polycab solar DC cable — Polycab product listing; Wire & Cable India
- Gloster Cables — company profile, TradeIndia listing
- Universal Cables — company catalogue listings
- Conductor resistance — IEC 60228 Class 5 tinned copper
- Design rules — IEC 62548 (PV array design)
