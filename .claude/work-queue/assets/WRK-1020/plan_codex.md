OpenAI Codex v0.111.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019ccb84-abdf-7232-8043-17bd63339eab
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
# WRK-1020 Plan: portfolio-signals.yaml cron
date: 2026-03-07
wrk_id: WRK-1020
route: B
complexity: medium
orchestrator: claude

## Objective

Build `scripts/cron/update-portfolio-signals.sh` that writes
`.claude/state/portfolio-signals.yaml` nightly with two signal layers:

- **L2**: per-provider WRK activity counts from last-30-day archive files
- **L3**: gemini capability research query (≤5 high-confidence signals, official sources)

Integrate into `comprehensive-learning-nightly.sh` — insert after rsync block (~lines 27/32), before `# Step 3b: AI agent readiness` (~line 35). Rename existing mislabelled `# Step 3:` → `# Step 3c:` to resolve label collision. Best-effort (`|| true`).

## What Exists (from WRK-1019)

- `scripts/skills/repo-portfolio-steering/compute-balance.py` — reads portfolio-signals.yaml
- `.claude/state/portfolio-signals.yaml` schema — defined and seeded
- Archive files in `.claude/work-queue/archive/YYYY-MM/*.md` with `orchestrator:` + `category:`

## Decisions (Stage 5 user review 2026-03-07)

| Question | Decision |
|---|---|
| L3 throttle | Daily — deduplicate by date field |
| portfolio-signals.yaml gitignored? | Yes — gitignored state file; cron overwrites nightly |
| Lookback window | 30 days (stable signal) |
| L3 prompt scope | **Dual-mode**: harness/general categories → general AI capability news; engineering category → engineering computation focus (subsea, structural, drilling, reservoir) |
| L3 fail strategy | **(b) carry forward** — preserve existing `capability_signals` from current file when gemini query fails |
| Integration placement | **Step 3a** — before AI readiness checks; best-effort `\|\| true` |

## Implementation Plan

### Step 1 — `scripts/cron/update-portfolio-signals.sh`

```bash
#!/usr/bin/env bash
# update-portfolio-signals.sh
# Writes .claude/state/portfolio-signals.yaml with L2 + L3 signals.
# Usage: bash update-portfolio-signals.sh [--dry-run] [--lookback N]
```

**L2 block** (provider activity):
```python
# Recursive glob: archive/**/*.md
# Date window: read completed_at: frontmatter field (not directory path)
# Missing orchestrator: → skip file (do not count toward any provider)
# Missing category: → treat as "other"
# Category mapping: harness→harness, engineering→engineering, data→data
#   platform/maintenance/business/personal/uncategorised → other
# Output: provider_activity.{claude,codex,gemini}.{harness,engineering,data,other}
# Add l2_meta: {files_scanned: N, files_with_orchestrator: N, files_skipped_no_orchestrator: N}
```

**L3 block** (capability research — structured-output prompt):
```bash
# Dual-mode prompt based on harness_pct from L2:
#   If engineering dominates (engineering_count >= harness_count): engineering-focused prompt
#   Default / tie: general AI capability news
# Structured-output prompt (ask gemini to respond ONLY in YAML):
PROMPT_ENG="List up to 5 AI capabilities announced in last 7 days relevant to
engineering computation (subsea, structural, drilling, reservoir). Respond ONLY in
YAML list format:
- date: YYYY-MM-DD
  provider: claude|codex|gemini
  capability: brief name
  engineering_domains: [domain1]
  impact: low|medium|high
  source: https://...
Output ONLY the YAML list, no prose."
# Parse gemini output with yaml.safe_load(); on parse failure → carry-forward
# Dedup by hash(provider+capability+date); prune entries older than 30 days
# Append up to 5 new entries; max 20 total retained
```

**Output**:
- Overwrites `.claude/state/portfolio-signals.yaml` (or prints to stdout with `--dry-run`)
- Schema compatible with WRK-1019 (no changes to existing keys)

### Step 2 — Integrate into `comprehensive-learning-nightly.sh`

