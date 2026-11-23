# Native Claude → Hermes Flow Evidence Checklist

Use when a user asks whether native Claude work is actually flowing through Hermes Agent rather than merely existing alongside Hermes.

## Evidence tiers

1. **Native activity exists**
   - Claude native/session logs show current activity for the target repo/workdir.
   - Capture timestamp window, native session file path, cwd/project, model/provider identity, and representative tool calls.

2. **Hermes observability exists**
   - Repo-local Hermes/orchestrator logs include Claude records, e.g. `logs/orchestrator/claude/session_*.jsonl`, or another Hermes-managed export/gateway artifact.
   - Capture exporter command/run timestamp, generated JSONL paths, and record counts.

3. **Flow-through is proven**
   - A join exists between native Claude logs and Hermes records: matching session id, native session file path, launch metadata, timestamp + command/file/task correlation, or gateway/dispatch record.
   - Without this join, report “Claude activity is observable; Hermes flow-through is not proven.”

## Answer discipline

- Do not answer from desired architecture, config intent, or memory.
- Separate runtime/proxy claims from audit/export claims.
- If the evidence only proves export into Hermes logs after the fact, call that “Hermes observability/export,” not necessarily “runtime traffic routed through Hermes.”
- State exact artifact paths checked and the timestamp range.
- End with the narrow next verification step needed to close any gap.
