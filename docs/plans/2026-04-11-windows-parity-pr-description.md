Title
Windows Claude parity hardening: template safety, hook portability, and tracked readiness proof

Summary
This change set hardens Windows Claude Code parity in workspace-hub by improving the managed Claude template baseline, making active hook execution more Windows-safe, and closing the repo-side licensed-win-1 readiness proof-path gap.

What changed
1. Managed Claude template hardening
- Trimmed config/agents/claude/settings.json to a more conservative shared baseline
- Removed aggressive/local runtime choices from the managed template:
  - skipDangerousModePermissionPrompt
  - statusLine

2. Windows-safe hook/runtime behavior
- Improved active hook portability in:
  - .claude/hooks/skill-content-pretooluse.sh
  - .claude/hooks/session-governor-check.sh
  - .claude/hooks/cross-review-gate.sh
- Replaced fragile python3 parsing in skill-content-pretooluse with jq
- Replaced unconditional uv-run execution paths with portable interpreter resolution in the other targeted hooks

3. Session telemetry completion
- Completed .claude/settings.json hook wiring so session logging runs on both pre and post
- Session review hook remains wired on stop

4. Windows readiness proof-path closure
- Unignored and added tracked Windows readiness artifact path:
  - .claude/state/harness-readiness-licensed-win-1.yaml
- Set licensed-win-1 workspace root in harness config to D:\workspace-hub
- Updated compare-harness-state.sh so a fresh non-pass Windows report still degrades status, rather than appearing OK purely because it is recent
- Clarified in setup-scheduler-tasks.ps1 that NightlyReadiness updates the shared readiness proof

Why this matters
- Windows Claude Code can already consume most shared repo intelligence
- The biggest remaining gaps were in portability of active runtime behavior and proof that licensed-win-1 participates in the same readiness surface
- These changes move the ecosystem from near-ready toward confidently ready for Windows Claude use

Known limits
- The bootstrap Windows readiness artifact is intentionally a placeholder until a real NightlyReadiness run on licensed-win-1 replaces it
- Remaining python3/uv-run grep hits in the targeted hooks are comments/help text/fallback references, not active execution-path blockers
- Windows write-back parity beyond readiness proofing may still require the follow-on Package 5 work

Suggested review focus
- Managed template scope in config/agents/claude/settings.json
- Hook portability behavior in the three targeted shell hooks
- Correctness and honesty of the tracked Windows readiness artifact path and compare-harness-state semantics
