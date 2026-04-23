# Exit handoff — LLM-wiki / tier-1 repo-routing focus waves

Date: 2026-04-23 17:09 CDT
Repo: `/mnt/local-analysis/workspace-hub`
Branch at exit: `integration/runbook-main-compatible`
Remote main verified at: `c5ef6e1c0`

## Session purpose

User asked to continue the LLM-wiki / knowledge and individual-repo GitHub issue review as parallel focus waves, then asked to document and prepare to exit.

This handoff records what was verified, what was changed, and what the next operator should do.

## High-level outcome

1. `#2460` is complete and landed on `origin/main`.
2. The `#2461`-`#2465` child issues are no longer blocked by `#2460`, but their plans drift from the landed contract and must be patched before implementation.
3. `#2369` readiness mismatch was verified and commented: first Batch Pack 2 execution slice should use DOT + OMAE + OTC, not ISOPE.
4. `#2216` and `#2227` remain `status:plan-review` and are not executable as written.
5. Two new ACMA unblocker issues were created: `#2470` and `#2471`.

## Git / landing state

### `#2460` contract landing

The duplicate background lane reported that the intended isolated clone did not perform the implementation. The real work initially landed on `integration/runbook-main-compatible`.

Verification and recovery performed in this session:

- Verified original landed commit:
  - `8e7b65a3d` — `docs(standards): add tier1 indexing contract for #2460`
- Found residual contract ambiguity: registry path still not exact enough.
- Patched contract + tests to lock canonical per-repo registry path:
  - `docs/registry/module-routing.yaml`
- Committed patch on integration branch:
  - `461e03f23` — `docs(#2460): lock tier1 registry path`
- Cherry-picked the two #2460 commits onto a clean main-line clone and pushed to `origin/main`:
  - `64dcee13c` — contract/checklist/tests
  - `c5ef6e1c0` — registry path lock

Verification after push:

```bash
git fetch origin main --quiet
git rev-parse --short origin/main
# c5ef6e1c0

git merge-base --is-ancestor c5ef6e1c0 origin/main
# ancestor_rc=0
```

### Validation run before main push

In clean main-line clone `/mnt/local-analysis/worktrees/workspace-hub-2460-exec-clone`:

```bash
uv run pytest tests/docs/test_tier1_indexing_contract.py -v
# 12 passed

uv run pytest tests/docs/test_banned_stale_references.py -v
# 16 passed
```

The same validation also passed in the main working checkout after the registry-path patch.

### Current local checkout status

At exit, the current working checkout is still not clean. Remaining dirty files are unrelated provider/quota/report churn and one nested modified worktree entry:

- modified provider/quota files under `config/ai-tools/`
- modified provider reports under `docs/reports/`
- untracked review prompt/output for `#2452` under `.planning/quick/`
- modified nested worktree pointer: `.planning/quick/issue-2408-staging`

Do not confuse these with the `#2460` landed artifact set.

## GitHub comments / issue actions performed

### Posted comments

- `#2369` readiness correction:
  - https://github.com/vamseeachanta/workspace-hub/issues/2369#issuecomment-4307803018
- `#2460` focus-wave gate check:
  - https://github.com/vamseeachanta/workspace-hub/issues/2460#issuecomment-4307806104
- `#2460` execution-start note:
  - https://github.com/vamseeachanta/workspace-hub/issues/2460#issuecomment-4307936690
- `#2227` blocker reconciliation:
  - https://github.com/vamseeachanta/workspace-hub/issues/2227#issuecomment-4307946594
- `#2216` blocker reconciliation:
  - https://github.com/vamseeachanta/workspace-hub/issues/2216#issuecomment-4307949156
- `#2460` final main-line verification:
  - https://github.com/vamseeachanta/workspace-hub/issues/2460#issuecomment-4308108328

### New issues created

- `#2470` — `feat(acma-codes): produce readable source-grounded summaries for OCIMF/CSA wiki promotion`
  - https://github.com/vamseeachanta/workspace-hub/issues/2470
- `#2471` — `feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract`
  - https://github.com/vamseeachanta/workspace-hub/issues/2471

## Current issue state snapshot

- `#2460` — CLOSED, `status:plan-approved`, priority high
  - Contract/checklist/tests landed on `origin/main`.
- `#2461` — OPEN, `status:plan-approved`, priority high
  - READY_AFTER_PATCH; plan path/scope drift must be fixed before execution.
- `#2462` — OPEN, `status:plan-approved`, priority high
  - READY_AFTER_PATCH; plan path/scope drift must be fixed before execution.
- `#2463` — OPEN, `status:plan-approved`, priority medium
  - READY_AFTER_PATCH; plan must absorb required registry file.
- `#2464` — OPEN, `status:plan-approved`, priority medium
  - READY_AFTER_PATCH; plan must add operator map + registry and demote routing index to supplementary curated surface.
- `#2465` — OPEN, `status:plan-approved`, priority medium
  - READY_AFTER_PATCH; plan must make contract/checklist authority and explicitly audit `docs/registry/module-routing.yaml`.
- `#2369` — OPEN, priority high
  - Needs body/plan patch from DOT/OMAE/ISOPE to DOT/OMAE/OTC before execution.
- `#2216` — OPEN, `status:plan-review`, priority medium
  - Needs governance-only redraft; not implementation-ready.
- `#2227` — OPEN, `status:plan-review`, priority medium
  - Not executable; blocked by content readiness and CSA routing decision.
- `#2470` — OPEN, priority medium
  - New ACMA summary-readiness unblocker.
