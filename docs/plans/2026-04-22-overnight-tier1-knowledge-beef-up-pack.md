# Overnight tier-1 knowledge beef-up pack

Date: 2026-04-22
Repo: `/mnt/local-analysis/workspace-hub`
Mode: Claude-only, planning/audit/prompt-hardening overnight run until tomorrow
Purpose: strengthen the llm-wiki + repo-routing ecosystem without requiring extra user approvals

## Objective

Use three self-contained overnight Claude terminals to improve the repo ecosystem around the durable knowledge layer:
- keep llm-wiki / knowledge-base work connected to repo execution reality
- harden the tier-1 routing/index contract
- prepare approval-ready or execution-ready planning artifacts for the next day
- avoid git contention completely

This is a repo-betterment / beef-up wave. It is planning-first, non-destructive, and does not require additional user approval before running.

## Live issue set in scope

| Issue | Title | Terminal |
|---|---|---|
| #2390 | epic(knowledge): llm-wiki strengthening roadmap and execution waves | T1 |
| #2460 | feat(repo-organization): tier-1 indexing and code-placement contract | T1 |
| #2464 | chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise | T1 |
| #2461 | chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work | T2 |
| #2462 | feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | T2 |
| #2463 | chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup | T3 |
| #2465 | feat(automation): daily tier-1 indexing freshness audit and scorecard refresh | T3 |

## Terminal assignment rationale

### Terminal 1 — contract + control plane
Owns the ecosystem contract and workspace-hub control-plane routing surfaces.

### Terminal 2 — engineering-core repos
Owns the two highest-value repo-routing remediations where future engineering issue work lands.

### Terminal 3 — website + sustaining automation
Owns the GTM/externalization repo and the recurring freshness audit loop.

## Git contention avoidance map

| Terminal | Allowed write paths |
|---|---|
| T1 | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`, `docs/plans/2026-04-22-issue-2464-*.md`, `docs/plans/README.md` for only #2460/#2464 rows, `docs/reports/2026-04-23-terminal-1-tier1-contract-summary.md`, `scripts/review/results/*2460*`, `scripts/review/results/*2464*` |
| T2 | `docs/plans/2026-04-22-issue-2461-*.md`, `docs/plans/2026-04-22-issue-2462-*.md`, `docs/plans/README.md` for only #2461/#2462 rows, `docs/reports/2026-04-23-terminal-2-engineering-routing-summary.md`, `scripts/review/results/*2461*`, `scripts/review/results/*2462*` |
| T3 | `docs/plans/2026-04-22-issue-2463-*.md`, `docs/plans/2026-04-22-issue-2465-*.md`, `docs/plans/README.md` for only #2463/#2465 rows, `docs/reports/2026-04-23-terminal-3-website-automation-summary.md`, `scripts/review/results/*2463*`, `scripts/review/results/*2465*` |

Zero overlap is mandatory.

## Negative write boundaries

- T1 must not edit #2461/#2462/#2463/#2465 plan files or their review artifacts.
- T2 must not edit #2390/#2460/#2464/#2463/#2465 plan files or their review artifacts.
- T3 must not edit #2390/#2460/#2464/#2461/#2462 plan files or their review artifacts.
- No terminal may write to `.planning/plan-approved/`, `src/`, `tests/`, nested tier-1 repos, or implementation code.
- No terminal may change approval labels to `status:plan-approved`.

## Execution rules for every terminal

1. Planning and adversarial review only.
2. No implementation code changes.
3. No user questions.
4. Use live GitHub issue state and current repo files; do not trust stale notes blindly.
5. If a canonical plan is missing, create it from `docs/plans/_template-issue-plan.md`.
6. If a plan exists, tighten it to be more approval-ready and truth-aligned.
7. Save review artifacts under `scripts/review/results/`.
8. Post concise GitHub comments describing plan state, blockers, and next step.
9. Do not create approval markers.
10. Prefer conservative status wording unless real review evidence supports stronger claims.

## Prompt files

- `docs/plans/overnight-prompts/2026-04-22-tier1-knowledge-beef-up/terminal-1-contract-and-control-plane.md`
- `docs/plans/overnight-prompts/2026-04-22-tier1-knowledge-beef-up/terminal-2-engineering-core-and-utilities.md`
- `docs/plans/overnight-prompts/2026-04-22-tier1-knowledge-beef-up/terminal-3-website-and-automation.md`

## Suggested launch pattern

In separate terminals:

```bash
cd /mnt/local-analysis/workspace-hub
PROMPT=$(< docs/plans/overnight-prompts/2026-04-22-tier1-knowledge-beef-up/terminal-1-contract-and-control-plane.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/claude-tier1-terminal-1.log
```

Repeat for terminals 2 and 3 with the matching prompt file.

## What you should have by morning

From Terminal 1:
- refreshed roadmap linkage between llm-wiki and tier-1 routing work
- tightened or created canonical plans for #2460 and #2464
- a control-plane summary artifact

From Terminal 2:
- tightened or created canonical plans for #2461 and #2462
- review artifacts for the engineering-core repo routing wave
- an engineering-routing summary artifact

From Terminal 3:
- tightened or created canonical plans for #2463 and #2465
- a defined daily-freshness planning path
- a website/automation summary artifact

## Success condition

By tomorrow, the repo ecosystem should have a cleaner, better-linked, more execution-ready plan set for the llm-wiki + tier-1 routing wave, with no git collisions and no ambiguous ownership.