Add after Step 2 (rsync), before Step 3b (AI agent readiness):

```bash
# Step 3a: portfolio signals update (best-effort — WRK-1020)
echo "--- Portfolio signals update $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/update-portfolio-signals.sh || \
  echo "WARNING: portfolio signals update failed — see above"
```

### Step 3 — TDD Tests

File: `tests/skills/test_update_portfolio_signals.py`

| Test | AC | Notes |
|---|---|---|
| `test_script_exists` | AC-1 | path + shebang check |
| `test_provider_activity_counts` | AC-2 | fixture archive files; 30-day window; uses `completed_at:` |
| `test_other_bucket_categories` | AC-2 | platform/maintenance/business/personal → `other` bucket |
| `test_dry_run_no_write` | AC-4 | stdout only, no file written |
| `test_gemini_query_skipped_no_gemini` | AC-3 | graceful fallback; L2 still written |
| `test_carry_forward_on_failure` | AC-3 | existing signals preserved when gemini fails |
| `test_output_schema_valid` | AC-1+AC-3 | required keys present |
| `test_integrated_in_nightly` | AC-5 | grep for script call in nightly sh |
| `test_gitignore_covers_signals` | AC-6 | .gitignore covers .claude/state/ |
| `test_missing_orchestrator_field_skipped` | AC-2 | file without orchestrator: not counted |
| `test_missing_category_field_to_other` | AC-2 | file without category: → other bucket |
| `test_l2_meta_provenance_written` | AC-2 | l2_meta block present in output |
| `test_structured_prompt_yaml_parsed` | AC-3 | mock gemini YAML response parsed correctly |
| `test_lookback_flag` | AC-4b | --lookback 7 vs --lookback 30 differ |
| `test_idempotent_no_duplicate_signals` | P2 | run twice same day → same signal count |
| `test_archive_recursive_glob` | P2 | finds files in both archive/ and archive/2026-03/ |

## Acceptance Criteria

- [ ] AC-1: `update-portfolio-signals.sh` generates valid portfolio-signals.yaml from archive
- [ ] AC-2: Provider activity counts match last-30-day archive
  - Recursive glob (`archive/**/*.md`); date from `completed_at:` field
  - Missing `orchestrator:` → skip (not counted); missing `category:` → `other`
  - `l2_meta` provenance block written: files_scanned, files_with_orchestrator, files_skipped
  - Script does NOT produce all-zero tables silently when fields are absent
- [ ] AC-3: Gemini capability research: structured-output YAML prompt; ≤5 new signals per run
  - Carry-forward existing signals on gemini failure; prune entries >30 days old
  - Dedup by hash(provider+capability+date); max 20 retained total
  - Dual-mode: engineering-focused when engineering≥harness; general AI news otherwise
