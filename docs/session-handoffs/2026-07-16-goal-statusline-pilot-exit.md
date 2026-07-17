# Goal and statusline pilot — exit handoff

## Active task

Pilot repo-managed native goals for substantive Claude/Codex sessions, make Codex context and usage telemetry clear and consistent across machines, and add machine-equivalence evidence under [#3555](https://github.com/vamseeachanta/workspace-hub/issues/3555).

## Completed

- Configured this machine's interactive Git Bash, Windows PowerShell, and PowerShell 7 sessions to start in `C:\ws`; noninteractive PowerShell automation retains its caller working directory.
- Created and pushed `plan/3555-goal-statusline-pilot`.
- Added the future-tense plan and HTML review surface.
- Ran two Codex adversarial review rounds. The plan now preserves the existing catalog, picklist, approval, and runner gates; specifies a cross-platform Claude renderer; defines five machine-equivalence rows; and makes pilot evidence privacy-safe and tests-first.
- Recorded the user correction that AGY (`agy`, Antigravity) is the Gemini-backed provider surface in `.claude/memory/KNOWLEDGE.md` and `.claude/memory/topics/feedback_agy_replaces_gemini_cli.md`; regenerated the managed topic index.
- Ran an adversarial review of the AGY memory/plan update, applied every finding inline, and retained the provider review plus disposition under `scripts/review/results/`.
- Filed [#3558](https://github.com/vamseeachanta/workspace-hub/issues/3558) for the discovered provider-startup-memory cap defect: canonical shared knowledge is recallable but can be omitted from the capped startup slice.
- Posted the reviewed state and blocker on issue #3555.

## Verified state

- Latest content/review commit before this handoff refresh: `04834b0eb0f2ca136f530197af7f07e8af19c3f2`; local and remote matched.
- Memory verification: `python -m pytest scripts/memory/tests/test_build_topics_index.py scripts/memory/tests/test_recall.py -q` → 11 passed; `python scripts/memory/recall.py agy --limit 5` returns the AGY topic.
- Canonical wrapper probe: `scripts/review/submit-to-agy.sh` exits 2 with `agy CLI not found (AGY_CMD=agy)` on `ace-win-2`.
- Legal diff scan: PASS.
- Issue state: OPEN, `status:needs-plan`.
- No implementation, pilot mutation, equality regeneration, or fleet rollout has started.

## Blocker

Claude CLI OAuth is expired. The user clarified that AGY (`agy`, Antigravity) replaces the legacy Gemini CLI for this ecosystem, but `agy` is not installed or discoverable in PowerShell or Git Bash on `ace-win-2`. The T3 plan therefore lacks provider-diverse clearance and is not approval-ready. Codex returned MAJOR in both rounds; the plan text incorporates responses to all six findings, but no provider has cleared that revised text and repository policy requires another provider signal rather than a same-provider auto-cycle.

## Next checkpoint

1. Install and authenticate AGY on `ace-win-2` (or re-authenticate Claude).
2. Run the canonical `scripts/review/submit-to-agy.sh` adversarial review against `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md` at the latest branch commit.
3. If no MAJOR remains, commit/push the review artifact, post evidence to #3555, and move only to `status:plan-review`.
4. Stop for explicit user approval; never self-apply `status:plan-approved`.

## Preserved local state

- `C:\ws\wt-workspace-hub-3555-plan` is the intentional isolated planning worktree.
- The canonical `C:\ws\workspace-hub` checkout has unrelated pre-existing dirty/divergent state and was not modified for this task.
- Machine-local shell profile changes are intentional and are not repository-tracked; #3555 covers the repo-managed agent UX work, not shell startup-directory deployment.
