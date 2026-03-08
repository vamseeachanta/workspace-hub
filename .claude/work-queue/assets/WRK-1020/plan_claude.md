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
