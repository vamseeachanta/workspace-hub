# Session digest — repeatable cross-machine agent-session review

Tracking issue: [#3973](https://github.com/vamseeachanta/workspace-hub/issues/3973). Cadence (owner decision 2026-10-08): **monthly, owner-triggered**.

This tool reviews Claude Code and Codex sessions across the fleet and turns them into workflow lessons. The first run on 2026-10-08 covered 1,469 logs on the two Windows workstations and produced the rules added to `config/agents/SHARED_SOUL.md` in #3974.

**Data handling:**
- Session logs and digests contain client content. They stay on their host or in a private repository; only this tool is committed here.
- Claude Code deletes transcripts after `cleanupPeriodDays`. The canonical setting is 180 days (`config/agents/claude/settings.json`), so a monthly review always has history to read.

## Procedure

1. **Extract on each machine.** Raw logs never leave their host.
   ```
   python -I scripts/review/session-digest/extract_sessions.py --label <machine> --out <scratch>/<machine>.jsonl
   ```
   For a remote host, copy the script there, run it over SSH, then copy back only the JSONL.
   - Windows OpenSSH hosts on this tailnet run MSYS bash, so use `/c/...` paths.
   - Delete the copied script and the JSONL on the remote host afterwards.
2. **Build digests.** This step splits at session boundaries, at about 330 kB per digest.
   ```
   python -I scripts/review/session-digest/build_digests.py --out <scratch>/digests <scratch>/*.jsonl
   ```
3. **Read each digest with a read-only reviewer.**
   - Inline the digest in the prompt. A path does not work: the Codex read-only sandbox on Windows cannot start a reader process.
   - Send the prompt on stdin, for example `codex exec -s read-only -o <out>.md - < prompt.md`.
   - The prompt asks for wins, friction, user corrections, candidate lessons and metrics. It requires evidence (session fragment, timestamp and quote) for every claim, a frequency counted in distinct sessions, and "not established" where evidence is thin.
4. **Synthesize** the findings into an internal HTML report in the reporting-conventions format. Spot-check quoted evidence against the digests.
5. **Promote durable lessons.** Shared rules go in `SHARED_SOUL.md`, scripts in `scripts/`, and runner changes as issues in the owning repo. Each recommendation goes on a decision board before it is acted on.

## Limits
- Prompts are truncated at 700 characters, and only closing agent messages are kept.
- Codex child sessions replay their parent's history, so repeated text does not prove repeated execution.
- Header counters are approximate:
  - Codex denial counts read zero even where policy rejections appear in the text.
  - Error counts include intentional RED tests.

Tests: `tests/review/test_session_digest.py`.
