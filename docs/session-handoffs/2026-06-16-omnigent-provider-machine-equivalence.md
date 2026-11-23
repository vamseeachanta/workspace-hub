# Session handoff — Omnigent-lens provider/OS-machine equivalence program

**Date:** 2026-06-15 → 2026-06-16 · **Host:** ace-linux-1 · **Umbrella:** [#3114](https://github.com/vamseeachanta/workspace-hub/issues/3114)

## What this was
Researched Databricks **Omnigent** (meta-harness; combine/control/share agents) and turned it into a provider- & OS/machine-equivalence program for the repo ecosystem. Filed an umbrella + 5 gap issues, then took each through the hard gate (Issue → Plan → Adversarial Review → decision). The umbrella thesis held: **provider-equivalence is achievable at the artifact layers (agents, tools) and ceiling-bound at the runtime layers (spend, session-attach).**

## Final disposition (all on `main` unless noted)
| Gap | Issue | Outcome | Landed via |
|---|---|---|---|
| G1 portable agent format | #3116 | ✅ on main | merged (automation push) + oracle-fix PR #3171 |
| G2 AGENTS.md drift-guard | #3117 | ✅ on main (caught+fixed a real CLAUDE.md↔AGENTS.md drift) | PR #3170 |
| G3 MCP-first tools | #3118 | ✅ on main (Phases 0–2; codex/gemini register+connect proven) | PR #3163 |
| G4 budget-as-policy | #3119 | ⛔ DEFERRED — infeasible at hook layer | — |
| G5 cross-surface sessions | #3120 | ⏸️ DEFERRED — feasibility ceiling + thin substrate | — |

Two bugs found & fixed: #3142 review-tooling executable (PR #3152, merged); #3143 automation destroys active worktrees (in-repo guard PR #3153, merged).

## Why G4/G5 are deferred (verified, not assumed)
- **G4**: a Claude PreToolUse hook CANNOT see cumulative token/cost spend (payload = tool metadata only; cost is statusline-only). Only tool-COUNT ceilings work in a hook (`session-governor-check.sh` already exists). Real spend enforcement belongs at the SDK/dispatch layer (`ResultMessage.total_cost_usd`). See memory `reference_claude_hooks_cannot_see_spend`.
- **G5**: Claude Code can't live-resume a terminal session from Telegram/web (only shared session-STATE continuity is feasible); substrate is thin/drifted (`claim.py` cited-not-found; behavior-contract↔AGENTS.md work-queue contradiction; protocol in external llm-wiki). Depends on #2998/#2720/#2847 maturing first.

## Open at-your-pace items (none blocking)
- **#3143 Task 3** — name + fix the OUT-OF-REPO worktree sweeper (a concurrent session / Hermes job, not a repo cron). Needs `crontab -l | grep -iE 'preserve|housekeep|overnight'` (agent-permission-gated).
- **G2 #3117 coverage half** — AGENTS.md presence audit across tier-1 repos (inherits the known partial-checkout hazard: only ~3/7 siblings checked out on a1).
- **G3 #3118 follow-ups** — model actually invokes the MCP tool under `codex exec`/`gemini` sandbox (deeper than the register+connect proof done); #2887 parity predicate; migrate further #2400 tools.
- **G4/G5** — revisit if/when the runtime surfaces (SDK spend hooks; session-state substrate) exist.

## Durable lessons saved to memory (`~/.claude/.../memory/`)
- `reference_claude_hooks_cannot_see_spend` — hooks can't see spend; cost is statusline-only.
- `feedback_g1_landing_worktree_destruction_and_push_gate` — /tmp worktrees destroyed within minutes; pre-push gates; API-push is auto-denied as hook-bypass; commit early, use `git -C`.
- `feedback_3provider_review_wrappers_env_workarounds` — Codex `env -u CLAUDECODE`; Gemini `GEMINI_CLI_TRUST_WORKSPACE=true`; never use schema-conformance as an equivalence bar.

## Meta-lesson
An adversarial **Phase-0 feasibility check** caught a "capability that doesn't exist" assumption on G1, G3, G4, AND G5 — now standing practice. And: in-chat `!`-pushes silently no-op here; push from a real terminal.

## Repo state at exit
- `main` carries G1+G2+G3 + both bug fixes; 27/27 Omnigent suite green.
- No dangling session worktrees (scratch worktrees + merged branches cleaned up).
- No pending external actions. Memory + GitHub issues are the durable record.
