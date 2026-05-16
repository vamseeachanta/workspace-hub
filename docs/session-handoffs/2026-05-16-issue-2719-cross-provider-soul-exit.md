# Exit handoff — Cross-provider SOUL.md unification ([#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) all 7 phases + [#2446](https://github.com/vamseeachanta/workspace-hub/issues/2446) closed)

Date: 2026-05-16
Repository: `vamseeachanta/workspace-hub`
Predecessor: user-initiated comprehensive cross-provider analysis request (Hermes / Claude / Codex sessions, skills, memory)

## Scope completed in this session

Started from a planning brainstorm; executed end-to-end through implementation. Full plan in [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719), reshaped via r3 inline patches after r1 (Claude) + r2 (Codex) both returned MAJOR with 11 distinct findings.

### Pipeline structure executed

```
user request — comprehensive analysis + propose SOUL updates
  → brainstorming skill: scope = parallel SOUL files; role = heavy ~250 lines; structure = build-step inheritance
  → Phase 0 — gh issue #2719 created with reshape body
  → r1 Claude adversarial review (MAJOR, 9 findings, 3 blockers)
  → r2 Codex (MAJOR, 5 findings, 4 blockers — 2 unique to Codex)
  → r2 Gemini (UNAVAILABLE, quota — 8h45m reset)
  → user-approves via gh label (status:plan-approved)
  → r3 inline patches absorb all 11 findings; issue body rewritten (174 → 250 lines)
  → Phase 1 Discovery (root-caused untracked sed-derivative ~/.codex/AGENTS.md)
  → Phase 2a/2b/2c/2d (Hermes adapter + SHARED_SOUL + 3 deltas + F11 inline)
  → Phase 3 (build script + 5 runtime artifacts + drift check)
  → Phase 4 (install script + bootstrap-machine.sh integration; live bug fix)
  → Phase 5 (empirical loader verification — dropped 2 no-op symlinks)
  → Phase 6 (adapter de-duplication, -6 net lines)
  → Phase 7 (NEW pytest, 40 cases, all pass — closes #2446)
  → exit handoff (this file)
```

### Commits landed (8 total, all `origin/main`)

