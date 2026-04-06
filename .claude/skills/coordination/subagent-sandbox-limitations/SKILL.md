---
name: subagent-sandbox-limitations
category: coordination
description: Critical limitations of delegate_task subagents — sandbox isolation prevents repo writes. Use for research/analysis only, not implementation.
---

# Subagent Sandbox Limitations

## Critical: Subagents CANNOT write to repos

delegate_task subagents run in **isolated sandboxes**. This means:

- **read_file/search_files/terminal READ work** — they can inspect repo files, search content, run read-only commands
- **write_file/patch do NOT persist** — any file modifications are lost when the subagent exits
- **git commit/push NEVER happen** — sandbox has no git access to the real repos
- **terminal writes to /tmp are preserved** — but only until the next sandbox lifecycle

This was discovered during overnight batch execution on 2026-04-06 when multiple delegate_task calls appeared to complete but produced zero repo changes.

## When to use delegate_task

**DO use delegate_task for:**
- Research/analysis that only reads files
- Generating summaries, reports, or markdown documents
- Synthesis tasks (combining information from multiple sources)
- Non-interactive brainstorm or planning
- Tasks that produce output for the main agent to consume

**DO NOT use delegate_task for:**
- Creating or modifying source code files
- Writing tests to disk
- Committing to git
- Modifying pyproject.toml or config files
- Any task where the final output must be persisted to the workspace

## For implementation tasks

Use execute_code with write_file, patch, and terminal tools directly. These operate in the real filesystem and produce real commits.

## Workspace-hub specific notes

- workspace-hub repo: /mnt/local-analysis/workspace-hub
- digitalmodel repo: /mnt/local-analysis/workspace-hub/digitalmodel (SEPARATE git repo)
- Always `cd` into the correct repo for git commands
- digitalmodel has its own venv and pyproject.toml — use `cd digitalmodel && uv run pytest`
- ~32K files bytecode-compile on every pytest run (~20s overhead) — expected behavior

## Gemini via CLI — 2026-04-06 Update

All three Gemini providers tested — behavior varies by request size:

| Provider | Small request (5 tokens) | Large request (65K tokens) |
|----------|-------------------------|--------------------------|
| openrouter (google/gemini-2.5-pro) | Works | HTTP 402 — credits exhausted |
| copilot (gemini-2.5-pro) | Works | HTTP 403 — programmatic access blocked |
| huggingface (google/gemini-2.5-pro) | Works | HTTP 401 — credentials expired |

Gemini is effectively unusable for non-trivial research tasks via CLI.
Quota is tracked in `hermes insights` — check token usage before launching large Gemini sessions (5M tokens typical monthly cap across 22 sessions).

## delegate_task file write persistence is UNRELIABLE

Testing on 2026-04-06 showed inconsistent behavior:

- **Subagents 1-2**: wrote files that did NOT persist (gyradius, conference indexing — zero output)
- **Subagent 3+**: wrote files that DID persist (subsea_bridge.py 17KB, index-conferences-lightweight.py 485 lines)

Pattern observed: earlier subagents in a batch tend to lose writes; later ones persist.
This may be a sandbox lifecycle timing issue.

**Practical rule**: If you MUST delegate implementation (not just research):
1. Send only ONE implementation subagent at a time
2. Always verify the output immediately: `ls -la <expected_file>`
3. Have a fallback path to implement directly if subagent fails
