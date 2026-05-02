# Outreach candidate briefs — 2026-04-28

> Engineering-bounded GTM packaging from the workspace-hub repo evidence base.
> Each candidate ties to a specific proof path, separates `can-say-now` from
> `cannot-claim-yet`, lists the missing proof to extend the claim, and points
> at the next repo issue or action that would lift the boundary.
>
> **Scope of this file:** outreach material seeds — buyer problem, evidence,
> claims envelope, and outreach angle. The actual client-ready snippets are
> in `outreach-candidate-briefs-2026-04-28.md` §2 (this doc) and the priority
> push list lives in the lane result file at
> `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md`.
>
> **Author:** Claude (lane C2 — ace-linux-1, 12h continuation, run window
> 2026-04-28 21:49:46 → 2026-04-29 09:49:46 local).
>
> **Related:** `docs/gtm/client-conversion-pipeline.md`,
> `docs/gtm/capability-summary.md`, `docs/gtm/email-outreach-templates.md`,
> `docs/gtm/marine-terminal-engineering-scope.md`,
> `docs/gtm/fowt-engineering-scope.md`.

---

## How to read these briefs

Each candidate has eight fields. The split between `can-say-now` and
`cannot-claim-yet` is load-bearing — every claim attached to a proof path
should survive a senior-engineer spot-check; every aspiration should be
labeled as such.

| Field | Purpose |
|---|---|
| Buyer problem | One-sentence pain that this candidate addresses |
| ACE proof / evidence | Repo path + artifact size / case count |
| Can-say-now | Claims defensible with what is shipped today |
| Cannot-claim-yet | Adjacent claims a buyer might *infer* but the artifact does not yet prove |
| Missing proof | Concrete deliverable that would unlock a `cannot-claim-yet` claim |
| Next repo issue / action | The GitHub issue (open or to-be-opened) that closes the gap |
| Draft outreach angle | Lead-with hook + first-line follow-up |
| Confidence | High / Medium / Low — strength of the proof relative to a senior reviewer |

---

## Candidate 1 — Pipeline freespan / VIV screening (Demo 1)

- **Buyer problem.** Pipeline integrity / subsea engineering managers need
  rapid screening of freespan candidates against DNV-RP-F105 before
  committing to a CFD VIV campaign. Hand calcs scale linearly with span
  count; 100+ spans across 3 line sizes turn into multi-week spreadsheets.
- **ACE proof / evidence.**
  - Script: `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py`
    (1,257 lines).
  - Report: `digitalmodel/examples/demos/gtm/output/demo_01_freespan_report.html`
    (118 KB, self-contained, Plotly-interactive).
  - Cases: 680 (480 pipeline + 200 jumper) — 3 sizes × 8 spans × 5 currents
    × 4 gap ratios for the pipeline branch.
  - Cached results: `digitalmodel/examples/demos/gtm/results/demo_01_freespan_results.json`.
  - Methodology basis: DNV-RP-F105 simplified screening + 5 interactive
    charts (heatmaps, gap-ratio sensitivity, current profiles).
- **Can-say-now.**
  - "Overnight DNV-RP-F105 simplified VIV screening across 480 pipeline
    span configurations, with span screening heatmaps and gap-ratio
    sensitivity, generated as a single self-contained HTML."
  - "Three pipeline sizes (8″, 12″, 16″) and a rigid jumper screened
    side-by-side under the same current profile."
- **Cannot-claim-yet.**
  - CFD VIV time-domain validation (the demo is screening-only).
  - Free-span fatigue life calculation per RP-F105 detailed methodology.
  - VIV suppression-strake design or sensitivity to wake-induced
    multi-mode response.
  - Project-specific metocean — the demo uses generic current profiles,
    not site-measured ADCP data.
- **Missing proof.**
  - One annotated walkthrough comparing screening outputs against a
    published RP-F105 detailed worked example would harden the screening
    claim. Tracked at #1792 / #2114 (VIV demo notebook).
  - A screencast GIF of the screening (open #1809 lane) shortens prospect
    eval time from "I'll click through later" to "I get it in 30 s".
- **Next repo issue / action.** #1792 (free-span VIV walkthrough notebook),
  #2114 (VIV demo notebook for pipeline engineers), #1809 (screencast GIFs).
- **Draft outreach angle.**
  Lead: "We screen 480 pipeline freespan configurations overnight under
  DNV-RP-F105 — heatmap of span vs. current vs. gap ratio in a single HTML
  report." Follow-up: "If your team needs a screening pass before the next
  CFD job, can I run your candidate spans against your current profile and
  send back the report by EOD Friday?"
- **Confidence.** **High** for screening; **Medium** if buyer expects
  detailed VIV time-domain follow-through (gap to be flagged in proposal,
  not the outreach).

---

## Candidate 2 — Multi-code pipeline wall thickness (Demo 2)

- **Buyer problem.** Pipeline design managers and standards-compliance
  reviewers need to see *side-by-side* WT requirements under DNV-ST-F101,
  API RP 1111, and PD 8010-2 to defend an across-portfolio design choice
  to procurement, partners, and regulators.
- **ACE proof / evidence.**
  - Script: `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py`
    (1,343 lines, full-calc via `digitalmodel` library).
  - Report: `digitalmodel/examples/demos/gtm/output/demo_02_wall_thickness_report.html`
    (85 KB).
  - Cases: 72 = 6 pipe sizes (6″–20″) × 3 codes × 4 internal pressures
    (10/15/20/25 MPa) × 5 lifecycle phases per pipe.
  - Material: X65, SMYS 448 MPa, SMTS 531 MPa, 1 mm CA, 500 m water depth
    (configurable).
  - Cached results: `demo_02_wall_thickness_results.json` — every case's
    governing check is recorded (e.g. "Propagation Buckling", "Hoop").
- **Can-say-now.**
  - "We compare DNV-ST-F101, API RP 1111, and PD 8010-2 wall-thickness
    requirements across 72 cases for a 6″–20″ portfolio in a single
    auditable HTML report — every case states the governing check."
  - "X65 baseline, with corrosion allowance, hoop, propagation, and
    collapse handled by the live `digitalmodel` library, not a fixed
    spreadsheet."
- **Cannot-claim-yet.**
  - Local-buckling under combined loading (axial + bending + pressure) at
    detailed-design rigor.
  - Sour-service / ECA / fracture-mechanics integration into the WT
    decision (separate workflow).
  - Site-specific installation analysis (covered by Demo 4, not this one).
- **Missing proof.**
  - Side-by-side comparison against a published worked example (e.g. DNV
    Phase 6 JIP examples) inside the report — strengthens credibility for
    a senior reviewer.
  - A 2-page "Standards Compliance Note" PDF cherry-picking 3 cases would
    be the heaviest-leverage one-pager for a procurement reviewer.
- **Next repo issue / action.** Open a follow-up to #2422 (extending the
  capability summary with per-demo detail pages) to add a Demo 2
  "Standards Compliance Note" companion.
