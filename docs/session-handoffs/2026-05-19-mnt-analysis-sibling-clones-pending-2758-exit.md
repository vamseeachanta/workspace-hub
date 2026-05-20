# Session Handoff — /mnt/local-analysis sibling clones (assetutilities + digitalmodel), deletion deferred pending #2731 (primary) / #2758 / #2754

> **Note on filename:** filename slug retains `pending-2758` for chronological grep continuity, but the primary blocker for the deletion question is actually [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — see "Dependency" section. Initial draft cited #2758 only; corrected before push after spotting `docs/plans/2026-05-19-issue-2731-data-repo-location-contract.md` in the post-commit status.

- **Timestamp:** 2026-05-19T21:30:00-05:00
- **Host:** ace-linux-1
- **Working repo for handoff:** `/mnt/local-analysis/workspace-hub`
- **Branch:** `main`
- **Purpose:** durable closeout after merging one stray Codex branch into `assetutilities/main`, and pausing the deletion question on `/mnt/local-analysis/{assetutilities,digitalmodel}` until the data/repo-location contract ([#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)) and per-machine placement issue ([#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) for ace-linux-1) land.

## Session arc

User directive evolved across the session:

1. **Initial**: "review the assetutilities and digitalmodel in /mnt/local-analysis and try to merge any work into to main and push to origin" → /repo-sync skill loaded, both repos audited (branches, stashes, reflog, remote topic branches).
2. **Decision**: one merge candidate surfaced (`origin/codex/burn-20260511-assetutilities-bundle`); user approved via AskUserQuestion → merged, pushed, topic branch deleted from origin.
3. **Follow-up**: "can we delete these 2 additional directories?" → discovery probe (untracked, worktrees, hooks, open handles, inbound refs) before answering.
4. **Pivot**: user flagged a parallel in-flight decision to move repos beside `workspace-hub` → deletion paused; this exit prepared.

## Commits landed on origin/main (external state changed)

| SHA | Title | Repo |
|---|---|---|
| [`1122e50`](https://github.com/vamseeachanta/assetutilities/commit/1122e50d9e1773872cbfd68b9d06c5f1f9dc330f) | `Merge codex/burn-20260511-assetutilities-bundle: CI test dep group` | assetutilities |

- Push line: `693685f..1122e50  main -> main` (accepted, no rejection, no branch-protection block).
- Post-push fetch: `HEAD == origin/main`, ahead/behind `0/0`.
- Remote topic branch `codex/burn-20260511-assetutilities-bundle` deleted from origin.
- Merged content: 2 files (`.github/workflows/tests.yml` switches to `uv sync --group test`; `tests/repo_structure/test_repo_structure_contract.py` adds a contract test pinning that convention). No conflict — main had not touched either file since merge-base `ff65300`.

No commits landed in `digitalmodel` this session (already 0/0 with origin/main at session start; today's 4 SIROCCO DOCX commits were already on origin).

## Disk state at exit

```
/mnt/local-analysis/
├── assetutilities/      (1.6 GB) — preserved, see "Why preserved" below
├── digitalmodel/        (6.9 GB) — preserved, see "Why preserved" below
└── workspace-hub/       (canonical, untouched apart from this handoff file)
```

| Path | HEAD | vs origin/main | Untracked / ignored | Worktrees | Open handles |
|---|---|---|---|---|---|
| `/mnt/local-analysis/assetutilities` | `1122e50` main | 0/0 | `src/assetutilities.egg-info/*` (setuptools, regeneratable) | none | none |
| `/mnt/local-analysis/digitalmodel` | `35b90685` main | 0/0 | `.venv/` (populated, expensive to rebuild) | none | none |

## Why preserved (not deleted)

User flagged a parallel in-flight decision to move sibling repos beside `workspace-hub`. The two dirs are already in the candidate target layout (peers of `workspace-hub` under `/mnt/local-analysis/`). Deleting now would:

- destroy a populated `.venv` in `digitalmodel` (~thousands of installed package binaries; rebuild is slow);
- force re-clone (~8.5 GB of network + I/O);
- risk inconsistency if the architecture contract specifies *how* sibling clones should be configured (sparse-checkout setup, remotes, hooks, .claude overlays).

Cost asymmetry favored holding: wait cost is disk only (8.5 GB on a volume reporting plenty of free space); premature-delete cost is re-bootstrap time plus the above risks.

**Precedent:** `feedback_wait_for_safety_bg_task_before_destructive_op` (memory, logged 2026-05-18 — same repo `digitalmodel`, premature `rm` against incomplete safety evidence).

**Ecosystem-isolation evidence (supports either future verdict):**
- `lsof +D` on both dirs → no open file handles.
- Grep `--include='*.{md,sh,py,json,yaml,yml}'` across `workspace-hub/.claude`, `config`, `scripts`, `CLAUDE.md`, `AGENTS.md` → zero hits for these paths.
- `find -type l` across `/home/vamsee`, `/mnt/local-analysis`, `/tmp` (depth 4) → zero symlinks pointing into either dir.

So nothing in the ecosystem is currently bound to these specific paths — the dirs are equally safe to keep OR to delete once the contract speaks.

## Dependency

Three related issues; **#2731 is the primary blocker** for this specific deletion question:

- **[#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — Data/repo location contract for llm-wiki promotion** (PRIMARY)
  - Plan: `docs/plans/2026-05-19-issue-2731-data-repo-location-contract.md` (status: draft, T3).
  - Plan summary excerpt: *"no existing single ledger will define the canonical checkout style for active repos under `/mnt/local-analysis`"*. This issue decides the canonical-checkout-style verdict — i.e., directly whether `/mnt/local-analysis/{assetutilities,digitalmodel}` are the canonical clones.
  - Resolution gate for this handoff: `status:plan-approved` on #2731.

- **[#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) — Agent/runtime folder architecture contract** (vocabulary)
  - Plan: `docs/plans/2026-05-19-issue-2758-agent-runtime-folder-architecture-contract.md` (status: draft, T3).
  - Plan explicitly scopes itself: *"no repo moves in this issue"*. Provides the schema (canonical source vs. generated runtime vs. user-home vs. sibling tier-1 repo vs. workspace-hub subfolder) that #2731 and the per-machine issues consume. Not the deletion decision itself, but relevant.

- **[#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) — Per-machine repo placement: ace-linux-1** (this host)
  - Listed in #2758 plan as one of four machine-specific consumers (#2754 ace-linux-1, #2755 ace-linux-2, #2756 licensed-win-1, #2757 licensed-win-2).
  - This is where the final "what's on ace-linux-1 at `/mnt/local-analysis/`" answer lands. If #2754 says "no `/mnt/local-analysis/` sibling clones on this host" → delete; if it says "tier-1 sibling clones at `/mnt/local-analysis/<repo>/`" → keep.

- **Adjacent skill ref:** `.claude/skills/workspace-hub/repo-structure/references/agent-runtime-authority-map.md` (untracked at session start; concurrent work; supports #2758 schema).

## Resume hooks (next session pickup)

When the #2758 decision lands:

1. **If contract confirms sibling-clone layout at `/mnt/local-analysis/<repo>/`:**
   - Keep both dirs as-is.
   - Verify remotes / hooks / sparse-checkout / `.claude` overlay state matches the contract; reconcile any deltas.
   - Close out by amending or superseding this handoff.

2. **If contract specifies a different location (e.g., under `~/`, under `/srv/`, or as worktrees of workspace-hub):**
   - Relocate both dirs per spec; do NOT delete-then-reclone if a move suffices.
   - For `digitalmodel`, factor the `.venv` rebuild cost into the migration plan — consider `cp -al` (hardlink) or `mv` to preserve the venv.

3. **If contract is silent on `/mnt/local-analysis` peer layout:**
   - Surface ambiguity to the user; do not infer. Default action remains "hold."

## Out of scope this session

- Did not open or modify any file in `#2758` plan / spec / skills.
- Did not post a comment on `#2758` — this handoff is the durable cross-link; user may choose to surface it on the issue.
- Did not touch `workspace-hub` tracked state apart from creating this handoff file. Pre-existing dirty state from SessionStart (`config/ai-tools/provider-*.json`, `docs/reports/provider-*.{md,html}`, `logs/orchestrator/hermes/skill-patches.jsonl`) is from concurrent Hermes auto-sync work and remains untouched.
- Did not run a workspace-wide `/repo-sync` push or any tier-1 ecosystem op.

## Cleanup-audit verdict: **CLEAN → EXPECTED**

Per pre-completion-cleanup-audit rubric (`.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`):

- **CLEAN:**
  - assetutilities + digitalmodel: HEAD == origin/main, no stashes, no untracked-from-this-session, no open file handles, no orphan worktrees.
  - One orphan background process (`ugrep` over workspace-hub) was killed before exit.
  - No partial-pull backups (`.claude.partial-pull-backup-*` etc.) created.
  - No `/tmp` scratch from this session.

- **EXPECTED (named residue, fine to leave):**
  - assetutilities `src/*.egg-info/`: setuptools build product, gitignored, regenerated on next `pip install -e .`.
  - digitalmodel `.venv/`: locally useful (populated CLIs); preserved deliberately to avoid rebuild cost.
  - workspace-hub pre-existing dirty state (concurrent Hermes auto-sync churn): not in scope; out-of-session.
  - This handoff file itself: intentional artifact, about to be committed.

- **UNEXPECTED:** none.

## Verification

- assetutilities: `git rev-list --left-right --count HEAD...@{u}` → `0 0`; HEAD = `1122e50d9e1773872cbfd68b9d06c5f1f9dc330f`; origin/main = same.
- digitalmodel: `git rev-list --left-right --count HEAD...@{u}` → `0 0`; HEAD = `35b90685` (unchanged this session).
- assetutilities remote branch list post-cleanup: only `origin/main` + `origin/HEAD` (topic branch deleted).
- No external action remains pending or in flight from this session.

## Cross-references

- Merge approval surface: user answered AskUserQuestion "Merge to main + push (Recommended)" → action authorized within session scope only.
- Precedent memory: `feedback_wait_for_safety_bg_task_before_destructive_op`, `feedback_check_parallel_work`, `feedback_autosync_silent_pusher`, `feedback_reflog_as_ground_truth`, `feedback_retry_loop_sweep_contamination`.
- Workflow skill loaded: `workspace-hub:repo-sync` (governed the merge / push / topic-branch deletion path).
