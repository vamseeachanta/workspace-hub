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
- `scripts/gtm/prospect_adapter.py` — interface + two validation gates:
  `load_and_validate()` (schema + cross-field checks) plus stubbed
  `materialize_demo_inputs()` and `run_demo()` raising NotImplementedError
  with descriptive messages. Argparse CLI with `--demo` and `--dry-run`.
  Type hints throughout; no `Any`.
- `scripts/gtm/tests/test_prospect_adapter.py` — 7 tests: happy paths
  (demo_05 + canonical Seven Borealis, demo_04 + canonical pipelay barge),
  malformed YAML rejection, Q6 demo_01 + vessel rejection, Q6 demo_03
  missing vessel rejection, stub NotImplementedError wiring for both
  deferred functions.
- `jsonschema>=4.26` added to workspace-hub `[project.optional-dependencies].dev`.

## Not done (follow-up work)

Future work on #2346 will need to land, in roughly this order:

- **Canonical vessels — remaining 1**: add `plsv.yaml` (PLSV class,
  TechnipFMC *Deep Energy* + OTC-25303 + DNV-RP-H103). Follow the
  2-citation-per-vessel rule from plan section "Canonical Vessel Source
  Pins".
- **`materialize_demo_inputs` per-demo logic**: fill in the stub. Write
  `csv_hlv_vessels.json` for demos 3/5, `pipelay_vessels.json` for demo 4,
  `<structure-kind>.json` for the structure body, and optional
  `prospect_env.json` for environment overrides. Honor
  `vessel.source == canonical_ref` by loading the referenced YAML and
  inlining its body.
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
