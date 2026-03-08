# WRK-1020 Plan: portfolio-signals.yaml cron
date: 2026-03-07
wrk_id: WRK-1020
route: B
complexity: medium
orchestrator: claude
synthesis: claude+codex (gemini timeout)

## Objective

Build `scripts/cron/update-portfolio-signals.sh` (thin bash wrapper) +
`scripts/cron/update_portfolio_signals.py` (Python entrypoint) that writes
`.claude/state/portfolio-signals.yaml` nightly with two signal layers:

- **L2**: per-provider WRK activity counts from last-30-day archive files
- **L3**: gemini capability research query (≤5 high-confidence signals, official sources)

Integrate into `comprehensive-learning-nightly.sh` — insert after rsync block (~lines 27/32),
before `# Step 3b: AI agent readiness` (~line 35). Rename existing mislabelled
`# Step 3:` → `# Step 3c:` to resolve label collision. Best-effort (`|| true`).

## What Exists (from WRK-1019)

- `scripts/skills/repo-portfolio-steering/compute-balance.py` — reads portfolio-signals.yaml
- `.claude/state/portfolio-signals.yaml` schema — defined and seeded
- Archive files in `.claude/work-queue/archive/YYYY-MM/*.md` with `orchestrator:` + `category:`

## Decisions (Stage 5 synthesis 2026-03-07)

| Question | Decision |
|---|---|
| L3 throttle | Daily — deduplicate by date field |
| portfolio-signals.yaml gitignored? | Yes — gitignored state file; cron overwrites nightly |
| Lookback window | 30 days (stable signal) |
| L3 prompt scope | **Dual-mode**: `engineering >= harness` → engineering computation (subsea, structural, drilling, reservoir); else → general AI capability news |
| L3 fail strategy | **carry forward** — preserve existing `capability_signals` on CLI missing, subprocess failure, timeout, parse failure, or zero valid results |
| Integration placement | **Step 3a** — before AI readiness checks; best-effort `|| true` |
| Architecture | **Thin bash wrapper** (`update-portfolio-signals.sh`) + **Python entrypoint** (`update_portfolio_signals.py`) |
| L3 source filter | Official/vendor sources only (Anthropic, OpenAI, Google) — explicitly testable |
| l3_meta | Written alongside l2_meta — records query attempt, result, signals_added, signals_pruned |
| Atomic write | Write to temp file then rename — prevents partial state file |
| uv enforcement | `uv run --no-project python` verified in **both** wrapper script and nightly script |

## Implementation Plan

### Step 1a — `scripts/cron/update-portfolio-signals.sh` (bash wrapper)

```bash
#!/usr/bin/env bash
# update-portfolio-signals.sh
# Thin wrapper — delegates to uv run --no-project python update_portfolio_signals.py
# Usage: bash update-portfolio-signals.sh [--dry-run] [--lookback N]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project python "${SCRIPT_DIR}/update_portfolio_signals.py" "$@"
```

### Step 1b — `scripts/cron/update_portfolio_signals.py` (Python entrypoint)

**L2 block** (provider activity):
```python
# Recursive glob: archive/**/*.md
# Date window: read completed_at: frontmatter field (not directory path)
# Missing orchestrator: → skip file (do not count; increment files_skipped)
# Unknown orchestrator (not claude/codex/gemini): → skip + increment files_skipped
# Malformed frontmatter: → skip file gracefully, do not crash
# Malformed completed_at: → skip file, increment files_skipped
# Missing category: → treat as "other"
# Category mapping: harness→harness, engineering→engineering, data→data
#   platform/maintenance/business/personal/uncategorised → other
# Output: provider_activity.{claude,codex,gemini}.{harness,engineering,data,other}
# l2_meta: {files_scanned, files_with_orchestrator, files_skipped_no_orchestrator,
#            files_skipped_malformed}
```