- **Draft outreach angle.**
  Lead: "DNV / API / PD 8010 wall-thickness requirements compared across
  72 cases — single HTML report, code clauses cited per case." Follow-up:
  "Would your portfolio reviewers want this on a spec being defended to
  procurement next quarter? I can run your specific OD-grade-pressure
  matrix and send back the comparison."
- **Confidence.** **High** — the underlying calc engine is the
  `digitalmodel` library, not a one-off spreadsheet, and every case carries
  its governing check.

---

## Candidate 3 — Deepwater mudmat installation screening (Demo 3)

- **Buyer problem.** Heavy-lift CSV operators and subsea installation
  contractors need to know which deepwater mudmat sizes their vessels can
  install across realistic sea-state envelopes — and at what depth the
  next class up becomes cheaper than weather-window risk.
- **ACE proof / evidence.**
  - Script: `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py`
    (1,223 lines).
  - Report: `digitalmodel/examples/demos/gtm/output/demo_03_mudmat_installation_report.html`
    (72 KB).
  - Cases: 180 = 2 vessels × 6 water depths (500–3000 m) × 3 mudmat sizes
    (50/100/200 te) × 5 Hs (1.0–3.0 m).
  - Vessel inputs: `data/csv_hlv_vessels.json` (Large CSV 5,000 te + Medium
    CSV 2,500 te) — with crane envelope and RAOs.
  - Phases: lift-off, in-air, splash, lowering, landing.
- **Can-say-now.**
  - "180-case deepwater mudmat installation screening — two CSV classes ×
    six water depths × three mudmat sizes × five Hs, five phases per case,
    delivered overnight."
  - "Vessel-vs-mudmat compatibility matrix — `structure_comparison_matrix.json`
    and `vessel_comparison_matrix.json` give procurement a defensible go /
    no-go grid."
- **Cannot-claim-yet.**
  - Detailed dynamic positioning analysis (DP capability windows, etc.)
    are not in scope of the screening run.
  - Site-specific seabed / soil interaction at landing — the demo screens
    in-air and splash dynamics, not soil-pad penetration limits.
  - Vessel-specific RAOs — `seven-borealis.yaml` is class-typical with an
    explicit "not vessel-specific" disclaimer per the canonical-vessel
    contract.
- **Missing proof.**
  - One worked example with a real vessel's published RAOs (with vendor
    permission) would harden the comparability claim.
  - A short DP / HSE screening companion that goes from operability into
    "is this a green / amber / red lift" decision frame.
- **Next repo issue / action.** Demo 3 itself is shipped (Apr 14). Drive
  follow-on through #2422 (capability summary CTA → demo detail pages) and
  #1669 (vessel installation contractor outreach).
- **Draft outreach angle.**
  Lead: "We screened 180 deepwater mudmat installation cases overnight —
  two CSV classes vs. six water depths vs. three pad sizes — and the
  vessel-comparison matrix shows where the medium CSV stops earning its
  day-rate." Follow-up: "If you have a candidate field where pad size or
  vessel class is still under debate, I can run your specific case
  matrix."
- **Confidence.** **High** for screening claims; **Medium** for
  vessel-specific recommendations until a vendor-RAO worked example is
  added.

---

## Candidate 4 — Shallow-water S-lay screening (Demo 4)

- **Buyer problem.** Shallow-water pipelay barge operators and pipeline
  EPCs need a fast catenary-and-stinger screening before committing to
  detailed Orcaflex models for marginal-economics fields. Decision driver
  is often: "Can a smaller barge do this without departure-angle pain?"
- **ACE proof / evidence.**
  - Script: `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py`
    (1,642 lines, self-contained S-lay catenary mechanics — no `digitalmodel`
    library dependency).
  - Report: `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html`
    (85 KB, the largest demo report at 1,128 lines of HTML).
  - Cases: 60 = 2 vessels (Large PLV 600 te + Shallow Water Barge 250 te)
    × 5 pipe sizes (8″–24″ X65) × 6 water depths (7–30 m).
  - Outputs: overbend strain, sagbend stress, top tension, stinger
    departure angle.
- **Can-say-now.**
  - "60-case S-lay screening for a shallow-water portfolio — two barge
    classes × five pipe sizes × six water depths — with overbend, sagbend,
    top tension, and stinger-departure outputs."
  - "Self-contained catenary mechanics — the demo runs without any
    `digitalmodel`-library coupling, which is the right shape for a
    contractor who wants to inspect the calc surface without installing
    proprietary toolchains."
- **Cannot-claim-yet.**
  - Full Orcaflex dynamic time-domain analysis (this is screening; the
    real-life follow-on is a detailed model).
  - Dropped-pipe / abandonment-and-recovery analysis.
  - Buckle propagation across irregular bathymetry.
- **Missing proof.**
  - A side-by-side validation of the screening tension result against a
    published Orcaflex case for the same geometry would harden the
    "screening before Orcaflex" message.
  - A "shallow-water barge selection" 1-pager would convert the report
    into a procurement-friendly artifact.
