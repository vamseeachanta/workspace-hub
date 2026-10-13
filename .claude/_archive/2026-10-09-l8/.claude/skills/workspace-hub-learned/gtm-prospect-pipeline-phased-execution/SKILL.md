---
name: gtm-prospect-pipeline-phased-execution
description: Phased execution pattern for #2346-style GTM prospect-data pipeline work — canonical vessel fixtures first, then demo-specific materialization, keeping cross-repo CLI/report work deferred until the workspace-hub adapter surface is hardened.
version: 1.0.0
---

# GTM prospect pipeline phased execution

Use when continuing the `#2346` prospect-data pipeline or any similar intake→adapter→demo pipeline where part of the implementation lives in `workspace-hub` and later steps spill into another repo (`digitalmodel`, `aceengineer-website`, etc.).

## When this is the right pattern
- The issue is already `status:plan-approved`
- There is a large approved plan, but the safest next move is a bounded sub-slice
- Canonical input fixtures and adapter logic can be hardened in `workspace-hub` before cross-repo execution work
- You want TDD evidence per slice instead of one giant partially-verified change

## Recommended slice order
1. Add canonical vessel fixtures one at a time
2. Add or tighten adapter validation tests around `canonical_ref`
3. Implement demo-specific `materialize_demo_inputs()` one demo at a time
4. Only after adapter materialization is solid, move to `run_demo()` subprocess dispatch
5. Only after that, touch cross-repo demo CLI flags / branded report / delivery state machine

For `#2346`, the proven order was:
- `pipelay-barge.yaml`
- demo_04 materialization path
- `plsv.yaml`
- next recommended: demos 3/5 `csv_hlv_vessels.json` materialization

## Proven TDD pattern for canonical fixtures
When adding a new canonical YAML:
1. Add a targeted adapter test that references the new `canonical_ref`
2. Run the single test first and confirm failure is specifically `canonical vessel reference not found`
3. Add the YAML file with the required disclaimer + citation block
4. Re-run the targeted test
5. Re-run the whole adapter test file
6. Update `docs/gtm/intake/IMPLEMENTATION-STATUS.md`

This worked for:
- `pipelay-barge.yaml`
- `plsv.yaml`

## Proven TDD pattern for demo-specific materialization
For a demo-specific materialization slice:
1. Add focused tests for the exact files the demo expects in `tmpdir/data/`
2. Keep the change narrow to one demo family at a time
3. Confirm RED while `materialize_demo_inputs()` still raises `NotImplementedError`
4. Implement only the target demo path
5. Keep all other demos explicitly stubbed until their own slice
6. Re-run the whole test file after the narrow pass

For demo_04, the required outputs were:
- `pipelay_vessels.json`
- `pipelines.json`
- optional `prospect_env.json`

## Important validation rule discovered during execution
Do not treat `canonical_ref` existence as sufficient.

You must also validate that the referenced canonical YAML matches the expected demo vessel family.

Concrete bug found in live execution:
- demo_04 declared `shape: pipelay`
- `canonical_ref: seven-borealis` existed on disk
- plain existence-check logic accepted it
- materialization would have silently written a CSV/HLV-style body into the demo_04 pipelay path

Required guard:
- for `pipelay`, canonical body must contain `pipelay_system` and not `crane_main`
- for `csv_hlv`, canonical body must contain `crane_main` and not `pipelay_system`

Always add a negative test for wrong-shape canonical refs when materializing a new demo family.

## Status-doc maintenance rule
After each bounded slice, update `docs/gtm/intake/IMPLEMENTATION-STATUS.md` immediately.

The most useful pattern is:
- move the landed artifact from “Not done” to “Done”
- increase the exact test count
- rewrite the remaining work in terms of the new state (for example, “remaining stub” rather than “fill in the stub”)

This kept the large approved plan operationally readable across multiple small commits.

## Commit discipline for these slices
Each slice should be commit-sized and evidence-rich:
- one canonical vessel fixture + its validating test
- or one demo-specific materialization path + its tests
- not both fixture families and multi-demo materialization in one jump unless the tests force it

Good commit boundaries used successfully:
- `feat(gtm): add canonical pipelay-barge fixture for #2346`
- `feat(gtm): materialize demo_04 prospect inputs for #2346`
- `feat(gtm): add canonical plsv fixture for #2346`

## What to defer on purpose
Do not silently absorb these into the same slice unless the test path truly forces it:
- `run_demo()` subprocess dispatch
- `digitalmodel` CLI flag additions
- branded report wrapper
- dual-delivery state machine
- gated URL / website publishing
- SOP / fallback sidecar / end-to-end workflow

Those belong in later bounded slices.

## Pitfalls
- Do not assume a canonical YAML is correct just because it exists; add a shape-compatibility check
- Do not broaden from one demo family into all demos in the same pass
- Do not mark `#2346` done just because adapter scaffolding or one materialization path passes
- Do not forget to update `IMPLEMENTATION-STATUS.md`; otherwise future sessions lose the exact “what remains” boundary
- Do not start cross-repo `digitalmodel` work until the `workspace-hub` adapter side is stable enough to justify the boundary crossing

## Minimal checklist
- [ ] Add one failing test first
- [ ] Confirm failure reason is the intended missing artifact/behavior
- [ ] Implement only the bounded slice
- [ ] Re-run the targeted test
- [ ] Re-run `uv run pytest scripts/gtm/tests/test_prospect_adapter.py -q`
- [ ] Update `docs/gtm/intake/IMPLEMENTATION-STATUS.md`
- [ ] Post a concise GitHub progress comment with RED/GREEN evidence and what remains
