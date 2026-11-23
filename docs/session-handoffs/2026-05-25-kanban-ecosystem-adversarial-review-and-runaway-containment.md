# Session Handoff — Kanban Ecosystem Adversarial Review + Runaway Containment

- **Date:** 2026-05-25 (~04:50–05:40 CDT)
- **Machine:** `ace-linux-1`
- **Session:** Claude main (`0449266f`)
- **Trigger:** `/goal adversarial review the kanban boards … aggressively suggest improvements inline with the repo missions`
- **Branch:** `docs/kanban-adversarial-review-20260525` (UNPUSHED, local-only)
- **Full record:** memory `project_kanban_ecosystem_runaway_state.md`; report `docs/reports/2026-05-24-kanban-ecosystem-adversarial-review.html`

## Outcome (one line)
Adversarial review delivered; a live 260-worker kanban runaway was found and **contained**; root cause traced to a skill-name collision and the specific offender fixed.

## What the review found (structural — boards still need rework)
- **Source-of-truth inversion:** `auto-decomposer` minted **528 child tasks** that live only in per-machine SQLite (`idempotency_key=NULL`), git-invisible, **duplicate on reload**. Contradicts the tier-0 #1 theme (consolidate memory to Hermes canonical) and "memory is in the repo."
- **Mission-inverted backlog:** workspace-hub (meta/tooling) holds **870/1536 cards (57%)** vs digitalmodel 265 / worldenergydata 68. `harness` board (300) alone > whole engineering product.
- **7 dead tier-0 `spans_boards` links:** `repo-workspace-hub-{hermes,governance,intel,cron}`, `repo-digitalmodel-mooring`, `repo-achantas-data-krishna`, `repo-readiness` — workspace-hub decomposed under two incompatible taxonomies.
- **7 empty tier-1 parents** (incl. GTM-ready worldenergydata with no roll-up). Staleness clean (0 closed mirrored).
- Recommendations R1–R6 in the report.

## Runaway: root cause (traced) — skill-name COLLISION
- Bulk-load → config default `kanban.auto_decompose: true` auto-decomposed triage every tick → spawned workers on 9 boards (the ones whose children got an assignee: travel, aceengineer-*, ecosystem, devakrishna, household/family/finance).
- Every worker aborted with `Error: Unknown skill(s): kanban-worker` → crash→respawn thrash: **138,929 `task_runs`**, cgroup peak **~10 cores / 18.7 GB / load 30**. 7-day output: 1613/1621 runs crashed, **0 done, 0 commits** from the swarm. No model-quota cost (workers die before any API call).
- **Mechanism (refined this session):** `skill_view('kanban-worker')` returned `success=False` ("Refusing to guess") because **2 candidates** existed — canonical `~/.hermes/skills/devops/kanban-worker/SKILL.md` AND a stray duplicate `/mnt/local-analysis/workspace-hub/.claude/skills/devops/kanban-worker/SKILL.md` (from backfill `b00a04fc8`, 2026-05-19). The preloader maps `success=False` → "missing" → abort. The dispatcher guard (`kanban_db.py:5590`) injected the flag anyway because it only checks raw file existence.
- **Broader issue:** **60 skills collide** root-home ↔ workspace-hub `.claude/skills` (30 identical, 30 DIVERGENT). workspace-hub `.claude/skills` is the PRIMARY library (~3118 unique skills) — do NOT deregister it; fix per-skill by removing the non-canonical copy.

## Actions taken this session (all defensive / reversible)
| # | Action | Evidence | State |
|---|--------|----------|-------|
| 1 | Source kill-switch `kanban.dispatch_in_gateway: false` + per-board cap `max_spawn/max_in_progress: 20` | `~/.hermes/config.yaml` (kanban section) | applied, YAML-valid |
| 2 | Gateway restart (`sudo systemctl restart hermes-gateway.service`, user-run) | 256→0 workers, 21.2 GB→138 MB, Telegram reconnected, crons up | verified |
| 3 | Report committed | branch @ `ddb095795` (temp-index plumbing — beat autosync index.lock storm) | done |
| 4 | Skill-collision fix: removed repo's `kanban-worker` duplicate | branch @ `6a2d617d7`; `skill_view` now `success=True` | done |
| 5 | Stale rows: 260 `running` → `blocked` (reason in `last_failure_error`, claim/pid/run cleared) across 9 boards | 0 running anywhere | verified |

## Current verified state (at exit)
- **Runtime:** gateway active, Tasks 6, ~123 MB, `dispatch_in_gateway: false`, **0 kanban workers**, Telegram connected, crons running.
- **Git:** branch `docs/kanban-adversarial-review-20260525` @ `6a2d617d7` → `ddb095795` → `175c80323` (main merge). **UNPUSHED.** Report + skill-fix both present. (`main` advances continuously via autosync — index.lock storm is live; use temp-index plumbing for any commit here.)
- **No external actions taken** — no pushes, no GH issues/comments, no messages sent. All changes local to `ace-linux-1` (config, local branch, local kanban DBs).

## Next steps (forward decisions — left for the user)
1. **Do NOT re-enable `dispatch_in_gateway`** until: (a) remaining skill collisions resolved (kanban-orchestrator, kanban-codex-lane + ~57 others — DIVERGENT copies need per-skill judgment), and (b) a **global** concurrency cap exists (current cap is per-board only; Hermes has no global semaphore — needs a code change).
2. **528 decomposer children remain git-invisible** with null idempotency keys — a reload duplicates them. Build a dump-back path (review R5) before any reload.
3. **Push the branch?** Currently local-only.
4. **Structural board rework** (R4/R6): rebalance 870 workspace-hub cards toward product missions; repair 7 dead tier-0 links + add Level-2 `check-kanban-spans-boards.py`; seed/delete empty parents.
5. Optional: a guard fix so `_kanban_worker_skill_available` uses the same resolver as the preloader (defense-in-depth; the data-fix in action #4 already resolves the immediate crash).

## Cross-session note
A parallel session co-authored this branch (it landed `6a2d617d7` on top of this session's `ddb095795`) and an adjacent handoff `2026-05-25-ecosystem-consolidation-and-crash-recovery.md`. Findings are consolidated in memory `project_kanban_ecosystem_runaway_state.md` — treat that as canonical.
