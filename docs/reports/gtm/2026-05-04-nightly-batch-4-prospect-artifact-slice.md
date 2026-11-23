# GTM nightly batch 4/5 — 2026-05-04 prospect-artifact slice

Generated: 2026-05-04 06:47 UTC
Repository: `vamseeachanta/workspace-hub`
Scope: GTM engineering artifacts and issue-plan readiness only; no outbound outreach.

## Live GTM issue inventory

| Issue | State observed | Labels / role | Batch decision |
|---|---|---|---|
| [#2346](https://github.com/vamseeachanta/workspace-hub/issues/2346) | OPEN | `domain:gtm`, `cat:engineering`, `status:plan-approved`, `status:working` | Only approved implementation lane found. Implemented one bounded workspace-hub slice: private fallback sidecar writer + package-exclusion guardrails. |
| [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) | CLOSED | `domain:gtm`, `status:done` | Capability-chart assets remain reusable brochure/report inputs. |
| [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) | CLOSED | `domain:gtm`, contractor matrix | No action; treated as landed source material only. |
| [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) | CLOSED | `domain:gtm`, brochure/send tracker | No outbound action; send tracker must remain owner-controlled. |
| [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) | CLOSED | `domain:gtm`, evidence-fill follow-up | No action; evidence-fill lane appears landed. |
| [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561) | CLOSED | `domain:gtm`, FOWT worked example | Potential reusable artifact family for a future approved report lane. |
| [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) | CLOSED | `domain:gtm`, GoM evidence lane | Potential reusable evidence family for a future approved report lane. |

Open `domain:gtm` inventory still includes planning/backlog items such as #2557, #2356, #2355, #2351, #2350, #2349, #2347, #2345, #2117, #2114, #2038, #2037, #2035, #2016, #1994, #1993, #1792, #1669, #197, #191, #117, and #108. None of these carried `status:plan-approved` in the live query except #2346.

## Recent GTM reports/assets after #2555

Confirmed reusable chart collateral under `docs/reports/gtm/assets/`:

- `c1-vessel-job-capability-heatmap.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `c2-pipelay-operating-envelope.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `c3-crane-utilisation-margin-map.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `vessel-capability-chart-pack-manifest.json`

Confirmed legal/provenance scan artifacts:

- `docs/reports/gtm/legal-scans/2026-04-30-chart-pack-scan.json`
- `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`

Confirmed sendable-bundle media already exists under `docs/gtm/sendable-bundles/2026-05-01/proof/`, but this batch did not send or publish anything.

## Gaps after #2555 / #2554 / #2556 closure

1. #2346 still needs executable demo dispatch (`run_demo()`), separate `digitalmodel` demo CLI flags, branded report wrapping, and the delivery state machine before a true 48-hour customized-demo pipeline is complete.
2. Delivery mechanics remain intentionally unexercised: no email sending, no private URL publication, no prospect contact, and no claim of customer delivery.
3. Future contractor-facing report families should choose one of the now-landed evidence/chart families and turn it into a plan-approved implementation lane before code or public collateral changes proceed.
4. Public-safe metadata must continue using logical repo paths only; runtime received prospect YAMLs, logos, generated prospect outputs, and private fallback logs must stay gitignored.

## Batch 4 approved implementation slice — #2346

Because #2346 is the only live `domain:gtm` issue with `status:plan-approved`, this batch implemented one bounded workspace-hub artifact slice:

- Added `write_fallback_sidecar()` in `scripts/gtm/prospect_adapter.py`.
  - Writes `private-log/fallback-applied.json` under the caller's runtime root.
  - Validates fallback code enum `F1`-`F5` and pre-authorization enum `explicit | implicit_allowlist | none`.
  - Rejects absolute local paths in `field_substituted` and `canonical_source` metadata to prevent workstation/proprietary path leakage.
- Added `exclude_private_fallback_sidecars()` in `scripts/gtm/prospect_adapter.py`.
  - Removes `private-log` entries and `fallback-applied.json` from email attachment / gated URL file lists.
- Added `.gitignore` guards for #2346 runtime-private paths:
  - `docs/gtm/intake/received/`
  - `docs/gtm/intake/logos/`
  - `digitalmodel/examples/demos/gtm/private-log/`
  - `digitalmodel/examples/demos/gtm/tests/fixtures/prospect-outputs/`
- Extended `scripts/gtm/tests/test_prospect_adapter.py` with TDD coverage for sidecar writing, invalid fallback-code rejection, package-list exclusion, and `git check-ignore` coverage.
- Updated `docs/gtm/intake/IMPLEMENTATION-STATUS.md` so the #2346 ledger reflects this slice as done while keeping the full issue open.

This slice does not produce a prospect report, does not send outreach, and does not mark #2346 complete.

## Verification

- `uv run pytest scripts/gtm/tests/test_prospect_adapter.py scripts/gtm/tests/test_prospect_demo_sop.py -q` → PASS, 22 tests.
- `uv run python -m py_compile scripts/gtm/prospect_adapter.py` → PASS.
- `bash scripts/legal/legal-sanity-scan.sh --diff-only` → PASS before writing this report; rerun required after this report is staged.

## Next GTM decisions needing owner approval

1. Approve the next #2346 implementation slice: `run_demo()` subprocess dispatch + output discovery, or defer until the separate `digitalmodel` CLI flag patches are approved.
2. Decide which post-#2555 asset family should become the next plan-approved contractor-facing report: vessel capability pack, FOWT mooring worked example, or GoM niche contractor evidence lane.
3. Confirm delivery mechanics policy before any future automation touches email, gated URLs, or send trackers. Current safe default remains: generate artifacts only; no outbound outreach.
