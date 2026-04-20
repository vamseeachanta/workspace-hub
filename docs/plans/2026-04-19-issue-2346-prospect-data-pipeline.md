# Plan for #2346: Prospect-Data Customized-Demo Pipeline — 48hr Turnaround + Pre-Staged Vessel Templates

> **Status:** plan-approved (2026-04-20 after 2 review rounds + v3.1 minor-fix pass, Claude-fallback APPROVE round 2)
> **Complexity:** T2
> **Date:** 2026-04-19 (v1), 2026-04-20 (v2, v3)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2346
> **Review artifacts:** `scripts/review/results/2026-04-20-plan-2346-claude.md` (v2, CHANGES-REQUESTED) | `scripts/review/results/2026-04-20-plan-2346-codex.md` (v2, MAJOR) | gemini (pending round-2)

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| v1 | 2026-04-19 | planner | Initial draft; 5 open design questions (Q4-Q8) flagged for user |
| v2 | 2026-04-20 | planner | Integrated user answers to Q4-Q8: (Q4) dual delivery = email + gated URL; (Q5) canonical vessels derived from public-class references (OTC papers, broker listings, class-society DBs) not synthetic; (Q6) `vessel:` block conditional-required (required for demos 3/4/5, optional/absent for demos 1/2); (Q7) refuse-vs-fix expanded to **5 authorized fallbacks F1-F5** (refuse, closest-canonical, canonical-class-default, one-clarification-email, reduced-scope-with-caveats); (Q8) E2E runs all 5 demos every PR with <10 min runtime budget leveraging `--from-cache`. |
| v3 | 2026-04-20 | planner | Round-1 reviewer integration. Addressed 7 Codex MAJORs + 3 Claude MAJORs + 4 Claude MINORs: (a) Q5 Canonical Vessel Source Pins subsection prescribes 2-citation-per-vessel rule with concrete OTC/broker/ISBN examples (Codex M1/M2, Claude m1); (b) JSON-Schema section rewritten as executable draft-07 with `$schema`, quoted keys, nested `required`, `if/then/else`, and `properties.vessel: false` defense-in-depth for demos 1/2 (Codex M3, Claude M2); (c) Dual Delivery State Machine subsection will define sequencing, partial-failure semantics, retry + compensating actions, delivery log schema (Codex M4); (d) Fallback sidecar path moved to `private-log/fallback-applied.json` with gitignore + test-asserted never-ships guarantee (Codex M5); (e) Canonical-fixture leakage contained via `tests/fixtures/prospect-outputs/` test-only sink with gitignore + CI-path-assertion test (Codex M6); (f) Gated URL mechanism grounded: `aceengineer-website/robots.txt` + `vercel.json` modifications added to Files to Change, unique-hash URL path scheme `/private/<hash>/<slug>.html` (Claude M1); (g) Upstream Dependencies Risks subsection prescribes merge-order vs inline-template fallback relative to #2342/#2343 (Claude M3); (h) Revision History reconciled to "5 authorized fallbacks F1-F5" (Codex M7); (i) gitignore coverage extended to `logos/` and prospect `output/` paths (Claude m4). Implementation not started; all new language in future/imperative tense. |
| v3.1-APPROVED | 2026-04-20 | planner | Round 2 verdict APPROVE from Claude as Codex fallback (Codex sandbox-blocked). Schema executed via jsonschema.Draft7Validator.check_schema(); 4 behavioral schema tests passed. 4 non-blocking NITs: N1 citation for API 17B/17J edition unpinned; N2 minor doc polish; N3-N4 documentation improvements — deferred to implementation-time. |
| v3.1 | 2026-04-20 | planner | Round-2 Claude review minor-fix pass (verdict MINOR, non-blocking). Fixes: (D1) Line 135 gating-mechanism table aligned with Files-to-Change — `/prospects/<hash>/index.html` reconciled to `/private/<hash>/<slug>.html` so the `robots.txt` `Disallow: /private/` rule + `X-Robots-Tag` header match a single top-level path across the plan. (D2) Sidecar schema enum + prose reconciled: line 459 prose will now state "all fallbacks F1-F5 are logged" (audit-trail completeness) and schema enum at line 472 will include `F4` so all five fallback codes are valid log values. (D3) New Risks subsection "Cross-repo deploy dependency" will document that `aceengineer-website/` is a nested separate git repository, requiring two distinct pushes (workspace-hub + aceengineer-website), a Vercel auto-rebuild on the aceengineer-website push, and a cross-repo rollback path — acceptance criteria at lines 622-623 reclassified as post-deploy verification steps. (TRIVIAL D6) Line 434 "four authorized fallbacks" rephrased as "five authorized fallbacks (F1 refuse + F2-F5 fix-paths)" for consistency with Revision History. D4 (DELIVERED_EMAIL_ONLY → DELIVERED recovery transition), D5 (F4 rationale comment), D7 (numerical-failure root-cause-detection protocol) deferred — D5 subsumed by D2's enum expansion; D4/D7 require >1-line edits and are filed as post-implementation refinements. Implementation not started; all new language in future/imperative tense. |

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` (1,257 lines, 680 cases) — loads via `load_pipe_catalog()` (reads `data/pipelines.json`) + `load_jumper_catalog()` (reads `data/rigid_jumpers.json`). CLI surface is `--from-cache` / `--force` only; **no CLI flag to override vessel or structure inputs** — today the parameter matrix is hard-coded at module scope (`WATER_DEPTHS`, `HS_VALUES`, etc.).
- Found: `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` (1,343 lines, 72 cases) — inline `json.load(DATA_DIR / "pipelines.json")` inside `main()`; no separate loader function. Same `--from-cache` / `--force` CLI only.
- Found: `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` (1,223 lines, 180 cases) — `load_vessels()` reads `data/csv_hlv_vessels.json`, `load_structures()` reads `data/mudmat_structures.json`. Hard-coded `WATER_DEPTHS`, `HS_VALUES` at module scope. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` (1,642 lines, 60 cases) — `load_vessels()` reads `data/pipelay_vessels.json` (different file from demos 3/5), `load_pipes()` reads `data/pipelines.json`. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` (1,229 lines, 300 cases) — `load_vessel_data()` reads `data/csv_hlv_vessels.json`, `load_jumper_data()` reads `data/rigid_jumpers.json`. Same CLI.
- Found: `digitalmodel/examples/demos/gtm/report_template.py` (620 lines) — `GTMReportBuilder` API already accepts `title`, `subtitle`, `demo_id`, `case_count`, `code_refs`; this is the per-report branding hook. It already emits self-contained HTML reports — the prospect pipeline can reuse it without API changes for the engineering body, and only needs a thin wrapper to inject client header/footer branding.
- Found: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` — shared by demos 3 + 5. Schema includes `id`, `name`, `representative_class`, `general.{loa_m,beam_m,displacement_te,dp_class,max_water_depth_m}`, `crane_main.{swl_max_te, swl_max_radius_m, crane_capacity_curve[], hoist_speed_m_per_min, main_wire_mbl_te, main_wire_diameter_mm}`, `motion_characteristics.{heave_rao,roll_rao,pitch_rao,natural_periods}`. This is the canonical CSV/HLV vessel shape.
- Found: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` — **different schema** from `csv_hlv_vessels.json`. Has `pipelay_system.{tensioner, stinger, firing_line}` instead of `crane_main` — demo 4 requires a pipelay-specific vessel shape. **The adapter MUST support two distinct vessel shapes**, not one unified shape.
- Found: `digitalmodel/examples/demos/gtm/data/rigid_jumpers.json` + `pipelines.json` + `mudmat_structures.json` + `freespan_scenarios.json` — four distinct structure schemas. Demo 1 uses pipelines+jumpers+freespan_scenarios; Demo 2 uses pipelines only; Demo 3 uses mudmat_structures; Demo 4 uses pipelines; Demo 5 uses rigid_jumpers.
- Found: `digitalmodel/examples/demos/gtm/data/freespan_scenarios.json` — environment block (`current_velocities_ms`, `turbulence_intensity`, `span_lengths`) is the Demo 1 parametric sweep definition, not a structure. This means the intake schema for Demo 1 must accept *environment* + *structure* + *pipe catalog* — three sub-documents, not two.
- Gap: no CLI flag on any of the 5 demos to point at an alternate data directory (all demos hard-code `DATA_DIR = SCRIPT_DIR / "data"`). Adapter work must add a `--prospect-config` flag to each.
- Gap: no YAML support anywhere in `examples/demos/gtm/` — current data files are JSON. Prospect intake is YAML-first (issue body asks for `docs/gtm/intake/prospect-template.yaml`) so we need a YAML→demo-input translator.
- Gap: no branded-report wrapper — `GTMReportBuilder` emits the digitalmodel brand; there is no hook today for "prospect XYZ Energy" header/footer text.
- Gap: no input-validation harness. Each demo currently `KeyError`s on a missing JSON field rather than refusing with a human-readable error. Under a 48hr SLA the fail mode must be "refuse with line-and-key reference" at intake, not a stack trace after 45 minutes of compute.

### Standards

Not applicable — this is a GTM infrastructure / pipeline issue, not new engineering calculation code. (The underlying engineering codes are already cited inside each demo: DNV-RP-H103, DNV-ST-F101, API 5L, etc.)

### Public-class vessel data sources (v3, per user answer to Q5 + Codex M1/M2 + Claude m1)

Per user direction, the 3 pre-staged canonical vessels will NOT be synthetic — they will be derived from **class-typical** values published in open literature. v3 upgrades the sourcing contract from "broad categories" to **pinned citations per vessel** so a reviewer can independently recompute each canonical vessel's parameters from the cited sources.

#### Canonical Vessel Source Pins (plan-time contract, NOT deferred)

Each canonical YAML will be committed with at least **two complementary citations** in its header comment — at minimum one vendor-disclosure source (marketing spec sheet, class-society registry, or OTC paper with general particulars) AND one class-typical methodology source (industry textbook or API/DNV recommended practice section). The pairing requirement exists because no single open source typically discloses full RAOs + full crane curve + full pipelay-system details for any one asset.

The plan prescribes the following pins as the v3 baseline; implementation MAY substitute an equivalent public source of equal or better auditability, but MUST commit the exact IDs used alongside the YAML in the same PR, and MUST NOT leave any citation as a placeholder at merge time.

| Canonical YAML | Vessel class | Primary citation (general particulars, crane/pipelay specs) | Complementary citation (motion/RAO methodology, class-typical envelopes) |
|---|---|---|---|
| `pipelay-barge.yaml` | S-lay pipelay barge (shallow/mid-water) | Allseas *Lorelay* public spec sheet (allseas.com/equipment/pipelay-vessels/lorelay) — LOA, beam, DP2, max lay depth, tensioner capacity, stinger radius. | Palmer & King, *Subsea Pipeline Engineering* (3rd ed., 2023, ISBN 978-1-5939-2378-7), chapter on S-lay barges — class-typical tensioner/stinger envelopes and barge RAO ranges. |
| `heavy-lift-csv.yaml` | Heavy-lift Construction Support Vessel (DP3, deepwater crane) | Subsea 7 *Seven Borealis* public spec sheet (subsea7.com/en/our-fleet) + OTC paper OTC-24523 (2013) "Installation of Subsea Structures Using Heavy-Lift CSVs" — LOA, beam, DP3, 5000 t main crane SWL curve. | Bai & Bai, *Subsea Engineering Handbook* (2nd ed., 2018, ISBN 978-0-12-812622-6), §21 installation vessel characterization — class-typical heave/roll/pitch RAOs for DP3 CSVs, natural periods. |
| `plsv.yaml` | Pipe-Lay Support Vessel (flex-lay / reel-lay, deepwater) | TechnipFMC *Deep Energy* public spec sheet (technipfmc.com/en/what-we-do/subsea/vessels) + OTC paper OTC-25303 (2014) "Deepwater Reel-Lay PLSV Installation Experience" — LOA, beam, DP3, reel/tensioner capacity, max lay depth. | DNV-RP-H103 *Modelling and Analysis of Marine Operations* (Oct 2021 ed.) §4 lay-vessel motion criteria + API 17B/17J — class-typical operability envelopes for PLSV installation. |

**Reviewer-reproducibility test:** for each YAML, the adversarial reviewer MUST be able to open each cited document (public URL or widely-available ISBN) and recompute at least the LOA, beam, DP class, max water depth, and one representative crane/tensioner capacity. If a reviewer cannot reproduce the numbers from the cited pair, the canonical YAML FAILS plan-acceptance criterion and MUST be revised before merge.

**Disclaimer contract:** every canonical vessel YAML file MUST include a top-of-file comment block stating: (a) "Class-typical values, not vessel-specific"; (b) "Do not represent any particular commercial asset"; (c) the two citations per the pins above, with URLs/DOIs/ISBNs; (d) last-reviewed date. The adapter will surface this disclaimer on the report cover page when a canonical vessel is used.

**Residual sourcing risk:** vendor spec sheets are subject to URL-rot. Mitigation: each YAML will snapshot the citation as ISO-8601 `accessed` date, and when a URL dies the class-society registry entry or textbook page will be the durable fallback. This is enforced by a `sources[].accessed_utc` field being REQUIRED in each YAML's header block.

### LLM Wiki pages consulted

No relevant wiki pages — this is a sales/ops pipeline, not a domain-knowledge question.

### Documents consulted

- `docs/gtm/gtm-plan-30day.md` lines 125-138 (Week 4 "Demo Customization — The Real Sales Event") — explicit claim: "The free demo-with-their-data is the **highest-conversion sales tool** — prioritize this over everything else." 48hr turnaround is set at line 135 ("Run parametric demo with THEIR data within 48 hours"). Risk mitigation quoted in issue body: "Always keep a clean demo environment ready; pre-stage common vessel types."
- `digitalmodel/examples/demos/gtm/README.md` lines 7-25 (Quick Start + Demos) + lines 117-125 (Common Flags) — confirms the 5 demos each emit one HTML report + one JSON result file. Lines 129-142 document the 7 data files. Confirms **only** `--from-cache` / `--force` exist on the CLI today; there is no prospect-override path.
- Issue #2342+#2343 plan `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — v4-lite self-approved 2026-04-19. Defines the published aceengineer-website detail-page shape (branded `<title>A&CE — ...</title>`, `partials/head-common.html` + `nav.html` + `footer.html` includes, vendored Plotly). Each prospect-demo report can be rendered as a one-off derivative page on the same template, posted to a private URL (see "Branded Report" below) — **no need to invent a new branded HTML skeleton**.
- Issue #2016 (umbrella "client conversion pipeline") — lines 25-31 identify parametric demo reports as a top gap; line 133 ("Demo Customization — The Real Sales Event") in the 30-day plan is the named Week 4 deliverable. This plan is the concrete execution of #2016's line-item "demo materials ready for outreach" for the *prospect-specific* case.
- Issue body #2346 — names the four concrete deliverables: (1) intake schema at `docs/gtm/intake/`, (2) 3 canonical vessel profiles pre-staged, (3) SOP at `docs/gtm/prospect-demo-sop.md`, (4) shared input adapter across 5 demos. Acceptance criteria include "Dry-run end-to-end <48 hr from dummy intake."
- Memory `feedback_adversarial_review_stance.md` — every plan must be defect-hunted, not charitably read. Informs the Risks section below (in particular the "48hr burnout" and "schema-drift" risks are flagged intentionally).
- Memory `feedback_queue_git_tracked.md` — any pre-staged vessel profile must be committed to git before it is referenced from the SOP (no floating local-only files).