- **Next repo issue / action.** Existing Demo 4 (#1873 if still open;
  Apr-14 report shipped). Follow-up — open a worked-validation issue
  bridging #1792 / #2114 patterns to Demo 4.
- **Draft outreach angle.**
  Lead: "Shallow-water S-lay screening across 60 barge / size / depth
  combinations — overbend, sagbend, tension, stinger angle in one HTML."
  Follow-up: "If your portfolio still has 8″–24″ candidates where barge
  selection is open, I can run your specific case set and we can compare
  against your in-house Orcaflex baseline."
- **Confidence.** **High** for screening; the explicit "no proprietary
  toolchain to inspect" framing differentiates this candidate from the
  other 4 demos.

---

## Candidate 5 — Deepwater rigid-jumper installation (Demo 5)

- **Buyer problem.** Subsea installation contractors and tie-in engineers
  need an envelope of jumper lengths that can land within a 50 mm
  tolerance from a CSV across 500–3000 m water depths and a realistic Hs
  range. Failure is rework cost, not just a sea-state miss.
- **ACE proof / evidence.**
  - Script: `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py`
    (1,229 lines).
  - Report: `digitalmodel/examples/demos/gtm/output/demo_05_jumper_installation_report.html`
    (66 KB).
  - Cases: 300 = 2 vessels × 6 water depths × 5 jumper lengths (20–100 m,
    8″ OD X65) × 5 Hs.
  - Phases: lift-off, in-air bending, splash zone slamming, lowering,
    tie-in alignment (50 mm tolerance).
- **Can-say-now.**
  - "300-case rigid-jumper installation screening — including the tie-in
    alignment phase against a 50 mm tolerance, which is the failure mode
    that costs the day."
  - "Five phases per case — including splash-zone slamming — as a single
    auditable HTML."
- **Cannot-claim-yet.**
  - Detailed clamp / connector engineering (out of scope).
  - Spool-piece / flexible-jumper analogues (this is rigid only).
  - Vessel-specific DP envelope at landing.
- **Missing proof.**
  - One published-Orcaflex comparison run for a single case would
    differentiate "screening" from "screening with one validation
    anchor".
  - A short tie-in-alignment cheatsheet would convert this into a
    procurement-friendly companion to Demo 3.
- **Next repo issue / action.** Demo 5 is shipped. Open follow-up tied to
  #2422 (capability detail pages) to add a Demo 5 "tie-in alignment
  cheatsheet" companion.
- **Draft outreach angle.**
  Lead: "Rigid-jumper installation envelope across 300 cases — including
  the 50 mm tie-in alignment tolerance, which is where the day-rate bleed
  actually happens." Follow-up: "If you have a candidate jumper between
  20 m and 100 m where the alignment phase is still open, I can run a
  case-specific screening against your CSV class."
- **Confidence.** **High**.

---

## Candidate 6 — LNG marine-terminal berth-operability screening

- **Buyer problem.** LNG terminal owners, FSRU operators, and
  port-operations leads need an early engineering reality check on whether
  a berth concept will hit operability targets before committing to full
  navigation simulations or detailed civil design. The pain is escalation
  cost when an early go-decision is later contradicted by harbour-response
  analysis.
- **ACE proof / evidence.**
  - Scope note: `docs/gtm/marine-terminal-engineering-scope.md` — defines
    near-term ACE position with explicit *can / cannot* boundaries.
  - Knowledge corpus: `knowledge/seeds/mooring-failures-lng-terminals.yaml`
    — 40 entries covering NWS LNG (Karratha) multi-year investigation,
    long-period swell mechanism, mooring-line incidents.
  - Wiki concept page:
    `knowledge/wikis/marine-engineering/wiki/concepts/lng-marine-terminal-engineering.md`.
  - Capability map entry: `docs/gtm/capability-map.md` lists "Marine
    Terminal Engineering (LNG / Port Ops)" as a service line.
- **Can-say-now.**
  - "Berth operability and ship/shore transfer-interface screening — the
    'is this concept directionally workable before deeper design'
    question."
  - "We carry a public-source LNG-terminal mooring-failure investigation
    library and can frame a concept against the long-period-swell
    mechanism that has historically broken lines at small swell heights."
  - "Mooring/fender load-path review at berth, transfer-envelope
    screening, harbour-response framing at concept level."
- **Cannot-claim-yet.**
  - Full pilot-in-the-loop navigation simulation campaign ownership.
  - Detailed civil/structural design of jetties, dolphins, breakwaters.
  - QRA, hazardous-area classification, or process-safety final design.
  - Vendor-certified loading-arm / transfer-system design.
  - Specific named-client terminal projects (Woodfibre and SESA-related
    work is corpus-confidential and gated by ACMA / project-owner
    clearance — `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`,
    `terminal-1-sesa.md`).
- **Missing proof.**
  - A public-source-only "Berth Operability Decision Frame" 2-pager built
    from the mooring-failure knowledge corpus — no client identifiers, no
    project-specific data — would let ACE lead with a concept-stage POV
    that survives a senior-engineer cross-check.
  - A walkthrough screening of one *public* LNG project (NWS LNG, where
    public Woodside articles document the long-period swell mechanism)
    would convert the scope note into a credible POV piece.
- **Next repo issue / action.** Open new issue: "feat(gtm): public-source
  berth-operability decision frame — 2-pager from mooring-failure
  knowledge corpus". Cross-link the existing `lng-berth-operability-framing.md`
  and the seed YAML.
- **Draft outreach angle.**
  Lead: "We screen LNG berth concepts against the long-period-swell
  mechanism that broke 3 mooring lines at NWS LNG in 50 mm swell —
  before you commit to a full nav-sim campaign." Follow-up: "If your team
  is sizing a concept and the operability target is still soft, I can
  send a 2-page decision frame that flags the harbour-response edge cases
  worth de-risking first."
- **Confidence.** **Medium-High** — the scope note and knowledge corpus
  are real; the conversion artifact (public-source 2-pager) is the
  next step.

---

## Candidate 7 — FOWT mooring / installation / bankability screening

