# Archived Skill: `provider-session-ecosystem-audit-and-exporters`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/provider-session-ecosystem-audit-and-exporters`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/provider-session-ecosystem-audit-and-exporters`
Consolidation date: 2026-04-29

---

---
name: provider-session-ecosystem-audit-and-exporters
description: Build and maintain cross-provider session-log audits for Claude, Codex, Hermes, and Gemini, including exporter design, normalization, and behavioral verification.
version: 1.1.0
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
- Decode only when the payload actually looks like spaced-character encoding.
- Preserve normal commands such as `git status --short`.
- Decode with this rule:
  - single/double spaces = encoding noise between characters
  - runs of 3+ spaces = one real token boundary
- After decoding, derive command families from the reconstructed shell string.
- For exporter tests, use a fake `python3` shim and copy `scripts/lib/python-resolver.sh` into the temp repo.
- For `--all` behavior, clear old exported JSONL/state before re-exporting to avoid duplicate append inflation.
- Exporter must handle native Codex command payloads in all observed shapes:
  - `command` as string
  - `cmd` as string
  - `cmd` as list
- Map Codex MCP/GitHub fetch/search tool variants into semantic categories where possible so Codex is not falsely read-light:
  - file/resource fetch variants -> `Read`
  - search/query variants -> `Grep`
- Capture semantic fields such as `file`, `query`, `search_root`, or `resource` when present.

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
  - strip wrapper/setup lines that are not the real command
  - strip leading and inline env-assignment prefixes such as `WT=...` or `GIT_PAGER=cat`
- `normalize_command_to_prefix(command, cleanup=False)`
  - multi-word prefixes like `git diff`, `uv run`, `python -m`, `python3 -m`

Use `cleanup=True` in the provider audit, but keep cleanup optional for permissions/allowlist tooling so behavior stays explicit.

## Report design
Separate event-time activity from corpus-shape churn.

### Executive summary blocks to maintain
### Executive summary blocks to maintain
Keep these machine-readable summary blocks in `analysis/provider-session-ecosystem-audit.json`:
- `recent_activity_since_previous_audit`
- `recent_activity_windows`
- `corpus_change_since_previous_audit`
- `provider_interpretation_summary`
- `executive_actions`

As the executive layer matures, keep these compact sub-blocks inside `provider_interpretation_summary` and mirror them into `executive_actions` when they are intended for operators/automation:
- `recommended_actions`
- `rank_movements`
- `health_overview`
- `watchlist`
- `change_alerts`
- `remediation_playbooks`
- `followup_issue_drafts`

Within `provider_interpretation_summary` / `executive_actions`, maintain compact operator/automation surfaces:
- `recommended_actions`
- `rank_movements`
- `health_overview`
- `watchlist`
- `change_alerts`

Use them for different operator questions:
- `recent_activity_since_previous_audit`
Use them for different operator questions:
- `recent_activity_since_previous_audit`
  - What actually happened since the last audit by event timestamp?
- `recent_activity_windows`
  - What happened in the rolling `last_24h` and `last_7d` windows, and is a provider bursty vs sustained?
- `corpus_change_since_previous_audit`
  - Did the exported corpus grow, shrink, or get rebuilt/backfilled?
- `provider_interpretation_summary`
  - Which provider needs attention and why?
- `executive_actions`
  - What should downstream automation or the operator do next?

For `recent_activity_windows`, keep at least:
- `generated_at`
- `status`
- `windows.last_24h`
- `windows.last_7d`

Each window should expose:
- `window_start`
- `window_end`
- `status`
- `scope_note`
- `providers`
- `ranked_providers`

Per-provider window stats should mirror the event-time recent-activity block where possible:
- `post_records`
- `sessions`
- `top_tools`
- `top_missing_repo_reads`
- `top_bash_command_families`