### Gaps identified

Verified against git state at plan-commit time (none of these artifacts exist in git; all will be created during implementation):

1. No YAML intake schema exists at `docs/gtm/intake/` — the directory itself does not exist in git; implementation will create it.
2. No pre-staged "canonical" vessel profiles exist at a stable path — `data/csv_hlv_vessels.json` has two vessels, but they are demo fixtures, not prospect-intake defaults. Three canonical vessel YAMLs will be created.
3. No shared input-adapter module — each demo ships its own bespoke `load_*()` functions against hard-coded JSON paths. `prospect_adapter.py` will be created.
4. No branded-output wrapper on `GTMReportBuilder` — today all reports say "digitalmodel" in the footer. `branded_report.py` will be created.
5. No SOP document — the 48hr runbook does not exist in any form. `docs/gtm/prospect-demo-sop.md` will be created.
6. No schema-validation + refuse-vs-fix decision tree for malformed prospect input. Both will be introduced by the adapter + SOP.
7. No test coverage for the end-to-end intake→demo→report path. Two new pytest modules will be created.

Distinct sources consulted: 11 (issue body + 30-day plan + 5 demo scripts + README + report_template.py + 4 data files + #2016 body + #2342/#2343 plan + 2 memory feedback entries). Exceeds minimum 3.

---

## Artifact Map

All rows below are **prescribed by this plan** (to be created during implementation) unless marked EXISTING (already in git at plan-commit time). Plan v2 is the only file in git for this issue; every other path below is a future-work artifact.

| Artifact | Path | Status |
|---|---|---|
| This plan | `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` | EXISTING (committed) |
| YAML intake schema (template) | `docs/gtm/intake/prospect-template.yaml` | PRESCRIBED |
| YAML intake schema (JSON-Schema validator) | `docs/gtm/intake/prospect-schema.json` | PRESCRIBED |
| Pre-staged canonical vessel — pipelay barge | `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml` | PRESCRIBED |
| Pre-staged canonical vessel — heavy-lift CSV | `docs/gtm/intake/canonical-vessels/heavy-lift-csv.yaml` | PRESCRIBED |
| Pre-staged canonical vessel — PLSV | `docs/gtm/intake/canonical-vessels/plsv.yaml` | PRESCRIBED |
| SOP runbook | `docs/gtm/prospect-demo-sop.md` | PRESCRIBED |
| Shared input adapter (module) | `digitalmodel/examples/demos/gtm/prospect_adapter.py` | PRESCRIBED |
| Branded-report wrapper | `digitalmodel/examples/demos/gtm/branded_report.py` | PRESCRIBED |
| Fallback-audit sidecar (private-log, gitignored, never shipped) | `digitalmodel/examples/demos/gtm/private-log/fallback-applied.json` | PRESCRIBED (runtime output; gitignored; schema in section G) |
| Test-only dual-delivery output sink (E2E canonical fixtures) | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/` | PRESCRIBED (gitignored; never published) |
| Deliveries log | `docs/gtm/deliveries-log.md` | PRESCRIBED |
| Golden regression test | `digitalmodel/examples/demos/gtm/tests/test_prospect_adapter.py` | PRESCRIBED |
| Dry-run end-to-end test | `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` | PRESCRIBED |
| Plan index row | `docs/plans/README.md` (one new row) | EXISTING (row update prescribed) |
| Plan review — Claude | `scripts/review/results/2026-04-19-plan-2346-claude.md` | PRESCRIBED (adversarial review not yet dispatched) |
| Plan review — Codex | `scripts/review/results/2026-04-19-plan-2346-codex.md` | PRESCRIBED |
| Plan review — Gemini | `scripts/review/results/2026-04-19-plan-2346-gemini.md` | PRESCRIBED |

---

## Deliverable

At the end of implementation: a repeatable pipeline that ingests one prospect YAML file (vessel specs + target structure + project conditions), validates it against a JSON-Schema, maps it through a shared `prospect_adapter` (to be created) to any of the 5 existing GTM demos, runs the demo in under the existing wall-clock budget, and emits a client-branded HTML report — delivered **via both email attachment AND a gated private URL on `aceengineer-website`** — all driven by a single SOP runbook that guarantees ≤48 hr end-to-end delivery, with three pre-staged canonical vessel templates (pipelay barge class, heavy-lift CSV class, PLSV class) derived from public-class references for scenarios where prospect data is incomplete. None of the pipeline artifacts exist in git at plan-commit time; this section describes the prescribed end-state.

### Dual delivery (v2, per user answer to Q4)

Every prospect report is delivered on **two channels simultaneously**:

1. **Email attachment (primary).** The HTML report (optionally PDF'd) is emailed to `prospect.contact` with NDA watermark when `nda_in_place=true`. This is the contractually-safest channel; email is the authoritative deliverable.

2. **Gated private URL (secondary / viewing convenience).** The same HTML is published to `aceengineer-website` under a gated path. **"Gated" is defined precisely** (plan decision — one of three mechanisms; implementation picks exactly one, documented in SOP):

   | Gating mechanism | Definition | Security | Complexity |
   |---|---|---|---|
   | **(a) Unique-hash URL** (RECOMMENDED) | Path = `/private/<sha256-hash-of-(prospect-id + salt + date)>/<slug>.html`. Hash is sent in the email body; not linked from anywhere on the public site. Crawler-blocked via `robots.txt` + `X-Robots-Tag: noindex, nofollow`. Path prefix `/private/` matches the single top-level `Disallow` rule in `robots.txt` and the `X-Robots-Tag` header applied at line 511-515. | Security-by-obscurity (acceptable given NDA already in place + email is primary channel) | Low — static file publish, no auth server |
   | (b) Basic-auth password | HTTP Basic Auth at edge (Vercel / Netlify env-var based). Password sent in email body. | Stronger — defense-in-depth | Medium — edge-config work |
   | (c) Expiring signed link | Time-limited signed URL (TTL=14 days); expires after deadline. | Strongest — auto-cleanup after deadline | High — requires signing service |

   **v2 plan default: (a) unique-hash URL** unless the prospect explicitly requests stronger gating in the intake. The `output` block gains a `gating: hash | basic-auth | signed` field with default `hash`.

3. **Coexistence rule:** email is ALWAYS sent. The URL is an optional additional channel the prospect can ignore; its publication is controlled by a top-level `output.publish_private_url: bool` flag (default `true`). If the prospect opts out (sets it `false` or an engineer overrides under sensitivity considerations), only email is delivered.

4. **Purge contract:** any gated URL publication must have a matching entry in `docs/gtm/deliveries-log.md` with `purge_after_utc` timestamp; an enforcement cron (filed as a follow-up issue — not in this plan's scope) verifies nothing stays published past the purge date.

### Dual Delivery State Machine (v3, per Codex M4)

The plan prescribes the following sequencing + partial-failure semantics. Implementation will encode this as a small state machine in `prospect_adapter.py::deliver()`; TDD tests will cover each transition.

1. **Sequencing (serial, email-first).** Email is sent FIRST. Only after email is confirmed delivered (SMTP 250 + queued-log entry) does the pipeline publish to the gated URL. Rationale: email is the authoritative, contractually-safe channel; if email fails, no URL is published, so the prospect never sees a URL without the accompanying email context.
2. **Email-success + URL-success** → write full delivery-log entry (email_sent_utc, url_published_utc, hash, purge_after_utc); state = `DELIVERED`.
3. **Email-failure** → abort. Do NOT publish URL. Log failure with SMTP/transport error; state = `FAILED_EMAIL`. Engineer is alerted via SOP Hour-44-48 checkpoint. Retry policy: 3 attempts with exponential backoff (30s, 2min, 10min) BEFORE declaring `FAILED_EMAIL`.
4. **Email-success + URL-publish-failure** → the prospect already has the email+attachment (authoritative deliverable satisfied). Retry URL publish 3× (30s, 2min, 10min). On persistent failure, state = `DELIVERED_EMAIL_ONLY`; delivery-log records `url_publish_error` and `url_retry_count=3`. No compensating action (email is not withdrawn) because the contract at line 129 declares email sufficient.
5. **Late URL publish** (URL succeeds on a retry after initial email but prospect has already opened email without URL) → allowed; deliveries-log records `url_published_utc` with the eventual timestamp. No follow-up email is auto-sent (avoids spam); SOP allows an engineer to manually send a "URL now available" email if the prospect requests.
6. **Compensating action for successful email + decision to un-publish** (e.g., NDA violation discovered post-publish) → `unpublish_url(hash)` will delete the gated file and record `unpublished_utc` + `unpublish_reason` in deliveries-log. Email is NOT recalled (not technically possible). This is a manually-triggered SOP action, not an automatic state transition.
7. **Delivery log schema** (each row, appended never mutated): `prospect_id`, `demo`, `email_attempt_count`, `email_sent_utc` (nullable), `url_publish_attempt_count`, `url_published_utc` (nullable), `gated_url_hash` (nullable), `purge_after_utc` (nullable), `state` (enum: `DELIVERED` | `DELIVERED_EMAIL_ONLY` | `FAILED_EMAIL` | `UNPUBLISHED`), `fallback_applied` (F1-F5 code or null), `notes`.

TDD coverage: `test_delivery_email_first_then_url`, `test_delivery_email_fail_aborts_url`, `test_delivery_url_fail_records_email_only_state`, `test_delivery_retry_backoff_bounds`, `test_delivery_unpublish_records_state`.

---

## Pseudocode

### A. YAML intake schema (`prospect-template.yaml`)

```yaml
# Top-level shape — all fields required unless noted "optional"
prospect:
  company: "Acme Marine Contractors"        # required, string
  contact: "jane.doe@acme.example"          # required, for report cover
  nda_in_place: true                        # required bool — gates report distribution
  target_demo: "demo_05"                    # required enum: demo_01..demo_05
  delivery_deadline_utc: "2026-04-21T17:00Z"  # required ISO8601

vessel:                                     # CONDITIONAL-REQUIRED per v2/Q6
  # Required when target_demo in {demo_03, demo_04, demo_05}
  # Optional / absent when target_demo in {demo_01, demo_02}
  shape: "csv_hlv"                          # required enum: csv_hlv | pipelay
  source: "prospect_provided"               # required enum: prospect_provided | canonical_ref
  canonical_ref: null                       # required-if source==canonical_ref, string id
  # Body omitted here when source==canonical_ref; otherwise inline body
  # must match the schema fragment csv_hlv_vessel_schema OR pipelay_vessel_schema
  body: { ... }                             # required-if source==prospect_provided

structure:
  kind: "rigid_jumper"                      # required enum matching demo
  # body shape selected by kind: rigid_jumper, pipeline, mudmat, freespan
  body: { ... }

environment:
  water_depths_m: [1500, 2000, 2500]        # optional — overrides demo default sweep
  hs_values_m: [1.5, 2.0, 2.5]              # optional
  current_velocity_ms: 0.5                  # optional
  # If absent, demo uses its module-level defaults

output:
  brand_header: "Prepared for Acme Marine"  # required string — report cover
  brand_footer: "Confidential — NDA"        # required string
  # Optional prospect logo (inline SVG or path under docs/gtm/intake/logos/)
  logo_inline_svg: null
  # v2 dual-delivery fields (Q4):
  publish_private_url: true                 # optional bool, default true. If false, email-only.
  gating: "hash"                            # optional enum: hash | basic-auth | signed. Default hash.
  purge_after_utc: "2026-05-20T00:00Z"      # required-if publish_private_url==true
```

### B. JSON-Schema validator (`prospect-schema.json`) — v3 executable draft-07

v3 rewrites this section as a real JSON-Schema document (quoted keys, nested `required` arrays, `$schema` declaration, explicit `if/then/else`). The schema below will be committed verbatim as `docs/gtm/intake/prospect-schema.json` and will pass `jsonschema`'s `Draft7Validator.check_schema()`. The Q6 "vessel FORBIDDEN for demos 1/2" contract will be expressed via BOTH `"not": { "required": ["vessel"] }` AND `"properties": { "vessel": false }` for defense-in-depth (Claude M2): the `false` subschema forbids the property, and the `not/required` gives a redundant rejection path that surfaces a clearer error message.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://aceengineer.com/schemas/prospect-intake-v3.json",
  "title": "Prospect Demo Intake",
  "type": "object",
  "additionalProperties": false,
  "required": ["prospect", "structure", "output"],
  "properties": {
    "prospect": {
      "type": "object",
      "additionalProperties": false,
      "required": ["company", "contact", "nda_in_place", "target_demo", "delivery_deadline_utc"],
      "properties": {
        "company": { "type": "string", "minLength": 1 },
        "contact": { "type": "string", "format": "email" },
        "nda_in_place": { "type": "boolean" },
        "target_demo": { "type": "string", "enum": ["demo_01", "demo_02", "demo_03", "demo_04", "demo_05"] },
        "delivery_deadline_utc": { "type": "string", "format": "date-time" }
      }
    },
    "vessel": {
      "type": "object",
      "additionalProperties": false,
      "required": ["shape", "source"],
      "properties": {
        "shape": { "type": "string", "enum": ["csv_hlv", "pipelay"] },
        "source": { "type": "string", "enum": ["prospect_provided", "canonical_ref"] },
        "canonical_ref": { "type": ["string", "null"] },
        "body": { "type": "object" }
      },
      "allOf": [
        {
          "if":   { "properties": { "source": { "const": "prospect_provided" } } },
          "then": { "required": ["body"] }
        },
        {
          "if":   { "properties": { "source": { "const": "canonical_ref" } } },
          "then": { "required": ["canonical_ref"], "properties": { "canonical_ref": { "type": "string", "minLength": 1 } } }
        }
      ]
    },
    "structure": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "body"],
      "properties": {
        "kind": { "type": "string", "enum": ["pipeline", "rigid_jumper", "mudmat", "freespan", "jumper_and_freespan"] },
        "body": { "type": "object" }
      }
    },
    "environment": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "water_depths_m": { "type": "array", "items": { "type": "number", "minimum": 0, "maximum": 4000 } },
        "hs_values_m":    { "type": "array", "items": { "type": "number", "minimum": 0, "maximum": 8 } },
        "current_velocity_ms": { "type": "number", "minimum": 0, "maximum": 5 }
      }
    },
    "output": {
      "type": "object",
      "additionalProperties": false,
      "required": ["brand_header", "brand_footer"],
      "properties": {
        "brand_header": { "type": "string", "minLength": 1 },
        "brand_footer": { "type": "string", "minLength": 1 },
        "logo_inline_svg": { "type": ["string", "null"] },
        "publish_private_url": { "type": "boolean", "default": true },
        "gating": { "type": "string", "enum": ["hash", "basic-auth", "signed"], "default": "hash" },
        "purge_after_utc": { "type": "string", "format": "date-time" }
      },
      "allOf": [
        {
          "if":   { "properties": { "publish_private_url": { "const": true } } },
          "then": { "required": ["purge_after_utc"] }
        }
      ]
    }
  },
  "allOf": [
    {
      "description": "Q6: demos 3/4/5 REQUIRE a vessel block.",
      "if":   { "properties": { "prospect": { "properties": { "target_demo": { "enum": ["demo_03", "demo_04", "demo_05"] } } } } },
      "then": { "required": ["vessel"] }
    },
    {
      "description": "Q6: demos 1/2 FORBID a vessel block (defense-in-depth: both properties.vessel=false AND not/required).",
      "if":   { "properties": { "prospect": { "properties": { "target_demo": { "enum": ["demo_01", "demo_02"] } } } } },
      "then": {
        "properties": { "vessel": false },
        "not": { "required": ["vessel"] }
      }
    }
  ]
}
```

Rationale: `"properties": { "vessel": false }` in draft-07 means "if the `vessel` key is present, validation fails" — this is the real forbidding mechanism Claude M2 called for. The accompanying `"not": { "required": ["vessel"] }` is redundant but surfaces the error on a different path, so whichever validator message the engineer sees first is intelligible. `additionalProperties: false` on every inner object guards against silent typos (the 48hr SLA will not allow a 30-min post-mortem on `target_dmo`).

### C. Shared input adapter (`prospect_adapter.py`)

```
MODULE prospect_adapter

CONSTANTS:
    SCHEMA_PATH = docs/gtm/intake/prospect-schema.json
    CANONICAL_DIR = docs/gtm/intake/canonical-vessels/
    DEMO_TO_VESSEL_SHAPE = {
        "demo_01": None,                    # no vessel, just pipe + environment
        "demo_02": None,                    # no vessel, just pipe + codes
        "demo_03": "csv_hlv",               # mudmat → CSV
        "demo_04": "pipelay",               # S-lay → PLV
        "demo_05": "csv_hlv",               # jumper → CSV
    }
    DEMO_TO_STRUCTURE_KIND = {
        "demo_01": ["pipeline", "jumper_and_freespan"],
        "demo_02": ["pipeline"],
        "demo_03": ["mudmat"],
        "demo_04": ["pipeline"],
        "demo_05": ["rigid_jumper"],
    }

function load_and_validate(yaml_path):
    intake = yaml.safe_load(yaml_path)
    schema = json.load(SCHEMA_PATH)
    jsonschema.validate(intake, schema)              # first gate: structural
    # Second gate: cross-field consistency (not expressible in JSON-Schema)
    demo = intake.prospect.target_demo
    expected_shape = DEMO_TO_VESSEL_SHAPE[demo]      # None for demo_01 / demo_02
    # v2/Q6 conditional-required handling:
    if expected_shape is None:
        # Demos 1, 2: vessel block MUST be absent; schema already checked, assert here for defence in depth
        assert "vessel" not in intake, "demo_01/demo_02 must not include vessel block"
    else:
        # Demos 3, 4, 5: vessel block MUST be present and shape-correct
        assert "vessel" in intake, f"{demo} requires vessel block"
        verify intake.vessel.shape == expected_shape
        verify intake.structure.kind in DEMO_TO_STRUCTURE_KIND[demo]
        if intake.vessel.source == "canonical_ref":
            canonical_path = CANONICAL_DIR / f"{intake.vessel.canonical_ref}.yaml"
            must exist, else raise ProspectIntakeError with refuse-message
            inline_body = yaml.safe_load(canonical_path)
            intake.vessel.body = inline_body
        # Third gate: numeric sanity — depth within vessel's max_water_depth_m
        if intake.vessel.shape == "csv_hlv":
            if any(d > intake.vessel.body.general.max_water_depth_m for d in intake.environment.water_depths_m):
                raise ProspectIntakeError("prospect requested deeper water than vessel rating")
    return intake

function materialize_demo_inputs(intake, tmpdir):
    # Rewrites intake.vessel + intake.structure into the JSON shapes the
    # existing demo scripts already expect — emits files into tmpdir/data/
    if intake.prospect.target_demo in ("demo_03", "demo_05"):
        write tmpdir/data/csv_hlv_vessels.json from intake.vessel.body
    elif intake.prospect.target_demo == "demo_04":
        write tmpdir/data/pipelay_vessels.json from intake.vessel.body
    write tmpdir/data/<structure_file>.json from intake.structure.body
    # Environment overrides are materialized as a separate env-override JSON
    # that each demo main() reads via the new --prospect-env flag (see patch D)
    if intake.environment:
        write tmpdir/data/prospect_env.json from intake.environment
    return tmpdir

function run_demo(intake, materialized_dir):
    demo = intake.prospect.target_demo
    script = f"digitalmodel/examples/demos/gtm/{demo}_*.py"    # glob-resolved
    subprocess: PYTHONPATH=... uv run python <script> \
        --prospect-data-dir <materialized_dir>/data \
        --prospect-env <materialized_dir>/data/prospect_env.json  (if env present)
    return path to generated output/*.html
```

### D. Per-demo CLI patches (5 scripts — smallest possible diffs)

Each demo gets a `--prospect-data-dir PATH` argparse flag that, when set, overrides the module-level `DATA_DIR` constant **for loaders only**. This is the **only** change to demo 01-05 scripts — no refactoring of the sweep logic, no change to existing `--from-cache`/`--force` behavior.

```python
# Added to each parse_args():
parser.add_argument("--prospect-data-dir", type=Path, default=None,
                    help="Override DATA_DIR for prospect-customized runs")
parser.add_argument("--prospect-env", type=Path, default=None,
                    help="Override module-level parameter sweep (WATER_DEPTHS etc) from JSON")
parser.add_argument("--brand-header", type=str, default=None)
parser.add_argument("--brand-footer", type=str, default=None)

# In main() after args parsed:
if args.prospect_data_dir:
    global DATA_DIR; DATA_DIR = args.prospect_data_dir
if args.prospect_env:
    override_constants_from(args.prospect_env)  # mutates WATER_DEPTHS, HS_VALUES in-module
```

### E. Branded-report wrapper (`branded_report.py`)

```
function wrap_with_client_branding(report_html_path, brand_header, brand_footer, nda_watermark):
    # Post-processes the GTMReportBuilder output — injects <div class="client-header"> and
    # <div class="client-footer"> plus a fixed-position "CONFIDENTIAL — <NDA>" watermark
    # if nda_watermark truthy. Uses BeautifulSoup to parse; writes back in-place.
    # The existing #2342+#2343 detail-page styling is preserved — this only overlays, never
    # replaces, the engineering body.
```

### F. SOP runbook (`prospect-demo-sop.md`) — 48hr decision tree

```
Hour 0-2: Receive prospect data (email, LinkedIn, form). File as docs/gtm/intake/received/YYYY-MM-DD-<company>.yaml
Hour 2-6: Run prospect_adapter.load_and_validate()
  - PASS → proceed to Hour 6-24
  - FAIL schema or cross-field → consult the refuse-vs-fix matrix (see section G)
Hour 6-24: Run demo via prospect_adapter.run_demo()
  - On numerical failure (NaN / exception) → flag specific phase, consult refuse-vs-fix
    matrix row "numerical-failure" for allowed fallback behaviour.
Hour 24-36: Render branded report, spot-check all 5 charts render, open in 2 browsers.
Hour 36-44: Internal review — 1 engineer reads the whole report; if any flag, fix or escalate.
Hour 44-48: Deliver on BOTH channels (v2/Q4):
  - Email prospect HTML + PDF (primary, always)
  - Publish to aceengineer-website gated URL (secondary, unless output.publish_private_url=false)
  - Record: prospect + date + demo + gated URL + purge_after_utc in docs/gtm/deliveries-log.md
```

### G. Refuse-vs-fix fallback matrix (v2, per user answer to Q7)

The SOP allows five authorized fallbacks (F1 refuse + F2-F5 fix-paths). These are pre-authorized — no ad-hoc escalation needed — but each has strict applicability bounds and a mandatory audit trail.

| Fallback | Code | Applies to which failures | Required prospect authorization | Report-cover disclosure |
|---|---|---|---|---|
| **F1** — Refuse + email back | `refuse` | Default for any unclear/ambiguous failure | None | N/A — no report rendered |
| **F2** — Use closest canonical vessel | `closest-canonical` | Missing `vessel` block (demos 3/4/5) OR vessel fails numeric-sanity gate | **Pre-authorized** (prospect said "use your closest vessel" in intake email) | Cover page: "Vessel spec supplied by ACE canonical library: <class-typical name>. Class-typical values; not vessel-specific." |
| **F3** — Use canonical class default field | `canonical-default-field` | Single missing scalar field inside an otherwise-complete vessel or structure block (e.g. `crane_main.swl_max_radius_m` missing but rest of vessel present). Allowed ONLY for fields on an explicit allowlist (see adapter const `FIELDS_ALLOWED_FOR_CLASS_DEFAULT`). | Implicit (no pre-auth needed for allowlist fields); explicit pre-auth for any other field | Cover page: line-item list of every substituted field with its source canonical-class value |
| **F4** — One clarification email | `clarify` | Any single well-defined missing field or ambiguous enum value that a prospect can answer in one reply | None (this IS the refuse) | N/A — no report rendered until reply |
| **F5** — Reduced-scope analysis with caveats | `reduced-scope` | Cross-field failure that can be sidestepped by narrowing the sweep (e.g. depth > vessel rating → cap the sweep at vessel rating and flag). Allowed ONLY for parametric-sweep failures, never for structural/schema failures. | **Pre-authorized** (prospect selected "deliver reduced-scope if needed" in intake email) OR explicit email confirmation within Hour 2-6 | Cover page: "Scope reduced: <what was cut>. Full-envelope analysis requires <what>." + red-banner caveat |

**Applicability-failure-mode matrix** (pure enumeration — implementation crib):

| Failure mode | F1 refuse | F2 closest-canonical | F3 class-default-field | F4 clarify | F5 reduced-scope |
|---|:---:|:---:|:---:|:---:|:---:|
| Schema missing top-level block (e.g. `structure`) | DEFAULT | — | — | ALLOWED | — |
| Schema missing required field | — | — | ALLOWED (allowlist only) | DEFAULT | — |
| Schema additionalProperties (typo) | — | — | — | DEFAULT | — |
| Schema type mismatch (string-where-number) | — | — | — | DEFAULT | — |
| Cross-field: wrong vessel shape for demo | DEFAULT | — | — | ALLOWED | — |
| Cross-field: depth > vessel rating | ALLOWED | — | — | ALLOWED | DEFAULT (if pre-auth) |
| Cross-field: entire vessel block missing (demos 3/4/5) | — | DEFAULT (if pre-auth) | — | ALLOWED (otherwise) | — |
| Numerical failure (NaN / solver blowup) | DEFAULT | ALLOWED (if pre-auth AND root cause is vessel) | — | ALLOWED | ALLOWED (if parametric edge) |
| Canonical-ref file not found | DEFAULT | — | — | — | — |
| Demo 1/2 with stray vessel block | — | — | — | DEFAULT | — |

Every fallback application must be logged in `docs/gtm/deliveries-log.md` (prescribed file — created during implementation) with the fallback code — **all fallbacks F1-F5 will be logged** (v3.1 reconciliation per Claude round-2 D2) so the full audit trail captures every refuse/fix decision, and the adapter (to be created) must emit a structured JSON record to a **private-log** fallback-audit sidecar so the pattern is auditable across prospects without ever reaching the prospect.

**v3 sidecar boundary (per Codex M5):** the sidecar path will be `digitalmodel/examples/demos/gtm/private-log/fallback-applied.json` — NOT in the `output/` tree. Rationale: `output/` holds prospect-facing HTML + JSON result files; a sidecar in that tree risks being accidentally emailed, zipped into a deliverable, or published to the gated URL. The `private-log/` directory will be a sibling of `output/`, committed to `.gitignore`, and explicitly excluded by name in the deliver() packaging function. The plan prescribes: (a) Pseudocode section C will rename `output/fallback-applied.json` references to `private-log/fallback-applied.json`; (b) Files to Change will add a `.gitignore` rule for `digitalmodel/examples/demos/gtm/private-log/`; (c) the deliver() packaging step will hard-exclude `private-log/**` from both the email-attachment bundle and the gated-URL publish set; (d) TDD tests `test_fallback_sidecar_never_in_email_attachment` and `test_fallback_sidecar_never_in_url_publish_set` will assert the sidecar path appears in NEITHER delivery channel's file list.

**v3 sidecar schema** (specified at plan time, per Claude m3):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["prospect_id", "timestamp_utc", "fallback_code", "failure_mode"],
  "properties": {
    "prospect_id":        { "type": "string" },
    "timestamp_utc":      { "type": "string", "format": "date-time" },
    "fallback_code":      { "type": "string", "enum": ["F1", "F2", "F3", "F4", "F5"] },
    "failure_mode":       { "type": "string" },
    "field_substituted":  { "type": ["string", "null"] },
    "canonical_source":   { "type": ["string", "null"] },
    "pre_authorization":  { "type": "string", "enum": ["explicit", "implicit_allowlist", "none"] },
    "engineer":           { "type": "string" }
  }
}
```
The E2E tests `test_e2e_fallback_matrix_F2_closest_canonical` / `..._F5_reduced_scope` will validate the sidecar content against this schema.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/gtm/intake/prospect-template.yaml` | Copy-paste starting point for prospect (and for our own data entry on their behalf) |
| Create | `docs/gtm/intake/prospect-schema.json` | Machine-checkable validation contract |
| Create | `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml` | Pre-staged fallback (Demo 4 vessel shape) |
| Create | `docs/gtm/intake/canonical-vessels/heavy-lift-csv.yaml` | Pre-staged fallback (Demo 3+5 vessel shape) |
| Create | `docs/gtm/intake/canonical-vessels/plsv.yaml` | Pre-staged fallback (Pipe-Lay Support Vessel) |
| Create | `docs/gtm/intake/README.md` | Short index describing what each file is for |
| Create | `docs/gtm/prospect-demo-sop.md` | 48hr runbook (section F pseudocode, expanded) |
| Create | `docs/gtm/deliveries-log.md` | Empty table header for future delivery records |
| Create | `digitalmodel/examples/demos/gtm/prospect_adapter.py` | load_and_validate + materialize_demo_inputs + run_demo |
| Create | `digitalmodel/examples/demos/gtm/branded_report.py` | wrap_with_client_branding helper |
| Create | `digitalmodel/examples/demos/gtm/tests/test_prospect_adapter.py` | TDD suite |
| Create | `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` | End-to-end golden-output regression test |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-valid.yaml` | Valid fixture for tests |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-missing-vessel.yaml` | Invalid fixture (schema-fail case) |
| Create | `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-depth-exceeds.yaml` | Invalid fixture (cross-field-fail case) |
| Modify | `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` | Add `--prospect-data-dir` / `--prospect-env` / `--brand-*` flags; swap `DATA_DIR` if set |
| Modify | `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` | Same minimal flag set |
| Modify | `digitalmodel/examples/demos/gtm/README.md` | Add "Prospect-customized runs" section with flag docs |
| Modify | `docs/plans/README.md` | Register this plan (status: draft v3) |
| Modify | `aceengineer-website/robots.txt` | Add `Disallow: /private/` so crawlers will skip gated prospect URLs (Claude M1) |
| Modify | `aceengineer-website/vercel.json` | Add `headers` entry with `source: /private/(.*)` setting `X-Robots-Tag: noindex, nofollow` (Claude M1) |
| Modify | `.gitignore` | Add `docs/gtm/intake/received/`, `docs/gtm/intake/logos/`, `digitalmodel/examples/demos/gtm/private-log/`, `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/`, and prospect `output/` artifacts (Claude m4, Codex M5/M6) |