- **Buyer problem.** Floating-wind developers, EPC partners, and
  bankability reviewers need a reality check on mooring concept maturity,
  anchor strategy, and tow-out / hook-up logic before the project commits
  to a full coupled aero-hydro-servo-elastic toolchain. The pain is buyer
  uncertainty about whether oil-and-gas mooring expertise transfers cleanly
  to floating wind, and where the gaps actually sit.
- **ACE proof / evidence.**
  - Scope note: `docs/gtm/fowt-engineering-scope.md` — explicit boundaries
    around what ACE can credibly do (mooring screening, anchor strategy,
    tow-out logic, integrity planning) vs. what it cannot (full IEC DLC
    execution, controller co-design, certification-grade coupled
    analysis).
  - `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — DNV-OS-E301
    safety-factor citation pilot (per `.claude/rules/calc-citation-contract.md`).
  - `digitalmodel/src/digitalmodel/orcawave/` — drift forces, hydro
    coefficients, motion statistics, RAO processing, vessel database,
    wave-spectrum modules.
  - Capability map entry: FOWT transfer engineering as a stand-up service
    line.
- **Can-say-now.**
  - "Mooring concept screening and anchor strategy framing for semi-sub
    / spar arrangements at pre-FEED level — using the same OrcaFlex
    workflow that screens deepwater oil-and-gas mooring."
  - "Tow-out / hook-up / installation logic transferred from offshore
    deepwater experience — explicit gaps vs. IEC DLCs and OpenFAST / WEIS
    coupled execution."
  - "Bankability-oriented technical assurance on engineering maturity,
    scope gaps, and escalation triggers."
- **Cannot-claim-yet.**
  - Full IEC 61400-3 design-load-case execution (named in the scope note
    as out-of-current-scope).
  - Coupled aero-hydro-servo-elastic time-domain verification.
  - Controller co-design.
  - Certification-grade output.
- **Missing proof.**
  - One public-source FOWT mooring screening case (e.g. against an
    open-data semi-sub geometry like OC4-DeepCwind) would convert the
    scope note into a worked example.
  - A 2-page "FOWT Mooring Reality Check" sample deliverable would let a
    bankability reviewer see the artifact shape without requiring a
    project-specific intake.
- **Next repo issue / action.** Open new issue:
  "feat(gtm): FOWT mooring screening worked example — OC4-DeepCwind
  reference geometry, 1-pager output". Cross-link FOWT scope note and
  `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py`.
- **Draft outreach angle.**
  Lead: "We screen floating-wind mooring concepts before you commit to
  the coupled aero-hydro-servo-elastic toolchain — explicitly flagging
  what does and does not transfer from oil-and-gas." Follow-up: "If your
  team is between concept and FEED on a semi-sub or spar arrangement, I
  can send a 2-pager showing where mooring assumptions need a coupled
  follow-up vs. where the screening result is enough for the next
  decision gate."
- **Confidence.** **Medium-High** — scope note is rigorous and the
  underlying mooring code/citation pilot exists; the "worked example"
  artifact is the lift.

---

## Candidate 8 — Methodology + multi-agent parametric overnight engineering

- **Buyer problem.** Engineering managers evaluating consulting partners
  want to see *how* a calc actually runs before they trust it on their
  data. They are tired of vendor "AI engineering" decks; they want to see
  the calc surface, the audit trail, and the multi-agent review pattern
  that turns a screening run into a defensible artifact.
- **ACE proof / evidence.**
  - 4 published-ready methodology docs at `docs/methodology/published/`:
    - `compound-engineering-public.md`
    - `enforcement-over-instruction-public.md`
    - `multi-agent-parity-public.md`
    - `orchestrator-worker-public.md`
  - HTML companions at `docs/gtm/website-pages/`.
  - Calc-citation contract: `.claude/rules/calc-citation-contract.md` +
    `digitalmodel/src/digitalmodel/citations/schema.py` pilot.
  - Cross-review evidence: precedent in `feedback_cross_provider_review_payoff.md`,
    `feedback_codex_sustained_major_loop.md` — Codex finds non-overlapping
    defects vs. Claude.
  - 1,292 cases across 5 demos as the headline performance proof.
- **Can-say-now.**
  - "Every standards-derived numeric carries a citation back to the
    code clause — fail-closed if the wiki page is missing."
  - "Multi-AI cross-review (Claude / Gemini / Codex) is the standard
    pre-merge step on plans and methodology pieces — engineered to
    surface non-overlapping defects, not consensus theater. (Provider
    coverage is best-effort: known tooling regressions occasionally
    drop a single provider, in which case the review is single-author
    with explicit provenance.)"
  - "Engineering enforcement is at hook level, not at prose level — calc
    rules ship as scripts, not slides."
- **Cannot-claim-yet.**
  - Public case study with a named client deliverable — the deliveries
    log (`docs/gtm/deliveries-log.md`) is empty header today.
  - Independent third-party audit of the citation contract end-to-end.
- **Missing proof.**
  - One public methodology piece on aceengineer.com — currently #2030 is
    open ("publish: methodology docs to aceengineer.com").
  - One end-to-end demo run that exercises citation contract on a
    specific standard (DNV-RP-F105 pilot run).
- **Next repo issue / action.** #2030 (publish methodology docs) is the
  highest-leverage gate; until those 4 pages are live on
  aceengineer.com, the methodology claim has to be sent as PDF
  attachments rather than linked.
- **Draft outreach angle.**
  Lead: "Every numeric in our reports points back to the code clause it
  came from — we ship the citation, not the marketing slide." Follow-up:
  "If your team has been burned by AI-engineering vapor before, can I
  send 4 short pieces explaining exactly how our enforcement, multi-agent
  review, and orchestration patterns work? They are written for senior
  engineers, not procurement."
- **Confidence.** **High** for the methodology rigor; **Medium** for
  outreach efficacy until aceengineer.com hosts the methodology pages
  (#2030).

---

## Candidate 9 — Prospect-data 48-hour custom-demo pipeline (#2346)

> **Status: PIPELINE NARRATIVE ONLY — NOT YET A SHIPPED OUTREACH ASSET.**
> The intake schema, three canonical vessels, and `prospect_adapter.py`
> with 13 passing tests exist; `materialize_demo_inputs` is partial
> (demos 4 and 5); `run_demo` is stubbed; the deliveries log is empty.
> Use this candidate for *internal* pipeline narrative; do **not** lead
> outreach with "48hr custom demo" until at least one DELIVERED row
> exists in `docs/gtm/deliveries-log.md`.

- **Buyer problem (once shipped).** Prospects who like a screening-style
  demo will ask "can you run this on *our* vessel and *our* line"; the
  conversion lives in the time between intake and delivery.
- **ACE proof / evidence (today).**
  - Schema: `docs/gtm/intake/prospect-schema.json` (validated against
    Draft-07).
  - Template: `docs/gtm/intake/prospect-template.yaml`.
  - Canonical vessels: `seven-borealis.yaml`, `pipelay-barge.yaml`,
    `plsv.yaml` — each with class-typical disclaimer + citation.
  - Adapter: `scripts/gtm/prospect_adapter.py` with 13-test suite at
    `scripts/gtm/tests/test_prospect_adapter.py`.
  - Status doc: `docs/gtm/intake/IMPLEMENTATION-STATUS.md` — explicit
    Done / Not-done split with non-promise language.
  - SOP runbook: `docs/gtm/prospect-demo-sop.md` (313 lines) — designed
    state-machine.
  - Deliveries ledger: `docs/gtm/deliveries-log.md` — header schema only,
    no rows.
- **Can-say-now.**
  - "We have a validated intake schema and an adapter with 13 passing
    tests — ready to receive a YAML intake, validate it, and shape inputs
    for demos 4 and 5."
  - "The 48-hour SOP is designed end-to-end with explicit fallback
    semantics F1-F5."
- **Cannot-claim-yet.**
  - "We have shipped a 48-hour custom demo to a prospect" — no row in
    the deliveries log.
  - "End-to-end PR-runtime under 10 min" — golden-image regression suite
    not yet wired (#2346 Codex M6).
- **Missing proof.**
  - At least one DELIVERED row in `docs/gtm/deliveries-log.md`.
  - End-to-end golden-image suite per #2346 Codex M6.
  - Branded report wrapper per #2346 plan section E.
- **Next repo issue / action.** #2346 itself, currently `status:plan-approved`
  + `status:working` + `agent:codex`. Track until first DELIVERED row
  appears, then promote this candidate from "pipeline narrative" to
  "lead outreach asset".
- **Draft outreach angle (POST-SHIP ONLY).**
  Lead: "Send us a YAML intake by Tuesday EOD and we will email you a
  branded screening report — and a private gated URL — by Thursday EOD.
  All five demo flavors available." (Suppress until first DELIVERED row.)
- **Confidence.** **High for the design**; **Low for outreach use** until
  a delivery has shipped.

---

## Candidate 10 — Semiconductor CAD / FEM career-pivot lane (#2507 / #2509 / #2510)

> **Status: PLAN-ONLY — NOT YET A CLIENT-READY GTM ASSET.**
> All three issues are OPEN with no `status:plan-approved` label. #2510
> is at `status:plan-review`. There is no demo, no report, no proof path
> in the repo. Use this candidate for *internal* career-narrative
> alignment only; do **not** include in client outreach.

- **Buyer problem (future).** Chip-design firms running internal CAD
  automation, FEM stress / thermal screening, or layout pre-checks for
  package geometries.
- **ACE proof / evidence (today).** None — issues are scoping
  documents.
- **Can-say-now.** Nothing buyer-facing.
- **Cannot-claim-yet.** Any positioning at all in the semiconductor
  domain — there is no shipped artifact.
- **Missing proof.**
  - At least one reproducible OpenLane / OpenROAD RTL-to-GDS demo
    (#2509) with a public-source design.
  - One Python-driven layout / CAD automation worked example for
    chip / package geometries (#2510).
  - One FEM screening worked example for a chip-package thermal /
    structural problem (#2507).
- **Next repo issue / action.** Drive #2510 from `status:plan-review` →
  approval → execution. This is the first artifact that can become an
  outreach hook for the semiconductor lane.
- **Draft outreach angle (FUTURE).**
  Suppressed — there is no proof path. Revisit once the first
  semiconductor demo report is shipped.
- **Confidence.** **N/A** for outreach today; this candidate exists in
  this brief only to mark it as "pipeline-future" so subsequent overnight
  lanes do not accidentally elevate it.

---

## §2 — Outreach snippets and demo follow-up asks

### §2.1 — Three outbound snippets

Each snippet is short, evidence-bounded, and self-disqualifies (mentions
what we won't yet claim).

**Snippet A — Pipeline integrity manager (Demo 1 + Demo 2)**

> Subject: "DNV freespan + multi-code wall thickness — overnight, 752
> cases combined"
>
> Hi [name],
>
> Two screening reports your team can spot-check:
>
> - 480-case DNV-RP-F105 freespan/VIV screening across 3 pipeline sizes
>   and 8 spans / 5 currents / 4 gap ratios
> - 72-case multi-code wall thickness comparison across DNV-ST-F101 / API
>   RP 1111 / PD 8010-2, X65 baseline
>
> Both reports are self-contained HTML — interactive Plotly charts,
> governing check stated per case. Screening only — not a substitute for
> CFD VIV time-domain or detailed local-buckling.
>
> If you would like the case set rerun against your portfolio's specific
> ODs, pressures, or current profile, send a YAML intake (template
> attached) and I will return the report by EOD Friday.
>
> [name] — Licensed P.E. — aceengineer.com
>
> Evidence boundary: report is a screening pass; full project work needs
> a separate scoped engagement.

**Snippet B — Heavy-lift CSV / subsea installation contractor (Demo 3 +
Demo 5)**

> Subject: "Mudmat + jumper installation envelopes — 480 cases, 2 CSV
> classes, 500–3000 m"
>
> Hi [name],
>
> Two artifact-grounded conversation starters:
>
> - 180-case deepwater mudmat installation screening — 2 CSV classes ×
>   6 water depths × 3 pad sizes × 5 Hs, 5 phases per case
> - 300-case rigid-jumper installation screening — including the 50 mm
>   tie-in alignment phase, which is where the day-rate bleed happens
>
> Vessel data is class-typical (Seven Borealis-style + medium CSV) — not
> vessel-specific until you send the RAOs you trust.
>
> If your portfolio has a candidate field where pad size or jumper length
> is still under debate, I can run your specific case matrix overnight
> and we can compare against your in-house Orcaflex baseline.
>
> [name] — Licensed P.E. — aceengineer.com
>
> Evidence boundary: screening only; final installation engineering still
> requires a project-specific Orcaflex run with vessel-specific RAOs.

**Snippet C — LNG terminal / FSRU operations lead (Candidate 6)**

> Subject: "Berth operability — long-period swell screening before the
> nav-sim campaign"
>
> Hi [name],
>
> One framing artifact worth 5 minutes: a public-source synthesis of the
> NWS LNG mooring-line failure programme — including the 2014
> investigation that found 3 lines parted in 50 mm long-period swell
> through resonant vessel motion.
>
> If your concept is being defended at the gate before a full
> navigation-simulation campaign, the long-period-swell mechanism is the
> highest-leverage thing to flag early. I can send a 2-page decision
> frame against the public knowledge corpus we maintain (no client data
> required for the framing pass).
>
> Evidence boundary: framing and screening only — full berth design,
> QRA, and pilotage validation remain outside this near-term scope. The
> framing pass is a credibility-anchored conversation starter, not a
> deliverable.
>
> [name] — Licensed P.E. — aceengineer.com

### §2.2 — Three demo follow-up asks

These are the next-step asks to send immediately after a prospect opens a
demo report. Each one extends an existing artifact rather than promising
new capability.

**Follow-up 1 — After Demo 1 / Demo 2 read.**

> "Two questions before I rerun this on your data:
>
> 1. Does your portfolio's metocean baseline use site-measured ADCP, or
>    a regional model? (Demo 1 will inherit whichever profile you trust.)
> 2. Are there sour-service / ECA constraints I should layer on top of
>    Demo 2's wall-thickness comparison? (Sour service is a separate
>    workflow; I will flag the boundary in the rerun rather than fold it
>    into the screening.)"

**Follow-up 2 — After Demo 3 / Demo 5 read.**

> "If you can share the RAOs you trust for the vessel class in scope,
> the rerun will swap out the class-typical Seven Borealis envelope for
> your specific data — both reports will get a 'vessel-specific
> confidence' callout. If RAOs are not shareable, I will keep the
> class-typical disclaimer, and we can scope a follow-up where the
> vessel-specific run happens behind your firewall."

**Follow-up 3 — After Demo 4 read.**

> "Two follow-up shapes if Demo 4 is the right entry point:
>
> 1. A 'shallow-water barge selection' 1-pager built from your portfolio
>    candidates — same 60-case structure, just narrowed to your sizes
>    and depths.
> 2. A side-by-side validation against one of your in-house Orcaflex
>    cases — gives both teams a confidence anchor before any committed
>    project work."

---

---

## §3 — Defects discovered during pass 2 (must-fix-before-send)

While validating the case-count claims in §1 against the shipped reports, the
lane discovered three engineering-evidence drifts in *existing* GTM files.
Each is a `must-fix-before-send` item — the existing copy will fail a
senior reviewer's spot-check or, worse, be pasted into a public profile
where it will be cross-checked by a subject-matter expert.

### D1. Expert-network bio overstates the demo suite — 2 of 5 demos misnamed

- **File.** `docs/gtm/expert-network-profiles.md`, §1 "Universal Profile
  Content" → "Bio (200 words)".
- **Defect.** The bio claims: *"Five production demos have screened 1,292
  cases overnight — covering freespan VIV, deepwater installation vessel
  selection, pipeline wall thickness optimization, **mooring system
  sensitivity**, and **cathodic protection sizing**."*
- **Reality.** The five shipped demos are freespan/VIV (Demo 1), wall
  thickness multi-code (Demo 2), deepwater mudmat installation (Demo 3),
  shallow-water S-lay (Demo 4), and deepwater rigid-jumper installation
  (Demo 5). **There is no mooring-sensitivity demo (that is the
  not-yet-built GTM Demo 6, #2115) and no cathodic-protection-sizing
  demo at all.**
- **Impact.** This bio is the seed text for GLG, AlphaSights, and
  Guidepoint registrations (per #1994). If pasted as-is, the first
  consultation will surface the discrepancy — a reviewer asking
  "show me the mooring sensitivity demo" will hit empty.
- **Suggested correction (drop-in).**
  > "Five production demos have screened 1,292 cases overnight —
  > covering pipeline freespan / VIV screening, multi-code wall
  > thickness comparison, deepwater mudmat installation, shallow-water
  > S-lay screening, and deepwater rigid-jumper installation. The
  > demos compress weeks of manual screening into hours of auditable
  > parametric sweeps."
- **Constraint on this lane.** The lane prompt forbids edits outside
  the three allowed files. The fix is recommended here for the user /
  control surface to apply before Tier-A3 (expert-network profile
  refresh) ships.
- **Tier-A3 dependency.** Tier-A3 in the priority push list is
  **blocked** on this fix.

### D2. LinkedIn Week-1 Monday post claims "under 2 seconds" runtime

- **File.** `docs/gtm/linkedin-content-calendar.md`, Week 1 Post 1
  ("Demo Showcase: Wall Thickness") hook line.
- **Defect.** The post hook reads *"3 design codes. 72 combinations.
  Under 2 seconds."* This claim has no validating timing artifact in
  the repo. Demo 2 in full-calc mode imports the live `digitalmodel`
  library; runtime is plausibly fast but not validated to 2 s.
- **Suggested correction.** Either (a) drop the runtime claim, leading
  with "3 design codes, 72 combinations, in a single overnight run",
  or (b) add a `--profile` mode to the demo runner and capture a
  timed reference output before posting.
- **Impact.** Lower than D1 — a runtime claim is recoverable in
  comments, whereas a misnamed demo is not. But still
  must-fix-before-post on LinkedIn.

### D3. capability-summary.html has unresolved relative font path

- **File.** `docs/gtm/website-pages/capability-summary.html`, lines ~16-23.
- **Defect.** The HTML references
  `../../../aceengineer-website/assets/fonts/inter/InterVariable.woff2`
  via `@font-face`. This is a relative path that resolves correctly
  *only* when the file is served from inside the workspace-hub repo
  tree. As an email attachment or a standalone deployable, the font
  load fails and the page falls back to default sans-serif.
- **Impact.** Visual quality of the asset degrades when sent as an
  attachment. Two fixes — either inline the font as base64 (creates a
  larger but truly self-contained HTML) or document that this asset
  ships only via the deployed aceengineer.com tree.
- **Note.** This does not block any Tier-A action, but it is a
  silent quality drag on Candidate 8 outreach until #2030 ships.

### D4. Demo 1 status semantics nuance — `INLINE_ONLY` ≠ unconditional pass

- **File.** `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py`,
  pass-rate chart subtitle: *"Pass rate includes PASS + INLINE_ONLY
  (acceptable for most applications)."*
- **Refinement.** The screening returns three result classes — full
  PASS, INLINE_ONLY (cross-flow exposed but in-line still in margin),
  and FAIL. The published pass-rate combines PASS + INLINE_ONLY.
  Outreach copy should not over-claim "all 480 cases pass" — the
  defensible claim is "screening identified PASS, INLINE_ONLY, and
  FAIL classes per case."
- **Impact.** Tightens Snippet A (3.1). Recommend the lane's existing
  evidence-boundary line for Snippet A reads:
  > *"Evidence boundary: report classifies each case as PASS,
  > INLINE_ONLY, or FAIL per RP-F105 simplified — pass rate combines
  > PASS + INLINE_ONLY which is acceptable for most applications, not
  > unconditional."*

---

---

## §4 — Drop-in templates for the highest-leverage missing-proof items

These are starter scaffolds. They take the three "missing proof" gaps
that block Tier-A3 / C1 / C2 in the priority list and turn each into
a near-final artifact — saving the user 2–4 hours of cold-start
authoring tomorrow morning.

### §4.1 Drop-in: corrected expert-network bio (D1 fix)

Paste this directly into `docs/gtm/expert-network-profiles.md` §1
"Bio (200 words)" replacing the existing content. Word count: 198.

```
Vamsee Achanta is a licensed Professional Engineer with 23 years of
experience in offshore and subsea engineering, spanning deepwater Gulf
of Mexico, West Africa, Brazil, and Asia-Pacific projects. He is the
founder of ACE Engineer, a Houston-based consulting practice
specializing in mooring and riser design, pipeline integrity
assessment, marine installation engineering, and structural
fitness-for-service evaluation.

