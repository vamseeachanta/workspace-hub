# Kanban Ecosystem — Recommendations (parallel-agent worked)

- **Date:** 2026-05-25 · **Machine:** ace-linux-1 · **Author:** Claude main (`0449266f`) + 4 Sonnet subagents
- **Companion to:** `docs/reports/2026-05-24-kanban-ecosystem-adversarial-review.html` (the review) and `docs/session-handoffs/2026-05-25-kanban-ecosystem-adversarial-review-and-runaway-containment.md`
- **Status:** RECOMMENDATIONS — none applied yet beyond the containment + 2 skill-collision removals already committed. Each section below is independently actionable on your approval.
- **Method:** four read-only subagents developed one workstream each; main session verified the two load-bearing factual claims (below) before enshrining.

**Verifications (trust-but-verify):**
- ✅ `tools/skills_tool.py:1011` `if len(candidates) > 1:` → "Refusing to guess" — confirms the skill-collision crash mechanism (WS4-B / root-cause c).
- ✅ `task_links` inverted: 85/159 links are null-key `parent_id` → keyed `child_id` on the ecosystem board — confirms WS3's dump traversal direction.

---

## WS1 — Repair dead tier-0 links + add enforcement (R6, structural)

**Finding:** all 7 dead `spans_boards` slugs map onto EXISTING boards — no new boards needed.

| Dead slug | → Resolution | Rationale |
|---|---|---|
| `repo-workspace-hub-hermes` | `repo-workspace-hub-harness` | harness = Hermes runtime/dispatcher/CLI plumbing |
| `repo-workspace-hub-governance` | `repo-workspace-hub-ops` | review-gates/policy/compliance = ops surface |
| `repo-workspace-hub-intel` | `repo-workspace-hub-data` | doc-intel + nightly researchers = ingestion/research |
| `repo-workspace-hub-cron` | `repo-workspace-hub-ops` | cron/scheduling = ops infrastructure |
| `repo-digitalmodel-mooring` | `repo-digitalmodel-subsea` | mooring is subsea-adjacent; no closer domain |
| `repo-achantas-data-krishna` | `repo-achantas-data-devakrishna` | direct rename (old slug convention) |
| `repo-readiness` | `repo-workspace-hub-ops` | readiness cron posts to a workspace-hub ops issue |

**Exact `ecosystem.yaml` edits** (12 `spans_boards:` lines across cards `eco:hermes-canonical-memory`, `eco:cross-review-gates`, `eco:doc-intel-operating-model`, `eco:krishna-typing-rotation`, `eco:goal-catalog-d7`, `eco:daily-readiness-cron`, `eco:solver-queue-production`, `eco:nightly-researchers`, `eco:hermes-installation-codex-quota`, `eco:ai-harness-evaluations`, `eco:claude-design-adoption`, `eco:mooring-knowledge-seeds`): apply the slug remaps above. Full old→new line pairs are in the session record.

**Enforcement (Level-2, per `.claude/rules/patterns.md` gradient):** add `scripts/enforcement/check-kanban-spans-boards.py` — fails (exit 1) if any `spans_boards` slug lacks a `boards/<slug>.yaml`. Follows `check-no-abs-paths.sh` conventions (exit 0/1, `KANBAN_SPANS_ALLOW=1` bypass, stderr-only, git-root anchored, degrades-open if PyYAML missing). Wire into pre-commit / CI. (Full ~150-line script in session record, ready to drop in.)

---

## WS2 — Rebalance backlog + seed product roll-ups (R4/R6)

**Target:** workspace-hub 870 → ~470 active cards (57% → ~41% of ecosystem).

| Board | Now | Ceiling | Shed | What to shed |
|---|---:|---:|---:|---|
| harness | 300 | 100 | ~200 | ~50 WRK-era ghost-opens (`Status: done` in body, `gh_state:open` — e.g. `#103-#107`, `#63`); ~80 priority-0 follow-on chains (`#2211/#2210/#2231-#2236`) → `gaps/`; ~10 misrouted (`#2628` digitalmodel-CI, `#2640` worldenergydata) → product boards |
| engineering | 234 | 120 | ~114 | Domain-sweep R1–R6 scaffolding (`#2677-#2682` mooring, `#2669-#2674` hydro, `#2688-#2693` subsea) → `gaps/` once parent sweep closes |
| ops | 120 | 80 | ~40 | resolved chores + misrouted harness items |
| ai-orchestration / data / business | 93/63/60 | 70/50/50 | ~46 | minor stale-proposal cleanup |