- [ ] AC-4: `--dry-run` prints to stdout, no file written
- [ ] AC-4b: `--lookback N` overrides default 30-day window; `--lookback 7` produces different count than `--lookback 30` when archive coverage differs
- [ ] AC-5: Integrated as Step 3a in nightly; `uv run --no-project python`; step labels fixed (`# Step 3:` → `# Step 3c:`)
- [ ] AC-6: `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0

## Workstation

ace-linux-1 (plan + execution)
mcp startup: no servers
codex
# WRK-1020 Plan: portfolio-signals.yaml cron
date: 2026-03-07
wrk_id: WRK-1020
route: B
complexity: medium
orchestrator: claude

## Objective

Build `scripts/cron/update-portfolio-signals.sh` that refreshes
`.claude/state/portfolio-signals.yaml` nightly with two signal layers:

- **L2**: per-provider WRK activity counts from archive items completed in the last N days
- **L3**: gemini capability research signals, capped to high-confidence items from official sources

Integrate it into `scripts/cron/comprehensive-learning-nightly.sh` after the rsync block and before AI readiness checks. The nightly integration must be best-effort (`|| true`) and must not block the rest of the cron pipeline.

## What Exists (from WRK-1019)

- `scripts/skills/repo-portfolio-steering/compute-balance.py` reads `.claude/state/portfolio-signals.yaml`
- `.claude/state/portfolio-signals.yaml` already exists and has a seeded schema
- Archive items live under `.claude/work-queue/archive/YYYY-MM/*.md` and include `orchestrator:` and `category:` frontmatter in normal cases

## Decisions (Stage 5 user review 2026-03-07)

| Question | Decision |
|---|---|
| L3 throttle | Daily; avoid duplicate same-day additions |
| portfolio-signals.yaml gitignored? | Yes; nightly state file, overwritten |
| Lookback window | 30 days by default |
| L3 prompt scope | Dual-mode: general AI capability news for harness/general-heavy portfolios; engineering-computation focus for engineering-heavy portfolios |
| L3 fail strategy | Carry forward existing `capability_signals` when gemini query fails or output is unusable |
| Integration placement | Step 3a, before AI readiness; best-effort `|| true` |

## Implementation Plan

### Step 1 — `scripts/cron/update-portfolio-signals.sh`

Keep the shell script thin. It should only parse CLI flags, resolve repo-relative paths, and invoke Python via:

```bash
uv run --no-project python scripts/cron/update_portfolio_signals.py "$@"
```

That is simpler to test and avoids embedding non-trivial Python in bash.

**CLI contract**:
```bash
#!/usr/bin/env bash
# update-portfolio-signals.sh
# Usage:
#   bash scripts/cron/update-portfolio-signals.sh [--dry-run] [--lookback N]
# Behavior:
#   - exit 0 on success
#   - non-zero on generation failure
#   - stdout emits YAML only for --dry-run
```

**Python implementation target**:
- Add `scripts/cron/update_portfolio_signals.py`
- Read existing `.claude/state/portfolio-signals.yaml` if present
- Scan archive files recursively under `.claude/work-queue/archive/**/*.md`
- Parse frontmatter defensively:
  - Missing or malformed frontmatter: count in meta as unreadable/skipped
  - Missing `orchestrator`: skip from provider counts
  - Missing `category`: bucket as `other`
  - Missing or malformed `completed_at`: skip from lookback counts and record in meta
- Use `completed_at` date, not folder name, for the lookback window
- Normalize orchestrator/provider values to lowercase and only count known providers: `claude`, `codex`, `gemini`
  - Unknown provider: skip and record separately in meta
- Normalize category mapping:
  - `harness` → `harness`
  - `engineering` → `engineering`
  - `data` → `data`
  - anything else or missing → `other`
- Compute `provider_activity.{provider}.{bucket}` with zero-filled structure for all providers and all buckets
- Write `l2_meta` with enough provenance to debug silent-zero outcomes:
  - `generated_at`
  - `lookback_days`
  - `files_scanned`
  - `files_in_window`
  - `files_with_orchestrator`
  - `files_skipped_no_orchestrator`
  - `files_skipped_bad_completed_at`
  - `files_skipped_unknown_provider`
  - `files_skipped_unreadable`

**L3 block**:
- Determine mode from L2 totals:
  - engineering-focused if total engineering activity `>` total harness activity
  - general mode otherwise
- Tie should stay general. That is safer and matches “default / tie” intent.
- Query gemini only if a CLI is available and executable
- Require official/vendor sources only for retained signals
- Ask for strict YAML output, but do not trust it:
  - parse with `yaml.safe_load`
  - require list of dicts
  - validate each item fields and types
  - reject malformed dates, missing provider, bad URL, unknown impact, or non-official source domains
- Dedup against retained history using a stable key:
  - normalized `(date, provider, capability)`
- Retention policy:
  - prune entries older than 30 days from today
  - add up to 5 validated new entries from current run
  - cap retained list at 20, newest first
- Failure behavior:
  - if gemini unavailable, command fails, times out, returns malformed YAML, or yields zero valid entries, carry forward existing valid `capability_signals`
  - still write L2 output
- Record `l3_meta`:
  - `mode`
  - `query_attempted`
  - `query_succeeded`
  - `signals_added`
  - `signals_retained`
  - `failure_reason` when applicable

**Output**:
- Preserve existing schema compatibility for consumers from WRK-1019
- Overwrite `.claude/state/portfolio-signals.yaml` atomically:
  - write temp file in same directory
  - rename into place
- `--dry-run` prints final YAML to stdout and performs no write
- Validate parent directory exists; create `.claude/state/` if needed

### Step 2 — Integrate into `comprehensive-learning-nightly.sh`

Insert after the rsync block and before AI readiness. Keep it explicitly best-effort.

```bash
# Step 3a: portfolio signals update (best-effort - WRK-1020)
echo "--- Portfolio signals update $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/update-portfolio-signals.sh || \
  echo "WARNING: portfolio signals update failed - see above"

