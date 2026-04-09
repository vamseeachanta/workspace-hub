We are in /mnt/local-analysis/workspace-hub.

Mission:
Produce an implementation-ready dossier for GitHub issue #2056 without implementing production code, because this repo currently has no open issues labeled status:plan-approved and AGENTS.md requires issue -> plan -> user approval -> implementation.

Issue:
- #2056: Session governance Phase 2: wire runtime enforcement into hooks
- Labels: enhancement, priority:high, cat:ai-orchestration, agent:claude

Source issue body:
## Context

#1839 Phase 1 delivered the checkpoint model (`governance-checkpoints.yaml`) and verification utility (`session_governor.py`). The gates exist as data but are not yet enforced at runtime.

## Task

Wire the two runtime auto-gates into Claude Code hooks so they fire automatically.

### Tool-Call Ceiling (200 calls)
- Create a hook that counts tool calls per session
- At 200 calls, auto-pause and present a progress summary
- User must confirm to continue (hard stop)
- Implementation option: Claude Code `settings.json` hook on `PostToolUse` that increments a counter

### Error Loop Breaker (3x same error)
- Track consecutive identical errors (by error message hash or pattern)
- After 3 consecutive repeats of the same error, hard stop
- Present: what errored, how many times, and suggest escalation

### Pre-Push Review Gate → Strict Mode
- Current `scripts/ai/review-routing-gate.sh` defaults to warning mode
- Promote to strict mode (exit 1 on failure) as default
- Add `REVIEW_GATE_MODE=strict` to default config
- Ensure `SKIP_REVIEW_GATE=1` bypass is logged/audited, not silent

### Tests
- Test hook counter logic
- Test error dedup/hashing
- Test gate mode switching

### References
- Checkpoint config: `scripts/workflow/governance-checkpoints.yaml`
- Session governor: `scripts/workflow/session_governor.py`
- Review gate: `scripts/ai/review-routing-gate.sh`, `scripts/ai/review_routing_gate.py`
- Governance doc: `docs/governance/SESSION-GOVERNANCE.md`
- Parent: #1839

Required behavior:
1. Do NOT ask the user any questions.
2. Do NOT implement production code, tests, hooks, workflows, or docs outside your assigned result file.
3. You MAY inspect the repo freely and you MAY write exactly one persisted artifact: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md`.
4. If you discover the issue is already fully or mostly implemented, convert the dossier into a delta report with exact remaining gaps and verification commands.
5. Use uv run for Python commands if you need Python.
6. If you need scratch notes, use /tmp only.
7. End only after `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md` exists and contains a complete dossier.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md

Intended code ownership to analyze (read-only today; use this to focus your inspection):
- docs/governance/, scripts/workflow/, .claude/hooks/, docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md

IMPORTANT negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to these other terminal outputs:
  - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-3-timeline-benchmarks.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-5-architecture-patterns.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
      - docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Required dossier structure in `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-7-governance-phase2-runtime-hooks.md`:
1. Title and issue metadata
2. Current-state findings
   - files/modules already present
   - tests already present
   - latest relevant commits if discoverable
3. Remaining implementation delta
   - exact missing behaviors
   - exact file paths that should change when implementation is approved
4. TDD-first execution plan
   - failing tests to add first
   - implementation steps second
   - verification commands
5. Risk/blocker analysis
   - plan-gate blockers
   - data/source dependencies
   - likely merge/contention concerns
6. Ready-to-execute prompt
   - a self-contained future Claude implementation prompt for this issue only
   - include acceptance criteria and cross-review requirements
7. Final recommendation
   - one of: READY AFTER LABEL UPDATE / NEEDS ISSUE REFINEMENT / ALREADY MOSTLY DONE

Verification before finish:
- confirm the dossier file exists
- include at least 3 concrete repo file paths in the analysis
- include at least 3 concrete verification commands
- include a clear recommendation line at the end
