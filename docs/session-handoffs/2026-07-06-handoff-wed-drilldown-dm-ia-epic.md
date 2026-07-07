# Session handoff — wed drill-down completion (#848/#849/#850) + dm capabilities IA (#1444)

> Date: 2026-07-06 · Machine: ace-linux-1 · Session: Claude (Fable 5) main
> Scope: owner request "capabilities pages for dm+wed; wed flow high-level → drill-down; track each phase vs the norm; issues as needed" + follow-ups ("dm menu grown a lot", nav linking)

## Shipped (all merged by owner, all verified on origin/main by content)

| Issue | PR | Delivered |
|---|---|---|
| wed #848 phase norms | #862 | `phase_norms` engine (leave-one-field-out play baselines, golden gate 184/46.5 exact), vs-norm chips on 10 posters, 5 stage pages, `_norms.json` contract. LIVE. |
| wed #849 well economics | #864 | `well_economics` engine (rig-days × `RegionalCostLoader`, benchmark revenue verbatim, indicative/degraded/suppressed coverage matrix), econ cards on 5 well pages + norm chips. LIVE. |
| wed #850 nav spine | #870 | Stdlib-only `scripts/site_nav.py` + `config/nav_spine.json` manifest; crumbs on ~13 families (8 dead-ends eliminated); link-graph CI gate (existence/exact-trail/fragments/BFS). Gate caught 2 REAL pre-existing defects on first run (phantom `#serviceability` id; 4 dead atlas hrefs). |
| dm #1444 capabilities IA | #1455 | 7-cluster taxonomy (machine SoT YAML), PR-evidenced recency metadata, generated reference index + spec, anchor-stability contract, `--check` freshness gate, DOMAINS + quality-gates CI wiring. |

Also: wed #848/#849/#850 + dm #1444 filed at session start from the owner's drill-down vision; skill `.claude/skills/workspace-hub-learned/wed-field-hub-drilldown-pages/SKILL.md` created; **dm #1456 filed** (10 section one-pager PDF gaps) with planner head-start intel on the issue.

## Governance trail
Every issue: plan (workspace-hub `docs/plans/2026-07-06-issue-*`) → 2-provider adversarial review (all 8 rounds returned MAJOR; r3 inline patches per `feedback_r3_inline_loop_break_pattern`) → owner approval in-session → TDD implementation → owner merge. Markers `.planning/plan-approved/{wed-848,wed-849,wed-850,dm-1444}.md` on remote; README index rows `completed`. Review artifacts local-only (`scripts/review/results/`, gitignored by convention) — durable evidence in issue comments.

## Next steps (owner-gated)
1. **dm #1456** — 10 section one-pager PDFs; at `needs-plan`; planner intel on the issue (SPECS entry shape, scoped builds, Chrome/sandbox, freshness-gate completion signal).
2. wed epic #754 remaining children: #756 (field hub page), #757 (economics subsection), #759, #761 — untouched by this session.
3. Country baselines for #848's ROADMAP chips ride on wed #681 (drilling-well database).
4. dm revamp lane (dormant): inherits `docs/capability-map/capabilities-ia-spec-1444.md` + anchor contract as input.

## Dirty exceptions / preserved state
- **workspace-hub stash `recovered-autostash-wed850` KEPT deliberately** — holds a provider-cron's uncommitted `config/ai-tools/*` telemetry (not this session's to drop). Disposition owner: provider-utilization cron / next ops session.
- workspace-hub main checkout carries the usual bridge-managed `.claude/memory` + auto-state dirt (auto-sync owns it). Local main may lag origin by design; auto-sync reconciles.
- All feature worktrees/branches removed (wed ×3, dm ×1, push-worktrees ×4). No orphan locks left by this session.

## Operational lessons (recorded in auto-memory topics)
- **workspace-hub live-writer git race**: autostash+rebase loses to cron writers even with `--autostash`; the working pattern is sparse temp-worktree cherry-pick push (`git worktree add --no-checkout` + `sparse-checkout set docs/plans` + cherry-pick + `push HEAD:main`). Zombie `rebase-merge` dirs holding only `autostash` = killed attempts; recover the stash SHA via `git stash store`, then remove.
- **Deploy parity (wed)**: Pages runs `build_pages.py` on bare python3.11, no deps — site tooling must be stdlib-only (AST-guard-tested); registries JSON not YAML.
- **dm new-test-domain contract = TWO registries**: `tests/DOMAINS.md` AND `.claude/quality-gates.yaml` (`tests-<domain>` key), else `KeyError` in the gate reader.
- **dm worktrees**: full checkout times out; use `--no-checkout` + sparse (include `assets/logo` — `build_onepagers` reads it at import).
- **dm git history truncated to 19 commits** (2026-07 slim): git-derived dating/forensics invalid; use `gh` PR metadata.
- isort is now **8.0.1** in wed's uv.lock (older notes said 6.0.1); `mergeStateStatus: UNSTABLE` = checks still running, not a failure state.

## No-external-action status
No emails sent, no publishes beyond the four owner-merged PRs and GitHub issues/comments; no secrets touched; no destructive git anywhere (one `reset --hard` inside a throwaway sparse push-worktree only).