# Step 3b: AI agent readiness
```

Also fix the existing label collision so subsequent comments are monotonic:
- rename current mislabelled `# Step 3:` to `# Step 3c:`

Integration checks:
- script path must be repo-relative and consistent with existing cron conventions
- failure warning must not mask the rest of the nightly run
- no bare `python` or `python3`; only `uv run --no-project python`

### Step 3 — TDD Tests

File: `tests/skills/test_update_portfolio_signals.py`

| Test | AC | Notes |
|---|---|---|
| `test_script_exists_and_uses_uv_no_project_python` | AC-1, AC-5 | shebang + wrapper invokes `uv run --no-project python` |
| `test_python_entrypoint_exists` | AC-1 | implementation separated from shell wrapper |
| `test_provider_activity_counts_from_completed_at` | AC-2 | counts only in-window items using `completed_at`, not directory name |
| `test_completed_at_window_boundary_inclusive` | AC-2 | define exact boundary behavior for day N |
| `test_missing_orchestrator_field_skipped` | AC-2 | skipped, not counted |
| `test_unknown_orchestrator_skipped_and_logged` | AC-2 | unknown provider not counted, meta increments |
| `test_missing_category_field_to_other` | AC-2 | missing category goes to `other` |
| `test_other_bucket_categories` | AC-2 | platform/maintenance/business/personal/uncategorised map to `other` |
| `test_malformed_frontmatter_skipped_with_meta` | AC-2 | unreadable archive file does not crash run |
| `test_bad_completed_at_skipped_with_meta` | AC-2 | malformed timestamp not counted |
| `test_recursive_archive_glob` | AC-2 | nested archive paths found |
| `test_l2_meta_provenance_written` | AC-2 | required meta counters present |
| `test_nonzero_skip_meta_prevents_silent_all_zero_debug_gap` | AC-2 | zero counts accompanied by provenance explaining why |
| `test_dry_run_no_write` | AC-4 | stdout only, no state file write |
| `test_atomic_write_replaces_file` | AC-1 | temp-write then rename behavior |
| `test_lookback_flag_changes_counts` | AC-4b | `--lookback 7` and `--lookback 30` differ when fixtures differ |
| `test_lookback_flag_rejects_invalid_values` | AC-4b | zero, negative, non-integer rejected |
| `test_gemini_query_skipped_when_cli_missing` | AC-3 | graceful fallback; L2 still written |
| `test_carry_forward_on_cli_failure` | AC-3 | non-zero subprocess preserves prior valid signals |
| `test_carry_forward_on_yaml_parse_failure` | AC-3 | malformed YAML preserves prior signals |
| `test_carry_forward_on_all_invalid_items` | AC-3 | valid parse but no usable signals still preserves prior list |
| `test_structured_prompt_yaml_parsed_and_validated` | AC-3 | accepts well-formed YAML list |
| `test_non_official_sources_rejected` | AC-3 | retain only official/vendor sources |
| `test_signal_retention_prunes_older_than_30_days` | AC-3 | old entries removed |
| `test_idempotent_no_duplicate_signals_same_day` | AC-3 | repeat run does not duplicate retained items |
| `test_signal_cap_limits_to_five_new_and_twenty_total` | AC-3 | both caps enforced |
| `test_mode_selection_engineering_vs_general` | AC-3 | engineering only when engineering total strictly exceeds harness |
| `test_mode_selection_tie_defaults_to_general` | AC-3 | tie behavior locked down |
| `test_output_schema_valid_for_compute_balance_consumer` | AC-1, AC-3 | consumer-compatible keys and structure |
| `test_state_directory_created_if_missing` | AC-1 | missing `.claude/state/` handled |
| `test_integrated_in_nightly_with_best_effort_call` | AC-5 | call inserted before readiness step with warning fallback |
| `test_nightly_step_labels_are_monotonic` | AC-5 | verifies `3a`, `3b`, `3c` sequence |
| `test_gitignore_covers_signals` | AC-6 | `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0 |

## Acceptance Criteria

- [ ] AC-1: `scripts/cron/update-portfolio-signals.sh` generates valid `.claude/state/portfolio-signals.yaml` from archive data using `uv run --no-project python`
- [ ] AC-2: Provider activity counts match the last-30-day archive window
  - Recursive glob under `.claude/work-queue/archive/**/*.md`
  - Lookback uses `completed_at:` field, not directory names
  - Missing `orchestrator:` skips the file
  - Missing `category:` maps to `other`
  - Unknown providers are skipped and counted in meta
  - Malformed frontmatter or bad `completed_at:` does not crash the run
  - `l2_meta` provenance is written with enough detail to explain zero-count outputs
- [ ] AC-3: Gemini capability research adds at most 5 validated new signals per run
  - Carry forward existing valid `capability_signals` on missing CLI, subprocess failure, timeout, parse failure, or zero valid results
  - Prune retained signals older than 30 days
  - Dedup by normalized `(date, provider, capability)`
  - Retain at most 20 total signals
  - Dual-mode prompt selection: engineering mode only when engineering activity strictly exceeds harness; tie/default is general
  - Retained signals must come from official/vendor sources only
  - `l3_meta` records query attempt/result details
- [ ] AC-4: `--dry-run` prints YAML to stdout and does not write the state file
- [ ] AC-4b: `--lookback N` overrides the default 30-day window and rejects invalid values
- [ ] AC-5: Nightly cron integrates the script as Step 3a before AI readiness, uses best-effort failure handling, fixes the step-label collision, and uses no bare `python` calls
- [ ] AC-6: `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0

