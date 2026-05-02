---
title: Matrix narrative edits (Adv-C F1 §3b remediation)
date: 2026-05-01
parent: vessel-contractor-matrix-2026-05-01.md
status: ready-for-merge
---

# Matrix Narrative Edits — Adv-C F1 §3b Remediation

This file resolves the two narrative-edit follow-ups left open by the URL-repair
pass (commit `83e8b46b1`, see
[`vessel-contractor-matrix-url-repairs-2026-05-01.md`](vessel-contractor-matrix-url-repairs-2026-05-01.md))
on the 2026-05-01 vessel-contractor matrix:

1. Row 14 — Bourbon / Gulf Offshore conflation
2. Row 17 — Otto Candies "Kelly Ann Candies" replacement (vessel sold to Aqueos)

Public-source evidence only. No PII; no project-confidential data. Main session
will merge.

---

## §1 — Row 14 decision: DROP "Gulf Offshore" reference; retitle to Bourbon Offshore only

### Recommendation

**DROP "Gulf Offshore" — retitle Row 14 to "Bourbon Offshore (post-SPP)".** Do
NOT split into 14a/14b. Reasoning below.

### Gulf Offshore status: ABSORBED into Tidewater (Row 18) since 2018

"Gulf Offshore" is **not a current standalone GTM target**. The historical
brand traces to two threads, both of which collapse into companies the matrix
already covers:

- **Gulf Offshore Norge AS / Gulf Offshore North Sea Ltd** were subsidiaries of
  **GulfMark Offshore Inc.** (originally Sea Truck, renamed Gulf Offshore Norge
  after the 2001 GulfMark $60M acquisition). GulfMark itself was merged into
  **Tidewater Inc. on 2018-11-15** in a $1.25B all-stock combination. The
  combined entity operates under the Tidewater brand only — there is no
  current "Gulf Offshore" corporate web presence, and the combined PSV/AHTS
  fleet (~375 vessels post-merger) is already represented as **Row 18
  (Tidewater Inc.)** in the matrix.
- The "Bourbon-related historical brand" parenthetical that landed in the
  matrix narrative was a documentation error introduced upstream; Bourbon
  Offshore (French operator, Marseille-headquartered) and Gulf Offshore
  (UK / Norway / GulfMark legacy) were never the same entity.