**L3 block** (capability research — structured-output prompt):
```python
# Dual-mode: engineering_count >= harness_count → engineering prompt
# Default/tie: general AI capability news
# Structured-output YAML prompt (gemini respond ONLY in YAML):
PROMPT_ENG="List up to 5 AI capabilities announced in last 7 days relevant to
engineering computation (subsea, structural, drilling, reservoir). Respond ONLY in
YAML list:
- date: YYYY-MM-DD
  provider: claude|codex|gemini
  capability: brief name
  engineering_domains: [domain1]
  impact: low|medium|high
  source: https://...
Output ONLY the YAML list, no prose."

# Parse with yaml.safe_load(); strip markdown fences before parse
# Carry-forward existing capability_signals when:
#   gemini CLI missing, subprocess failure, timeout, parse failure,
#   or zero valid results after source filter
# Official/vendor source filter: retain only entries whose source URL
#   matches anthropic.com, openai.com, deepmind.google, blog.google, cloud.google.com
# Dedup by hash(provider+capability+date)
# Prune entries older than 30 days on carry-forward
# Append ≤5 new entries; max 20 total retained
# l3_meta: {query_attempted, query_mode, parse_success, signals_added,
#            signals_pruned, carry_forward}
```

**Output**:
- Atomic write: write to `.claude/state/portfolio-signals.yaml.tmp`, then rename
- Create `.claude/state/` directory if missing
- `--dry-run`: print to stdout, no file written
- `--lookback N`: override 30-day default; reject invalid values (zero, negative, non-integer)
- Schema compatible with WRK-1019 (no changes to existing keys)

### Step 2 — Integrate into `comprehensive-learning-nightly.sh`

Add after Step 2 (rsync), before Step 3b (AI agent readiness):

```bash
# Step 3a: portfolio signals update (best-effort — WRK-1020)
echo "--- Portfolio signals update $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/update-portfolio-signals.sh || \
  echo "WARNING: portfolio signals update failed — see above"

# Step 3b: AI agent readiness
```

Also rename existing mislabelled `# Step 3:` → `# Step 3c:` for monotonic labels.

### Step 3 — TDD Tests

File: `tests/skills/test_update_portfolio_signals.py`

| Test | AC | Notes |
|---|---|---|
| `test_script_exists_and_uses_uv_no_project_python` | AC-1, AC-5 | shebang + wrapper invokes `uv run --no-project python` |
| `test_python_entrypoint_exists` | AC-1 | Python module separate from shell wrapper |
| `test_provider_activity_counts_from_completed_at` | AC-2 | counts only in-window items using `completed_at` |
| `test_completed_at_window_boundary_inclusive` | AC-2 | exact boundary behavior for day N |
| `test_missing_orchestrator_field_skipped` | AC-2 | skipped, not counted |
| `test_unknown_orchestrator_skipped_and_logged` | AC-2 | unknown provider not counted, meta increments |
| `test_missing_category_field_to_other` | AC-2 | missing category → other bucket |
| `test_other_bucket_categories` | AC-2 | platform/maintenance/business/personal/uncategorised → other |
| `test_malformed_frontmatter_skipped_with_meta` | AC-2 | unreadable file does not crash run |
| `test_bad_completed_at_skipped_with_meta` | AC-2 | malformed timestamp not counted |
| `test_recursive_archive_glob` | AC-2 | finds files in archive/ and archive/YYYY-MM/ |
| `test_l2_meta_provenance_written` | AC-2 | all required meta counters present |
| `test_nonzero_skip_meta_prevents_silent_all_zero` | AC-2 | zero counts accompanied by provenance |
| `test_dry_run_no_write` | AC-4 | stdout only, no state file written |
| `test_atomic_write_replaces_file` | AC-1 | tmp write then rename |
| `test_state_directory_created_if_missing` | AC-1 | missing .claude/state/ handled |
| `test_lookback_flag_changes_counts` | AC-4b | `--lookback 7` differs from `--lookback 30` |
| `test_lookback_flag_rejects_invalid_values` | AC-4b | zero, negative, non-integer rejected |
| `test_gemini_query_skipped_when_cli_missing` | AC-3 | graceful fallback; L2 still written |
| `test_carry_forward_on_cli_failure` | AC-3 | non-zero subprocess preserves prior signals |
| `test_carry_forward_on_yaml_parse_failure` | AC-3 | malformed YAML preserves prior signals |
| `test_carry_forward_on_all_invalid_items` | AC-3 | valid parse but no usable signals preserves prior |
| `test_structured_prompt_yaml_parsed_and_validated` | AC-3 | well-formed YAML list accepted |
| `test_non_official_sources_rejected` | AC-3 | unofficial sources filtered out |
| `test_signal_retention_prunes_older_than_30_days` | AC-3 | old entries removed on carry-forward |
| `test_idempotent_no_duplicate_signals_same_day` | AC-3 | repeat run does not duplicate |
| `test_signal_cap_limits_to_five_new_and_twenty_total` | AC-3 | both caps enforced |
| `test_mode_selection_engineering_vs_general` | AC-3 | engineering when engineering >= harness |
| `test_mode_selection_tie_goes_engineering` | AC-3 | tie (equal counts) → engineering prompt |
| `test_l3_meta_written` | AC-3 | l3_meta block present in output |
| `test_output_schema_valid_for_compute_balance_consumer` | AC-1, AC-3 | consumer-compatible keys |
| `test_integrated_in_nightly_with_best_effort_call` | AC-5 | call inserted before readiness step |
| `test_nightly_step_labels_are_monotonic` | AC-5 | 3a, 3b, 3c sequence verified |
| `test_gitignore_covers_signals` | AC-6 | `git check-ignore -v` exits 0 |

