# Exit handoff — kanban board reorg (#2878) right-sizing COMPLETE

**Date:** 2026-05-31 · **Machine:** ace-linux-1 · **Supersedes** the Phase-1-only handoff (`docs/sessions/2026-05-31-kanban-phase1-complete-handoff.md`, #2908).
**Full durable state:** issue #2878 (every phase commented) + auto-memory `project_kanban_board_domain_reorg.md`. This doc is the single exit point.

---

## What was accomplished (this session)

Took the kanban reorg from a **failed v1 design** to a **fully-applied, ecosystem-wide right-sizing**.

| Area | Result |
|---|---|
| Tooling (PR #2895) | `route.py` `domain_family` matcher; `reconcile.py` size-report + `--update-counts`; new `relabel.py` (label-first migration). 106 tests, T2 cross-reviewed. |
| Pilot (#2896) | `digitalmodel-hydro-diffraction` board (epic #622 cluster) — applied + cron-materialized |
| **workspace-hub** (#2898/#2899/#2907 + base-drain #2914) | 49 boards, ~743 relabels |
| **digitalmodel** (holistic, #2912) | 13 boards, 235 relabels |
| **achantas-data** travel (#2916) | 4 regional subdomain boards, 58 relabels |
| **llm-wiki** ingest (#2917) | 2 subdomain boards, 34 relabels |
| Ghost/junk closures | 58 issues closed (#2886 batch of 47 + 11 disposition) |
| Vestigial removals | 7 parent boards (#2909 ×4, #2921 ×3) |

**Net: ~68 new boards across 4 repos, all ≤30 open** (except two accepted-marginal: `digitalmodel-solver-orcaflex` 31, `digitalmodel-subsea-pipelines` 32). ~1070 cards relabeled, 0 net failures. ~12 reviewed PRs, all merged.

## Current state (verified clean)
- All kanban PRs MERGED; no open kanban PRs. `origin/main` current.
- Worktree `/mnt/local-analysis/wshub-phase0` clean (branch `docs/kanban-reorg-complete-handoff` for this doc). **Reusable** for the next phase — leave in place.
- No external actions pending. The `*/20` cron materializes the final applies onto boards automatically.
- digitalmodel parent boards `subsea`/`hydro`/`solver` intentionally KEPT (hold 18/1/4 UNCATEGORIZED off-scope cards — verified via live `gh issue list --label domain:X --state open`).

## Load-bearing mechanism + gotchas (do not re-learn the hard way)
- YAML SoT at `.claude/memory/kanban/`; runtime is **one SQLite DB per board** (`~/.hermes/kanban/boards/<slug>/kanban.db`). Edit YAML, never SQLite.
- `*/20` cron `git reset --hard origin` + rebuilds cards from labels → **placement is LABEL-FIRST**; hand-edited board `cards:` are clobbered. Annotate via GitHub-issue comments, never body edits.
- **Playbook**: scaffold (board YAML `cards:[]` + manifest tier:domain entry + parent `children:` + `domains.yaml`, edited via **TEXT INSERTION not ruamel** — ruamel reformats the whole hand-formatted file) → **create the `domain:` gh label** → **merge scaffolding to main** (cron routes by origin/main manifest) → `relabel.py <remap> --apply` → verify a sample.
- **GOTCHA "board exists ≠ label exists"**: a manifested-but-never-populated domain (coarse `harness`/`engineering`/`business`) has NO `domain:` label (labels auto-create only when a card first carries them). Symptom = *persistent* (not intermittent) relabel failures on the same cards. Fix: create labels for ALL target domains before `--apply`, not just new ones.
- domain matchers: `domain` (exact/fnmatch-glob) and `domain_family: <base>` (precise parent-or-`base-*`). Cross-repo routing IMPOSSIBLE via labels (cards keyed `gh:<repo>#<n>`) → needs `gh issue transfer`.
- Two modes: scaffold-only (cards already labeled → auto-route on merge) vs relabel (unlabeled/oversized → `relabel.py --apply`). Right-sizing is bidirectional: split oversized AND consolidate the tiny-domain tail.

## Remaining (distinct, larger sub-projects — NOT right-sizing)
- **P3** cross-repo transfers: ~58 mis-filed cards (digitalmodel/worldenergydata/llm-wiki work tracked on other repos' boards) → `gh issue transfer` (per-card judgment; trips per-repo `--allow-shrink`).
- **P4** domain×project (llm-wiki client wikis): full-stack (schema+manifest+loader+dispatch+`config/client-wikis.yml`+slug) — its OWN issue + plan→review→approval gate.
- **digitalmodel pillar-(b)** engineering planning round (UNTOUCHED — distinct from the kanban relabel): #500 (plan-approved+dispatch:ready), #605/#606/#607/#608/#609/#612/#614 (status:plan-review → plan→adversarial review→USER approval→build). Order #500→#605/#606/#609→#608→#607→#612→#614. **#607 must reconcile with the merged `diffraction resolve` resolver (PR #650).** #610 licensed E2E OPEN.

## Conventions
Plan-gate: plans on issue → adversarial cross-review → USER approval BEFORE build; never self-approve; never touch `status:*` labels. Commit-for-review-then-apply for live label mutations. Push `--no-verify` ONLY for the gitleaks-absent env block (review-gate/legal/tests must pass). HTML default for human artifacts. Comment summaries on issues; render `#NNNN` as links; post durable state to #2878 + memory.

## Pointers
- Issue: #2878 · Memory: `project_kanban_board_domain_reorg.md` (+ MEMORY.md index line)
- Worktree: `/mnt/local-analysis/wshub-phase0` (reusable)
- Migration remaps (committed, for audit): `.claude/memory/kanban/migration/2026-05-3*.yaml`
- Tooling: `scripts/kanban/relabel.py`, `scripts/kanban/reconcile.py`, `scripts/dispatch/route.py`