### Provider interpretation summary
For each provider, include compact operator-facing fields such as:
- `urgency_score`
- `urgency_tier`
- `urgency_rank`
- `previous_urgency_rank`
- `urgency_rank_delta`
- `urgency_rank_direction`
- `urgency_score_delta`
- `urgency_movement_summary`
- `activity_status`
- `activity_trend`
- `corpus_status`
- `debt_status`
- `debt_trend`
- `drift_trend`
- `python_hygiene_status`
- `python_hygiene_trend`
- `activity_window_profile`
- `last_24h_post_records`
- `last_24h_sessions`
- `last_7d_post_records`
- `last_7d_sessions`
- `health_status`
- `health_reasons`
- `health_summary`
- `primary_issue`
- `recommended_action`
- `recommended_actions`
- `missing_repo_reads_per_1k_records`

For the operator-action layer, also expose:
- watchlist trigger metadata:
  - `trigger_level`
  - `trigger_reason`
  - `suggested_followup`
- change-detection metadata:
  - `change_type`
  - `previous_trigger_level`
  - `current_trigger_level`
  - `previous_health_status`
  - `current_health_status`
  - `previous_urgency_rank`
  - `current_urgency_rank`
  - `summary`
- remediation routing metadata:
  - `inspect_paths`
  - `canonical_targets`
  - `first_steps`
  - `reference_doc`
  - `guidance`
  - `owner_surface`
  - `owner_team`
  - `preferred_fix_lane`
- follow-up issue draft metadata:
  - `title`
  - `severity`
  - `body`

Sort provider rows by descending `urgency_score` so markdown and JSON agree on priority.

### Markdown sections to render
Include these report sections:
- `## Provider interpretation summary`
- `Focus this week:`
- `Recommended actions:`
- `## Recent activity since previous audit`
- `## Corpus change since previous audit`

Render provider rows compactly with inline trend annotations, for example:
- `activity=active (stable)`
- `debt=high_debt (improving)`
- `python=uv_preferred (stable)`

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

For the executive provider interpretation layer, expose both human-readable and machine-readable movement context across audits:
- per-provider fields:
  - `urgency_rank`
  - `previous_urgency_rank`
  - `urgency_rank_delta`
  - `urgency_rank_direction`
  - `urgency_score_delta`
  - `urgency_movement_summary`
  - `activity_window_profile`
  - `last_24h_post_records`
  - `last_24h_sessions`
  - `last_7d_post_records`
  - `last_7d_sessions`
  - `health_status`
  - `health_reasons`
  - `health_summary`
- compact executive block:
  - `focus_this_week`
  - `recommended_actions`
  - `rank_movements`
  - `health_overview`
  - `watchlist`
  - `change_alerts`
  - `remediation_playbooks`

Guidance:
- derive rank movement from the previous audit's `provider_interpretation_summary.providers` ordering, not from ad hoc score sorting outside the tracked artifact
- explain movement using the already-derived trends (`activity_trend`, `debt_trend`, `drift_trend`, `python_hygiene_trend`) plus corpus anomalies
- add rolling event-time windows for `last_24h` and `last_7d` using the same raw-log filtering logic as the since-previous-audit block; keep them separate from snapshot/corpus reconciliation logic
- derive a compact `activity_window_profile` such as `dormant`, `burst_active`, `sustained_background`, or `light_recent`
- derive `health_status` from urgency tier + debt/drift/python signals + rolling-window profile so the report has an immediate red/yellow/green operator surface
- derive `watchlist` from health/urgency/activity-profile conditions and keep levels compact (`page`, `act_this_week`, `investigate`, `monitor`)
- derive `change_alerts` only for meaningful state transitions versus the previous tracked audit: trigger escalation, health worsening, new watchlist entry, cleared watchlist, or urgency-rank improvement
- derive `remediation_playbooks` from provider-specific `missing_repo_read_remediation_hints` when a mapped rule exists; otherwise fall back to generic playbooks for drift/export anomalies/monitoring
- attach explicit routing metadata to remediation playbooks (`owner_surface`, `owner_team`, `preferred_fix_lane`) so downstream issue generation and triage do not need to rediscover ownership
- derive `followup_issue_drafts` from watchlist + remediation playbooks for every non-monitor provider; include at least `title`, `severity`, `owner_team`, `preferred_fix_lane`, and an issue-ready `body`
- add draft dedupe metadata so recurring audits can detect repeated issue seeds without spam:
  - `draft_key`
  - `dedupe_scope`
  - `duplicate_of_previous_draft_key`
