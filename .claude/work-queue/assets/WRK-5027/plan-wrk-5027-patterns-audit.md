# WRK-5027 Plan: Patterns Audit — 25% Repetition Rule Conversions

## Overview

Audit skill prose and rules for recurring LLM-reasoning operations that should be scripts,
then implement the top-5 conversions. Output: `docs/patterns-audit-25pct-rule.md` + 5 scripts.

## Phase 1: Run Existing Scanner + Build Audit Report

**Step 1.1** — Run `scripts/skills/identify-script-candidates.sh` to refresh the candidates list.

**Step 1.2** — Write `scripts/skills/audit-prose-operations.py`: a new scanner that focuses on
*specific inline operations* within skills (vs whole-skill classification). Targets verb phrases
like "count the", "read each", "for each file", "check if", "parse the", "tally" across
`.claude/skills/**/*.md`, `.claude/rules/*.md`, `.claude/docs/*.md`.

**Step 1.3** — Write `docs/patterns-audit-25pct-rule.md` with flagged items table:

| # | File | Operation | Frequency estimate | Classification | Script exists? |
|---|------|-----------|-------------------|----------------|----------------|
| 1 | session-start Step 3 | Quota threshold check | Every session | new-utility | No |
| 2 | session-start Step 2 | Snapshot age check | Every session | new-one-liner | No |
| 3 | claude-reflect | Pattern score calculation | Daily | new-utility | Partial |
| 4 | session-start Step 4 | Top items per category filter | Every session | existing-script | whats-next.sh |
| 5 | workflow-gatepass Stage 15 | Category inference | Per WRK | existing-script | infer-category.py |

## Phase 2: Top-5 Conversions

### Conversion 1: `scripts/session/quota-status.sh` (new utility)

**Interface contract**:
- Input: `[--json-path <path>]` (default: `config/ai-tools/agent-quota-latest.json`)
- Stdout: one formatted line per provider when threshold triggers; nothing when <70%
- Stderr: only on file-read errors
- Exit code: always 0 (informational, never blocks session start)
- Stale data: if file mtime > 4h, prints `WARN: quota data may be stale (>4h old)` then continues

**Threshold logic**: `utilization = 100 - pct_remaining`
- >=90%: `WARN [<provider>]: <util>% used — route tasks to alternative provider`
- 70-89%: `NOTE [<provider>]: <util>% used — approaching limit`
- <70%: no output
- `pct_remaining: null` (source: unavailable): prints `NOTE [<provider>]: quota data unavailable`

**Tests** (TDD, bash): `scripts/session/tests/test_quota_status.sh`
- `test_below_70_silent` — utilization 40% → no warn line, exit 0
- `test_70_89_note` — utilization 75% → contains "approaching limit", exit 0
- `test_90_plus_warn` — utilization 92% → contains "WARN", exit 0
- `test_null_pct_remaining` — source=unavailable → contains "unavailable", exit 0
- `test_stale_cache` — mtime > 4h → contains "stale", exit 0
- `test_missing_file` — no JSON → prints nothing, exit 0

**Session-start update**: Step 3 prose → `bash scripts/session/quota-status.sh`

### Conversion 2: `scripts/session/snapshot-age.sh` (new one-liner)

**Interface contract**:
- Input: `[--snapshot-path <path>]` (default: `.claude/state/session-snapshot.md`)
- Stdout: age description e.g. `snapshot: 2h old (fresh)` or `snapshot: 72h old (stale)`
- Exit code: 0 = fresh (<48h), 1 = stale (>=48h) or missing/malformed
- Timestamp format: extracts ISO8601 from `# Session Snapshot — <ISO_TS>` on line 1

**Tests** (bash): `scripts/session/tests/test_snapshot_age.sh`
- `test_fresh_snapshot` — timestamp within 24h → stdout contains "fresh", exit 0
- `test_stale_snapshot` — timestamp > 48h → stdout contains "stale", exit 1
- `test_missing_file` — no snapshot → stdout contains "missing", exit 1
- `test_malformed_timestamp` — no ISO date in line 1 → exit 1

**Session-start update**: Step 2 staleness check → `bash scripts/session/snapshot-age.sh`

### Conversion 3: `scripts/skills/audit-prose-operations.py` (new utility)

**Interface contract**:
- Input: `[--skills-dir <dir>] [--rules-dir <dir>] [--docs-dir <dir>] [--output <path>]`
- Stdout: progress summary; Markdown report written to `--output` (default: `docs/patterns-audit-25pct-rule.md`)
- Exit code: 0 always (informational)
- Structured output: TSV (tab-separated) plus human-readable Markdown table