## Workstation

ace-linux-1 (plan + execution)

## Codex Notes

- The draft put substantial logic inside a shell-script plan. That is harder to test and easier to break on quoting, YAML escaping, and subprocess handling. A thin shell wrapper plus Python entrypoint is the more robust implementation.
- The draft’s tie rule was inconsistent: objective text said engineering-focused when `engineering_count >= harness_count`, but prompt notes also said “default / tie: general AI capability news.” The plan should pick one. I locked tie to general.
- The draft did not define behavior for malformed `completed_at`, malformed frontmatter, unknown orchestrators, invalid `--lookback`, missing state directory, atomic writes, or all-invalid gemini responses. Those are practical cron failure modes and should be explicit.
- “Do not produce all-zero tables silently” needs measurable behavior. I translated that into required provenance counters in `l2_meta`.
- L3 source quality was underspecified. “High-confidence” is not testable unless retention filters define acceptable sources. I made that “official/vendor sources only.”
- The nightly integration risk is low, but only if the step is best-effort and the warning path does not alter exit semantics for the rest of the cron script.
- The plan must explicitly verify `uv run --no-project python` anywhere Python is invoked. The original tests only checked this in the nightly script, not in the new wrapper itself.
tokens used
37,794
# WRK-1020 Plan: portfolio-signals.yaml cron
date: 2026-03-07
wrk_id: WRK-1020
route: B
complexity: medium
orchestrator: claude

## Objective

Build `scripts/cron/update-portfolio-signals.sh` that refreshes
`.claude/state/portfolio-signals.yaml` nightly with two signal layers:

