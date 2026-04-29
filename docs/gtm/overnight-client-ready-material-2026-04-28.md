# Overnight client-ready material — 2026-04-28

> Send-ready GTM blocks distilled from the full candidate-brief workup at
> `docs/gtm/outreach-candidate-briefs-2026-04-28.md`.
>
> **What this file is.** A morning-ready packet of (a) one-paragraph
> capability blurbs by service line, (b) per-demo "what you can / cannot
> claim" capsules, and (c) three send-ready outreach scripts.
>
> **What this file is not.** It is not a substitute for tailoring outreach
> to a specific prospect, and it does NOT mean the lane has authorized
> sending any of these. The control surface (ace-linux-1) drives all
> sends; this file is staged content, not sent content.
>
> **Engineering boundary discipline.** Every block carries an evidence
> envelope: `proof path`, `can-say`, `cannot-claim-yet`. If a sentence
> would be defensible only after a missing artifact ships, it is in
> `cannot-claim-yet` — not in the send block.
>
> **Run window.** ace-linux-1 lane C2 — 2026-04-28 21:49:46 → 2026-04-29
> 09:49:46 local. Author: Claude.

---

## §1 — Capability blurbs by service line (one paragraph each)

Reusable as section copy for outreach emails, expert-network profiles,
LinkedIn DMs, or aceengineer.com service pages. Every blurb is bounded
to *what is shipped*.

### 1.1 Pipeline integrity & freespan/VIV screening

> ACE Engineer screens pipeline freespan / VIV exposure under
> DNV-RP-F105 simplified methodology across hundreds of span
> configurations in a single overnight run. A typical screening pass —
> 480 cases across 3 pipeline sizes, 8 spans, 5 currents, and 4 gap
> ratios — produces a self-contained interactive HTML report with
> screening heatmaps and gap-ratio sensitivity. Screening is a *go /
> no-go pass before CFD VIV time-domain*, not a substitute for it.
>
> *Proof:* `digitalmodel/examples/demos/gtm/output/demo_01_freespan_report.html`
> (118 KB, 680 cases when the rigid jumper branch is included).

### 1.2 Pipeline wall thickness — multi-code comparison

> ACE Engineer compares wall-thickness requirements under DNV-ST-F101,
> API RP 1111, and PD 8010-2 *side-by-side*, with the governing check
> stated per case (propagation, hoop, collapse). A typical sweep covers
> 6 pipe sizes (6″–20″), 4 internal pressures, and 5 lifecycle phases.
> The calc engine is the live `digitalmodel` Python library — not a
> one-off spreadsheet — and every case carries its own auditable
> result.
>
> *Proof:* `digitalmodel/examples/demos/gtm/output/demo_02_wall_thickness_report.html`
> (85 KB, 72 cases) and
> `digitalmodel/examples/demos/gtm/results/demo_02_wall_thickness_results.json`.

### 1.3 Deepwater installation envelopes — mudmat & rigid jumper

> ACE Engineer screens deepwater installation envelopes for mudmats and
> rigid jumpers across CSV class, water depth, structure size, and
> sea-state. Reports cover lift-off, in-air bending, splash-zone
> slamming, lowering, and — for jumpers — the 50 mm tie-in alignment
> phase that drives day-rate bleed. Vessel data is *class-typical* (not
> vessel-specific) until the prospect supplies trusted RAOs.
>
> *Proof:*
> `digitalmodel/examples/demos/gtm/output/demo_03_mudmat_installation_report.html`
> (180 cases) and
> `digitalmodel/examples/demos/gtm/output/demo_05_jumper_installation_report.html`
> (300 cases).

### 1.4 Shallow-water S-lay screening

> ACE Engineer screens shallow-water S-lay barge selection across pipe
> size and water depth before a detailed Orcaflex commitment. Outputs
> include overbend strain, sagbend stress, top tension, and stinger
> departure angle. The catenary mechanics are self-contained — no
> proprietary toolchain required to inspect the calc surface.
>
> *Proof:* `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html`
> (60 cases, 2 barge classes × 5 pipe sizes × 6 water depths).

### 1.5 Marine terminal — berth operability and ship/shore interface

> ACE Engineer screens LNG terminal and FSRU berth concepts for
> operability, mooring/fender load paths, and ship/shore transfer
> envelope at the *concept* and *FEED-readiness* stages. The framing
> draws on a public-source mooring-failure investigation library —
> including the NWS LNG long-period-swell mechanism that broke 3
> mooring lines in 50 mm swell. Scope is screening and decision frame,
> *not* full terminal design, navigation simulation, or QRA.
>
> *Proof:* `docs/gtm/marine-terminal-engineering-scope.md`,
> `knowledge/seeds/mooring-failures-lng-terminals.yaml` (40 entries),
> `knowledge/wikis/marine-engineering/wiki/concepts/lng-marine-terminal-engineering.md`.