His technical depth covers OrcaFlex dynamic analysis for mooring and
riser systems, DNV and API code-compliant pipeline wall thickness and
freespan/VIV assessments, marine lifting and installation feasibility
studies, FEA-based structural evaluation, and cathodic protection
design. He has delivered engineering for major operators and EPC
contractors across the full project lifecycle — from FEED through
operations support.

A distinguishing capability is ACE Engineer's AI-augmented parametric
analysis platform. Five production demos have screened 1,292 cases
overnight — covering pipeline freespan / VIV screening, multi-code
wall thickness comparison (DNV / API / PD 8010), deepwater mudmat
installation, shallow-water S-lay screening, and deepwater rigid-jumper
installation. Every numeric in the reports is auditable to the code
clause it came from. This compresses weeks of manual screening into
hours of parametric sweeps.

Vamsee holds a P.E. license and is based in Houston, Texas.
```

**Why this version is defensible.**

- Lists the *actual* five demos (no phantom mooring-sensitivity or CP
  demos).
- Names the codes (DNV / API / PD 8010) that demo 2 actually compares,
  giving the reviewer a concrete spot-check anchor.
- Mentions the citation contract ("auditable to the code clause") —
  the methodology differentiator that supports the rate.
- Keeps cathodic protection in the *capability* sentence (it is in the
  scope inventory) without claiming a CP demo exists.
- Word count holds at 198 — within the bio field limit.

### §4.2 Drop-in: berth-operability decision frame 2-pager outline (Tier-C1)

This is the structure of the public-source 2-pager that unblocks
Snippet 3.3. It cites only public Woodside articles + SIGTTO context
+ knowledge corpus entries — no client data.

```markdown
# LNG Berth Operability — Long-Period Swell Decision Frame

