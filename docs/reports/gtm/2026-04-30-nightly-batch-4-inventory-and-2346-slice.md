# GTM nightly batch 4/5 — inventory and #2346 bounded implementation slice

Generated: 2026-04-30 UTC; refreshed by cron batch 4/5 on 2026-05-01 UTC
Repository: `vamseeachanta/workspace-hub`
Scope: GTM engineering artifacts and issue-plan readiness only; no outbound outreach.

## Live GTM issue inventory

| Issue | State observed | Labels / role | Nightly decision |
|---|---|---|---|
| [#2346](https://github.com/vamseeachanta/workspace-hub/issues/2346) | OPEN | `status:plan-approved`, `status:working`, `cat:engineering`, `domain:gtm` | Approved implementation lane. Batch 4 executed one bounded workspace-hub adapter slice. |
| [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) | CLOSED | `status:done` per handoff | Vessel capability chart pack already landed; treat as source asset for #2556 after evidence gates clear. |
| [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) | OPEN | `status:blocked`, contractor outreach matrix | Still blocked on official evidence fill (#2560) and re-review. No outreach. |
| [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) | OPEN | brochure + outbound tracker | Do not assemble/send until #2554/#2560 clears or owner explicitly waives dependency and approves send. |
| [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) | OPEN | high-priority evidence fill | Next planning/artifact lane: official-domain deep-link and pain-point evidence for high-priority vessel contractors. |
| [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561) | OPEN | FOWT mooring worked example | Good candidate for plan hardening; no implementation without approval. |
| [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) | OPEN | GoM niche evidence lane | Good candidate for artifact discovery; no implementation without approval. |

Additional open `domain:gtm` backlog observed includes #2422, #2356, #2355, #2351, #2350, #2349, #2347, #2345, #2117, #2115, #2114, #2038, #2037, #2035, #2030, #2016, #1994, #1993, #1792, #1669, #197, #191, #117, and #108.

## Recent GTM reports/assets after #2555

The #2555 chart-rendering slice produced the following public-facing collateral assets under `docs/reports/gtm/assets/`:

- `c1-vessel-job-capability-heatmap.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `c2-pipelay-operating-envelope.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `c3-crane-utilisation-margin-map.{brochure.png,print.svg,1page.pdf,caption.txt,metadata.json}`
- `vessel-capability-chart-pack-manifest.json`
- Legal scan artifact: `docs/reports/gtm/legal-scans/2026-04-30-chart-pack-scan.json`

Open GTM collateral scaffolds already present:

- `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`

## Gaps after #2555

1. #2555 chart assets are ready as brochure inputs, but #2554 is still blocked by contractor evidence quality.
2. #2556 remains gated because the brochure/send tracker must not consume an unapproved or evidence-thin contractor matrix.
3. #2346 still lacks demo subprocess dispatch, digitalmodel per-demo CLI flags, branded report wrapping, and executable dual-delivery state-machine code. The workspace-hub SOP runbook is now hardened and test-covered.
4. Public-facing claims need continued provenance checks against repo evidence before promotion into brochure copy.
5. No outbound contact is authorized by this batch.

## Batch 4 approved implementation slice — #2346

Because #2346 is already `status:plan-approved`, this batch implemented one bounded workspace-hub adapter slice:

- Added `demo_03` materialization to `scripts/gtm/prospect_adapter.py`.
- Demo 3 prospect intake now writes:
  - `tmpdir/data/csv_hlv_vessels.json`
  - `tmpdir/data/mudmat_structures.json`
  - optional `tmpdir/data/prospect_env.json`
- Added TDD coverage in `scripts/gtm/tests/test_prospect_adapter.py` for canonical heavy-lift CSV + mudmat materialization.
- Hardened the public-safe #2346 SOP at `docs/gtm/prospect-demo-sop.md` with:
  - no-outbound-outreach boundary,
  - 48-hour decision tree,
  - F1-F5 refuse-vs-fix matrix,
  - `private-log/fallback-applied.json` sidecar schema,
  - email-first/no-private-URL-on-email-failure delivery invariant,
  - logical-path-only rule for public artifacts.
- Added `scripts/gtm/tests/test_prospect_demo_sop.py` to enforce the SOP contract and catch local/proprietary path leakage.
- Updated `docs/gtm/intake/IMPLEMENTATION-STATUS.md` so the remaining #2346 gap list reflects that demos 3/4/5 have workspace-hub materialization support and the SOP artifact slice is done.

This does not send any outreach, does not publish a private URL, and does not claim #2346 complete.

## Remaining #2346 work needing future approval/execution discipline

- Implement `run_demo()` subprocess dispatch and output discovery.
- Patch the separate `digitalmodel` demo scripts to accept prospect data-directory/environment/branding flags.
- Build branded report wrapper.
- Implement executable dual-delivery state machine only after explicit approval for delivery mechanics; no email or message sending in this batch.
- Re-run public-facing legal/provenance checks before any brochure/report leaves the repo.
