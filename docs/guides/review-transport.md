# Review Transport Guide

## Scope

This guide documents the non-interactive transport contract for `scripts/review/submit-to-claude.sh`
and `scripts/review/submit-to-gemini.sh`.

## Root Cause

Observed on 2026-02-27 while investigating WRK-640:

- Running `claude -p` and `gemini -p` from the `workspace-hub` repository loaded the full local
  project context, policies, and skill trees.
- In that repo-scoped mode, Claude frequently hung until timeout even for trivial prompts.
- Gemini often drifted into execution/planning behavior or stalled before returning a usable review.

Both providers returned quickly when launched from an isolated temporary directory instead of the
repository root. The transport issue was therefore primarily environment isolation, not just prompt wording.

## Provider Contract

### Claude

- Run from an isolated temporary directory.
- Use `--tools ''` to prevent tool execution.
- Use `--permission-mode bypassPermissions`.
- Use `--disable-slash-commands` and `--no-session-persistence`.
- Request `--output-format json` with a JSON schema.
- Parse `structured_output` and render the shared markdown review schema locally.

### Gemini

- Run from an isolated temporary directory.
- Use `--yolo` in headless mode to avoid hidden approval waits.
- Use `--output-format json`.
- Parse the top-level `response` field, extract the embedded JSON payload, and render the shared
  markdown review schema locally.
- Ignore the credential and YOLO banner lines that may precede the JSON body.

## Retry Policy

- Retry only for transport failures: timeout, non-zero exit, empty output, or unrenderable structured output.
- Do not retry schema-valid substantive reviews just because the verdict is unfavorable.
- Current default: `2` attempts for Claude and Gemini.

## Known Constraints

### Claude: Nested-Session Protection

Claude CLI (2.x+) refuses to start inside an existing Claude Code session. When invoked from a
terminal that has `CLAUDECODE` set (or from a process tree rooted in a session), it exits immediately
with:

```
Error: Claude Code cannot be launched inside another Claude Code session.
```

This causes `submit-to-claude.sh` to classify the result as `NO_OUTPUT` even on healthy content.
The result is _not_ a parser or prompt failure — it is an environment guard.

**Mitigation:** Run `submit-to-claude.sh` from a plain terminal (outside Claude Code) or via a cron
job. Do not invoke cross-review from within an interactive Claude Code session when a live Claude
review is required.

**Unset bypass (use carefully):** `env -u CLAUDECODE bash submit-to-claude.sh ...` — only safe when
the Claude session itself is idle and you accept shared resource risk.

### Claude: Large Diff Timeouts

For diffs or bundles exceeding ~8 KB, Claude frequently times out on the first attempt. The 2-attempt
retry with exponential back-off handles most transient cases. For large bundles, prefer a targeted
review (parser + tests + validator, no unrelated context) and use `CLAUDE_TIMEOUT_SECONDS=300`.

## Raw Artifact Preservation

`scripts/review/cross-review.sh` preserves the original provider output as a `.raw.md` sidecar before
normalizing a failed result to `NO_OUTPUT` or `INVALID_OUTPUT`. This keeps debugging evidence without
weakening the review gate.