- `#2471` — OPEN, priority medium
  - New CSA wiki routing/durability unblocker.

## Landed `#2460` contract decisions that child plans must use

1. Operator map host/path:
   - per-repo `docs/maps/<repo>-operator-map.md`

2. Canonical machine-readable registry path:
   - per-repo `docs/registry/module-routing.yaml`

3. Workspace-hub scorecards:
   - local attestation only
   - not canonical authority
   - exact negative authority sentence is in the contract/checklist

4. Freshness audit:
   - `daily freshness review`
   - every 24 hours / once per day minimum
   - refresh/regenerate `docs/reports/tier-1-indexing-freshness-latest.md`
   - `#2465` is the follow-through issue

## Next recommended wave

Do a planning-patch wave for `#2461`-`#2465` before any implementation wave.

### `#2461` patch requirements

Status: READY_AFTER_PATCH

Patch the plan to:

- replace workspace-hub-hosted operator map references with:
  - `assetutilities/docs/maps/assetutilities-operator-map.md`
- replace registry placeholder with:
  - `assetutilities/docs/registry/module-routing.yaml`
- remove stale `#2460` gate language now that `#2460` is landed
- update status/review text that still says draft/blocked if present
- narrow owned paths to repo-local canonical surfaces
- fix coverage logic so actual routed `assetutilities` surfaces are covered, not only `__init__.py` package directories

### `#2462` patch requirements

Status: READY_AFTER_PATCH

Patch the plan to:

- replace workspace-hub-hosted `docs/maps/digitalmodel-operator-map.md` with:
  - `digitalmodel/docs/maps/digitalmodel-operator-map.md`
- replace `specs/module-registry.yaml` / placeholder language with:
  - `digitalmodel/docs/registry/module-routing.yaml`
- remove stale `#2460` gate language
- treat existing workspace-hub OrcaWave/OrcaFlex map as supplementary/historical, not canonical
- replace fixed “30 domains” prose with live-tree-derived wording

### `#2463` patch requirements

Status: READY_AFTER_PATCH

Patch the plan to:

- replace “proposed under #2460” language with landed contract/checklist refs
- expand from routing triad to full required routing set
- add:
  - `aceengineer-website/docs/registry/module-routing.yaml`
- add tests/acceptance for registry exposure
- state scorecards/freshness report are attestation only

### `#2464` patch requirements

Status: READY_AFTER_PATCH

Patch the plan to:

- remove `#2460`-pending gate language
- frame `docs/TIER1_ROUTING_INDEX.md` as supplementary curated routing surface, not the only canonical surface
- add:
  - `docs/maps/workspace-hub-operator-map.md`
  - `docs/registry/module-routing.yaml`
- update `docs/README.md` and `docs/CONTENT_INDEX.md` expectations accordingly

### `#2465` patch requirements

Status: READY_AFTER_PATCH

Patch the plan to:

- change authority from scorecard to landed contract + checklist
- audit exact per-repo path:
  - `docs/registry/module-routing.yaml`
- add finding types for missing / wrong registry path
- add fixture case for non-canonical registry path or missing module-routing.yaml

## ACMA / LLM-wiki next work

### `#2369`

Do not execute until issue/plan references are corrected:

- First Batch Pack 2 execution slice should be DOT + OMAE + OTC.
- ISOPE is not ready for this issue because:
  - catalog status is `not_indexed`
  - `conference-phase-a-results.jsonl` has 0 ISOPE rows
- ISOPE appears in inventory/index artifacts, but not in the phase-A summary output surface required by Batch Pack 2.

### `#2216`

Redraft as governance-only umbrella/current-state reconciliation.

Remove direct implementation file-change/test sections because source registration, ledger, accessibility, and related child work already landed or was split.

### `#2227`

Do not approve/execute current plan.

Blockers:

- #2227 target summary artifacts exist but have empty `summary` fields.
- `docs/reports/acma-wiki-unblock-2245-handoff.yaml` says `ready_for_2227: false`.
- CSA routing/durability is unresolved.

Use new blockers:

- `#2470` for readable source-grounded summaries
- `#2471` for sanctioned CSA wiki routing/durability

After those resolve, rewrite #2227 as a non-conditional implementation-only plan, ideally OCIMF-only first if CSA is still unresolved.

## Process lessons from this session

1. Isolated-clone dispatch can silently fail if the subagent sandbox is scoped only to the main checkout. Use `--add-dir` / equivalent or dispatch within the allowed tree.
2. After Claude/background execution, verify commit location vs intended worktree before trusting the final report.
3. Separate remote landing truth from local checkout cleanliness.
4. For child waves, do not trust live `status:plan-approved` alone when plan text still has stale gates; reconcile plan text against landed parent contracts first.

## Suggested next commands

```bash
cd /mnt/local-analysis/workspace-hub

git fetch origin main

git merge-base --is-ancestor c5ef6e1c0 origin/main && echo '#2460 is on origin/main'

# Start next wave as plan patching, not implementation:
# - #2461/#2462 in one parallel lane
# - #2463/#2464/#2465 in another parallel lane
# Keep edits to docs/plans/*246[1-5]* first, then rerun adversarial review/approval-state reconciliation as needed.
```

## Exit caveats

- Main checkout branch `integration/runbook-main-compatible` contains local branch history ahead of `origin/main` plus unrelated dirty provider/report churn.
- `origin/main` is the canonical landing target for #2460 and is at `c5ef6e1c0` at the time of this handoff.
- Do not start #2461-#2465 implementation directly from stale child plan text. Patch plans first.