- **L2**: per-provider WRK activity counts from archive items completed in the last N days
- **L3**: gemini capability research signals, capped to high-confidence items from official sources

Integrate it into `scripts/cron/comprehensive-learning-nightly.sh` after the rsync block and before AI readiness checks. The nightly integration must be best-effort (`|| true`) and must not block the rest of the cron pipeline.

## What Exists (from WRK-1019)

- `scripts/skills/repo-portfolio-steering/compute-balance.py` reads `.claude/state/portfolio-signals.yaml`
- `.claude/state/portfolio-signals.yaml` already exists and has a seeded schema
- Archive items live under `.claude/work-queue/archive/YYYY-MM/*.md` and include `orchestrator:` and `category:` frontmatter in normal cases

## Decisions (Stage 5 user review 2026-03-07)

| Question | Decision |
|---|---|
| L3 throttle | Daily; avoid duplicate same-day additions |
| portfolio-signals.yaml gitignored? | Yes; nightly state file, overwritten |
| Lookback window | 30 days by default |
| L3 prompt scope | Dual-mode: general AI capability news for harness/general-heavy portfolios; engineering-computation focus for engineering-heavy portfolios |
| L3 fail strategy | Carry forward existing `capability_signals` when gemini query fails or output is unusable |
| Integration placement | Step 3a, before AI readiness; best-effort `|| true` |

## Implementation Plan

### Step 1 — `scripts/cron/update-portfolio-signals.sh`

Keep the shell script thin. It should only parse CLI flags, resolve repo-relative paths, and invoke Python via:

```bash
uv run --no-project python scripts/cron/update_portfolio_signals.py "$@"
```

That is simpler to test and avoids embedding non-trivial Python in bash.

**CLI contract**:
```bash
#!/usr/bin/env bash
# update-portfolio-signals.sh
# Usage:
#   bash scripts/cron/update-portfolio-signals.sh [--dry-run] [--lookback N]
# Behavior:
#   - exit 0 on success
#   - non-zero on generation failure
#   - stdout emits YAML only for --dry-run
```

**Python implementation target**:
- Add `scripts/cron/update_portfolio_signals.py`
- Read existing `.claude/state/portfolio-signals.yaml` if present
- Scan archive files recursively under `.claude/work-queue/archive/**/*.md`
- Parse frontmatter defensively:
  - Missing or malformed frontmatter: count in meta as unreadable/skipped
  - Missing `orchestrator`: skip from provider counts
  - Missing `category`: bucket as `other`
  - Missing or malformed `completed_at`: skip from lookback counts and record in meta
- Use `completed_at` date, not folder name, for the lookback window
- Normalize orchestrator/provider values to lowercase and only count known providers: `claude`, `codex`, `gemini`
  - Unknown provider: skip and record separately in meta
- Normalize category mapping:
  - `harness` → `harness`
  - `engineering` → `engineering`
  - `data` → `data`
  - anything else or missing → `other`
- Compute `provider_activity.{provider}.{bucket}` with zero-filled structure for all providers and all buckets
- Write `l2_meta` with enough provenance to debug silent-zero outcomes:
  - `generated_at`
  - `lookback_days`
  - `files_scanned`
  - `files_in_window`
  - `files_with_orchestrator`
  - `files_skipped_no_orchestrator`
  - `files_skipped_bad_completed_at`
  - `files_skipped_unknown_provider`
  - `files_skipped_unreadable`

**L3 block**:
- Determine mode from L2 totals:
  - engineering-focused if total engineering activity `>` total harness activity
  - general mode otherwise
- Tie should stay general. That is safer and matches “default / tie” intent.
- Query gemini only if a CLI is available and executable
- Require official/vendor sources only for retained signals
- Ask for strict YAML output, but do not trust it:
  - parse with `yaml.safe_load`
  - require list of dicts
  - validate each item fields and types
  - reject malformed dates, missing provider, bad URL, unknown impact, or non-official source domains
- Dedup against retained history using a stable key:
  - normalized `(date, provider, capability)`