### 1.6 FOWT — mooring concept screening and bankability assurance

> ACE Engineer screens floating-wind mooring and installation concepts
> at pre-FEED level using OrcaFlex workflows transferred from deepwater
> oil-and-gas mooring engineering. Scope includes mooring concept
> selection, anchor strategy framing, tow-out / hook-up logic, and
> bankability-oriented technical assurance on engineering maturity and
> escalation triggers. Scope explicitly excludes IEC 61400-3 design
> load case execution, controller co-design, and certification-grade
> coupled aero-hydro-servo-elastic verification.
>
> *Proof:* `docs/gtm/fowt-engineering-scope.md`,
> `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (with
> DNV-OS-E301 citation pilot per
> `.claude/rules/calc-citation-contract.md`),
> `digitalmodel/src/digitalmodel/orcawave/`.

### 1.7 Engineering rigor — citation-bound, multi-AI cross-reviewed

> ACE Engineer ships every standards-derived numeric with a citation
> pointing back to the code clause it came from — fail-closed if the
> wiki page is missing. Plans and methodology are cross-reviewed by
> three independent AI providers (Claude, Gemini, Codex) explicitly
> tuned to surface non-overlapping defects rather than build consensus.
> Engineering enforcement lives in scripts and hooks, not in slides.
>
> *Proof:* `docs/methodology/published/` (4 publication-ready
> methodology docs), `.claude/rules/calc-citation-contract.md`,
> `digitalmodel/src/digitalmodel/citations/schema.py`.

---

## §2 — Per-demo claim envelopes (capsule format)

Compact decision capsules for use in proposal sections and demo cover
emails. The pattern is: 1 line headline, 1 line proof, 1 line "can
say", 1 line "cannot claim yet". Every capsule survives a senior
reviewer's spot-check.

### 2.1 Demo 1 — DNV freespan / VIV screening (680 cases)

| | |
|---|---|
| Headline | "DNV-RP-F105 simplified VIV screening across 480 pipeline + 200 jumper cases overnight." |
| Proof | `output/demo_01_freespan_report.html` (118 KB) + `results/demo_01_freespan_results.json` |
| Can say | 3 pipeline sizes × 8 spans × 5 currents × 4 gap ratios — interactive heatmaps, governing scenario per case. |
| Cannot claim yet | CFD VIV time-domain, RP-F105 detailed fatigue life, suppression-strake design. |

### 2.2 Demo 2 — Wall thickness multi-code (72 cases)

| | |
|---|---|
| Headline | "DNV-ST-F101 vs API RP 1111 vs PD 8010-2 — 72-case comparison, governing check per case." |
| Proof | `output/demo_02_wall_thickness_report.html` (85 KB) + `results/demo_02_wall_thickness_results.json` |
| Can say | 6 sizes × 3 codes × 4 pressures × 5 lifecycle phases, X65 baseline, full-calc via `digitalmodel`. |
| Cannot claim yet | Detailed local-buckling under combined loading, sour-service/ECA integration. |

### 2.3 Demo 3 — Deepwater mudmat installation (180 cases)

| | |
|---|---|
| Headline | "Mudmat installation envelope — 2 CSV classes × 6 depths × 3 pad sizes × 5 Hs, 5 phases per case." |
| Proof | `output/demo_03_mudmat_installation_report.html` (72 KB) + `results/demo_03_mudmat_installation_results.json` |
| Can say | Lift-off / in-air / splash / lowering / landing — vessel-vs-mudmat compatibility matrix. |
| Cannot claim yet | DP capability windows, soil-pad penetration limits, vessel-specific RAOs. |

### 2.4 Demo 4 — Shallow-water S-lay (60 cases)

| | |
|---|---|
| Headline | "Shallow-water S-lay screening — overbend, sagbend, tension, stinger angle in one HTML." |
| Proof | `output/demo_04_shallow_pipelay_report.html` (85 KB) + `results/demo_04_shallow_pipelay_results.json` |
| Can say | 2 barge classes × 5 pipe sizes × 6 water depths, self-contained catenary mechanics. |
| Cannot claim yet | Full Orcaflex dynamic time-domain, drop / abandonment-and-recovery, irregular bathymetry. |

### 2.5 Demo 5 — Deepwater rigid jumper installation (300 cases)

| | |
|---|---|
| Headline | "Rigid-jumper envelope — 50 mm tie-in alignment phase included, 300 cases." |
| Proof | `output/demo_05_jumper_installation_report.html` (66 KB) + `results/demo_05_jumper_installation_results.json` |
| Can say | 2 vessels × 6 depths × 5 jumper lengths × 5 Hs — five phases per case. |
| Cannot claim yet | Detailed clamp / connector engineering, flexible-jumper analogues, vessel-specific DP at landing. |

---

## §3 — Send-ready outreach scripts

Three short, prospect-tier-aware messages. Each is **send-ready
content** — the *send authorization* still rests with the user / control
surface.

### 3.1 Pipeline integrity manager — Demo 1 + Demo 2

```
Subject: Overnight DNV freespan + multi-code wall thickness — 752 cases combined