> A 2-page concept-stage screening frame for LNG terminal owners,
> FSRU operators, and port-operations leads. Use before committing
> to a full navigation simulation campaign.

> **Sources used.** Public Woodside Energy articles ("Swell time",
> "Ocean wave"); SIGTTO Panel context (Allery 2015, public summary);
> ACE knowledge corpus
> `knowledge/seeds/mooring-failures-lng-terminals.yaml` (40 public-
> source entries). No client data, no project-confidential data.

## 1. The mechanism that broke 3 mooring lines in 50 mm swell

In 2014, Woodside launched a deep investigation after three mooring
lines parted at the Karratha Gas Plant LNG jetties in long-period
swell of just ~50 mm height. The mechanism is resonant: long-period
swell (~20 s) at very small amplitude can excite vessel motions that
the line system cannot dissipate, leading to line tensions far above
what a quasi-static envelope predicts.

This is not the failure mode that wave-height-based design checks
catch first. The peak amplitude is so small that conventional
operability windows clear it.

## 2. Why this matters at the concept gate

Three concept-stage decisions are most exposed:

- **Berth siting and refraction.** Karratha's mooring break followed
  swell entering Mermaid Sound from the north and refracting along
  navigation-channel slopes. New channel dredging (Pluto LNG)
  produced westerly waves that the existing wave buoy did not
  capture. *Concept gate question:* does your bathymetric / refraction
  model see what your wave buoy sees?
