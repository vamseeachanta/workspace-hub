# #2346 Prospect Data Pipeline — Implementation Status

Tracks progress against the approved plan at
`docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` (v3.1-APPROVED).

> This is scaffolding only. Full implementation is a follow-up task. Do NOT
> mark #2346 as done until every item in the "Not done" section below reads
> DONE.

## Done (scaffold — T2 part 1 of N)

- `docs/gtm/intake/prospect-schema.json` — executable draft-07 JSON Schema
  per plan section B. Passes `jsonschema.Draft7Validator.check_schema()`.
- `docs/gtm/intake/prospect-template.yaml` — starter YAML intake with every
  field + contract comments.
- `docs/gtm/intake/README.md` — short workflow doc (drop YAML, run adapter,
  receive branded PDF + gated URL).
- `docs/gtm/intake/canonical-vessels/seven-borealis.yaml` — first canonical
  vessel (heavy-lift CSV, DP3 class). Source-pinned to Subsea7 public fleet
  page + OTC-24523 (2013) for particulars and Bai & Bai *Subsea Engineering
  Handbook* 2nd ed. for class-typical RAOs. Disclaimer block stating
  "class-typical, not vessel-specific" included.
- `docs/gtm/intake/canonical-vessels/pipelay-barge.yaml` — second canonical
  vessel (S-lay pipelay barge / Lorelay class-typical reference). Source-
  pinned to the Allseas Lorelay public vessel page + Palmer & King *Subsea
  Pipeline Engineering* for class-typical lay-system / motion envelopes.
  Disclaimer block stating "class-typical, not vessel-specific" included.
- `docs/gtm/intake/canonical-vessels/plsv.yaml` — third canonical vessel
  (PLSV / Deep Energy class-typical reference). Source-pinned to the
  TechnipFMC Deep Energy public vessel page + OTC-25303 / DNV-RP-H103 /
  API 17B/17J installation context for class-typical motion / operability
  envelopes. Disclaimer block stating "class-typical, not vessel-specific"
  included.
- `scripts/gtm/prospect_adapter.py` — interface + two validation gates:
  `load_and_validate()` (schema + cross-field checks) plus partial
  `materialize_demo_inputs()` support for demos 3, 4, and 5. Demo_03 writes
  `csv_hlv_vessels.json`, `mudmat_structures.json`, and optional
  `prospect_env.json`; demo_04 writes `pipelay_vessels.json`,
  `pipelines.json`, and optional `prospect_env.json`; demo_05 writes
  `csv_hlv_vessels.json`, `rigid_jumpers.json`, and optional
  `prospect_env.json` into `tmpdir/data/`. Canonical references are now
  shape-checked (`pipelay` vs `csv_hlv`) before materialization so the wrong
  vessel family cannot be silently inlined. `run_demo()` remains stubbed and
  demos 1/2 still raise NotImplementedError. Argparse CLI with `--demo` and
  `--dry-run`. Type hints throughout; no `Any`.
- `scripts/gtm/tests/test_prospect_adapter.py` — 13 tests: happy paths
  (demo_05 + canonical Seven Borealis, demo_05 + canonical PLSV,
  demo_04 + canonical pipelay barge), negative validation for wrong-shape
  canonical refs, malformed YAML rejection, Q6 demo_01 + vessel rejection,
  Q6 demo_03 missing vessel rejection, demo_03 materialization of csv_hlv
  vessel / mudmat / environment override files, demo_04 materialization of
  pipelay vessel / pipeline / environment override files, demo_05
  materialization of csv_hlv vessel / rigid-jumper files, and stub
  NotImplementedError wiring for `run_demo()`.
- `jsonschema>=4.26` added to workspace-hub `[project.optional-dependencies].dev`.

## Not done (follow-up work)

Future work on #2346 will need to land, in roughly this order:

- **Canonical vessels — done**: `seven-borealis.yaml`, `pipelay-barge.yaml`,
  and `plsv.yaml` now exist under `docs/gtm/intake/canonical-vessels/` with
  the required disclaimer + citation blocks. Remaining work shifts to
  materialization, demo dispatch, and delivery/reporting layers.
- **`materialize_demo_inputs` per-demo logic — workspace-hub layer done for
  vessel-bearing demos**: demos 3, 4, and 5 now materialize their required
  vessel/structure/environment JSON files from prospect YAML into `tmpdir/data/`.
  Remaining adapter materialization work is limited to deciding whether demos
  1 and 2 need prospect-specific pipeline/freespan input overrides despite the
  approved Q6 contract forbidding vessel data for those demos.
- **`run_demo` subprocess dispatch**: subprocess-launch
  `digitalmodel/examples/demos/gtm/demo_0{N}_*.py` with the new
  `--prospect-data-dir` / `--prospect-env` / `--brand-header` /
  `--brand-footer` flags (plan section D), capture the generated HTML
  path, and return it.
- **Per-demo CLI patches in `digitalmodel/`**: extend each of demo_01..demo_05
  `parse_args()` to accept the four new flags. Separate commit in the
  `digitalmodel/` repo.
- **Branded report generation**: `branded_report.py` wrapper that injects
  client header/footer + NDA watermark into the existing demo HTML output
  (plan section E). Must preserve the #2342/#2343 detail-page styling.
- **Dual-delivery state machine**: email + gated private URL on
  `aceengineer-website` under `/private/<hash>/<slug>.html`; includes
  `robots.txt` and `vercel.json` updates per plan v3 Claude M1.
  Partial-failure semantics + retry + compensating actions per plan section
  "Dual Delivery State Machine" (v3 Codex M4).
- **SOP runbook**: `docs/gtm/prospect-demo-sop.md` — the 48hr decision-tree
  runbook per plan section F, plus the refuse-vs-fix matrix for the 5
  authorized fallbacks F1-F5 (plan v2/Q7).
- **Fallback sidecar**: wire the `private-log/fallback-applied.json` path
  (gitignored; test-asserted never-ships) per plan v3 Codex M5.
- **E2E regression suite**: golden-image test that runs all 5 demos on
  canonical fixtures within the <10 min PR-runtime budget using
  `--from-cache`, outputs routed to the gitignored test-only sink at
  `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/`
  (plan v3 Codex M6).

## Explicit non-promise

This scaffold delivers the validation + interface surface. It does NOT
produce a report, does NOT deliver anything, and does NOT exercise any of
the five demos. Any reviewer, PR, or release note claiming #2346 is "done"
based on this scaffold alone is wrong — check against the "Not done" list.