**Note on gated URL path scheme (v3):** the unique-hash URL scheme will be `/private/<sha256-hash(prospect-id + salt + date)>/<slug>.html`. `/private/` (not `/prospects/`) is chosen so the `Disallow` rule in `robots.txt` matches a single top-level path. If basic-auth is selected instead (opt-in, per intake field `output.gating: basic-auth`), Vercel Password Protection (Pro-tier feature, ~$20/mo add-on per project) will be used — the plan acknowledges this cost and documents it as a gating-upgrade decision in the SOP.

**Note on `.gitignore`:** four new patterns will be added (see row above). Rationale: (a) `intake/received/` holds NDA-covered prospect YAMLs; (b) `intake/logos/` holds potentially copyrighted prospect brand assets; (c) `private-log/` holds fallback-audit records that must never leave the engineer's machine; (d) `tests/fixtures/prospect-outputs/` holds CI-generated HTML from canonical vessels that must never be mistaken for prospect-facing content. Each pattern will be verified by a `git check-ignore` acceptance test.

---

## TDD Test List

Tests written against `pytest` with `uv run pytest digitalmodel/examples/demos/gtm/tests/ -v`.

### Schema validation tests (`test_prospect_adapter.py`)

| Test name | What it verifies | Input | Expected |
|---|---|---|---|
| test_valid_yaml_passes_schema | Happy path: valid YAML passes both JSON-Schema and cross-field check | `fixtures/prospect-valid.yaml` | no exception, returns dict |
| test_missing_vessel_body_fails | Missing required `vessel.body` when source=prospect_provided | `fixtures/prospect-missing-vessel.yaml` | raises `ProspectIntakeError` with "vessel.body required" in msg |
| test_unknown_top_level_key_fails | Typo like `prospct:` triggers additionalProperties=false | mutated fixture | raises `ProspectIntakeError` |
| test_wrong_demo_vessel_shape_mismatch | Demo 4 asked with shape=csv_hlv (mismatch) | mutated fixture | raises `ProspectIntakeError` with "demo_04 requires pipelay shape" |
| test_depth_exceeds_vessel_rating | `environment.water_depths_m` max > `vessel.body.general.max_water_depth_m` | `fixtures/prospect-depth-exceeds.yaml` | raises `ProspectIntakeError` with both numbers in msg |
| test_canonical_ref_loads_inline | `vessel.source=canonical_ref` with `canonical_ref=heavy-lift-csv` | fixture | returned dict has `vessel.body` inline-populated from canonical YAML |
| test_canonical_ref_unknown_id_fails | `canonical_ref=does-not-exist` | fixture | raises `ProspectIntakeError` |
| test_enum_target_demo_rejects_demo_99 | `prospect.target_demo=demo_99` | mutated fixture | raises `ProspectIntakeError` |

