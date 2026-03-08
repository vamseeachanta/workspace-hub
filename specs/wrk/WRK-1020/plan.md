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

Integrate into `comprehensive-learning-nightly.sh` as Step 3a (before exec pipeline).

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
# Parse archive/*.md frontmatter for orchestrator + category
# Count by (orchestrator, category) for items archived in last N days
# Output: provider_activity.{claude,codex,gemini}.{harness,engineering,data,other}
```

**L3 block** (capability research):
```bash
# Run gemini query for new AI capabilities in last 7 days
# Parse output for provider/capability/impact/source entries
# Deduplicate against existing entries by date+provider+capability hash
# Append up to 5 new entries, preserve existing entries (max 20 total)
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

| Test | AC |
|---|---|
| `test_script_exists` | AC-1 |
| `test_provider_activity_counts` | AC-1 fixture test |
| `test_dry_run_no_write` | AC-4 |
| `test_gemini_query_skipped_no_gemini` | AC-2 graceful fallback |
| `test_output_schema_valid` | AC-1 + AC-3 |
| `test_integrated_in_nightly` | AC-5 |
| `test_gitignore_covers_signals` | AC-6 |

## Acceptance Criteria

- [ ] `update-portfolio-signals.sh` generates valid portfolio-signals.yaml from archive
- [ ] Provider activity counts match manual count of last-30-day archive files
- [ ] Capability research: gemini query runs; ≤5 signals written; source URLs included
  - Graceful fallback if gemini CLI absent or query fails (L2 still written)
- [ ] `--dry-run` flag prints without writing file
- [ ] Script integrated into `comprehensive-learning-nightly.sh`
- [ ] `.claude/state/portfolio-signals.yaml` confirmed gitignored

## Open Questions for User (Stage 5)

1. **L3 prompt strategy**: Should the gemini query ask for general AI capability news, or focus specifically on Claude/Codex/Gemini CLI tool improvements relevant to engineering computation?
2. **L3 fail strategy**: If gemini query fails (quota, network), should (a) L3 block be omitted from output entirely, or (b) carry forward previous `capability_signals` from existing file?
3. **Integration placement**: Before AI readiness check (Step 3b) or at very end of nightly (Step 8+)?

## Workstation

ace-linux-1 (plan + execution)
