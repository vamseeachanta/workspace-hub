# Workspace ecosystem Codex burn lane selection

Use this reference when the user asks to burn Codex quota across a workspace-hub-style repo ecosystem and wants the selection informed by history, ambitions, and live issue queues rather than only the generated provider queue.

## Inputs to combine

1. Provider telemetry
   - Run `bash scripts/cron/provider-utilization-refresh.sh` when available.
   - Read `config/ai-tools/provider-routing-scorecard.json` and `config/ai-tools/provider-work-queue.json`.
   - Treat utilization as directional when quota sources are estimated/unavailable.

2. Live issue state
   - Prefer plan-approved, open GitHub issues.
   - Respect explicit `agent:*` labels and existing `status:working` state.
   - For large repos, avoid huge `gh issue list` payloads that can truncate; query per repo and/or by label.
   - `gh issue list --json` does not expose a `repository` field; when scanning multiple repos, add the repo name externally in the loop.

3. User history and ambition signals
   - Search recent sessions for durable themes: AI usage optimization, autonomous orchestration/control plane, repo modernization, engineering/data pipelines, document intelligence, governance/review gates, zero-waste spend.
   - Use these themes to rank equally safe issues, not to bypass plan approval or blockers.

## Safe autonomous Codex lanes

Prioritize work that is repo-local, bounded, testable, and reversible:
- CI/dependency/test-environment repair.
- CLI smoke tests and public example verification.
- Scheduler/no-op timeout diagnosis with local reproducers.
- Mechanical refactors with regression tests.
- Harness/preflight/readiness checkers.
- Provenance/citation contract work backed by fixtures.
- Dry-run automation for security or operational tasks.

## Human-in-loop / avoid lanes

Do not assign unattended Codex execution to work that depends on:
- credentials, external accounts, email/mobile/chat integrations, or live org settings;
- licensed or machine-specific environments unless already on the correct machine and authorized;
- ambiguous architecture/product strategy decisions;
- tax/personal finance decisions or source documents;
- blocked issues where the block is not explicitly bypassable by local prep.

Codex may still produce dry-run scripts, inventory reports, or blocker reports for these, but should not claim completion.

## Output shape for recommendations

When presenting a 12-hour burn plan, include:
1. primary lane bundle and why it is safest;
2. secondary/high-value lane bundle tied to user ambitions;
3. backup lane if the first repo blocks;
4. explicit avoid/blocker list;
5. provider allocation rationale; and
6. transactional closeout expectations: push, evidence comment, clean-state proof, branch/worktree disposition, and no closure before those are complete.

## Example from 2026-05 workspace-hub ecosystem review

High-confidence autonomous lanes:
- `assetutilities`: merge-marker/editable-install and CI dependency-path cleanup.
- `worldenergydata`: scheduler no-op diagnosis, CLI smoke tests, and bounded FDAS migration refactors.
- `workspace-hub`: Hermes/workstation preflight readiness and repo-local scheduled-task/runbook automation.

Caution lanes:
- broad CI architecture epics should be narrowed to an inventory/reporting or first-slice implementation and reviewed before wider execution.
- blocked document-intelligence, OpenFOAM, Windows/licensed-machine, and live integration work should remain prep-only unless the block is resolved.
