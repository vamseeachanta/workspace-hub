---
name: provider-session-ecosystem-audit
description: Audit Claude/Codex/Hermes/Gemini session logs, normalize provider-specific quirks, and wire recurring exports/reporting for ongoing ecosystem health checks.
version: 1.0.0
tags: [sessions, audit, providers, claude, codex, gemini, hermes, observability]
---

# Provider Session Ecosystem Audit

Use when you need a cross-provider audit of actual AI work done in the repo, or when session-log observability is incomplete and needs to be strengthened.

## When to use
- User asks for session log analysis across providers
- You need to compare Claude/Codex/Gemini/Hermes work patterns
- You need to explain missing-provider visibility gaps
- You are wiring recurring provider audit/report generation
- You need to export Gemini native sessions into repo-local orchestrator JSONL

## Core approach
1. Start from repo-local orchestrator logs and existing saved audit artifacts.
2. Treat providers differently; do not assume one common native format.
3. Separate symbolic skill/tool reads from filesystem reads before reporting missing files.
4. Prefer raw logs over saved precomputed audit artifacts when both are available.
5. Add recurring wrappers/tests/docs in the same change so the audit becomes operational, not one-off.

## Execution steps

### 1. Inventory actual data sources
Check these first:
- `logs/orchestrator/README.md`
- `logs/orchestrator/<provider>/session_*.jsonl`
- saved artifacts under `analysis/` and `docs/reports/`
- existing exporters like:
  - `scripts/cron/hermes-session-export.sh`
  - `scripts/cron/codex-session-export.sh`
  - `scripts/cron/comprehensive-learning-nightly.sh`

Do not trust docs alone; compare against actual files in the checkout.

### 2. Build/patch the provider audit script
A reusable provider audit should:
- emit stable outputs:
  - `analysis/provider-session-ecosystem-audit.json`
  - `docs/reports/provider-session-ecosystem-audit.md`
- report per provider:
  - sessions
  - post-hook records
  - top tools
  - top repos
  - top reads
  - missing repo reads
  - missing external reads
  - blank-read count
  - python3 vs `uv run ... python`
- treat provider-specific quirks correctly.

#### Codex command normalization rule
Codex logs may encode commands as single characters separated by spaces.
Do not flatten all whitespace.
Use this rule instead:
- 1-2 spaces = encoding noise between characters
- 3+ spaces = actual token boundary

This preserves meaningful shell structure such as:
- `&&`
- pipes
- redirects like `2>/dev/null`
- heredoc markers

If you flatten all whitespace, policy and usage analysis becomes misleading.
#### Required classification rules
- Hermes `skill_view` and `session_search` reads are often symbolic, not files
- slash-delimited symbolic names like `coordination/workspace/repo-capability-map` may be skills, not repo paths
- `~/.hermes/...` and similar should be expanded and classified as external, not repo-local
- repo aliases like `/mnt/workspace-hub/...` may map to the current repo root and should be normalized
- Codex command logs may be stored with single-character spacing and must be normalized before policy checks
- If raw Claude logs exist at `logs/orchestrator/claude/session_*.jsonl`, use them instead of stale saved Claude audit artifacts

### 3. Operationalize the audit
Add all three together:
- wrapper script, e.g. `scripts/cron/provider-session-ecosystem-audit.sh`
- scheduled task entry in `config/scheduled-tasks/schedule-tasks.yaml`
- lightweight tests for wrapper/schedule presence and output sanity

The wrapper should:
- run `uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py`
- verify JSON and Markdown outputs exist
- sanity-check required provider keys in the JSON output
- log to `logs/quality/provider-session-ecosystem-audit-*.log`

### 4. Update discoverability docs
Update at least:
- `logs/orchestrator/README.md`
- root `README.md`
- relevant AI docs index if one exists

Document:
- canonical command to run the audit
- canonical output paths
- scheduled task id
- input expectations per provider

## Gemini native session export
Gemini is the tricky provider.

### Native sources
Do not assume only one path. Check both:
- `~/.gemini/tmp/<repo-name>/chats/session-*.json`
- `~/.gemini/tmp/<projectHash>/chats/session-*.json`

Filter by:
- `projectHash == sha256(abs_repo_path)`

This matters because docs may mention only the repo-name path while actual sessions can live in the hash-based path too.

### Export target
Write to:
- `logs/orchestrator/gemini/session_YYYYMMDD.jsonl`

### Export record shape
For each Gemini tool call, emit records with at least:
- `ts`
- `hook: post`
- `tool`
- `gemini_tool`
- `project`
- `repo`
- `model`
- `session_id`

Useful extras:
- `project_hash`
- `tool_status`
- `native_session_file`
- `session_kind`
- `session_summary`
- `tool_call_id`
- `cmd` / `file` / `query` / `todo_count` / `error`

