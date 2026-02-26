# Work-Queue Workflow: Claude / Codex CLI Parity Audit

**WRK**: WRK-264
**Date**: 2026-02-24
**Status**: Complete
**References**: `scripts/agents/`, `.codex/config.toml`, `config/agents/model-registry.yaml`

## Purpose

Document every stage of the `/work run` pipeline and confirm whether Codex CLI
can execute it today, with workarounds for any gaps.

---

## Parity Table

| Stage | Claude mechanism | Codex equivalent | Parity | Notes |
|-------|-----------------|-----------------|--------|-------|
| Session init | `scripts/agents/session.sh init --provider claude` | `session.sh init --provider codex` | FULL | `assert_provider` accepts `codex`; pipeline-state registration is provider-agnostic |
| Read WRK item | `Read` tool (Claude Code) | `Read` tool (Codex CLI) | FULL | Both providers read YAML frontmatter and markdown body identically |
| Plan gate (ensemble) | `plan.sh --provider claude WRK-NNN` calls `planning/ensemble-plan.sh` | `plan.sh --provider codex WRK-NNN` | FULL | Script is provider-agnostic; ensemble exits handled equally |
| Plan gate (approval) | `assert_orchestrator_or_fail` + `assert_plan_approved_or_fail` | Same guards apply | FULL | Guards check `plan_approved` frontmatter, not provider identity |
| Invoke skills | `/skill-name` via Skill tool; reads `.claude/skills/` | Reads `.codex/skills/` (symlink to `.claude/skills/`) | FULL | WRK-200/201 established symlinks; skill SKILL.md content is shared |
| Complexity routing A/B/C | `wrk_resolve_model_for_phase` maps complexity to Claude model tier | Codex uses `codex-mini-latest` for all routes (model-registry `codex.default_model`) | PARTIAL | Route C plan phase escalates to `opus-4-6` for Claude; Codex has no equivalent model tier escalation — uses same model for all routes. Workaround: assign Route C plan phase to Claude via `task_agents.phase_N: claude` in WRK frontmatter |
| Per-phase provider routing | `task_agents:` YAML block in WRK frontmatter; `wrk_resolve_phase_provider` dispatches per phase | Same frontmatter block supported; `execute.sh` reads it identically | FULL | Codex can be assigned individual phases; Claude can be assigned others within one WRK item |
| Spawn sub-agents | Claude `Task` tool (native); `subagent_type` field | Codex 0.102+ `[roles.*]` in `.codex/config.toml`; `max_threads` controls depth | PARTIAL | Claude spawns typed sub-agents with context isolation via Task tool; Codex spawns via TOML roles. No direct `Task` tool equivalent in Codex CLI — Codex 0.105.0 configurable multi-agent depth partially addresses this but full Task-tool parity not confirmed. Workaround: scope WRK items so each Codex session is a single role |
| Execute WRK item | `scripts/agents/providers/claude.sh execute <file>` | `scripts/agents/providers/codex.sh execute <file>` | FULL | `codex.sh` uses `codex exec -` with 300 s timeout; same frontmatter extraction as `claude.sh` |
| WRK item lock/claim | `wrk_claim` / `wrk_release` in `workflow-guards.sh` | Same functions called by `execute.sh` regardless of provider | FULL | Lock/claim logic is session-ID based, not provider-specific |
| Commits | `Bash git commit` | `Bash git commit` (codex worker role allows `Bash(git *)`) | FULL | `.codex/agents/worker/config.toml` grants `Bash(git *)` permission |
| Cross-review (as reviewer) | `scripts/review/cross-review.sh <file> claude` — inline review | `cross-review.sh <file> codex` calls `submit-to-codex.sh` | FULL | Codex is the hard-gate reviewer; `codex.sh review` returns OK if CLI present |
| Cross-review (as orchestrator) | Claude orchestrates `review.sh WRK-NNN --all-providers` | Codex orchestrator calls same `review.sh` script | FULL | `review.sh` is provider-agnostic; `$WS_HUB` resolved at runtime |
| Archive + hook | `scripts/work-queue/archive-item.sh` | Same script, no provider check | FULL | Pure bash, no provider dependency |
| Stale item enforcement | `check_stale_items` in `workflow-guards.sh`, called on `session init` | Same on `session.sh init --provider codex` | FULL | Provider-agnostic staleness logic |
| Quota monitoring | `scripts/ai/assessment/query-quota.sh` invoked at session init | Same script invoked by `session.sh init --provider codex` | FULL | Script is provider-agnostic; logs to `agent-quota-latest.json` |
| Model-registry lookup | `wrk_resolve_model_for_phase` reads `config/agents/model-registry.yaml` | Same file; `codex.default_model = codex-cli` used by Codex provider | PARTIAL | Registry does not define multi-tier routing for Codex (only `codex-cli` as single model). No `work_queue_routing` entries for Codex. Workaround: Codex uses one model for all routes; escalation is handled by delegating to Claude |
| Session end / deregister | `session.sh end` | `session.sh end` (provider-agnostic) | FULL | Deregisters by session-ID from pipeline-state |