### Adapter materialization tests

| Test name | What it verifies |
|---|---|
| test_materialize_csv_hlv_writes_correct_file | Demo 3 or 5 target → `csv_hlv_vessels.json` exists in tmpdir with expected schema |
| test_materialize_pipelay_writes_correct_file | Demo 4 target → `pipelay_vessels.json` exists in tmpdir |
| test_materialize_env_override | `environment.water_depths_m=[500,1000]` → `prospect_env.json` contains same |

### Pre-staged canonical vessel tests

| Test name | What it verifies |
|---|---|
| test_each_canonical_vessel_validates_against_schema | All 3 canonical YAMLs pass `load_and_validate` as bodies (with wrapper prospect-stub) |
| test_canonical_coverage_spans_three_vessel_shapes | Pipelay + heavy-lift + PLSV cover the two schemas (csv_hlv × 2, pipelay × 1) |

### End-to-end tests (`test_prospect_pipeline_e2e.py`) — v2/Q8: ALL 5 demos in CI

Per user answer to Q8, the E2E suite runs all 5 demos on every PR using canonical intakes. To stay within a reasonable PR-gate budget, each demo uses `--from-cache` where the cache is pre-warmed as a one-time CI setup (mirrors the common dev workflow of "cache-warm once locally, re-read cheaply thereafter").

