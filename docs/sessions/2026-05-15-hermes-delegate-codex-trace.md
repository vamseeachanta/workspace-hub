# Hermes delegate_task → Codex hand: empirical trace (#2702)

> **Status:** partial — captured from the 2026-05-14/15 kanban-worker incident rather than a fresh live `hermes chat -z` invocation, since [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) makes tool-using delegations hang indefinitely.
> **Issue:** [#2702](https://github.com/vamseeachanta/workspace-hub/issues/2702)
> **Related:** [#2718](https://github.com/vamseeachanta/workspace-hub/issues/2718) (kanban-worker dispatch hazards), [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) (codex-cli 0.130.0 stdin-hang)

## What delegate_task actually does on this Hermes install

Verified via direct source inspection of `~/.hermes/hermes-agent/tools/delegate_tool.py`:

- `delegate_task` is a **TOOL** registered against the `delegation` toolset (ToolSpec: `name="delegate_task", toolset="delegation"`), not a CLI subcommand. Invocation surface is `hermes chat -z "<prompt that uses delegate_task tool>" --toolsets delegation,...`.
- Recursive delegation is blocked (`DELEGATE_BLOCKED_TOOLS` includes `delegate_task` itself), as are `clarify`, `memory`, `send_message`, `execute_code`.
- Tool parameters: `goal`, `context`, `toolsets`, `tasks`, `max_iterations`, `acp_command`, `acp_args`, `role`.
- The `acp_command` parameter is the explicit knob for routing a child to a specific ACP server (e.g., `claude` for Claude Code CLI).

## Codex-hand round-trip: empirical evidence from kanban-worker incident

The kanban worker is a `delegate_task`-equivalent spawn (the dispatcher forks `hermes -p default --skills kanban-worker chat -q work kanban task <id>` for each ready task — equivalent semantics to `delegate_task` with `acp_command` implicit and `goal` derived from the task body). Tonight's incident captured two distinct failure shapes for this routing path:

### Run 1 — `t_03958890` (2026-05-15 04:00 UTC)

| Event | Time | Detail |
|---|---|---|
| claimed | 04:00 | lock=`ace-linux-1:51414`, PID 231350 |
| spawned | 04:00 | `hermes -p default --skills kanban-worker chat -q work kanban task t_03958890` |
| crashed | 04:02 | `exit_kind=nonzero_exit`, `exit_code=1` (≈ 2 min after spawn) |
| gave_up | 04:02 | `failures=1`, `effective_limit=1`, trigger=`crashed` |

Logs at `~/.hermes/logs/errors.log` around that window showed only a benign `Skill name collision for 'kanban-worker'` warning (since cleaned). **The actual exit reason was not captured in any inspected log file** — `agent.log`, `gateway.log`, `errors.log`, `sessions/` did not record the worker's exit cause. Diagnostic gap.

### Run 2 — `t_bb46b4a1` (2026-05-15 04:20 UTC)

After resolving the skill-collision red herring (deletion of repo-local `kanban-worker/SKILL.md`):

| Event | Time | Detail |
|---|---|---|
| claimed | 04:20 | lock=`ace-linux-1:693351`, PID 693424 |
| spawned | 04:20 | same invocation pattern |
| claim_extended | 04:36, 04:51, 05:06 | `reason=pid_alive`, **`last_heartbeat_at: None`** for ALL three extensions |
| SIGTERM by monitor | 05:20 | Worker ran 60m wall-clock, used ~54s CPU (≈1.5% util), zero progress comments on the issue, zero file edits, zero commits |

### Provider routing chain (verified)

- `hermes status` shows `Provider: OpenAI Codex`.
- `~/.hermes/hermes-agent/.venv/bin/hermes --version` → `Hermes Agent v0.13.0 (2026.5.7)`.
- `hermes tools list | grep delegation` → `✓ enabled  delegation  👥 Task Delegation`.
- `Provider: OpenAI Codex` means Hermes routes via `codex exec` subprocess for tool-using prompts (per [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) "Hermes routing also affected" section). The kanban worker IS a tool-using prompt.

### Interpretation

The kanban-worker invocation is functionally `delegate_task` to a default-profile (Codex-routed) child with full tool surface. Two empirical observations from tonight:

1. **Tool-using delegate_task does NOT round-trip cleanly** on this install. Run 2's silent-hang for 60 min with no heartbeats is the [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) "hangs on tool-using prompts" symptom manifesting at the kanban-worker layer.
2. **Trivial (30-byte) delegate_task does round-trip** per [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715)'s own evidence ("a 30-byte 'say hello' probe returns in 30s, exit 0"). The infrastructure mechanically works; the regression is upstream in `codex exec`.

The plan's `check_codex_roundtrip` AC is therefore **PARTIAL**: round-trip mechanics confirmed for trivial probes, broken for real-work tool-using prompts until [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) closes.

## What was NOT done in this session (deferred)

- Fresh live `hermes chat -z "...delegate_task..."` invocation with the Codex hand and full stdout/stderr capture. Tonight's #2718 evidence is sufficient given the recurrence of the upstream regression on tool-using prompts; a fresh attempt would likely reproduce the 60-min hang and burn quota for no new information.
- ACP-mode test where Hermes calls `delegate_task` with `acp_command="claude"` for the Claude Code hand. Deferred pending [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) (so we can isolate Claude-side behavior from the Codex-route hang).
- Anthropic console.anthropic.com pre/post snapshots — point-in-time observations that require an actually-completing call to bracket meaningfully.

Recommend the live re-runs after [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) closes; the audit can complete its `check_dashboard_moved` and `check_d7_reconciliation` steps then.