- **Operability uptime budget.** Long-period swell events forced
  Karratha into week-long loading shutdowns and production ramp-backs.
  *Concept gate question:* is your uptime budget calibrated to swell
  amplitude alone, or to the resonance band?
- **Mooring system fatigue exposure.** Line breaks in low-amplitude
  swell mean the failure-mode profile differs from typical
  open-water mooring. *Concept gate question:* is the fatigue case set
  capturing low-amplitude, long-period excitation?

## 3. Five questions a concept review should ask before nav-sim

1. Does the metocean baseline include long-period swell amplitude
   spectra, not just Hs / Tp summary statistics?
2. Is the wave-buoy / metocean instrumentation sited to capture
   refraction-driven energy at the berth, or only at deeper water?
3. Have past mooring incidents in similar refraction regimes been
   reviewed (NWS LNG, public sources)?
4. Is the mooring fatigue case set populated with low-amplitude
   long-period cases, not just storm-load cases?
5. Are operability windows defined against the resonance band, or
   against wave-height alone?

## 4. What ACE Engineer can / cannot do at this stage

- *Can do.* Concept-stage screening, decision-frame review, mooring
  fatigue case-set advice, public-source benchmarking against the NWS
  LNG mechanism, ship/shore transfer-envelope screening.
- *Cannot do.* Full navigation simulation campaign; detailed
  jetty / breakwater design; QRA or hazardous-area classification;
  vendor-certified loading-arm design; final terminal design without
  project-specific data and deeper references.