**Fixed pattern taxonomy** (6 categories):
1. `count_ops` — "count the", "tally", "how many", "number of"
2. `iteration_ops` — "for each (file|repo|item|step)", "iterate over", "loop through"
3. `parse_ops` — "parse the (yaml|json|md)", "read and extract", "extract the field"
4. `generate_ops` — "generate the yaml", "build the list", "construct the json by hand"
5. `threshold_ops` — "check if.*greater", "compare.*percent", "above.*threshold"
6. `filter_ops` — "filter by", "select only", "narrow to"

**Exclusions**: text inside ` ```bash ... ``` ` or ` ```python ... ``` ` fences is skipped.

**Output schema per row**: `file`, `line`, `category`, `matched_text`, `classification`
where classification ∈ {`existing-script`, `new-one-liner`, `new-utility`, `llm-only`}.

**Tests** (bash using subprocess): `scripts/skills/tests/test_audit_prose_operations.sh`
- `test_flags_count_inline` — "count the files" → row with category=count_ops
- `test_skips_bash_block` — count inside ```bash → not flagged
- `test_flags_iteration` — "for each repo" → category=iteration_ops
- `test_generates_markdown_table` — output has required columns
- `test_classifies_existing_script` — known path → classification=existing-script

### Conversion 4: `scripts/session/session-briefing.sh` (new utility)

**Interface contract**:
- Input: `[--category <name>]` (passed through to whats-next.sh)
- Stdout: formatted briefing sections; always exits 0 (non-blocking by design)
- Error propagation: each subsection runs in isolation; failure of one prints section header
  with `(unavailable)` and continues — session start is never blocked
- Exit code: always 0

**Execution order** (each section independent):
1. Print `## Snapshot` — calls `snapshot-age.sh`; if fresh, prints snapshot summary
2. Print `## Quota` — calls `quota-status.sh`; prints provider lines
3. Print `## Top Unblocked` — calls `whats-next.sh [--category <name>]`

**Tests** (bash): `scripts/session/tests/test_session_briefing.sh`
- `test_includes_quota_section` — stdout contains "## Quota"
- `test_includes_top_items` — stdout contains "## Top Unblocked"
- `test_nonzero_subsection_continues` — if quota-status.sh missing → still exits 0

**Session-start update**: Steps 2, 3, 4 → single call to `bash scripts/session/session-briefing.sh`

### Conversion 5: `scripts/session/repo-map-context.sh` (new utility)

**Interface contract**:
- Input: `<WRK-NNN>` positional arg; reads `.claude/work-queue/working/WRK-NNN.md`
- Stdout: formatted repo entries for each matched target_repo (name, purpose, test_command)
- Exit code: 0 always (non-blocking); no output when target_repos absent
- Parsing: `target_repos` is a YAML list field in WRK frontmatter; each entry is a bare repo name
  matching the `name:` key in `config/onboarding/repo-map.yaml`
- Unknown repos: prints `NOTE: <name> not found in repo-map.yaml` (non-blocking)

**Tests** (bash): `scripts/session/tests/test_repo_map_context.sh`
- `test_known_repo` — WRK with `target_repos: [digitalmodel]` → output contains "digitalmodel"
- `test_unknown_repo` — target_repos with non-existent name → output contains "not found"
- `test_no_target_repos` — WRK without target_repos → no output, exit 0
- `test_missing_wrk` — nonexistent WRK file → no output, exit 0

**Session-start update**: Step 5b inline LLM read → `bash scripts/session/repo-map-context.sh <WRK-ID>`

## Phase 3: Tests and Cross-Review

**TDD protocol**:
- Write all test files first (before any implementation)
- Run tests → red → implement → green
- No exceptions per `.claude/rules/testing.md`

**Coverage target**: ≥80% for new Python scripts.

**Cross-review**: Gemini review of `docs/patterns-audit-25pct-rule.md` before closing (per ACs).

## Acceptance Criteria Mapping

| AC | Phase | Deliverable |
|----|-------|-------------|
| Audit report with flagged items table | 1.3 | `docs/patterns-audit-25pct-rule.md` |
| Each item classified | 1.2 | audit-prose-operations.py output |
| Top 5 conversions with tests | 2.1-2.5 | 4 new scripts + 1 prose update |
| Prose updated to call scripts | 2.1, 2.2, 2.4, 2.5 | session-start, comprehensive-learning |
| Gemini cross-review on audit report | 3 | cross-review evidence |

## File Plan

```
scripts/session/quota-status.sh          (new)
scripts/session/snapshot-age.sh          (new)
scripts/session/session-briefing.sh      (new)
scripts/session/tests/test_quota_status.py    (new)
scripts/session/tests/test_snapshot_age.sh    (new)
scripts/session/tests/test_session_briefing.sh (new)
scripts/skills/audit-prose-operations.py (new)
scripts/skills/audit-prose-operations.sh (new wrapper)
scripts/skills/tests/test_audit_prose_operations.py (new)
docs/patterns-audit-25pct-rule.md        (new)
.claude/skills/workspace-hub/session-start/SKILL.md (update Steps 2,3,4)
```