- Retention policy:
  - prune entries older than 30 days from today
  - add up to 5 validated new entries from current run
  - cap retained list at 20, newest first
- Failure behavior:
  - if gemini unavailable, command fails, times out, returns malformed YAML, or yields zero valid entries, carry forward existing valid `capability_signals`
  - still write L2 output
- Record `l3_meta`:
  - `mode`
  - `query_attempted`
  - `query_succeeded`
  - `signals_added`
  - `signals_retained`
  - `failure_reason` when applicable

**Output**:
- Preserve existing schema compatibility for consumers from WRK-1019
- Overwrite `.claude/state/portfolio-signals.yaml` atomically:
  - write temp file in same directory
  - rename into place
- `--dry-run` prints final YAML to stdout and performs no write
- Validate parent directory exists; create `.claude/state/` if needed

### Step 2 — Integrate into `comprehensive-learning-nightly.sh`

Insert after the rsync block and before AI readiness. Keep it explicitly best-effort.

```bash
# Step 3a: portfolio signals update (best-effort - WRK-1020)
echo "--- Portfolio signals update $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/update-portfolio-signals.sh || \
  echo "WARNING: portfolio signals update failed - see above"

# Step 3b: AI agent readiness
```

Also fix the existing label collision so subsequent comments are monotonic:
- rename current mislabelled `# Step 3:` to `# Step 3c:`

Integration checks:
- script path must be repo-relative and consistent with existing cron conventions
- failure warning must not mask the rest of the nightly run
- no bare `python` or `python3`; only `uv run --no-project python`

### Step 3 — TDD Tests

File: `tests/skills/test_update_portfolio_signals.py`