## Acceptance Criteria

- [ ] AC-1: `update-portfolio-signals.sh` (wrapper) + `update_portfolio_signals.py` (entrypoint)
  generate valid portfolio-signals.yaml; wrapper uses `uv run --no-project python`;
  atomic write (tmp → rename); creates `.claude/state/` if missing
- [ ] AC-2: Provider activity counts match last-30-day archive
  - Recursive glob (`archive/**/*.md`); date from `completed_at:` field
  - Missing/unknown `orchestrator:` → skip; missing `category:` → `other`
  - Malformed frontmatter or bad `completed_at:` → skip gracefully
  - `l2_meta` block: files_scanned, files_with_orchestrator, files_skipped_no_orchestrator,
    files_skipped_malformed
  - Does NOT produce all-zero tables silently when fields are absent
- [ ] AC-3: Gemini capability research
  - Structured-output YAML prompt; `yaml.safe_load()`; strip markdown fences before parse
  - Carry-forward on: CLI missing, failure, timeout, parse failure, zero valid results
  - Official/vendor sources only (anthropic.com, openai.com, deepmind.google, blog.google,
    cloud.google.com)
  - Prune entries >30 days; dedup by hash(provider+capability+date); max 20 total; ≤5 new/run
  - Dual-mode: `engineering >= harness` → engineering prompt; else → general AI news
  - `l3_meta` block: query_attempted, query_mode, parse_success, signals_added, signals_pruned,
    carry_forward
- [ ] AC-4: `--dry-run` prints to stdout, no file written
- [ ] AC-4b: `--lookback N` overrides 30-day default; rejects zero/negative/non-integer
- [ ] AC-5: Integrated as Step 3a in nightly; `uv run --no-project python` in wrapper;
  step labels monotonic (3a → 3b → 3c)
- [ ] AC-6: `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0

## Synthesis Notes

- Claude draft: 16 tests, inline Python in bash, `>=` tie-break, basic carry-forward
- Codex draft: 33 tests, wrapper+entrypoint architecture, explicit source filter, l3_meta,
  atomic write, 5 additional L2 edge cases, expanded carry-forward triggers
- Gemini: timed out (plan draft too large for 300s pipe — see WRK for follow-up)
- All Codex additions accepted except tie-break rule (kept Claude's `>=` → engineering)

## Workstation

ace-linux-1 (plan + execution)