| Phase | Commit | What landed |
|---|---|---|
| 2a | [354774856](https://github.com/vamseeachanta/workspace-hub/commit/354774856) | `config/agents/hermes/SOUL.md` adapter pointer + Hard Gates block |
| 2b | [a798e31b8](https://github.com/vamseeachanta/workspace-hub/commit/a798e31b8) | `config/agents/SHARED_SOUL.md` (109-line cross-provider canonical) |
| 2c | [00e0793f4](https://github.com/vamseeachanta/workspace-hub/commit/00e0793f4) | Claude/Codex/Gemini `SOUL.delta.md` (61+60+45 lines) |
| 3 | [965c124f0](https://github.com/vamseeachanta/workspace-hub/commit/965c124f0) | `build-soul-runtime.sh` + 5 runtime artifacts + `check-soul-runtime-drift.sh` |
| 4 | [1c5c11eb7](https://github.com/vamseeachanta/workspace-hub/commit/1c5c11eb7) | `install-soul-runtime.sh` + `bootstrap-machine.sh` §2.5 integration |
| 5 | [bc280bd43](https://github.com/vamseeachanta/workspace-hub/commit/bc280bd43) | Phase 5 loader verification — dropped no-op `~/.codex/SOUL.md`, `~/.gemini/SOUL.md` |
| 6 | [bbaaa4554](https://github.com/vamseeachanta/workspace-hub/commit/bbaaa4554) | CLAUDE.md / GEMINI.md / AGENTS.md / `.codex/CODEX.md` updated with runtime pointers (-6 net) |
| 7 | [9fa7dd490](https://github.com/vamseeachanta/workspace-hub/commit/9fa7dd490) | NEW `tests/enforcement/test_agent_bootstrap_surfaces_receive_constraints.py` (40 cases, all pass) |

Total: **8 commits, +1602 net lines across 13 unique files, 0 regressions.**

## Repo states at session end

- `workspace-hub` HEAD: `f73139055` on `origin/main` (auto-sync added 2 unrelated commits after Phase 7 — `f73139055` is a separate exit handoff for llm-wiki PE Phase 3, `3883ee9ae` is daily solver dashboard regen).
- Working tree: ~30 modified/untracked files, all auto-sync state / kanban / quota / memory snapshots — **none touched by this session's commits** (pathspec form preserved isolation per `feedback_retry_loop_sweep_contamination`).
- Tests: `uv run python -m pytest tests/enforcement/` → 62 passed in 2.12s (40 new + 22 pre-existing).
- Drift check: `scripts/enforcement/check-soul-runtime-drift.sh` → all 5 runtime artifacts in sync with sources.
- Live runtime symlinks on `ace-linux-1`:
  - `~/.hermes/SOUL.md` → `config/agents/hermes/SOUL.runtime.md` (181 lines)
  - `~/.codex/AGENTS.md` → `config/agents/codex/AGENTS.runtime.md` (176 lines; Phase 1 bug GONE)
  - `~/.codex/SOUL.md` not present (Phase 5 dropped as no-op)
  - `~/.gemini/SOUL.md` not present (Phase 5 dropped as no-op)
  - `~/.codex/AGENTS.md.pre-install-backup.20260516T042128Z` preserved (broken sed-derivative kept for forensics)

## Issues touched

- [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) — OPEN, `status:plan-approved`. **Ready to close.** All 7 phases delivered; Phase 8 (Gemini r2 rerun) optional and explicitly deferred. Final status at [issuecomment-4466515710](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4466515710).
- [#2446](https://github.com/vamseeachanta/workspace-hub/issues/2446) — OPEN. **All 5/5 acceptance criteria satisfied.** Final status at [issuecomment-4466516063](https://github.com/vamseeachanta/workspace-hub/issues/2446#issuecomment-4466516063). Ready to close.

## What this session unblocks

1. **Codex sessions** on `ace-linux-1` now read the canonical SHARED_SOUL.md + codex/SOUL.delta.md via `~/.codex/AGENTS.md` → `AGENTS.runtime.md` symlink. The broken `Read \`.Codex/memory/\`` instruction (rooted at an untracked sed-derivative) is gone live.
2. **Hermes sessions** (5 active at session start) inherit cross-provider gates + must-fire rules through `~/.hermes/SOUL.md` → `SOUL.runtime.md` symlink. Per-message reinforcement of never-self-approve, `/goal` catalog gate, citation contract, etc.
3. **Cross-machine bootstrap parity**: `bash scripts/memory/bootstrap-machine.sh` on `ace-linux-2` or `licensed-win-1` will materialize the same symlink layout via the new §2.5 integration.
4. **Drift detection**: `scripts/enforcement/check-soul-runtime-drift.sh` catches any source-vs-runtime divergence — hookable into pre-commit or daily cron.
5. **#2446 narrow gap** (Hermes adapter-pattern non-conformance from 2026-04-21) is fully closed as a side-effect of the broader cross-provider work.

## Next-step candidates (for follow-on session)

1. **Close [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) and [#2446](https://github.com/vamseeachanta/workspace-hub/issues/2446)** via gh label / state change — user-applied per `feedback_never_offer_to_self_label_plan_approved`. Both have final status comments and ready-to-close recommendations posted.
2. **Optional Phase 8 — Gemini r2 rerun** against the as-built artifacts (quota reset window ~2026-05-16T07:00Z). Adds independent third-provider review verdict on the cross-provider integration; current verdict is T2 consensus (Claude + Codex MAJOR both absorbed via r3).
3. **Cross-machine bootstrap dry-run** on `ace-linux-2`: clone workspace-hub fresh, run `bash scripts/memory/bootstrap-machine.sh`, verify all 4 symlinks materialize correctly and drift check passes. Validates Phase 4 cross-machine claim.
4. **Promote `feedback_codex_bootstrap_untracked_sed_origin` memory** (referenced in `codex/SOUL.delta.md` line 173 as "write-time pending") to a formal feedback file documenting the discovery + fix.
5. **Audit other repos** for similar adapter-pattern outliers — `digitalmodel/`, `assetutilities/`, `llm-wiki/`, etc. each have their own `.claude/`, `.codex/`, `~/.hermes/` surfaces; same pattern may apply.

## No external-action status

- No external messages sent (Gmail, GitHub PRs to other repos, etc.).
- No mutation of shared infrastructure (CI/CD, secrets, deploys).
- No subagent dispatches (all work in main session, with two background cross-review dispatches that completed cleanly).
- All issue mutations were comments on issues already authored/authorized by user (2719 + 2446).

## Reviewer artifacts (for audit)

- Plan reshape body: [#2719 issue body](https://github.com/vamseeachanta/workspace-hub/issues/2719) (250 lines)
- R1 Claude review: [issuecomment-4464173306](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464173306)
- R2 Codex review: [issuecomment-4464194605](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464194605)
- R2 Gemini UNAVAILABLE: [issuecomment-4464183836](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464183836)
- Review synthesis + Path B selection: [issuecomment-4464198699](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464198699)
- R3 inline-patch summary: [issuecomment-4464222752](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464222752)
- Phase 1 Discovery resolution: [issuecomment-4464316028](https://github.com/vamseeachanta/workspace-hub/issues/2719#issuecomment-4464316028)