**Runtime budget:** <10 min preferred for the full 5-demo suite on the standard PR runner. If any demo exceeds its per-demo budget the test is marked `@pytest.mark.slow` and only runs on nightly CI, not on PR — but the PR suite must still cover schema validation, materialization, refuse-fast, and at least one smoke-level E2E (demo_05 with canonical vessel).

| Test name | What it verifies | Performance gate |
|---|---|---|
| test_e2e_demo_01_pipe_freespan_viv | Valid YAML (NO vessel block, per v2/Q6) → adapter → demo_01 → report | `--from-cache` enabled — target <120 s |
| test_e2e_demo_02_wall_thickness | Valid YAML (NO vessel block) → adapter → demo_02 → report | `--from-cache` enabled — target <60 s |
| test_e2e_demo_03_mudmat_installation | Valid YAML (csv_hlv canonical vessel) → adapter → demo_03 → report | `--from-cache` enabled — target <120 s |
| test_e2e_demo_04_pipelay | Valid YAML (pipelay canonical vessel) → adapter → demo_04 → report | `--from-cache` enabled — target <120 s |
| test_e2e_demo_05_rigid_jumper | Valid YAML (csv_hlv canonical vessel) → adapter → demo_05 → report | `--from-cache` enabled — target <90 s |
| test_e2e_report_contains_brand_strings | Generated HTML (any demo) contains `brand_header` + `brand_footer` literals | n/a |
| test_e2e_report_has_nda_watermark_when_requested | `nda_in_place=true` → watermark div present in HTML | n/a |
| test_e2e_report_has_canonical_class_disclaimer | Canonical vessel used → report cover page includes class-typical disclaimer + citations | n/a |
| test_e2e_dual_delivery_artifacts_present | After pipeline: both email-ready HTML AND gated-URL HTML exist in output dirs | n/a |
| test_e2e_gated_url_hash_deterministic | Same prospect id + salt + date → same hash URL (repeatability) | n/a |
| test_e2e_golden_regression_demo_05 | Canonical "heavy-lift-csv" vessel + fixture structure → charts' underlying JSON payload matches committed golden file byte-for-byte (modulo timestamps) | n/a — regression guard |
| test_e2e_refuse_on_malformed_yaml | Invalid YAML → pipeline exits non-zero before any compute | < 5 s — must fail fast |
| test_e2e_fallback_matrix_F2_closest_canonical | Demo 5 intake with missing vessel + pre-auth → F2 applied, cover disclosure present, `private-log/fallback-applied.json` sidecar written and validates against section-G schema | `--from-cache` enabled — target <90 s |
| test_e2e_fallback_matrix_F5_reduced_scope | Depth exceeds vessel rating + pre-auth → F5 applied, scope-reduced banner present, sweep capped | `--from-cache` enabled — target <90 s |
| test_e2e_demo_01_with_stray_vessel_rejected | Demo 1 intake that wrongly includes `vessel:` → pipeline refuses at schema time (v3: both `properties.vessel: false` AND `not/required` paths surface an error) | < 5 s |
| test_fallback_sidecar_never_in_email_attachment | Simulated deliver() with an F2 fallback: email-attachment file list MUST NOT include `private-log/fallback-applied.json` | < 5 s |
| test_fallback_sidecar_never_in_url_publish_set | Simulated deliver() with an F2 fallback: URL-publish file list MUST NOT include `private-log/fallback-applied.json` | < 5 s |
| test_canonical_fixture_output_path_isolation | E2E output for canonical-vessel runs lands under `tests/fixtures/prospect-outputs/` only; asserted-absent from `aceengineer-website/` and `docs/gtm/website-pages/` | < 5 s |
| test_delivery_email_first_then_url | State machine: email sent before URL publish attempted | mocked — < 2 s |
| test_delivery_email_fail_aborts_url | State machine: email failure → URL NOT published, state=FAILED_EMAIL | mocked — < 2 s |
| test_delivery_url_fail_records_email_only_state | State machine: email OK + URL publish fails 3× → state=DELIVERED_EMAIL_ONLY | mocked — < 2 s |
| test_delivery_retry_backoff_bounds | Retry schedule 30s/2min/10min respected within ±10% tolerance | mocked — < 3 s |
| test_delivery_unpublish_records_state | unpublish_url() deletes gated file and records state=UNPUBLISHED with reason | mocked — < 2 s |
| test_robots_txt_disallows_private | `aceengineer-website/robots.txt` contains `Disallow: /private/` | < 1 s |
| test_vercel_json_noindex_header_on_private | `aceengineer-website/vercel.json` `headers` block sets `X-Robots-Tag: noindex, nofollow` on `source: /private/(.*)` | < 1 s |
| test_gitignore_covers_private_log | `git check-ignore digitalmodel/examples/demos/gtm/private-log/x.json` exits 0 | < 1 s |
| test_gitignore_covers_logos | `git check-ignore docs/gtm/intake/logos/sample.svg` exits 0 | < 1 s |
| test_gitignore_covers_test_fixture_outputs | `git check-ignore digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/x.html` exits 0 | < 1 s |

