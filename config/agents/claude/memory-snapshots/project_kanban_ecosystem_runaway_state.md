---
name: project_kanban_ecosystem_runaway_state
description: "Hermes kanban bulk-load tripped the triage auto-pipeline — 260 live workers on personal/admin boards, 528 tasks git-invisible; adversarial review 2026-05-24"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0449266f-206e-4363-ab68-bace76753639
---

The 45-board kanban ecosystem (`.claude/memory/kanban/`) all loaded live into per-board SQLite DBs at `~/.hermes/kanban/boards/<slug>/kanban.db` (NOT a `boards` table — one DB per board; top-level `~/.hermes/kanban.db` is a legacy default with 7 stale test tasks).

Adversarial review 2026-05-24 (`docs/reports/2026-05-24-kanban-ecosystem-adversarial-review.html`) found the load recreated the exact [[feedback_hermes_triage_is_pipeline_entry]] runaway: `--triage` did NOT park cards — config default `kanban.auto_decompose: True` (config.py:1566) makes the dispatcher auto-decompose triage every tick, spawning **528 children → 2064 total tasks, ~260 concurrent workers** on the 9 boards whose children got an assignee (travel, aceengineer-strategy/admin/website, ecosystem, devakrishna, household/family/finance). digitalmodel/worldenergydata/workspace-hub stayed inert in `ready` NOT by deprioritization but because raw loader cards have **no assignee** (gateway/run.py:5421 only spawns ready+assigned); anything that assigns them later re-triggers fan-out.

CORRECTION (user 2026-05-25): the workers are "false" — **no quota burn**. Verified: 262 procs but **summed CPU 0.0%**, all in S/D state, **zero heartbeats ever** (last_heartbeat_at NULL, 0 heartbeat-events). They spawn, wedge instantly (signature matches [[feedback_codex_cli_0_124_upstream_regression]] stdin-detection hang), never call a model, get reclaimed, respawn. Real damage is a **spawn→wedge→respawn thrash: 138,929 task_runs** across 9 boards (travel 38k, aceengineer-strategy 23k, ecosystem 22k). No billing cost; massive process/IO churn + untrackable worker count.

Two structural defects: (1) the 528 decomposer children have `idempotency_key=NULL`, exist only on ace-linux-1, are git-invisible, and **duplicate on reload** — violates "memory is in the repo" + contradicts the tier-0 #1 theme (consolidate memory to Hermes canonical). YAML SoT is 528 behind by design (no dump-back path). (2) tier-0 `spans_boards` has 7 dead slugs (`repo-workspace-hub-{hermes,governance,intel,cron}`, `-digitalmodel-mooring`, `-achantas-data-krishna`, `repo-readiness`) — workspace-hub was decomposed under two incompatible taxonomies.

Also: workspace-hub (meta/tooling) owns 870/1536 cards (57%) vs digitalmodel 265 / worldenergydata 68 — scaffolding-over-mission. 7 empty tier-1 parents. Staleness clean (0 closed mirrored). 

Recommendations R1–R6 in the report. R2: never bulk-load to triage (use `blocked`-with-reason per [[feedback_hermes_blocked_status_auto_unblocked]]). R3: build dump-back or stop calling YAML the SoT.

CONFIG CHANGE 2026-05-25: added `kanban:` section to `~/.hermes/config.yaml` with `max_in_progress: 20` + `max_spawn: 20`. **Caveat — these are PER-BOARD caps** (gateway/run.py:_tick_once loops every board, passes the same cap to each dispatch_once at run.py:5371); global worst case = 20×(active boards). True global cap needs a code-level semaphore (follow-up). **Cap is INERT until gateway restart** — running gateway pid 1332383 started 01:16, ~3.6h before the 04:54 edit, so it holds the old uncapped config. Restart `hermes gateway run --replace` to activate (disruptive: drops Telegram/Discord/cron adapters; also reap the ~260 wedged workers). Deeper fix than cap: set `kanban.auto_decompose: false` or `dispatch_in_gateway: false` to stop the spawn loop at source; fix worker stdin-hang wedge.