- compute `draft_key` from a stable fingerprint of provider, primary issue, preferred fix lane, owner team, severity, and trigger level
- `dedupe_scope` should be human-readable, e.g. `provider:primary_issue:preferred_fix_lane`
- compare against the prior audit's `followup_issue_drafts` to populate `duplicate_of_previous_draft_key` when the draft fingerprint is unchanged
- add follow-up draft lifecycle metadata so downstream automation can distinguish stable recurring work from net-new or changed work:
  - `draft_state` (`new`, `unchanged`, `changed`)
  - `previous_title`
  - `previous_severity`
  - `previous_owner_team`
- derive `draft_state` by matching the prior audit's draft set first by provider identity and then by `draft_key`
- emit `cleared_followup_issue_drafts` for providers that had a prior actionable draft but no longer produce one in the current audit; each cleared row should carry the prior draft identity and use `draft_state = cleared`
- add issue-posting readiness metadata so downstream automation can safely decide whether to open a GitHub issue now:
  - per draft: `minimum_evidence_present`, `should_open_issue`, `issue_open_reason`, `blocker_reason`, `evidence_gaps`
  - executive block: `issue_posting_readiness`
- compute `minimum_evidence_present` from the presence of concrete remediation evidence such as `inspect_paths`, `canonical_targets`, `first_steps`, `reference_doc`, `guidance`, `trigger_reason`, `suggested_followup`, `owner_team`, and `preferred_fix_lane`
- if evidence is incomplete, set `should_open_issue = false` and populate `blocker_reason` with the missing fields
- if evidence is complete but `draft_state == unchanged`, keep `should_open_issue = false` and explain that duplicate issue creation should wait until linked-issue state is known
- only mark drafts `ready` / `should_open_issue = true` when evidence is complete and the draft is materially `new` or `changed`
- add live GitHub issue linkage awareness before the final open/no-open decision:
  - load a repo-local issue index via `gh issue list --state all --json number,title,state,url`
  - enrich readiness rows with `linked_issue_number`, `linked_issue_url`, `linked_issue_state`, `linkage_confidence`, `should_open_issue_final`, `final_posting_status`, `final_open_reason`, and `final_blocker_reason`
  - final decision policy:
    - incomplete evidence -> blocked
    - linked open issue -> blocked (`final_blocker_reason` should cite the issue number)
    - linked closed issue -> ready to open a fresh follow-up
    - unchanged + unlinked -> ready once (do not keep blocking merely because the draft is unchanged)
- make issue linkage resilient to title drift by emitting deterministic draft linkage identity:
  - per draft: `linkage_key`, `linkage_aliases`
  - `linkage_key` should be stable and compact, e.g. `provider:primary_issue:severity:preferred_fix_lane`
  - `linkage_aliases` should include the current title, severity-stripped title, previous title when present, severity-stripped previous title, `linkage_key`, and `dedupe_scope`
- match linked issues in this order and expose provenance in readiness rows:
  1. exact current title
  2. exact previous title
  3. exact alias match
  - emit `matched_on` and `linked_issue_match_reason` so operators/automation can see why a link was chosen
- when readiness is called on synthetic/minimal draft rows (for tests or future consumers), derive fallback `linkage_key` and `linkage_aliases` from title/provider/severity/lane rather than assuming they were precomputed by draft generation
- render `state=...` inline in markdown draft summaries, add a compact `Issue posting readiness:` section, and include `matched_on=...` plus the final open/block reason
- include movement text, watchlist text, change-alert text, remediation routing text, issue-posting readiness, and issue-draft summaries in markdown so operators can triage without opening the JSON

  - expose `linked_issue_number`, `linked_issue_url`, `linked_issue_state`, `linkage_confidence`
  - derive `should_open_issue_final`, `final_posting_status`, `final_open_reason`, `final_blocker_reason`