Sources:
- [Tidewater Completes Combination with GulfMark Offshore (gCaptain)](https://gcaptain.com/tidewater-completes-combination-with-gulfmark-offshore/)
- [Tidewater And GulfMark To Combine (Tidewater IR)](https://investor.tdw.com/news/news-details/2018/Tidewater-And-GulfMark-To-Combine-To-Create-Global-Offshore-Leader/default.aspx)
- [Gulf Offshore Norge AS (energy-oil-gas.com)](https://energy-oil-gas.com/news/gulf-offshore-norge-as/)
- [Tidewater Marine Fleet (current corporate)](https://www.tdw.com/services-fleet/tidewater-marine/fleet/)

### Why DROP rather than SPLIT

A 14b "Gulf Offshore" row would either:

1. Resolve to **Tidewater** — which is already Row 18, creating an in-matrix
   duplicate counting against the unique-prospect total (now 26).
2. Resolve to **a different small entity** (e.g. Gulf Offshore LLC, Gulf
   Offshore Logistics, Gulf Offshore Rentals — none of which are subsea
   construction vessel operators; they are crew, rental, and logistics
   businesses unrelated to the GTM thesis).

Neither candidate produces a credible standalone GTM target for the
demo→buyer mapping. DROP is the correct narrative repair.

### Replacement Row 14 — Bourbon Offshore (post-SPP)

Drop-in row, replacing the existing Row 14 in the matrix table:

```
| 14 | Bourbon Offshore (post-SPP) | OSV / subsea / IMR (PSV / AHTS / MPSV) | 3 | global (WAfrica, Mediterranean, Asia-Pacific, North Sea) | Bourbon Evolution 800 series, Bourbon Trieste, Bourbon Enterprise — MPSVs for subsea construction and IMR; PSV / AHTS legs cover marine-logistics | Quick-turn wall-thickness screening for tieback projects (D2); subsea installation operability windows on smaller MPSVs (D3) | https://www.bourbonoffshore.com/en (deep MPSV link: https://www.bourbonoffshore.com/en/services/subsea/our-fleet/MPSV — 200) | company researched only | P3 | subsea-installation, IMR |
```

**Evidence verified.** Corporate root `https://www.bourbonoffshore.com/en`
returns HTTP 200 (Drupal 10, X-Drupal-Cache HIT). Deep-link
`/en/services/subsea/our-fleet/MPSV` returns 200 and lists Bourbon Evolution
800 series (4,860 t DWT), Bourbon Trieste (3,210 t DWT), Bourbon Enterprise
(1,862 t DWT), and Bahtera Azalea (1,823 t DWT). Bourbon was acquired by
Société Phocéenne de Participations (SPP) on 2020-01-10; the homepage cites
"4,600 employees / 159 vessels / 32 countries" as of 2025-12-31.

**Tier rationale.** P3 (not P2) because Bourbon's subsea fleet is
mid-tier MPSV (Evolution 800 / Trieste class), not heavy-construction. PSV /
AHTS line items overlap with Tidewater (Row 18) and DOF (Row 7); the demo-fit
density is lower than Tier-1 / Tier-2 contractors. Niche-fit is "subsea
installation, IMR" — D2 / D3 are the natural demo-mapping landings.

### §3 evidence-quality table edit (auxiliary)

The existing §3 row reading "14 | Gulf Offshore | Bourbon corporate fleet
page used as proxy; 'Gulf Offshore' historic brand link uncertain
post-Bourbon restructuring (2019 admin) | Verify current operating entity
and fleet listing before sending; consider re-classing to 'Bourbon' or
dropping if entity is dormant" should be **deleted** — the disambiguation is
now resolved by the row retitle.

The §3b table row for Row 14 ("Bourbon / Gulf Offshore") should be
**marked RESOLVED** with a back-reference to this file.

The §4 "Changed (re-classified)" bullet
("Bourbon/Gulf Offshore in templates.md → flagged as evidence-weak pending
entity verification (§3)") should be updated to:
"Bourbon/Gulf Offshore in templates.md → split: Bourbon retained as Row 14
(retitled 'Bourbon Offshore (post-SPP)'); 'Gulf Offshore' reference dropped
(legacy GulfMark brand absorbed into Tidewater Row 18 since 2018-11-15)."

---

## §2 — Row 17 vessel substitution: M/V Sub-Sea Candies replaces Kelly Ann Candies

### Recommendation

**Replace "Kelly Ann Candies" with "M/V Sub-Sea Candies"** in Row 17's
Vessel/Fleet Angle column. Pair it with the already-confirmed Ross Candies for
a strong two-vessel matrix narrative. No row deletion needed.

### Why Sub-Sea Candies is the best fit

The matrix's stated outreach fit for Otto Candies is "subsea installation
support, light construction, GoM IMR / DSV work." Sub-Sea Candies (formerly
Harvey Sub-Sea, acquired by Otto Candies from Harvey Gulf in the 4-vessel
2024 MPSV deal) is the textbook match:

| Spec | Sub-Sea Candies | Why it matches matrix fit |
|---|---|---|
| Class | DP2 MPSV | "GoM IMR / DSV" requires DP2 minimum |
| Length × Beam | 340' × 73' | Larger than Ross Candies (309'); supports "light construction" |
| Crane | 250-MT AHC knuckle-boom, 4,000m wire, below-deck winch (107 mt at 12,000 ft) | Direct match to "subsea installation support" — comparable to Cal Dive Q4000-class for jumper / mudmat work |
| Moon pool | 24' × 24' | DSV-class; ROV deployment evidence |
| Berths | 150 (1- or 2-person) | "Light construction" campaign-grade accommodation |
| Deck space | 13,000 sq ft | Comparable to Hornbeck HOS Achiever class |
| Designation per operator marketing | "subsea operations / IMR / light construction" | Exact wording match to matrix outreach fit |
| Flag / region | US-flag, Jones-Act compliant, GoM-primary | "GoM IMR / DSV" requirement |
| Build | Eastern Shipbuilding 2014 | Modern fleet entry; not a legacy vessel |

Compared to alternatives:

- **Blue-Sea Candies** is the sister vessel (also 340' DP2 MPSV from the
  same Harvey Gulf acquisition). Equally valid, but Sub-Sea is the
  lead-cited vessel in operator marketing and shipping-press coverage.
- **Cade Candies** appears twice in the fleet listing (IMR and SOV). The
  SOV-classified version was historically chartered to Oceaneering for IMR
  and survey work, but the operator now markets it primarily as a
  Service-Operation Vessel — wind-farm-shaped, not "GoM subsea installation
  support" shaped. Less precise fit than Sub-Sea.
- **Intervention Candies** is a 300' DP2 IRM-survey-light-construction
  vessel rated to 3,000m water depth. Strong fit, but smaller than Sub-Sea
  and lower-profile in marketing copy.

### New evidence URL

**Per-vessel deep link:** `https://ottocandies.com/fleets/m-v-sub-sea-imr/`
(HTTP 200; Apache+nginx, x-nginx-cache: WordPress).

**Corporate fleet roster (already in matrix):**
`https://ottocandies.com/fleets/` — HTTP 200; lists all 21 current vessels.

Both URLs are public, evidence-grade, and resolve cleanly.

### Suggested narrative-column edit

Old Row 17 Vessel/Fleet Angle column text:

> Ross Candies, Kelly Ann Candies — MPSV / subsea-support fleet with crane capability for GoM intervention

New Row 17 Vessel/Fleet Angle column text:

> Ross Candies (309' DP2, 150-MT crane, 25'x23' moonpool), Sub-Sea Candies (340' DP2, 250-MT AHC crane, 24'x24' moonpool) — MPSV / subsea-support fleet with crane capability for GoM intervention

(Note: Kelly Ann Candies was sold to Aqueos Corp in early 2026 and is no
longer in the Otto Candies fleet listing; replacement evidence-grounded.)

### Optional §3 evidence-quality entry

Add a Row 17 entry to §3 documenting the freshness consideration:

| 17 | Otto Candies | Ross Candies + Sub-Sea Candies are current as of 2026-05-01; Kelly Ann Candies removed (sold to Aqueos in early 2026) | Re-verify fleet listing before each outreach quarter — 4-vessel Harvey Gulf acquisition (2024) and Kelly Ann divestiture (2026) indicate active fleet churn |

Sources for Row 17:
- [Otto Candies fleet page](https://ottocandies.com/fleets/)
- [Otto Candies expands fleet with four MPSVs from Harvey Gulf (gCaptain)](https://gcaptain.com/otto-candies-expands-fleet-with-four-multi-purpose-support-vessels-from-harvey-gulf/)
- [Aqueos boosts fleet with Otto Candies DSV (Offshore Energy)](https://www.offshore-energy.biz/aqueos-boosts-fleet-with-otto-candies-dsv/)
- [DSV Kelly Ann Candies spec sheet (Aqueos, post-acquisition owner)](https://aqueossubsea.com/wp-content/uploads/2024/10/DSV-Kelly-Ann-Candies.pdf)
- [Helix Robotics Ross Candies LTR (helixesg.com)](https://www.helixesg.com/downloads/Helix_Robotics_-_Ross_Candies_LTR_01-16-2020-FINAL.pdf)

---

## §3 — Cross-check questions — RESOLVED 2026-05-01

All four business-judgment questions answered by human reviewer 2026-05-01.
Decisions logged below for the audit trail.

1. **Bourbon priority** → ✅ **KEEP at P3.** Decision rationale: Bourbon's
   WAfrica + Mediterranean geographic spread is differentiated from
   Tidewater's GoM-heavy footprint; P3 is already the lowest priority
   so dropping doesn't free outreach capacity, just reduces optionality.
   Status: no matrix change needed (Row 14 already P3 post-retitle).

2. **Aqueos as a new prospect** → ⏸ **DEFER to next quarterly refresh.**
   Decision rationale: matrix is past acceptance threshold at 26 rows;
   spot-adding a 27th row mid-cycle would burn ~30 min of research with
   no clear gating event. Aqueos will resurface in the next quarterly
   matrix recheck (per `sanity-review-log.md` cadence) if their fleet /
   strategy still warrants. Status: no matrix change.

3. **Otto Candies tier review** → ✅ **MOVE from P2 to P1.** Decision
   rationale: the Harvey Gulf 4-MPSV acquisition (2024) materially changed
   Otto's positioning — Sub-Sea Candies (340' DP2, 250-MT AHC crane) is
   peer to Hornbeck's HOS-Achiever class. P2 reflected pre-acquisition
   state; P1 reflects current. Otto Candies now joins the GoM P1 block
   (Hornbeck + Edison Chouest + Otto Candies) per #2562. Status: ✅ MERGED
   — Row 17 priority column updated to P1; §1 Tier 1 Priority Sequence
   gains item 9 with rationale.

4. **Helix charter reference** → ✅ **KEEP INTERNAL — do not cite in
   outreach.** Decision rationale: cold outbound to Otto Candies is aimed
   at Otto's business-development surface, not at Helix or Helix-adjacent
   buyers. Citing Helix's historical Ross Candies charter would be useful
   in outreach if we were pitching Helix on Otto Candies — different
   audience. The Helix LTR stays in matrix sources for our internal
   context only. Status: no outreach copy change; no matrix change.

**Net matrix changes from this resolution pass:** 1 row priority shift
(Row 17 P2→P1) + 1 §1 priority-sequence row added (item 9 Otto Candies).
Prospect count remains 26.

---

*End of narrative-edit report. Merge plan: main session updates Row 14
(retitle + URL + body), Row 17 (vessel-name replacement in narrative
column), §3 (delete one row, add one row), §3b (mark RESOLVED), §4
(re-classification bullet edit). No new rows; total prospect count remains
26.*
