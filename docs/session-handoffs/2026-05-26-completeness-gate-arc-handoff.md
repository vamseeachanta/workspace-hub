# Session handoff — #2798 completeness-gate arc

- **Date:** 2026-05-26 · **Machine:** ace-linux-1 · **Issue:** [#2798](https://github.com/vamseeachanta/workspace-hub/issues/2798)
- **Status:** BUILD COMPLETE — gate implemented, hardened, merged, comprehensive. One human step remains (verify+close #2798).

## What shipped (all merged to main)

| PR | What | Why |
|---|---|---|
| #2800 | Gate implementation (score module, gate decision, runner, GH Action, advisory script, HTML renderer, rule, wiring) | the capability |
| #2803 | Opt-in (`gate:completeness`) + inert-when-unconfigured | post-merge the gate reopened its own issue (owners unset, owners-check before scope) |
| #2807 | `verifier≠closer` made opt-in (`COMPLETENESS_REQUIRE_SEPARATE_CLOSER`) | dogfood found it blocked solo operation (same actor verifies+closes) |
| #2808 | Auto-apply `gate:completeness` on `status:plan-approved` | keep coverage comprehensive for new work |

Plus: 910/910 open issues bulk-labeled `gate:completeness`; repo var `COMPLETENESS_OWNERS=vamseeachanta` set; labels `gate:completeness` + `status:completeness-verified` created.

## How the gate works (operating procedure)

The gate enforces at `gh issue close` for issues that are **`completed` + `gate:completeness` + `status:plan-approved`**. To close such an issue:

1. **Compute** the completeness record: `code` class (changed files map to a `src/<pkg>/` package → reuses #1629 `quality_score`/`test_source_ratio`, fail-closed on stale snapshot, threshold 90) or `evidence` class (ops/docs/governance → weighted met-evidence ratio, threshold 80). Module: `scripts/workflow/completeness_score.py`.
2. **Stamp** the record on the issue body as a fenced ```completeness {json}``` block (must include `issue_number` + `cls`; `generated_at`). Optionally render `docs/reports/<date>-<issue>-completeness.html` via `render_completeness_html.py`.
3. **Owner verifies** by applying `status:completeness-verified` — **a human owner's act** (a `COMPLETENESS_OWNERS` member; the runner rejects others). Apply it **after** the body stamp (freshness check) and don't edit the body afterward.
4. **Close** (`--reason completed`). The Action (`.github/workflows/completeness-gate.yml`) checks: record present + bound to issue, threshold from server-side config (not the body), owner-applied label, body-fresh, pct ≥ threshold. On fail it **reopens + comments**.

Pre-flight locally: `COMPLETENESS_OWNERS=… scripts/enforcement/check-completeness-before-close.sh <issue>` (advisory; `COMPLETENESS_ALLOW=1` bypass).

## Pending HUMAN actions (kept in the loop — agent will not do these)

1. **Verify + close #2798** (the dogfood capstone): record is stamped (100%, evidence). Apply `status:completeness-verified`, then `gh issue close 2798 --reason completed`. Gate will ALLOW.
2. **Progress the other 41 plan-approved issues** via the ranking dashboard `docs/reports/2026-05-26-completeness-ranking-plan-approved.html` (sorted closest-to-done; #2695 leads at 92%). Each needs a record stamped, then owner verify + close.
3. **Optional:** repo ruleset restricting who can apply `status:completeness-verified` (defense-in-depth; the runner already rejects non-owner appliers). Set `COMPLETENESS_REQUIRE_SEPARATE_CLOSER=1` only if you want team separation-of-duties.

## Lessons (in memory: `feedback_completeness_score_before_closure`)
- Ship fail-closed enforcement gates **opt-in + inert-when-unconfigured** (a gate without a rollout ramp reopened its own issue on merge).
- Don't bake **team-shaped separation-of-duties** into controls a **solo operator** must pass (verifier≠closer blocked solo verify+close).
- Each validation layer (plan review → code review → production merge → dogfood) caught a *different* defect class — the design converged through use.