### Recommended Gemini tool mapping
- `run_shell_command` -> `Bash`
- `read_file` -> `Read`
- `list_directory` -> `Read`
- `write_file` -> `Write`
- `replace` -> `Edit`
- `grep_search` -> `Grep`
- `glob` -> `Grep`
- `search_file_content` -> `Grep`
- `google_web_search` -> `Browser`
- `write_todos` -> `Write`
- `codebase_investigator` -> `ToolSearch`
- `cli_help` -> `ToolSearch`
- leave interactive tools like `ask_user` unmapped unless you intentionally add a user-input category

### Critical dedupe rule
Gemini native session JSON files are mutable and get rewritten as the conversation grows.
Do NOT use a simple mtime-only append exporter.

Instead, persist state such as:
- `logs/orchestrator/gemini/.export-state.json`
- keyed by `sessionId`
- storing `exported_tool_call_ids`

Preferred dedupe key:
- native `toolCall.id`
- fallback to a fingerprint of session id + timestamp + tool name + args

Without this, repeated exports will duplicate historical Gemini tool calls.

## Verification checklist
After implementing or patching:
1. Run targeted pytest suites for the audit and wrapper/export scripts.
2. Validate scheduled tasks with the repo validator.
3. Run exporter in `--dry-run` first.
4. Run real exporter.
5. If using `--all`, make sure the exporter clears old JSONL/state first so counts are not duplicated.
   - This rule applies to Hermes, Codex, and Gemini exporters.
6. Regenerate the provider audit.
7. Confirm the audit now shows real provider coverage and low/no blank-read noise.
8. Confirm the report now includes per-provider Bash command-family summaries, not just raw Bash totals.

### Hermes exporter-specific rules
To avoid false blank reads:
- `skill_view -> Read` and export `file` + `skill_name`
- `skills_list -> ToolSearch` and export `file` + `skill_category`
- `session_search -> Grep` and export:
  - `file=__session_history__`
  - `search_query`
  - `role_filter`
  - `limit`
- Export `session_id` so Hermes runtime-session counts are meaningful
- When rerunning with `--all`, clear prior generated Hermes JSONL/state first so counts do not inflate

This change can reduce Hermes blank reads from hundreds to effectively zero.

### Codex exporter-specific rules
Codex native rollout files are mutable and often get rewritten as the conversation grows.
Do NOT rely on file mtime alone for incremental export.

Instead:
- use `uv run --no-project python`, not ad-hoc `python3 -c`
- persist state in `logs/orchestrator/codex/.export-state.json`
- key state by native rollout file path or native session id when available
- store `exported_tool_call_ids`
- prefer native payload ids such as `call_id` / `id`
- fall back to a fingerprint of session file + session id + timestamp + tool name + args

Export at least:
- `native_session_file`
- `tool_call_id`
- `session_id`
- `codex_tool`
- `cmd` / `file` / `query` / `search_root` where applicable

Without per-tool-call dedupe, rerunning the exporter after Codex appends new function calls will duplicate the already-exported history and distort provider comparisons.

### Bash command-family summaries
After provider-specific command decoding, add a lightweight cleanup pass before prefix extraction:
- drop blank/comment-only leading lines
- strip simple `cd ... &&` wrappers

Then bucket commands by family using multi-word prefixes such as:
- `git diff`
- `git status`
- `uv run`
- `python -m`
- `python3 -m`

Report per provider:
- top 8 Bash command families
- count
- share of Bash calls
- example command in JSON output

This is much more useful than a raw `Bash` tool count alone.

Example high-value verification sequence:
- `bash scripts/cron/gemini-session-export.sh --dry-run`
- `uv run pytest tests/analysis/test_provider_session_ecosystem_audit.py tests/cron/test_provider_session_ecosystem_audit_wrapper.py tests/cron/test_gemini_session_export.py`
- `uv run --no-project python scripts/cron/validate-schedule.py`
- `bash scripts/cron/gemini-session-export.sh`
- `bash scripts/cron/provider-session-ecosystem-audit.sh`

## Pitfalls
- Docs may claim Claude raw logs are absent when they are actually present in the checkout
- Hermes symbolic skill names can massively inflate false missing-file counts if treated as paths
- Codex spaced-command logging can hide `python3` policy violations unless normalized first
- Gemini cross-review `.log` files are not enough for parity analysis; you need exported native sessions
- Gemini exporter must scan both repo-name and project-hash native directories
- Gemini exporter must dedupe per tool call, not just per file timestamp

## Outcome to aim for
A good implementation leaves the repo with:
- stable cross-provider audit artifacts
- recurring scheduled refresh
- corrected provider-specific read classification
- raw Gemini session coverage in repo-local orchestrator logs
- tests proving the wrapper/export/report path remains intact