Hi [first name],

Two screening reports your team can spot-check:

  - 480-case DNV-RP-F105 freespan / VIV screening across 3 pipeline
    sizes and 8 spans / 5 currents / 4 gap ratios.
  - 72-case multi-code wall thickness comparison across DNV-ST-F101,
    API RP 1111, and PD 8010-2 — X65 baseline, governing check per case.

Both reports are self-contained interactive HTML. Screening only — not
a substitute for CFD VIV time-domain or detailed local-buckling under
combined loading.

If you would like the case set rerun against your portfolio's specific
ODs, pressures, or current profile, send a YAML intake (template in the
attached zip) and I will return the report by EOD Friday.

Vamsee Achanta — Licensed P.E. — aceengineer.com

Evidence boundary: report is a screening pass; project work needs a
separate scoped engagement with vessel-specific or site-specific data.
```

**Attach.** `demo_01_freespan_report.html`, `demo_02_wall_thickness_report.html`,
`docs/gtm/intake/prospect-template.yaml`. **Do not** attach raw JSON
results unless the prospect asks; the HTML is the buyer artifact.

### 3.2 Heavy-lift CSV / installation contractor — Demo 3 + Demo 5

```
Subject: 480 deepwater installation cases overnight — mudmat + jumper envelopes

Hi [first name],

Two artifact-grounded conversation starters for your vessel
operations team:

  - 180-case deepwater mudmat installation screening — 2 CSV classes
    × 6 water depths × 3 pad sizes × 5 Hs, with vessel-vs-mudmat
    compatibility matrix.
  - 300-case rigid-jumper installation screening — including the 50 mm
    tie-in alignment phase, which is where the day-rate bleed
    typically lands.

Vessel data is class-typical (Seven Borealis-style + medium CSV) — not
vessel-specific until you send the RAOs you trust.

If your portfolio has a candidate field where pad size, jumper length,
or vessel class is still under debate, I can run your specific case
matrix overnight and we can compare against your in-house Orcaflex
baseline.

Vamsee Achanta — Licensed P.E. — aceengineer.com

Evidence boundary: screening only — final installation engineering
still requires a project-specific Orcaflex run with vessel-specific RAOs.
```

**Attach.** `demo_03_mudmat_installation_report.html`,
`demo_05_jumper_installation_report.html`, capability summary PDF.

### 3.3 LNG terminal / FSRU operations lead — berth operability framing

```
Subject: Berth operability framing — long-period swell screening before nav-sim

Hi [first name],

One framing artifact worth 5 minutes — a public-source synthesis of
the NWS LNG mooring-line failure programme, including the 2014
investigation that found 3 lines parted in 50 mm long-period swell
through resonant vessel motion.

If your concept is being defended at a gate before a full
navigation-simulation campaign, the long-period-swell mechanism is the
highest-leverage thing to flag early. I can send a 2-page decision
frame against the public knowledge corpus we maintain (no client data
required for the framing pass).

Scope is screening and decision frame — full berth design, navigation
simulation, and QRA remain out of this near-term scope. The framing
pass is a credibility-anchored conversation starter, not a deliverable.

