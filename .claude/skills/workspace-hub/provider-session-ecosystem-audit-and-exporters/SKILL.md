---
name: provider-session-ecosystem-audit-and-exporters
description: Build and maintain cross-provider session-log audits for Claude, Codex, Hermes, and Gemini, including exporter design, normalization, and behavioral verification.
version: 1.0.0
category: workspace-hub
tags: [session-audit, exporters, claude, codex, hermes, gemini, observability]
---

# Provider Session Ecosystem Audit and Exporters

Use when you need to audit AI-provider activity across the workspace-hub repo, improve session-log observability, or add/fix exporter pipelines for Claude/Codex/Hermes/Gemini.

## When to use
- Cross-provider session quality / drift analysis
- Building or fixing `logs/orchestrator/<provider>/session_*.jsonl`
- Reducing false positives in read-path audits
- Adding recurring audit jobs and report artifacts
- Verifying shell exporters with behavioral subprocess tests

## Core approach

1. Prefer raw provider logs over saved precomputed reports when both exist.
2. Treat symbolic tool/skill reads separately from filesystem paths.
3. Normalize provider-specific command encodings before deriving Bash metrics.
4. Add exporter behavioral tests using temp repo + temp HOME + fake shims.
5. Regenerate audit artifacts after any exporter/schema change.

## Key implementation rules

### 1. Claude
- Raw Claude orchestrator logs live at `logs/orchestrator/claude/session_*.jsonl`.
- If raw logs exist, audit them directly; only fall back to saved Claude audit JSON when raw logs are absent.
- Historical Claude raw logs may not persist `session_id`, so `unique_runtime_sessions` can be unavailable on old corpus slices; report that limitation explicitly instead of inventing heuristics.
- The minimal safe producer-side fix is in `.claude/hooks/session-logger.sh`:
  - parse `.session_id // ""` from hook stdin JSON
  - append optional top-level `session_id` to the emitted ENTRY object
  - keep existing fields and both write paths unchanged
- Once this patch is active, new Claude raw logs can support real `unique_runtime_sessions`; old logs remain legacy/no-session-id.

### 2. Codex
- Codex log commands are often stored in a spaced-character encoding.
- Do not strip all whitespace blindly.
- Decode with this rule:
  - single/double spaces = encoding noise between characters
  - runs of 3+ spaces = one real token boundary
- After decoding, derive command families from the reconstructed shell string.
- For exporter tests, use a fake `python3` shim and copy `scripts/lib/python-resolver.sh` into the temp repo.
- For `--all` behavior, clear old exported JSONL/state before re-exporting to avoid duplicate append inflation.

### 3. Hermes
- Hermes exporter false blank reads came primarily from:
  - `session_search`
  - `skills_list`
- Export them as semantic non-file search/discovery events:
  - `session_search -> Grep`
    - `file = __session_history__`
    - `search_query`, `role_filter`, `limit`
  - `skills_list -> ToolSearch`
    - `file = category or __all__`
    - `skill_category`
  - `skill_view -> Read`
    - `file = skill name`
    - `skill_name`
- Always export `session_id` from Hermes sessions.
- Hermes `--all` should remove prior `session_*.jsonl`, correction files, and state before rebuilding.
- Behavioral test should verify:
  - main JSONL output
  - correction JSONL output
  - repeated patch/write to same file creates one correction record

### 4. Gemini
- Native Gemini sessions may exist under both:
  - `~/.gemini/tmp/<repo-name>/chats/session-*.json`
  - `~/.gemini/tmp/<sha256(abs_repo_path)>/chats/session-*.json`
- Filter sessions by `projectHash == sha256(real repo root path)`.
- Gemini session files are mutable, so dedupe by `tool_call_id` (or stable fingerprint fallback) in `.export-state.json`.
- Safe tool mappings discovered:
  - `run_shell_command -> Bash`
  - `read_file`, `list_directory -> Read`
  - `write_file`, `write_todos -> Write`
  - `replace -> Edit`
  - `grep_search`, `glob`, `search_file_content -> Grep`
  - `google_web_search -> Browser`
  - `codebase_investigator`, `cli_help -> ToolSearch`
- Do not force-map `ask_user` unless you intentionally introduce a user-input category.
- Gemini `--all` should clear exported JSONL/state before rebuilding.

## Shared normalization helper
Create and reuse a shared helper for Bash family extraction, e.g. `scripts/bash_command_prefixes.py`.

It should provide:
- `cleanup_bash_command(command)`
  - remove blank/comment-only leading lines
  - strip `cd ... &&` wrappers
- `normalize_command_to_prefix(command, cleanup=False)`
  - multi-word prefixes like `git diff`, `uv run`, `python -m`, `python3 -m`

Use `cleanup=True` in the provider audit, but keep cleanup optional for permissions/allowlist tooling so behavior stays explicit.

## Report design
For each provider, keep these sections:
- top tools
- top repos
- top reads
- top symbolic reads
- top Bash command families
- top missing repo reads
- top missing external reads

For Bash command families, include:
- `prefix`
- `count`
- `share_of_bash_calls`
- `example_command` in JSON artifact (markdown can stay compact)

## Behavioral test pattern
For shell exporters, prefer subprocess tests over string-only tests.

### Common pattern
1. Copy the exporter script into a temp repo so it derives repo root from that temp location.
2. Create a temp HOME with native session fixtures.
3. Prepend a fake shim to PATH:
   - fake `uv` for Gemini/Hermes inline-python exporters
   - fake `python3` for Codex resolver-based exporter
4. Run the real shell script with `subprocess.run(..., cwd=temp_repo, env=env, capture_output=True, text=True)`.
5. Assert:
   - exit code is 0
   - output JSONL exists
   - state file exists
   - mapped fields are correct
   - rerun dedup/skip behavior works where applicable
6. Also add one hook-level behavioral test for Claude logger changes:
   - run `.claude/hooks/session-logger.sh` directly in a temp repo
   - pass stdin JSON containing `session_id`, `tool_name`, and `tool_input`
   - verify both `.claude/state/sessions/session_YYYYMMDD.jsonl` and `logs/orchestrator/claude/session_YYYYMMDD.jsonl` receive the new field without breaking existing fields

## Verification checklist
After any exporter/audit change:
1. Run targeted tests for the changed exporter and provider audit.
2. Re-run the exporter with `--all` if schema changed materially.
3. Re-run `bash scripts/cron/provider-session-ecosystem-audit.sh`.
4. Confirm in the report:
   - false blank reads dropped as expected
   - tool buckets look sane
   - command-family summaries render correctly
   - Claude limitation remains explicit if session ids are still absent

## Pitfalls
- Do not count symbolic skill/tool names as missing files.
- Do not append `--all` exports on top of existing JSONL files.
- Do not rely on only the repo-name Gemini directory; hashed project directories also matter.
- Do not estimate Claude runtime sessions from time gaps; report unavailability unless logger schema changes.
- Do not flatten Codex commands by removing all whitespace.