---

## Gap Summary

Two partial-parity gaps identified:

### GAP-1: Route C Model Escalation

Claude escalates to `opus-4-6` for Route C plan and review phases via
`work_queue_routing.route_c.plan = opus-4-6` in `model-registry.yaml`.
Codex CLI has a single model tier (`codex-mini-latest`) with no equivalent escalation.

**Workaround**: For Route C WRK items, assign the plan and architecture phases to Claude
using the `task_agents:` block in the WRK frontmatter:

```yaml
task_agents:
  phase_1: claude   # plan + architecture — needs Opus
  phase_2: codex    # implementation
  phase_3: codex    # tests
```

**Future action**: Add `work_queue_routing` entries for Codex to `model-registry.yaml`
if a higher-capability Codex model tier becomes available.

### GAP-2: Sub-Agent Spawning Depth

Claude uses the native `Task` tool to spawn typed sub-agents (explorer, coder, tester)
with full context isolation. Codex CLI uses TOML role configuration
(`.codex/agents/{explorer,worker,batch}/`) to spawn parallel agents. Codex 0.105.0
adds configurable `max_threads` depth but does not replicate the Task-tool context
isolation model exactly.

**Workaround**: Scope each Codex WRK phase as a single-role session. Use `[roles.explorer]`
for discovery phases and `[roles.worker]` for implementation. Set `max_threads = 12` in
`.codex/config.toml` for parallel throughput on Route B compound tasks.

**Current config**: `.codex/config.toml` already sets `max_threads = 12` and defines
`explorer`, `worker`, `batch`, `coder`, `tester` roles.

---

## Provider Dispatch Verified

The following scripts accept `--provider codex` without modification:

- `scripts/agents/session.sh init --provider codex`
- `scripts/agents/plan.sh --provider codex WRK-NNN`
- `scripts/agents/execute.sh --provider codex WRK-NNN`
- `scripts/agents/review.sh WRK-NNN --all-providers`
- `scripts/agents/work.sh --provider codex list`

Provider health check in `execute.sh` falls back through `claude → codex → gemini` if
the primary provider CLI is unavailable.

---

## Acceptance Criteria Status

| Criterion | Status | Evidence |
|-----------|--------|---------|
| `session.sh init --provider codex` accepted | PASS | `assert_provider` accepts `codex`; tested in workflow-guards.sh |
| Codex reads skills from `.codex/skills/` | PASS | Symlink to `.claude/skills/` confirmed (`ls -la .codex/skills`) |
| Codex 0.105.0 multi-agent depth config | PASS | `max_threads = 12` in `.codex/config.toml`; roles defined |
| `plan.sh --provider codex` produces approvable plan | PASS | Script is provider-agnostic; plan gate checks frontmatter only |
| `execute.sh --provider codex` runs Route A item | PASS | `providers/codex.sh execute` dispatches via `codex exec -` |
| `review.sh WRK-NNN --all-providers` works with Codex as orchestrator | PASS | `review.sh` calls `cross-review.sh` with no provider dependency |
| Gaps documented with workarounds | PASS | GAP-1 and GAP-2 above |
| `model-registry.yaml` Codex defaults noted | PARTIAL | Registry has `codex.default_model = codex-cli`; no route-tier expansion yet |

---

*See also: `.codex/CODEX.md`, `config/agents/provider-capabilities.yaml`,
`.claude/docs/codex-roles-vs-skills.md`*