| Test | AC | Notes |
|---|---|---|
| `test_script_exists_and_uses_uv_no_project_python` | AC-1, AC-5 | shebang + wrapper invokes `uv run --no-project python` |
| `test_python_entrypoint_exists` | AC-1 | implementation separated from shell wrapper |
| `test_provider_activity_counts_from_completed_at` | AC-2 | counts only in-window items using `completed_at`, not directory name |
| `test_completed_at_window_boundary_inclusive` | AC-2 | define exact boundary behavior for day N |
| `test_missing_orchestrator_field_skipped` | AC-2 | skipped, not counted |
| `test_unknown_orchestrator_skipped_and_logged` | AC-2 | unknown provider not counted, meta increments |
| `test_missing_category_field_to_other` | AC-2 | missing category goes to `other` |
| `test_other_bucket_categories` | AC-2 | platform/maintenance/business/personal/uncategorised map to `other` |
| `test_malformed_frontmatter_skipped_with_meta` | AC-2 | unreadable archive file does not crash run |
| `test_bad_completed_at_skipped_with_meta` | AC-2 | malformed timestamp not counted |
| `test_recursive_archive_glob` | AC-2 | nested archive paths found |
| `test_l2_meta_provenance_written` | AC-2 | required meta counters present |
| `test_nonzero_skip_meta_prevents_silent_all_zero_debug_gap` | AC-2 | zero counts accompanied by provenance explaining why |
| `test_dry_run_no_write` | AC-4 | stdout only, no state file write |
| `test_atomic_write_replaces_file` | AC-1 | temp-write then rename behavior |
| `test_lookback_flag_changes_counts` | AC-4b | `--lookback 7` and `--lookback 30` differ when fixtures differ |
| `test_lookback_flag_rejects_invalid_values` | AC-4b | zero, negative, non-integer rejected |
| `test_gemini_query_skipped_when_cli_missing` | AC-3 | graceful fallback; L2 still written |
| `test_carry_forward_on_cli_failure` | AC-3 | non-zero subprocess preserves prior valid signals |
| `test_carry_forward_on_yaml_parse_failure` | AC-3 | malformed YAML preserves prior signals |
| `test_carry_forward_on_all_invalid_items` | AC-3 | valid parse but no usable signals still preserves prior list |
| `test_structured_prompt_yaml_parsed_and_validated` | AC-3 | accepts well-formed YAML list |
| `test_non_official_sources_rejected` | AC-3 | retain only official/vendor sources |
| `test_signal_retention_prunes_older_than_30_days` | AC-3 | old entries removed |
| `test_idempotent_no_duplicate_signals_same_day` | AC-3 | repeat run does not duplicate retained items |
| `test_signal_cap_limits_to_five_new_and_twenty_total` | AC-3 | both caps enforced |
| `test_mode_selection_engineering_vs_general` | AC-3 | engineering only when engineering total strictly exceeds harness |
| `test_mode_selection_tie_defaults_to_general` | AC-3 | tie behavior locked down |
| `test_output_schema_valid_for_compute_balance_consumer` | AC-1, AC-3 | consumer-compatible keys and structure |
| `test_state_directory_created_if_missing` | AC-1 | missing `.claude/state/` handled |
| `test_integrated_in_nightly_with_best_effort_call` | AC-5 | call inserted before readiness step with warning fallback |
| `test_nightly_step_labels_are_monotonic` | AC-5 | verifies `3a`, `3b`, `3c` sequence |
| `test_gitignore_covers_signals` | AC-6 | `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0 |

## Acceptance Criteria

- [ ] AC-1: `scripts/cron/update-portfolio-signals.sh` generates valid `.claude/state/portfolio-signals.yaml` from archive data using `uv run --no-project python`
- [ ] AC-2: Provider activity counts match the last-30-day archive window
  - Recursive glob under `.claude/work-queue/archive/**/*.md`
  - Lookback uses `completed_at:` field, not directory names
  - Missing `orchestrator:` skips the file
  - Missing `category:` maps to `other`
  - Unknown providers are skipped and counted in meta
  - Malformed frontmatter or bad `completed_at:` does not crash the run
  - `l2_meta` provenance is written with enough detail to explain zero-count outputs
- [ ] AC-3: Gemini capability research adds at most 5 validated new signals per run
  - Carry forward existing valid `capability_signals` on missing CLI, subprocess failure, timeout, parse failure, or zero valid results
  - Prune retained signals older than 30 days
  - Dedup by normalized `(date, provider, capability)`
  - Retain at most 20 total signals
  - Dual-mode prompt selection: engineering mode only when engineering activity strictly exceeds harness; tie/default is general
  - Retained signals must come from official/vendor sources only
  - `l3_meta` records query attempt/result details
- [ ] AC-4: `--dry-run` prints YAML to stdout and does not write the state file
- [ ] AC-4b: `--lookback N` overrides the default 30-day window and rejects invalid values
- [ ] AC-5: Nightly cron integrates the script as Step 3a before AI readiness, uses best-effort failure handling, fixes the step-label collision, and uses no bare `python` calls
- [ ] AC-6: `git check-ignore -v .claude/state/portfolio-signals.yaml` exits 0

## Workstation

ace-linux-1 (plan + execution)

## Codex Notes

- The draft put substantial logic inside a shell-script plan. That is harder to test and easier to break on quoting, YAML escaping, and subprocess handling. A thin shell wrapper plus Python entrypoint is the more robust implementation.
- The draft’s tie rule was inconsistent: objective text said engineering-focused when `engineering_count >= harness_count`, but prompt notes also said “default / tie: general AI capability news.” The plan should pick one. I locked tie to general.
- The draft did not define behavior for malformed `completed_at`, malformed frontmatter, unknown orchestrators, invalid `--lookback`, missing state directory, atomic writes, or all-invalid gemini responses. Those are practical cron failure modes and should be explicit.
- “Do not produce all-zero tables silently” needs measurable behavior. I translated that into required provenance counters in `l2_meta`.
- L3 source quality was underspecified. “High-confidence” is not testable unless retention filters define acceptable sources. I made that “official/vendor sources only.”
- The nightly integration risk is low, but only if the step is best-effort and the warning path does not alter exit semantics for the rest of the cron script.
- The plan must explicitly verify `uv run --no-project python` anywhere Python is invoked. The original tests only checked this in the nightly script, not in the new wrapper itself.