- final decision rules that worked well in practice:
  - missing evidence -> final blocked
  - linked OPEN issue -> final blocked (`linked open issue already exists: #<n>`)
  - linked CLOSED issue -> final ready (`safe to open a fresh follow-up`)
  - no linked issue + new/changed draft -> final ready
  - no linked issue + unchanged draft -> final ready once (`unchanged draft has no linked issue; safe to open once`)
- keep both layers in the JSON: draft-layer readiness (`should_open_issue`) and linkage-aware final readiness (`should_open_issue_final`) so operators can distinguish evidence sufficiency from duplicate-prevention logic
- render `state=...` inline in markdown draft summaries, add a compact `Issue posting readiness:` section including `final_should_open` and `linked_issue=...`, and add a compact cleared-drafts section when non-empty
- include movement text, watchlist text, change-alert text, remediation routing text, issue-posting readiness, and issue-draft summaries in markdown so operators can triage without opening the JSON

  - `page -> critical`
  - `act_this_week -> high`
  - `investigate -> medium`
  - `monitor -> low`
- skip follow-up issue draft creation for `monitor` providers so recurring audits do not seed low-value issue spam
- include issue-draft summaries in markdown so operators can scan draftable work without opening the JSON
- include movement text, watchlist text, change-alert text, remediation routing text, and issue-draft text in markdown so operators can triage without opening the JSON
- keep `rank_movements` filtered to meaningful entries (`up`, `down`, `new`) so the machine-readable executive block stays compact even when all providers are stable
- keep `health_overview`, `watchlist`, and `remediation_playbooks` unfiltered so dashboards and cron consumers always have a compact per-provider status table

- derive `health_status` from urgency tier + debt/drift/python signals + rolling-window profile so the report has an immediate red/yellow/green operator surface
- derive a `watchlist` with `trigger_level`, `trigger_reason`, and `suggested_followup` so the audit becomes actionable rather than purely descriptive
- emit `change_alerts` only for meaningful threshold crossings relative to the previous tracked audit:
  - trigger escalation
  - health-color worsening
  - new watchlist entry
  - cleared watchlist
  - meaningful urgency-rank rise
- build `remediation_playbooks` from rule-backed remediation hints when available (`missing_repo_read_remediation_hints` / `LEGACY_REMEDIATION_RULES`), otherwise fall back to generic playbooks for drift/backfill/corpus-anomaly cases
- include exact `inspect_paths`, `canonical_targets`, `first_steps`, `reference_doc`, and `guidance` in the remediation playbooks so operators can start work immediately
- include both movement text and health text in markdown so operators can triage without opening the JSON
- keep `rank_movements` filtered to meaningful entries (`up`, `down`, `new`) so the machine-readable executive block stays compact even when all providers are stable
- keep `health_overview` unfiltered so dashboards and cron consumers always have a compact per-provider status table

- keep `health_overview` unfiltered so dashboards and cron consumers always have a compact per-provider status table
- allow `change_alerts` to be empty when no threshold crossed; that is the desired noise-reduction behavior, not a data-loss bug

  - `trigger_reason`
  - `suggested_followup`
  - `health_status`
  - `urgency_tier`
  - `primary_issue`
- keep watchlist sorted by escalation severity so cron consumers can act without recomputing policy
- include movement text, health text, and watchlist trigger text in markdown so operators can triage without opening the JSON
- keep `rank_movements` filtered to meaningful entries (`up`, `down`, `new`) so the machine-readable executive block stays compact even when all providers are stable
- keep `health_overview` unfiltered so dashboards and cron consumers always have a compact per-provider status table
- keep `watchlist` unfiltered as the canonical escalation surface for downstream notifications and alert-threshold logic

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

## Operator closeout workflow for audit-refresh tasks
When the user asks to review provider work / strengthen the repository ecosystem, the reusable closeout pattern is:

