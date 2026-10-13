# Codex exec review patterns

Use this when launching Codex as a non-interactive adversarial reviewer from Hermes or shell automation.

## Known-good read-only review command

```bash
codex exec \
  -C /abs/path/to/repo \
  -s read-only \
  - < /abs/path/to/review-prompt.md \
  > /tmp/codex-review.out 2>&1
```

Notes:
- Use `-C` for workdir in `codex exec` lanes.
- Use `-s read-only` for review-only lanes. Use `--sandbox workspace-write` / `-s workspace-write` only for write-capable implementation lanes.
- Use `- < prompt.md` for long prompts. This avoids shell quoting limits and makes the prompt artifact auditable.
- Redirect stdout/stderr to a log file and read/verify the final verdict from that artifact.
- Do not pass legacy/top-level approval flags into `codex exec` unless confirmed by `codex exec --help`; unsupported flags can fail before review starts.

## Rerun rule after fixing MAJOR findings

If Codex returns `MAJOR` on an implementation review:
1. Extract the specific blockers into tests or explicit verification checks.
2. Fix implementation under TDD.
3. Regenerate the review prompt from the latest diff/artifacts.
4. Rerun Codex from a fresh prompt/log path.
5. Preserve both initial review and re-review artifacts when they are part of closeout evidence.

## Trust boundary

When Codex says sandbox restrictions prevented file reads, treat its verdict as based only on prompt-provided context. For high-stakes reviews, embed the complete relevant diff/plan/test evidence in the prompt instead of relying on Codex to inspect the filesystem.