**Buckets:** *Close* = body says done + open GH state (ghosts). *Demote to `gaps/`* = priority-0, no `plan-approved`/`working`, >90d old, or post-sweep receipts. *Keep* = priority≥1, `plan-approved`/`working`, or <90d (issue# >~2400).

**Seed product roll-ups** (the products have NO repo-level view):
- `repo-worldenergydata` (0 cards): GTM-readiness gate (wraps wed#364/#363), marketing-pipeline epic (wed#423), data-quality gate, revenue-first roadmap, worldenergydata-wiki corpus.
- `repo-digitalmodel` (legacy WRK cards): CI/test-debt epic (wh#2628), catenary canonicalization (wh#2686/#2694), solver-queue multi-machine, calc-citation coverage (wh#2685), sweep→product consolidation.

**Empty-parent disposition:** DELETE boards `repo-hobbies` + `repo-llm-wiki-acma` (no software/children; content repos). SEED `repo-achantas-data` (2: data policy + devaKrishna milestones), `repo-assethold` (1: product phase), `repo-llm-wiki` (2: private-corpus rollout wh#2774 + sibling-routing wh#2778), `repo-sabithaandkrishnaestates` (1: annual closeout gate), `repo-worldenergydata` (5, above).

---

## WS3 — `dump.py`: close the source-of-truth loop (R5)

**Problem (verified):** the auto-decomposer minted 528 child tasks with `idempotency_key=NULL`, git-invisible, duplicate-on-reload. `load.py` is one-way. `task_links` uses an **inverted rollup** convention (null subtask=`parent_id` → keyed theme=`child_id`; 85/159 on ecosystem ✓).

**Design:**
- **Stable key scheme:** `decomposed:<board>:<nearest-keyed-ancestor-key-slug>:<title-slug>` (+ `:sha1(title)[:4]` collision discriminator; `orphan:<hash>` fallback). Anchored to the YAML parent + title → stable across body rewrites; a title change correctly mints a new key. Traversal = BFS following `task_links` child direction (toward keyed tasks).
- **Upsert merge:** never touch the `board:` header; YAML-wins on author intent fields (`source`, `source_url`, `gh_*`, `spans_*`, `notes`), DB-wins on runtime-promotable (`priority`, `skills`, `assignee`); preserve YAML-only `detected_gap` cards.
- **DAG preservation:** emit `decomposed_children:`, `parent_idempotency_key:`, `sequential_dependencies:`, `also_serves:` (multi-parent). `load.py` reconstructs `task_links` via a post-create link pass.
- **Round-trip contract:** dump→commit→`load.py` on machine B yields no dups (idempotency-key upsert). `load.py` needs 2 small changes: stop skipping `source: decomposed`, and add the link-reconstruction pass.
- **Flags:** `--dry-run` (unified diff), `--board`, `--no-children`, `--status-field` (off by default).

**Risk list (must-honor):** R1 `status` is runtime — do NOT round-trip (default `triage`). R5 filter machine-local `workspace_path` (`/.hermes/`, `/workspaces/`). R6 preflight `pgrep` for active workers (`feedback_hermes_active_preflight_check`). R7 prefer `ruamel.yaml` or append-only to preserve hand-authored YAML style. (Full ~300-line skeleton + core functions in session record.)

---

## WS4 — Hermes: global concurrency cap + guard-resolver fix (R3 + c)

> ⚠️ These patch the user's Hermes runtime (`~/.hermes/hermes-agent/`), which **auto-updates** and may overwrite source patches. Config workarounds survive; code patches should be **upstream PRs**. Do not apply without explicit decision.

**A — Global cap (no global knob exists today):** caps are per-board (`run.py:_tick_once` loops boards, each `dispatch_once` counts only its own DB). Add config `kanban.max_global_concurrency`; in `_tick_once`, sum `running` across all boards before the loop, pass a shrinking per-tick budget into each `_tick_once_for_board(slug, global_budget=…)` so the SUM never exceeds the ceiling. *Config-only stopgap (survives update):* `max_in_progress: 1` → global worst case = N boards. PR: `feat(kanban): kanban.max_global_concurrency`.

**B — Guard/preloader drift (the crash cause):** the guard `_kanban_worker_skill_available` (`kanban_db.py:5590`) checks raw SKILL.md existence; the preloader (`cli.py:14715` → `skill_view`) **refuses on name collision** (`skills_tool.py:1011`, `len(candidates)>1` ✓). Fix: make the guard call the same `skill_view` resolution (env-swap `HERMES_HOME` to the worker's, check `success`), so it OMITS `--skills` on collision instead of injecting a flag the preloader rejects. Skill is supplementary (lifecycle via `KANBAN_GUIDANCE`) so omission is safe. *Config/data stopgap (already done for 2 lane skills):* remove the colliding external copy. PR: `fix(kanban): guard uses same resolver as preloader`.

---

## Recommended sequencing

1. **Now (safe, additive):** WS1 enforcement script + ecosystem.yaml link remaps; WS4-B remaining worker-relevant collision fixes (already done for kanban-worker + kanban-codex-lane).
2. **Before re-enabling dispatch:** WS4-A global cap (config stopgap `max_in_progress:1` immediately; code patch as PR) — this is a gate.
3. **Before any kanban reload:** WS3 `dump.py` (else reload duplicates 528 tasks) — this is a gate.
4. **Ongoing hygiene:** WS2 rebalance (close ghosts → demote → seed roll-ups → delete/seed parents).

The 42 divergent skill collisions remain per-skill judgment work (not crash drivers — deferred).

---

## Re-enable gate status — 2026-05-25 update (codex-cli 0.133.0 reassessment)

Triggered by the harness-flow-paths verification (`docs/reports/2026-05-25-harness-flow-paths.html`). codex-cli upgraded 0.130.0 → 0.133.0; the **worker-wedge (stdin-hang) that motivated the kill-switch is now cleared in testing** — foreground + non-TTY-subshell (`CLAUDECODE=1`, `</dev/null`) probes and two live `hermes -z` tool-using tasks all completed clean, no wedged subprocess.

**Verdict: NO-GO to flip `dispatch_in_gateway:true`.** One hard gate remains open.

| Gate | Status | Note |
|---|---|---|
| 1 · Global concurrency cap | 🔴 OPEN (hard) | No `max_global_concurrency` code knob. **Config stopgap applied this session** (see below) — durable code PR still owed. |
| 2 · Skill-collision hygiene | 🔴 OPEN | Collisions still fire live (2026-05-25 Gemini probe); 42 divergent copies per WS4-B remain per-skill judgment. |
| 3 · Worker-wedge (codex hang) | 🟢 CLOSED | codex 0.133.0 verified this session. Previously the blocker that needed a "worker-wedge fix". |
| 4 · Routing policy | 🟡 PARTIAL | `feat/2795-domain-dispatch` Phase A landed; incomplete. |
| (5) · `dump.py` reload loop (WS3) | 🔴 OPEN | Gate for any kanban *reload* (528 git-invisible children would duplicate). Independent of dispatch but on the same critical path. |

**Live backlog if flipped now:** ~464 `ready` tasks across ~20 ready-bearing boards (subsea alone = 131); 39 boards total. Pre-stopgap worst case = 39 × 20 = up to 780 concurrent workers (prior runaway peak: 260).

**Applied this session (safe, reversible, dispatch stays OFF):** WS4-A config stopgap `kanban.max_in_progress: 1` + `kanban.max_spawn: 1`. Drops worst-case global concurrency from ~780 → **≤39** (1 per board). Update-surviving per WS4-A. Takes effect only when dispatch is re-enabled AND the gateway restarted. **Revert:** `hermes config set kanban.max_in_progress 20 && hermes config set kanban.max_spawn 20`.

**Path to GO (unchanged priority, gate 3 now retired):** (1) land WS4-A `kanban.max_global_concurrency` code PR for durable global enforcement; (2) WS4-B/skill-collision hygiene; (3) WS3 `dump.py` before any reload; (4) finish routing on `feat/2795`. Even at GO, stage the flip on one board first.