1. Regenerate the audit and run the targeted provider-audit tests.
2. Read the current `executive_summary.provider_interpretation_summary`, especially `watchlist`, `followup_issue_drafts`, and `issue_posting_readiness`.
3. Before creating any new GitHub issue from a ready draft, run targeted `gh issue list --state all --search ...` queries for the draft's provider, primary issue, key stale path families, and generic terms like `provider-session` / `migration debt`.
4. If existing open issues cover the finding, do not create duplicates. Add a concise audit-refresh comment to the most relevant umbrella/remediation issues with:
   - generated audit timestamp and artifact paths
   - current provider priority metrics
   - exact verification commands and pass/fail results
   - recommendation to reconcile issue mapping before opening more tickets
5. Commit only durable regenerated artifacts such as `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md`. Leave transient `.claude/state/*` session/correction churn uncommitted unless the task explicitly asks to preserve it.
6. If `git add` or `git commit` fails on `.git/index.lock`, first check for live git/gh processes with `ps`; if none are active, remove the stale lock and retry.
7. Verify `origin/main` matches `HEAD` after push, then report commit SHA, tests, issue comments, and any intentionally uncommitted transient state.

## Drift-classification expansion pattern
When provider audits show large `missing_repo_reads` for Codex/Hermes, first classify the path drift before creating remediation work. The #2333 pattern that worked:

1. Sample top missing reads and separate true actionable repo drift from benign/generated/cross-repo noise.
2. Add narrow taxonomy buckets before changing urgency policy. For generated/static-site paths, use a `non_repo_artifact` bucket for attested examples such as `content/demos/`, `content/partials/`, `examples/demos/gtm/output/`, `build.js`, `vercel.json`, and root `package.json` when they are absent from the repo.
3. Preserve precedence: existing repo files remain `repo`, known sibling workspace repos remain `sibling_repo`, absolute external/transient paths remain external/transient; only missing repo-relative attested artifacts become `non_repo_artifact`.
4. Exclude non-repo artifacts from actionable `missing_repo_reads`, `top_missing_repo_reads`, and remediation hints, but expose them separately in JSON/Markdown as `top_non_repo_artifact_reads` and `non_repo_artifact_read_total` so noise reduction remains auditable.
5. Keep schema parity for raw providers and fallback/precomputed summaries by adding empty/default values for new fields.
6. Add tests for classifier precedence, summary exclusion, markdown rendering, fallback schema defaults, positive/zero/negative corpus reconciliation gaps, and JSON scope notes before regenerating artifacts.
7. Re-run the provider audit wrapper after tests, but if the only subsequent changes are timestamp/recent-activity churn from re-running the wrapper after commit/review, restore generated artifacts to the committed verified snapshot rather than creating noisy follow-up commits.

## Verification checklist
After any exporter/audit change:
1. Run targeted tests for the changed exporter and provider audit.
2. Re-run the exporter with `--all` if schema changed materially.
3. Re-run `bash scripts/cron/provider-session-ecosystem-audit.sh`.
4. Confirm in the report/JSON:
   - false blank reads dropped as expected
   - tool buckets look sane
   - command-family summaries render correctly
   - recent event-time activity and corpus-change sections do not contradict each other
   - provider interpretation ordering matches urgency sorting
   - trend annotations render and compare against the previous tracked audit
   - watchlist and change-alert outputs are present and consistent with prior-audit deltas
   - empty `change_alerts` on a stable run is acceptable and should not be treated as a failure
   - Claude limitation remains explicit if session ids are still absent

## Pitfalls
- Do not count symbolic skill/tool names as missing files.
- Do not append `--all` exports on top of existing JSONL files.
- Do not rely on only the repo-name Gemini directory; hashed project directories also matter.
- Do not estimate Claude runtime sessions from time gaps; report unavailability unless logger schema changes.
- Do not flatten Codex commands by removing all whitespace.
- Do not confuse event-time recent activity with corpus backfill/rebuild churn.
- Do not prioritize providers from raw counts alone once urgency scores/tiers exist; use the interpretation summary.