**Budget-concern flag:** the 5-demo suite will approach the 10-min budget on cold CI. Mitigations (in priority order): (a) `--from-cache` is mandatory in CI; (b) CI job warms the cache once per workflow; (c) if budget is breached, split into `pr-smoke` (3 demos: 02/05/refuse-cases, <4 min) and `nightly-full` (all 5 + golden regressions). This split is a filed follow-up decision, not a v2 plan commitment — the plan commits to the 5-demo target and flags the risk.

### SOP tests (trivial — markdown link-checks)

| Test name | What it verifies |
|---|---|
| test_sop_references_exist | Every path referenced in `prospect-demo-sop.md` (adapter, schema, canonical-vessels dir) resolves on disk |

---

## Acceptance Criteria

- [ ] `docs/gtm/intake/prospect-template.yaml` exists, validates against `prospect-schema.json`, and contains inline comments explaining each field (including v2/Q4 `output.publish_private_url`, `output.gating`, `output.purge_after_utc` and v2/Q6 conditional-vessel note)
- [ ] `docs/gtm/intake/prospect-schema.json` is draft-07 JSON-Schema with `additionalProperties: false` on every object and `allOf`-conditional vessel-required block per v2/Q6
- [ ] Schema rejects demo_01/demo_02 intake that contains a `vessel:` block (explicit test)
- [ ] Schema rejects demo_03/demo_04/demo_05 intake that lacks a `vessel:` block (explicit test)
- [ ] Three canonical vessel files exist at `docs/gtm/intake/canonical-vessels/{pipelay-barge,heavy-lift-csv,plsv}.yaml`, each validates standalone, and each contains the **public-class disclaimer block** with source citations (OTC / broker / class-society / industry-text references) per v2/Q5
- [ ] `digitalmodel/examples/demos/gtm/prospect_adapter.py` exposes `load_and_validate`, `materialize_demo_inputs`, `run_demo` per pseudocode, including v2/Q6 conditional handling
- [ ] `digitalmodel/examples/demos/gtm/branded_report.py` exposes `wrap_with_client_branding` per pseudocode AND emits the class-typical disclaimer on the cover page when a canonical vessel was used
- [ ] All 5 demo scripts accept `--prospect-data-dir`, `--prospect-env`, `--brand-header`, `--brand-footer` flags; behavior unchanged when flags absent (regression-protected)
- [ ] `docs/gtm/prospect-demo-sop.md` exists with the 48hr decision tree AND the **v2/Q7 refuse-vs-fix fallback matrix** (all 5 fallbacks F1-F5 with applicability rules)
- [ ] Dual-delivery pipeline (v2/Q4): email HTML always produced; gated URL artifact produced when `output.publish_private_url=true`; both have content parity (same sha256 on report body modulo header/footer gating)
- [ ] Gated URL uses unique-hash mechanism by default; `docs/gtm/deliveries-log.md` records `purge_after_utc` for every gated publication
- [ ] `docs/gtm/deliveries-log.md` exists with table headers including `prospect_id`, `demo`, `delivered_utc`, `gated_url_hash`, `purge_after_utc`, `fallback_applied` (F1-F5 code)
- [ ] `docs/gtm/intake/received/` appears in `.gitignore` (NDA / PII isolation)
- [ ] `.gitignore` entry verified with `git check-ignore docs/gtm/intake/received/sample.yaml` returning exit 0
- [ ] `uv run pytest digitalmodel/examples/demos/gtm/tests/ -v` passes — all schema, materialization, e2e, golden, SOP tests green
- [ ] v2/Q8: E2E suite covers all 5 demos on every PR; total runtime < 10 min with `--from-cache` warm
- [ ] `test_e2e_refuse_on_malformed_yaml` completes in < 5 s (fail-fast verified)
- [ ] Fallback-audit sidecar `private-log/fallback-applied.json` (v3) is written whenever F2/F3/F5 triggers and matches the schema specified in section G
- [ ] Fallback-audit sidecar never appears in the email-attachment bundle (asserted by `test_fallback_sidecar_never_in_email_attachment`)
- [ ] Fallback-audit sidecar never appears in the gated-URL publish set (asserted by `test_fallback_sidecar_never_in_url_publish_set`)
- [ ] `aceengineer-website/robots.txt` contains `Disallow: /private/` (verified by `curl https://aceengineer.com/robots.txt`)
- [ ] `aceengineer-website/vercel.json` sets `X-Robots-Tag: noindex, nofollow` on `/private/(.*)` (verified by `curl -I https://aceengineer.com/private/<hash>/index.html`)
- [ ] `.gitignore` covers `docs/gtm/intake/logos/`, `digitalmodel/examples/demos/gtm/private-log/`, and `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/` — each verified via `git check-ignore` in tests
- [ ] Canonical-fixture E2E HTML files will land only under `tests/fixtures/prospect-outputs/`; test asserts no CI-generated files appear under `aceengineer-website/` or `docs/gtm/website-pages/`
- [ ] Dual delivery state machine tests (`test_delivery_email_first_then_url`, `..._email_fail_aborts_url`, `..._url_fail_records_email_only_state`, `..._retry_backoff_bounds`, `..._unpublish_records_state`) all pass
- [ ] Each canonical YAML header block includes ≥2 citations per v3 Source Pins table, with URLs/DOIs/ISBNs and `accessed_utc` field populated
- [ ] Golden regression test committed with a canonical golden JSON output file
- [ ] `docs/plans/README.md` has a new row for #2346 in the index (v2 status)
- [ ] No regression in existing demos: `uv run python digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py --from-cache` still produces identical HTML when no prospect flags are passed
- [ ] Review artifacts posted to `scripts/review/results/` from at least 2 providers (Claude + Codex) before any implementation

