# Plan for #3184: Harness install-doctor — scheduled repair arm for per-provider install drift

> **Status:** plan-review
> **Complexity:** T2 (single script + catalog config + test; harness domain → 2-provider adversarial review)
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3184
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3184-claude.md | ...-codex.md (pending)

> **Disclosure (not a completeness claim):** a working draft of the script + catalog entry was built and dry-run/real-run proven on ace-linux-2 during the originating session (exit 0, non-destructive verified). This plan is written future-tense for the reviewable scope; the draft stands in for a prototype and is subject to revision from review findings. Nothing is committed to `main`; work lives on branch `harness/3184-install-doctor` pending approval.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/monitoring/equivalence-sentinel.sh` (#3059) — fingerprints this box → publishes to the `equivalence-state` git ref → compares all boxes → alerts on WARNING/CRITICAL. **Report-only**: its final stage is `gh issue comment`; it never repairs. This is the gap the doctor fills.
- Found: `scripts/agents/install-soul-runtime.sh` (#2719 Phase 4) — idempotent installer that creates/retargets `~/.hermes/SOUL.md` and `~/.codex/AGENTS.md` symlinks, backing up non-symlink files. **Has no scheduler** — runs only by hand, so secondary boxes drift. Explicitly **skips** Gemini `SOUL.md` (line 84, Phase-6 deferred) and does **not** touch `~/.codex/skills`.
- Found: `scripts/enforcement/check-soul-runtime-drift.sh` (#2719 Phase 3) — verifies committed `*.runtime.md` **content** matches a rebuild. Complementary but orthogonal: it checks artifact *content* drift, not per-machine *install* state.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — SSoT for all scheduled tasks (HARD RULE: no direct crontab edits). Rendered by `scripts/cron/cron_render.py`, validated by `scripts/cron/validate-schedule.py`, applied by `scripts/cron/setup-cron.sh`.
- Found: `config/agents/codex/AGENTS.runtime.md` — line 165 (`~/.codex/skills` symlinks to `.claude/skills`) is **vestigial/wrong now**: line 173 states Codex has *no native skill loader* and reads workspace skills from the repo `.claude/skills/<family>/` via the Skill index. `~/.codex/skills` holds Codex's own `.system` skills — symlinking it over `.claude/skills` would **shadow** them. Codex memory surface is the repo-tracked `config/agents/codex/MEMORY.runtime.md` (auto-gen by `bridge-hermes-claude.sh`), **not** `~/.codex/memories/`.
- Gap: there is no scheduled, provider-neutral **repair** of install state. A `SessionEnd`/`Stop` hook is Claude-only and cannot heal after Codex/agy sessions.

### Standards
Not applicable (harness infrastructure).

### LLM Wiki pages consulted
No relevant wiki pages (harness-internal; out of scope of wiki-sibling routing per `coding-style.md` / `wiki-sibling-routing.md` §"Do not apply when").

### Documents / config consulted
- `.claude/rules/patterns.md` — enforcement gradient (prose→script→hook). This is a Level-2 script + Level-3-adjacent cron.
- `config/agents/SHARED_SOUL.md` / `CLAUDE.md` adapter — provider-neutral identity layer; confirms `~/.claude/CLAUDE.md` is the bootstrap global (correct as a plain file, not a runtime symlink).
- `config/agents/drift-policy.yaml` — confirms hermes `memories/`/`skills/` are `never_sync` (per-provider local), informing the "report-only, never mutate `~/.codex/skills`" guardrail.

### Gaps to build from scratch
1. The repair-arm script `scripts/maintenance/harness-install-doctor.sh`.
2. Its test suite `scripts/maintenance/tests/test_harness_install_doctor.sh`.
3. The catalog entry in `schedule-tasks.yaml`.

---

## Approach

A small, surgical **repair arm** that composes existing blessed installers — it invents no new install semantics.

1. **`scripts/maintenance/harness-install-doctor.sh`** (idempotent, non-destructive, `DOCTOR_DRY_RUN=1`):
   - Step 1 — run `install-soul-runtime.sh`; record its summary as the core repair.
   - Step 2 — **report-only** guardrail: confirm `~/.codex/skills` is a real dir holding `.system` and is **not** a stray symlink (which would shadow native skills). Never mutate it.
   - Step 3 — **report-only**: `~/.gemini/GEMINI.md` is Phase-6-deferred; flag presence/absence, never force.
   - Step 4 — **verify-only**: repo-tracked `config/agents/codex/MEMORY.runtime.md` + `AGENTS.runtime.md` exist and aren't stale (>14d → SKIP note; bridge owns refresh, not the doctor — regeneration is a token-heavy `claude -p` job owned by `provider-dream-bridge`).
   - Exit 0 unless an unrepairable `NEEDS-ATTENTION` item exists (exit 1).

2. **Catalog entry** (id `harness-install-doctor`, `5 */6 * * *`, machines `[dev-primary, ace-linux-1, dev-secondary, ace-linux-2]`, `requires: [bash, git]`, `is_claude_task: false`) — runs 12 min before the `:17` sentinel each 6h cycle (repair → detect). **Cron, not a hook**, so healing is provider-neutral and out-of-session.

3. **Test** `scripts/maintenance/tests/test_harness_install_doctor.sh` — see TDD section.

## TDD

Implementation drafted ahead of tests during the prototype session (disclosed above); the test suite is authored now and must pass before merge. Cases:
- `--syntax` / `bash -n` clean.
- `DOCTOR_DRY_RUN=1` changes nothing on disk (snapshot `~/.codex` before/after; assert identical).
- Guardrail: when `~/.codex/skills` is a real dir with `.system`, doctor reports `OK`/`SKIP` and **does not** convert it to a symlink (assert still a dir, `.system` present).
- Guardrail: when `~/.codex/skills` is a (simulated) stray symlink in a sandbox HOME, doctor reports `NEEDS-ATTENTION` and exits 1 (no auto-clobber).
- Exit code 0 on a healthy sandbox; exit 1 when a `NEEDS-ATTENTION` condition is forced.
- Idempotency: two consecutive real runs both exit 0 with no backups created on the second.

Tests use a sandboxed `HOME` (tmpdir) so they never touch the operator's real `~/.codex`.

## Adversarial review (T2)

Plan-stage: 2 independent reviewers (Claude inline + a second lens), adversarial stance (default non-APPROVE), focused on: (a) does the doctor ever destructively mutate provider runtime state? (b) is the `~/.codex/skills` guardrail correct given line-165 vs line-173 tension? (c) catalog correctness (schedule collisions, machine list, log path); (d) failure modes under network/auth loss (must not crash cron). Cross-provider (Codex/Gemini) review can additionally run via `scripts/review/plan-review-fanout.sh`.

## Risks & mitigations
- **R1 — shadowing Codex `.system`** (already hit + reverted in prototype): mitigated by making Step 2 report-only; test enforces no-mutation.
- **R2 — shared live clone**: workspace-hub is a shared checkout; work is isolated on a feature branch; commits use pathspec form per `feedback_multi_agent_commit_serialization`.
- **R3 — cron noise**: doctor exits 0 when healthy and writes a dated log; only `NEEDS-ATTENTION` (exit 1) surfaces in cron-health.
- **R4 — over-reach into bridge territory**: doctor only *verifies* the memory surface; refresh stays with `provider-dream-bridge`/`bridge-hermes-claude.sh`.

## Out of scope
- Repairing the cross-repo gsd-hook propagation gap (separate finding; own issue).
- Windows boxes (Task Scheduler) — Linux-only for v1; mirror later if warranted.
- Gemini `GEMINI.md` install (Phase-6, tracked separately).

## Acceptance criteria
Mirror issue #3184: script exists (idempotent/non-destructive/dry-run); test suite passes; catalog validates + renders for all 4 boxes; plan + adversarial review filed; documented as #3059's repair arm in the epic.
