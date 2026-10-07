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
  - remediation hints for stale repo reads
  - missing external reads
  - blank-read count
  - python3 vs `uv run ... python`
- emit an executive migration-debt summary derived from remediation-mapped stale reads
- treat provider-specific quirks correctly.

  - known migration debt per 1k records
  - rule-cluster count
  - top migration rule id / reads / share
  - provider rank by migration-debt density
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
### 4. Update discoverability docs
Update at least:
- `logs/orchestrator/README.md`
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
- where stale-path redirects live (`docs/ops/legacy-claude-reference-map.md`)
- which docs are intentionally allowed to mention legacy paths vs which should stay clean

When the audit reveals stale path drift, also patch the redirect surfaces that teach agents what to do instead. In this repo the highest-value targets were:
- `docs/ops/legacy-claude-reference-map.md`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`
- `GEMINI.md`
- `.planning/templates/route-c-*.md`
- `.planning/skills/skill-knowledge-map.md`

Then add docs regression tests so deleted paths cannot silently spread back into current planning/onboarding docs.



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

### Migration-debt remediation summaries
When stale repo reads cluster around known removed workflow surfaces, add redirect intelligence directly into the audit output rather than only listing missing files.

Recommended pattern:
- maintain a small static rule catalog in the audit script
- group top missing repo reads into reusable remediation clusters
- include for each cluster:
  - `rule_id`
  - `matched_paths`
  - `total_count`
  - `canonical_targets`
  - `guidance`
  - `reference_doc`
- expose this per provider as `missing_repo_read_remediation_hints`
- render a markdown subsection such as `### <provider> remediation hints for stale repo reads`

High-value legacy clusters seen in practice:
- old `scripts/work-queue/*` transition scripts -> governance docs/hooks
- old `generate-html-review.py` -> `scripts/review/cross-review.sh` + current review evidence/template surfaces
- old work-queue lifecycle scripts -> `scripts/refresh-agent-work-queue.*`, `notes/agent-work-queue.md`, `.planning/`, GitHub issues
- removed work-queue skills -> `AGENTS.md`, GSD command/workflow surfaces
- removed `scripts/agents/*` wrapper tree -> `AGENTS.md`, current architecture docs, review/planning entrypoints
- local `.claude/work-queue/*` item files -> GitHub issues + `.planning/` as canonical source of truth

Also add an executive-summary migration-debt ranking using remediation-mapped stale reads:
- `known_migration_debt_reads`
- `known_migration_debt_per_1k_records`
- `known_migration_debt_rule_count`
- `top_migration_rule_id`
- `top_migration_rule_reads`
- `top_migration_rule_share_pct`
- `migration_debt_rank`

Rank providers primarily by `known_migration_debt_per_1k_records`, then by mapped debt volume.
Label the scope clearly: this is a bounded/actionable migration-debt view derived from remediation-mapped entries in top missing repo reads, not a full census of all missing reads.

### Migration-debt and stale-path remediation summaries
After computing `top_missing_repo_reads`, add a remediation layer:
- match known stale paths/prefixes to canonical redirect rules
- group matched stale paths into remediation clusters
- emit per-provider `missing_repo_read_remediation_hints`
- include:
  - `rule_id`
  - `total_count`
  - `matched_paths`
  - `canonical_targets`
  - `guidance`
  - `reference_doc`

Then build an executive-summary migration-debt ranking using remediation-mapped stale reads:
- `known_migration_debt_reads`
- `known_migration_debt_per_1k_records`
- `known_migration_debt_rule_count`
- `top_migration_rule_id`
- `top_migration_rule_reads`
- `top_migration_rule_share_pct`
- `migration_debt_rank`

Important scope note:
- this metric is intentionally bounded to remediation-mapped stale reads from the provider's top missing repo reads, not all missing-path drift

This turns the audit from a dead-file leaderboard into an actionable migration-debt report.

### Doc guardrails to keep drift from returning
After cleaning high-value stale references in tracked planning/docs files, add regression tests such as:
- a strict banned-reference test for curated instructional files
- an allowlist-based test proving stale-path mentions remain confined to explicit legacy/reference docs only

Good first strict targets:
- `.planning/templates/route-c-*.md`
- `docs/context-pipeline.md`

Good allowlisted legacy/reference docs:
- `GEMINI.md`
- `docs/work-queue-workflow.md`
- `docs/ops/legacy-claude-reference-map.md`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`

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

## Regression guardrails for stale-path drift
After the audit starts surfacing recurring stale repo reads, add lightweight regression tests so cleaned docs/templates do not drift back toward deleted workflow paths.

Recommended pattern:
- create a shared helper under `tests/helpers/` that centralizes banned stale-path regexes and a file scanner
- add a strict curated docs test for high-value instructional files (for example Route-C templates and current workflow docs)
- add an allowlist-based docs test proving stale-path mentions are confined to explicit legacy/reference docs only
- expand the allowlist-scan over time as more live docs are cleaned
- add an audit test proving remediation hints still cover the highest-value stale families:
  - `scripts/work-queue/*`
  - `scripts/agents/*`
  - `.claude/work-queue/*`
  - old work-queue skill paths

This turns the audit from passive reporting into an active anti-regression system.

## Executive migration-debt summary
Once remediation hints exist, add a compact executive-summary ranking so the worst provider drift rises to the top immediately.

Recommended derived fields:
- `known_migration_debt_reads`
- `known_migration_debt_per_1k_records`
- `known_migration_debt_rule_count`
- `top_migration_rule_id`
- `top_migration_rule_reads`
- `top_migration_rule_share_pct`
- `migration_debt_rank`
- `migration_debt_status`

Preferred ranking:
- sort by `known_migration_debt_per_1k_records` descending
- tie-break with total known mapped debt, then top-rule volume

Important scope note:
- label this as remediation-mapped / top-missing-read migration debt, not a full census of all missing-path drift

## Outcome to aim for
A good implementation leaves the repo with:
- stable cross-provider audit artifacts
- recurring scheduled refresh
- corrected provider-specific read classification
- raw Gemini session coverage in repo-local orchestrator logs
- remediation hints for stale repo reads in both JSON and Markdown outputs
- executive migration-debt ranking across providers
- docs/tests guardrails that prevent cleaned workflow surfaces from reintroducing deleted paths
- tests proving the wrapper/export/report path remains intact
