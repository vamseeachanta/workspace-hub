# Provider Usage + Inventory Readiness Exit Handoff

> **Generated:** 2026-04-25T11:54:01Z  
> **Repository:** `vamseeachanta/workspace-hub`  
> **Worktree:** `/mnt/local-analysis/worktrees/workspace-hub-2487-approval`  
> **Current completed issue:** [#2487](https://github.com/vamseeachanta/workspace-hub/issues/2487)  
> **Final implementation commit:** `e39d28773f28515bd99e4c2de138110b73e33e5f`

## 1. Session outcome

The provider-usage operating model has been converted into a computable inventory-readiness dispatch surface for the full pipeline:

```text
raw data -> inventory -> llm-wiki -> calculation code -> parametric outputs -> website/GTM
```

Completed and closed:

- [#2487 — feat(inventory-readiness): raw-data to GTM readiness matrix and dispatch board](https://github.com/vamseeachanta/workspace-hub/issues/2487)
- Closeout comment: https://github.com/vamseeachanta/workspace-hub/issues/2487#issuecomment-4319069602
- Final state: `CLOSED`

## 2. Landed artifacts

The #2487 implementation landed these durable artifacts:

| Artifact | Purpose |
|---|---|
| `config/knowledge/inventory-readiness.yaml` | canonical machine-readable readiness matrix / dispatch board |
| `scripts/knowledge/validate_inventory_readiness.py` | schema validator and Markdown report renderer |
| `tests/knowledge/test_inventory_readiness.py` | TDD coverage for readiness semantics and report output |
| `docs/reports/inventory-readiness-matrix-2026-04-25.md` | derived dispatch report for operator use |
| `scripts/review/results/2026-04-25-implementation-2487-schema.md` | implementation review evidence: schema/validator lane PASS |
| `scripts/review/results/2026-04-25-implementation-2487-governance.md` | implementation review evidence: governance/closeout lane PASS |

## 3. Validation evidence

Final validation before closeout:

```bash
uv run pytest tests/knowledge/test_inventory_readiness.py -q
uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --validate-only
uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --output docs/reports/inventory-readiness-matrix-2026-04-25.md
uv run python -m py_compile scripts/knowledge/validate_inventory_readiness.py
```

Observed result:

```text
23 passed in 0.62s
valid inventory-readiness matrix: 3 package family/families
wrote docs/reports/inventory-readiness-matrix-2026-04-25.md
final deterministic report check passed
```

Adversarial implementation review:

- Initial review found MAJOR blockers:
  - dispatch dependencies did not mirror actionable non-reference issue refs
  - report did not clearly surface blocked/partial/missing evidence
- Fixes landed:
  - `_validate_dispatch_dependency_mirror(...)`
  - regression coverage for dependency mirroring
  - report section `## Blocked / partial / missing evidence`
- Re-review result:
  - schema/validator lane: `PASS`
  - governance/closeout lane: `PASS`

## 4. Provider usage operating model

Recommended provider order remains:

```text
Codex -> Gemini -> Claude
```

Rationale captured during the workstream:

| Provider | Primary role | Why |
|---|---|---|
| Codex | implementation, tests, calculation code, CI fixes, mechanical refactors | most underused; best aligned with approved implementation packages |
| Gemini | raw data discovery, recon/scouting, source scans, competitor/GTM research, gap discovery | underused; best suited for broad scouting and source/package discovery |
| Claude | planning, adversarial review, synthesis, governance/architecture decisions | conserve for review, plan hardening, and cross-provider synthesis |

Weekly burn target for true weekly quotas:

| Day | Cumulative target |
|---:|---:|
| 1 | 18% |
| 2 | 36% |
| 3 | 54% |
| 4 | 72% |
| 5 | 90% |
| 6 | 95% |
| 7 | 100%, preserving emergency closeout buffer |

Important Gemini caveat:

- If Gemini is hard-capped at `1,000/day`, then only `5,000/7,000 = 71.4%` of the weekly-equivalent budget can be consumed by day 5.
- Under that cap, Gemini should be paced daily rather than forced into a mathematically impossible 90%-by-day-5 weekly burn.

## 5. Current dispatch snapshot

The derived readiness report records the provider queue snapshot from `docs/reports/provider-work-queue.md` as observed values, not acceptance thresholds:

| Queue | Observed count |
|---|---:|
| Codex candidates | 4 |
| Gemini tasks | 1 |
| Claude reviews | 17 |

Current package readiness summary from `docs/reports/inventory-readiness-matrix-2026-04-25.md`:

| Package | Owner | Preferred next | Raw data | Inventory | LLM wiki | Calculation code | Parametric outputs | Website/GTM |
|---|---|---|---|---|---|---|---|---|
| `inventory_readiness_spine` | codex | codex | READY | READY | PARTIAL | PARTIAL | MISSING | PARTIAL |
| `raw_data_scouting_backlog` | gemini | gemini | READY | PARTIAL | MISSING | MISSING | MISSING | MISSING |
| `plan_review_and_governance_backlog` | claude | claude | READY | READY | PARTIAL | PARTIAL | MISSING | PARTIAL |

Readiness semantics:

- `READY` requires concrete implemented artifact evidence.
- Approved plans and downstream issue references may support `PARTIAL`, but cannot be treated as `READY`.
- Downstream issues are candidates/dependencies only; #2487 did not execute them.

## 6. Next recommended execution order

Use the new dispatch board to choose the next package by underused provider and approval state.

### A. Codex lane — next implementation package

1. [#2464](https://github.com/vamseeachanta/workspace-hub/issues/2464) — split curated tier-1 routing index from raw inventory
   - Strongest immediate Codex candidate.
   - Reason: directly strengthens inventory stage and helps create more dispatchable downstream work.

2. [#2465](https://github.com/vamseeachanta/workspace-hub/issues/2465) — daily tier-1 indexing freshness audit and scorecard refresh
   - Execute after re-audit if still plan-approved and scope remains current.
   - Reason: keeps readiness/freshness computable.

### B. Gemini lane — next scouting/research package

1. [#2403](https://github.com/vamseeachanta/workspace-hub/issues/2403) — embeddings model-selection spike
   - Good Gemini candidate because it is research/model-selection heavy.

2. [#2392](https://github.com/vamseeachanta/workspace-hub/issues/2392) — wiki coverage-gap detector
   - Needs planning/approval before implementation.
   - Good Gemini-assisted recon target to identify source/wiki gaps.

### C. Claude lane — next review/governance package

1. Review/harden downstream plans before user approval and provider execution.
2. Prioritize packages that unlock the full chain:
   - [#2464](https://github.com/vamseeachanta/workspace-hub/issues/2464) inventory
   - [#2403](https://github.com/vamseeachanta/workspace-hub/issues/2403) llm-wiki/model selection
   - [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) calculation-output citation contract
   - [#2346](https://github.com/vamseeachanta/workspace-hub/issues/2346) website/GTM customized-demo pipeline

## 7. Operating loop for next session

Start the next session with this loop:

```bash
cd /mnt/local-analysis/workspace-hub
bash scripts/cron/provider-utilization-refresh.sh
uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --validate-only
uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --output docs/reports/inventory-readiness-matrix-$(date -u +%F).md
```

Then pick work by provider underuse:

1. If Codex is below burn line and a `status:plan-approved` implementation package exists, dispatch Codex to the next implementation/test/refactor package.
2. If Gemini daily use is below target, dispatch a scouting/research batch against raw-data/wiki/GTM gaps.
3. If Claude has review backlog, dispatch plan or implementation review packages.
4. If no approved implementation work exists, stop coding and refill the plan-review pipeline.
5. If provider usage is ahead of target, reserve that provider for failures, reviews, and closeout.

## 8. Exit-state cautions

- The isolated #2487 worktree was clean before this handoff note was created.
- Primary checkout `/mnt/local-analysis/workspace-hub` may still be on a planning branch observed earlier as `plan/issue-2369-batch-pack-2`; re-check before using it for mainline work.
- Do not rerun standalone learning/reflection pipelines during active task sessions; defer to the nightly comprehensive-learning pipeline.
- Do not treat the current queue counts as acceptance thresholds; they are observed dispatch-board state.
- Do not mark a stage `READY` from approved-plan evidence alone.

## 9. Clean exit checklist

Before fully exiting or handing off to another operator:

```bash
git status --short --branch
git log --oneline -5
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
gh issue view 2487 --json number,state,closed,url --jq '{number,state,closed,url}'
uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --validate-only
```

Expected scoped outcome:

- #2487 remains closed.
- `config/knowledge/inventory-readiness.yaml` validates.
- The readiness report remains derived from the YAML.
- Any new work proceeds through:

```text
plan -> adversarial plan review -> user approval -> implementation -> adversarial implementation review -> closeout
```