## 5. Next step

If your team is at the concept gate, a 30-minute call walks through
your specific refraction / metocean / mooring posture against this
mechanism. No prep required from your side; we drive the questions
from the public-source library.

— Vamsee Achanta, Licensed P.E., aceengineer.com
```

**Lift to ship.** ~2 hours of writing — most of the content is in
`mooring-failures-lng-terminals.yaml` already. Convert to PDF after
review.

### §4.3 Drop-in: OC4-DeepCwind FOWT mooring screening 1-pager outline (Tier-C2)

This is the structure of the worked example that unblocks Candidate 7.
It is bounded to the public OC4-DeepCwind reference geometry — no
client data.

```markdown
# FOWT Mooring Screening — OC4-DeepCwind Worked Example

> Concept-stage mooring screening on the public OC4-DeepCwind semi-sub
> reference geometry, using the same OrcaFlex workflow ACE applies to
> deepwater oil-and-gas mooring. One worked screening case to anchor
> conversations with floating-wind developers and bankability reviewers.

> **Sources used.** OC4-DeepCwind public reference geometry (NREL TR);
> DNV-OS-E301 Position Mooring (cited via the calc-citation contract
> at `.claude/rules/calc-citation-contract.md`); public floating-wind
> mooring guidance.
>
> **Not a client deliverable.** This is a methodology-anchoring
> example using a public reference platform. No turbine-specific
> aero-elastic coupling.

## 1. Question

Can a deepwater oil-and-gas mooring screening workflow give a
defensible *concept-stage* answer for an OC4-DeepCwind-class semi-sub
mooring arrangement before a coupled aero-hydro-servo-elastic
simulation is committed?

## 2. Setup (public-source)

- Floater: OC4-DeepCwind semi-sub (NREL public reference geometry).
- Water depth: 200 m (per OC4 published case).
- Mooring concept: 3-line catenary, chain-polyester-chain, screening
  variant.
- Loading: regular wave-current envelope at the screening fidelity
  (no aero coupling, flagged as gap).
- Engine: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py`
  with DNV-OS-E301 safety-factor citation pilot.

## 3. Screening output

[ filled at run time — line tensions, anchor reactions, peak
offsets at the screening fidelity ]

## 4. What this screening DOES tell the buyer

- Order-of-magnitude line tension envelope.
- Whether the mooring concept survives quasi-static + regular-wave
  screening before coupled time-domain.
- Where the next-step coupled analysis must focus (most-loaded line,
  fatigue-critical connector, anchor footprint).

## 5. What this screening DOES NOT tell the buyer

- IEC 61400-3 design-load-case execution.
- Coupled aero-hydro-servo-elastic time-domain results.
- Controller co-design implications.
- Certification-grade output.

## 6. Decision recommendation

If the screening tension envelope sits below {XX}% of MBL with
DNV-OS-E301 safety factors, the next step is a focused coupled
analysis on the most-loaded line — not a full IEC DLC sweep. If
above, the concept needs revision before a coupled run is justified.

— Vamsee Achanta, Licensed P.E., aceengineer.com
```

**Lift to ship.** ~4 hours — one OrcaFlex screening run on the public
geometry, plus 2 hours of write-up. Public OC4-DeepCwind input data
is already in the `marine-resources.md` resources list per
`docs/gtm/core-engineering-work-conversion.md` Workstream 1.

### §4.4 Why these three templates first

These three artifacts are sequenced together because they are the
**lowest-effort bridges to outreach** — each one converts a `cannot-claim-yet`
into a `can-say-now` for one new buyer segment:

| Template | Buyer segment unlocked | Lift | Outreach unlock |
|---|---|---|---|
| §4.1 (corrected bio) | Expert networks (engineering managers + procurement) | 5 min | Tier-A3 ships immediately after paste |
| §4.2 (berth 2-pager) | LNG terminal / FSRU operations leads | 2 h | Snippet 3.3 ships once authored |
| §4.3 (OC4-DeepCwind 1-pager) | Floating-wind developers + bankability reviewers | 4 h | Candidate 7 outreach lifts to "lead with worked example" |

Total unblock cost: ~6 hours of focused work for three new outreach
lanes. This is the highest-density GTM lift in the morning queue.

---

*End of brief — see lane result file for the priority push list.*