---

## Adversarial Review Summary

<!-- To be filled in after Step 4. Not yet dispatched. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** TBD

---

## Risks and Open Questions

### Risks

- **Risk: prospect data leakage (PII / NDA).** Prospect vessel specs, project coordinates, and contact information are commercial-sensitive and may be covered under NDA. Mitigation: (1) `docs/gtm/intake/received/` is `.gitignore`d and verified by test; (2) SOP mandates explicit NDA check before any report leaves ACE; (3) `nda_in_place: true` gates watermark application; (4) deliveries-log.md records prospect + date + demo but NOT vessel specs. **Residual risk:** a human forgetting to add `.gitignore` entry for a new subfolder — mitigation is the git-check-ignore acceptance test.
- **Risk: turnaround burnout under 48hr SLA.** A single engineer running this on nights/weekends will degrade quality after week 1. Mitigation: the SOP's explicit refuse-rather-than-guess rule is the burnout backstop — if schema fails, the clock resets at prospect's end, not ACE's. Plan explicitly rejects "silently fill defaults" as a failure mode.
- **Risk: quality drift under pressure.** Under time pressure an engineer might skip the Hour 36-44 internal review. Mitigation: the golden-regression test + the in-report NDA watermark are both CI-enforced artifacts that cannot be faked; they don't eliminate the risk but make violations auditable after the fact.
- **Risk: vessel-shape mismatch not caught pre-run.** If a prospect submits a pipelay vessel shape for a demo_05 jumper analysis, the engineering output would be nonsense. Mitigation: `DEMO_TO_VESSEL_SHAPE` + cross-field validation gate; TDD test `test_wrong_demo_vessel_shape_mismatch` locks this.
- **Risk: 5-demo CLI-patch blast radius.** Touching all 5 demos risks a regression in an already-working sweep. Mitigation: the patches are the minimal possible diff (2 lines of argparse + 2 lines in main() per demo); regression acceptance criterion explicitly includes running `--from-cache` on demo_05 and comparing HTML byte-level.
- **Risk: YAML injection / file-read attacks in canonical_ref.** If prospect supplies `canonical_ref: "../../../etc/passwd"`, the adapter should refuse. Mitigation: adapter must sanitize `canonical_ref` against an allowlist constructed at module load by `glob(CANONICAL_DIR / "*.yaml")`, not by string concat. Acceptance test `test_canonical_ref_unknown_id_fails` + a new `test_canonical_ref_traversal_rejected` must both pass.
- **Risk: schema drift between YAML intake and existing JSON data files.** Demo data files may evolve; the adapter's materialization step could silently break. Mitigation: the golden regression test re-materializes and compares against committed golden output — drift surfaces as a failing test, not a silent malformed report delivered to a prospect.
- **Risk: Demo 1 intake is 3-document (environment + structure + pipe catalog).** More complex than other demos' intake. Mitigation: schema uses `oneOf` per `structure.kind`; Demo 1 fixture committed and test-covered.
- **Risk (v2/Q5): public-class disclaimer drift.** Class-derived canonical vessels may be read by a prospect as endorsement of a specific commercial asset. Mitigation: (a) every canonical YAML file has a mandatory top-of-file disclaimer block with source citations; (b) the report cover page auto-emits the disclaimer when a canonical vessel is used; (c) acceptance criteria + test assert the disclaimer presence; (d) sources restricted to public / class-society / industry-text materials — never internal, never confidential. **Residual risk:** a reader ignoring the disclaimer and quoting numbers as if they were vendor-disclosed — not mitigable by plan; relies on SOP-level engineer instruction.
- **Risk (v2/Q4): gated URL complexity and leakage.** Dual-channel delivery doubles the attack surface. Mitigations: (a) default gating mechanism is unique-hash (simplest; no server-side auth state to leak); (b) `robots.txt` + `X-Robots-Tag: noindex, nofollow` blocks crawlers; (c) `purge_after_utc` enforcement (cron follow-up issue); (d) deliveries-log.md records every hash → traceability if leak discovered. **Residual risk:** prospect forwarding the hash URL to an unauthorized third party — not mitigable at plan level; SOP must make the NDA boundary explicit in the email body.
- **Risk (v2/Q8): 10-min CI budget under pressure.** Running all 5 demos in CI on every PR is the user's mandate but the sum-of-durations approaches the budget. Mitigations: (a) `--from-cache` enforced in CI; (b) cache warmed by CI setup step; (c) filed follow-up to split `pr-smoke` vs `nightly-full` if breached. **Residual risk:** cache-drift causing phantom passes — golden regression test catches this on the cache-warming job itself, not on each PR.
- **Risk (v2/Q7): fallback matrix over-reach.** Five authorized fallbacks (F1-F5) widen the refuse-vs-fix decision surface. A tired engineer might silently apply F3 (class-default-field) to a field outside the allowlist. Mitigations: (a) allowlist enforced in code, not in the SOP prose; (b) fallback-audit sidecar JSON written every time a fallback triggers — auditable post-hoc; (c) acceptance test verifies non-allowlist field substitution raises `ProspectIntakeError`.

