# Session handoff — memory-bridge fix (#3384) + equality-matrix work — 2026-07-06

## Scope
Started as "run machine equivalence metrics + get the HTML matrix report." Cascaded into diagnosing and fixing a memory-bridge that had been silently non-committing for ~6 weeks. All primary work is **shipped and live**.

## Final repo state
- **workspace-hub `main`**: clean, `0 ahead / 0 behind` origin, HEAD `5305e58c4` (the merged #3384 fix).
- No dirty source files; regenerable memory-mirror churn may be present in the working tree (bridge output — safe to `git checkout --`/leave).
- Backup tags (safe to delete once confident): `backup/pre-wedge-2026-07-05`, `backup/pre-merge-reconcile-3384`.
- No pending external actions (no emails/messages sent; nothing published beyond the GitHub PR/issues below).

## What shipped
**PR [#3388](https://github.com/vamseeachanta/workspace-hub/pull/3388) — squash-merged to `main`, all 13 CI checks green. Closes #3384.**
- `scripts/memory/bridge-commit.sh` (new) — extracted commit path: commits **before** stashing (fixes the self-stash bug where the bridge stashed its own staged output and committed nothing), daily machine-independent **liveness heartbeat**, bounded non-FF push retry, owner-gated.
- `bridge-hermes-claude.sh` — buggy inline block → `source` + `bridge_commit_and_push`.
- `audit_memory_freshness.py` — freshness clocked by the heartbeat (`RECENCY_GIT_SURFACES`); content surfaces graded by filesystem **presence** (`PRESENCE_SURFACES`), detects deletion. `schema_version` → 2.
- `schedule-tasks.yaml` — Linux bridge runs `--commit`; Windows dry-run.
- `.gitignore` — un-ignore `.claude/state/memory-bridge-heartbeat.json` (its commit time IS the freshness clock).
- 35 TDD tests (`scripts/memory/tests/test_bridge_commit.py`, `tests/curation/test_audit_memory_freshness.py`).

Root-cause + plan + 2 adversarial review rounds documented on #3384 and in `docs/plans/2026-07-06-issue-3384-bridge-commit-self-stash.md`.

## Open work
1. **[#3387](https://github.com/vamseeachanta/workspace-hub/issues/3387)** (`status:needs-plan`) — defect #3: bridge step-5 snapshot is non-monotonic (a compacted live `MEMORY.md` can overwrite a richer committed snapshot). Content-quality dimension deferred from #3384. Note: post-#3384, content surfaces are presence-graded, so a *stale-but-present* slice is a known-uncovered case until #3387 lands.
2. **Completeness-gate friction (NOT a bug — correction of an earlier mis-claim in this session).** I twice told the user the gate was "misconfigured (COMPLETENESS_OWNERS unset) → deadlock." **That was wrong** — it was a local-run artifact (the advisory script reads `COMPLETENESS_OWNERS` from the env; my local run didn't pass it; the GitHub Action passes `vars.COMPLETENESS_OWNERS`, which IS set to `vamseeachanta`). Verified facts:
   - `COMPLETENESS_OWNERS=vamseeachanta` is set (repo variable, 2026-05-26).
   - `autoapply-completeness-label.yml` (`d418833ae`, #2798) **intentionally** adds `gate:completeness` to every `status:plan-approved` issue ("comprehensive for NEW work"; only-adds-a-label, safe by construction).
   - `completeness-gate.yml` reopens on `issues.closed` when the issue is opted-in but lacks a computed completeness record + owner `status:completeness-verified` label.
   - **The friction:** a PR-merge auto-close (`Closes #NNNN`) fires the gate before any completeness record is computed → reopen. #3384 hit this; the user cleared it by removing `gate:completeness` then closing.
   - **Filed as [#3389](https://github.com/vamseeachanta/workspace-hub/issues/3389)** (`status:needs-plan`) — workflow friction (not a config bug). Fix options in the issue: (a) exempt PR-merge closes, (b) compute+stamp the record during the PR, or (c) restore true opt-in by guarding autoapply. Owner decides direction at plan stage; no enforcement workflow was changed this session.

## Key behavioral lessons (candidate memory)
- **Never fake a green.** Every STALE/EXPIRED/reopened signal this session was surfaced honestly rather than papered over; that is what found a 6-week-dead subsystem instead of a cosmetic dashboard fix.
- **Step-1.5 reproduction before concluding** caught TWO of my own mis-framings this session (the original #3384 "byte-stable" framing, and the completeness-gate "misconfig" claim). Reproduce against real state before asserting a root cause OR a fix.
- **End-to-end verify earns its keep**: 35 unit tests passed, but running the real bridge exposed two gitignore traps (heartbeat under `.claude/state/*`, helper under `lib/`) the temp-repo tests structurally could not see.
- **The push churn on ace-linux-1** that plagued the whole session was ONE untracked `docs/reports/*.html` colliding with an incoming tracked path → every `git pull --rebase` aborted with `could not detach HEAD`. `--autostash` handles tracked dirt, not untracked-vs-incoming-tracked collisions. Move the one file aside → rebase works.

## Next action (recommended)
Plan #3387 (defect #3) when ready — normal Issue → Plan → approve → TDD flow. The completeness-gate friction is an owner decision, not queued work.