Vamsee Achanta — Licensed P.E. — aceengineer.com
```

**Attach.** Berth-operability framing 2-pager (NOT YET BUILT — see
candidate 6 missing-proof entry; do not send this snippet until that
2-pager exists).

---

## §4 — Pre-send check (must pass for every snippet)

Before any block in §3 leaves ACE's outbox, the sender confirms each
line below. Failures are *blockers* — bounce back to the lane.

1. **Proof path exists.** Every artifact named in the email is at the
   path listed and opens correctly in a fresh browser session.
2. **Class-typical disclaimer present.** If the report references vessel
   data, the canonical-vessel disclaimer block must be visible (the
   report template already does this).
3. **No project-confidential data.** No mention of client-named ACMA
   projects (Woodfibre, SESA, etc.). The Elements-wave outputs are
   `metadata-only` and gated by ACMA / project-owner clearance — see
   `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/`.
4. **Evidence boundary line present.** Every email ends with a one-line
   "Evidence boundary:" disclaimer naming what the artifact does NOT
   prove. This is the line that survives a senior-engineer pushback.
5. **Cannot-claim-yet items absent.** Cross-check the email against
   each candidate's `cannot-claim-yet` list in
   `outreach-candidate-briefs-2026-04-28.md` — if any cannot-claim-yet
   item appears in the body without a hedge, edit it out before sending.

---

## §5 — Material gaps (what is missing to extend coverage)

| Gap | Unblocks | Lift size | Issue |
|---|---|---|---|
| First DELIVERED row in `docs/gtm/deliveries-log.md` | Promotes Candidate 9 (#2346) from "pipeline narrative" to lead outreach asset; adds a public proof of the 48-hour SOP working end-to-end. | Small — needs `materialize_demo_inputs` + `run_demo` + branded report wrapper for one path | #2346 (status:plan-approved + status:working) |
| 4 methodology docs live on aceengineer.com | Lifts Candidate 8 from "PDF attachments" to "linked authoritative URL" — strongest lever for engineering-manager outreach | Small — content exists; deploy step is the gate | #2030 (publish methodology docs) |
| Public-source berth-operability decision frame 2-pager | Unblocks Candidate 6 outreach (Snippet 3.3 cannot ship without this) | Medium — synthesis of `mooring-failures-lng-terminals.yaml` (40 entries) into a 2-page POV piece, no client data | New issue (proposed in Candidate 6) |
| OC4-DeepCwind FOWT mooring screening worked example | Unblocks Candidate 7 outreach for floating-wind bankability reviewers | Medium — public-source semi-sub geometry, single OrcaFlex screening run, 1-pager output | New issue (proposed in Candidate 7) |
| Demo 5 detail page on aceengineer-website | Strengthens Demo 5 link-rather-than-attach pattern | Small | #2422 (extending capability-summary CTA to 5 demo detail pages) |
| Screencast GIFs for demos | Shortens prospect eval from "I'll click later" to "I get it in 30 s" | Medium — manim / mp4 → gif pipeline, 5 screens | #1809 (open) |
| Wired GTM unified smoke runner | Prevents silent demo rot before next outreach push | Small | #2345 (open) |

---

## §6 — Evidence boundary one-liner library

Reusable end-of-email lines, ranked by force. Copy whichever matches
the artifact in the body.

1. *"Evidence boundary: this is a screening pass — final engineering
   work needs project-specific data and a separate scoped engagement."*
2. *"Evidence boundary: vessel data is class-typical and not
   vessel-specific until you send RAOs you trust."*
3. *"Evidence boundary: this is a framing artifact built from
   public-source material — no client data required, no client data
   used, and no project-specific deliverable claimed."*
4. *"Evidence boundary: this report covers screening only — detailed
   buckling / fatigue / DP / soil-pad / certification scope all sit
   outside this run, and would be flagged in any follow-on proposal."*
5. *"Evidence boundary: methodology docs describe how the engineering
   pipeline works; they do not, by themselves, deliver a project."*

---

---

## §7 — Pass-2 defects discovered (must-fix-before-send)

While validating the case-count claims in §1 against the shipped reports,
the lane discovered three engineering-evidence drifts in *existing* GTM
files. Each is a `must-fix-before-send` item. Full detail in
`docs/gtm/outreach-candidate-briefs-2026-04-28.md` §3.

| ID | File | Severity | Blocks |
|---|---|---|---|
| D1 | `docs/gtm/expert-network-profiles.md` (bio overstates 2 of 5 demos: claims "mooring system sensitivity" + "cathodic protection sizing" — neither exists in the demo suite) | **HIGH** | Tier-A3 expert-network profile refresh — do not paste this bio into GLG / AlphaSights / Guidepoint until corrected |
| D2 | `docs/gtm/linkedin-content-calendar.md` Week 1 Post 1 ("Under 2 seconds" runtime claim, no validating artifact) | Medium | LinkedIn Week-1 Monday post |
| D3 | `docs/gtm/website-pages/capability-summary.html` (relative font path `../../../aceengineer-website/assets/fonts/inter/...` breaks when sent as standalone HTML attachment) | Low | Standalone HTML attach pattern; non-blocking via PDF version |
| D4 | Demo 1 status semantics — pass rate combines `PASS + INLINE_ONLY`, not unconditional pass | Low | Snippet A (3.1) — tightens evidence-boundary line; correction in briefs §3 |

D1 is the highest-leverage fix in the morning queue. The corrected bio
text is provided as a drop-in in the briefs file §3.D1.

---

*End of overnight client-ready material — 2026-04-28.*
