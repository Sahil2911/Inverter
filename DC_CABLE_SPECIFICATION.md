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
  for total DC side. This is what actually drives the size.
- **Ambient:** Ahmedabad rooftop. Ratings below are quoted at **60 °C ambient**;
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

Worked for a representative modern string: **16 × 580 Wp** module,
I_mpp = 13.3 A, V_mpp(string) ≈ 696 V. Conductor resistance corrected to
**90 °C** (factor 1.275) — the conservative case. **One-way** route length:

| Size | ≤1 % drop | ≤1.5 % drop | ≤2 % drop |
|---|---|---|---|
| 2.5 mm² | 25 m | 37 m | 50 m |
| **4 mm²** | **40 m** | 60 m | 81 m |
| **6 mm²** | **61 m** | 91 m | 121 m |
| 10 mm² | 105 m | 158 m | 210 m |
| 16 mm² | 165 m | 248 m | 331 m |
| 25 mm² | 258 m | 387 m | 516 m |

Formula to re-run with your actual numbers:

```
ΔV = 2 × L(m) × I_mpp(A) × R₉₀(Ω/m)        [×2 for go + return]
R₉₀ = R₂₀ × 1.275
% drop = ΔV / V_mpp(string) × 100
```

### 2.5 Recommended selection

| Application | Size | Note |
|---|---|---|
| Module-to-module interconnection | 4 mm² | Normally **factory-fitted leads with MC4** — usually nothing to buy |
| String cable, array → inverter MPPT, run ≤40 m | **4 mm²** | Default. 55 A rating vs ~17.5 A design current — huge margin |
| String cable, run 40–60 m | **6 mm²** | Use wherever the run exceeds ~40 m to hold 1 % |
| String cable, run >60 m | 10 mm² | Or relocate the inverter — cheaper than copper |
| Array JB / combiner → inverter (only if SCB used) | 16–25 mm² | Size on combined string current × 1.25 |

**Default the BOQ to 4 mm², with 6 mm² for the long rows.** Do not let a
supplier push 2.5 mm² — it holds only 25 m at 1 %.

---

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

**Rule of thumb: 7–12 m of 4 mm² per kW of DC capacity**, depending on how far
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

1. **Which arrays have M50A inverters, and how many** — the repo gives array
   capacities but not inverter make/model per array.
2. **Module make/model** — specifically **I_sc, I_mpp, V_oc, V_mpp** and Wp.
3. **Modules per string** and **total strings** per affected array.
4. **Which replacement inverter you select** (sets MPPT count → string routing).
5. **Longest and shortest string route length**, roof to inverter, following the
   actual tray/conduit path — not straight-line distance.
6. Whether array junction / combiner boxes are retained or deleted.
7. Mounting: conduit, cable tray, or open-clipped (affects §2.3 derating).

Give me items 1–5 and I will produce the sized BOQ with per-string lengths, a
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