### Upstream Dependencies (v3, per Claude M3)

- **Risk: cross-plan sequencing with #2342/#2343.** `branded_report.py` (this plan) will optionally overlay client branding onto the #2342/#2343 detail-page template (`partials/head-common.html`, `nav.html`, `footer.html`, vendored Plotly). If #2342/#2343 merges BEFORE #2346, those templates will exist and `branded_report.py` will layer on top. If #2346 ships FIRST, the templates will not exist yet and `branded_report.py` would fail at import-time. **Mitigation (two-path):**
  1. **Preferred path:** implement #2346 AFTER #2342/#2343 Commit 2 merges. This is the lower-complexity path and will be the default.
  2. **Fallback path:** if scheduling forces #2346 to ship first, `branded_report.py` will include a minimal inline HTML template (self-contained `<head>` + brand header/footer div + inline CSS, no external partials, no vendored Plotly — charts will fall back to static PNG via matplotlib) that can later be SUPERSEDED by the #2342/#2343 template when available. The inline template will be marked `# DEPRECATED-ON-#2342-MERGE` in-source and a follow-up issue will be filed to strip it.
  Decision gate: merge order will be resolved at the first implementation kickoff; both paths are pre-authorized so implementation will not block on a re-planning cycle. Acceptance criterion will assert that the chosen path is documented in `branded_report.py` module docstring with the relevant commit SHA of #2342/#2343 OR the DEPRECATED marker.

### Cross-repo deploy dependency (v3.1, per Claude round-2 D3)

- **Risk: aceengineer-website is a separate nested git repository — edits to `aceengineer-website/robots.txt` and `aceengineer-website/vercel.json` do NOT ship via workspace-hub commits.** Verified during #2342+#2343 Commit 1 implementation: `aceengineer-website/.git` is a distinct repo with its own remote, and `git ls-files` in workspace-hub returns zero matches for the `aceengineer-website/` prefix. The plan's Files-to-Change rows at lines 511-512 therefore describe edits that will land in a different remote than the rest of this plan.
- **Two pushes required for acceptance:** (1) one push on the workspace-hub remote for the plan + review artifacts + adapter/schema/SOP/test files; (2) one separate push on the aceengineer-website remote for the `robots.txt` + `vercel.json` edits. The two pushes are independent git operations, not a single atomic deploy.
- **Vercel auto-rebuild is triggered by the aceengineer-website push,** not the workspace-hub push. Acceptance criteria at lines 622-623 (`curl https://aceengineer.com/robots.txt` and `curl -I .../private/...`) will only pass AFTER the aceengineer-website push has been merged AND Vercel has completed its auto-rebuild. Implementation sequence MUST push aceengineer-website first (or at least verify the Vercel rebuild has settled) before asserting the curl-based acceptance tests.
- **Rollback scope:** any rollback of the gated-URL plumbing requires reverting the relevant commit IN the aceengineer-website repository, not in workspace-hub. A `git revert` in workspace-hub will NOT unpublish the `robots.txt`/`vercel.json` changes; the SOP runbook will document the cross-repo rollback path explicitly.
- **Mitigation:** SOP runbook will include a "cross-repo deploy checklist" section naming the two remotes, the required push order, the Vercel rebuild wait, and the revert procedure per repo. Acceptance criteria lines 622-623 will be reclassified as **post-deploy verification steps** (not implementation-complete gates) to make the cross-repo sequencing explicit.

### Open questions for user (remaining after v2 integration)

User-answered in v2 (see Revision History):
- ~~Q4 — delivery channel~~ → dual (email + gated URL)
- ~~Q5 — canonical vessel realism~~ → public-class-derived
- ~~Q6 — vessel block~~ → conditional-required per demo
- ~~Q7 — refuse-vs-fix~~ → 5 authorized fallbacks F1-F5
- ~~Q8 — E2E runtime~~ → all 5 demos, <10 min, --from-cache

Still open (lower-priority, do NOT block round-1 adversarial review):

1. **Q9 — gating mechanism default.** Plan commits to unique-hash as the default gating; basic-auth and signed-link alternatives are documented as intake-opt-in. Confirm default `hash` is acceptable, OR request `basic-auth` as default for higher security at the cost of edge-config work.
2. **Q10 — purge-enforcement cron owner.** Dual-delivery plan assumes a follow-up issue will file a purge-enforcement cron that deletes gated URLs past `purge_after_utc`. Confirm this can be deferred to a post-implementation follow-up, or must be part of this plan's implementation scope.
3. **Q11 — canonical vessel citation completeness.** Plan flags specific OTC / broker / class-society document IDs for "populate during implementation". Confirm this is acceptable, OR request the document IDs be enumerated in v3 of the plan before implementation begins.

---

## Complexity: T2

**T2** — new module (adapter + branded-report wrapper), new docs (schema + template + SOP + 3 canonical vessels), minimum-diff modifications to 5 existing demo scripts, full TDD coverage including a golden-regression test. No new engineering calculations, no standards gap work, no cross-machine infrastructure. Blast radius is contained to `docs/gtm/intake/` + `digitalmodel/examples/demos/gtm/` + one README row. Not T3 (no architectural decisions, no new subsystem) and not T1 (multi-file, multi-module, schema design).
