# Session Handoff: Phase 4 Follow-ups Complete

> **Date:** 2026-04-16
> **Session scope:** Fix three follow-up issues from the llm-wiki unified review Phase 4, then integrate conformance + freshness into weekly cron
> **Base commit:** 583506e8f (Phase 4 delivery)

---

## Commits (7 total, 6 from this session)

```
4c0d74063  chore(sync): auto-sync 2026-04-16
1affe6cf8  feat(knowledge): weekly conformance + freshness cron (#2206, #1614, #2105)
c1a3c83b0  chore(wiki): backfill legacy source page frontmatter dates
3a1d462d8  fix(knowledge): harden Phase 4 review tooling
5677a1f6c  fix(index): correct content_hash mislabeling — MD5 no longer tagged as sha256 (#2304)
24eccfc49  fix(registry): update 8 dead URLs, archive 1 defunct resource (#2302)
59723631f  fix(knowledge): emit added/last_updated in batch-ingest frontmatter (#2303)
```

## Issues closed

| Issue | Title | Fix commit |
|-------|-------|-----------|
| #2302 | 9 dead links in online-resource-registry.yaml | 24eccfc49 |
| #2303 | batch-ingest pages lack last_updated (DT-1 failure) | 59723631f + c1a3c83b0 |
| #2304 | content_hash MD5 mislabeled as sha256 | 5677a1f6c |

All three issues commented and closed on GitHub.

## What was built

### 1. Frontmatter fix (#2303)
- `_build_source_page()` in `llm_wiki.py` now emits `added:` and `last_updated:`
- `_repair_legacy_source_page_frontmatter()` — auto-backfills during batch-ingest re-runs
- `_parse_frontmatter()` + `_check_frontmatter()` — frontmatter validation wired into `lint` command
- Legacy backfill executed: ~19K source pages now have date fields (commit c1a3c83b0)

### 2. Dead link fixes (#2302)
- 8 URLs updated with working replacements in `online-resource-registry.yaml`
- 1 archived as dead (whitson-org GitHub org dissolved)
- Notable: thermopack moved to thermotools org, OrcaFlex docs consolidated, IACS restructured

### 3. Hash mislabel fix (#2304)
- `inventory.py` now uses `hashlib.sha256()` (was `hashlib.md5()`)
- `phase-a-index.py` detects 32-char legacy hashes → `md5:` prefix, 64-char → `sha256:`
- Existing `index.jsonl` NOT reindexed (forward-looking fix only)

### 4. Weekly governance cron (#2206, #1614, #2105)
- New script: `scripts/knowledge/weekly-governance-check.sh`
- Schedule: Monday 04:45 UTC (after wiki-ingest 02:15, before hermes-parity 04:30)
- Runs: pyramid-conformance-check.py + registry-freshness-check.py
- Auto-creates GitHub issues on failures (labels: `conformance`, `registry-health`)
- Entry added to `config/scheduled-tasks/schedule-tasks.yaml`
- Dry-run tested successfully

## Remaining uncommitted files

These are pre-existing modifications from earlier sessions, NOT from this session:

```
config/ai-tools/agent-quota-latest.json
config/ai-tools/provider-*.json
docs/reports/provider-*.md
```

These are routine auto-generated dashboard files. Safe to commit via `chore(sync)` or leave for the next auto-sync.

## What's next — unified review Phases 1-3 open items

Ordered by impact (from Section 8 of the unified review plan):

### High priority
- **#1878** — Fix 647K unknown content_type in index.jsonl (L2 registry critical bug)
  - Prerequisite for #2207 provenance contract implementation
  - Diagnosis report exists: `docs/reports/2026-04-16-issue-1878-diagnosis.md`
- **#2293** — Make nightly ingest idempotent and push-status truthful

### Medium priority (cross-wiki knowledge graph)
- **#2011** — Extend wiki-cross-links.py with provenance/tag/entity/standards-chain link types
- **#2068** — Build JSONL cross-link store
- **#2044** — Wire cross-links into wiki index pages

### Medium priority (agent auto-search)
- **#2123** — Build wiki-lookup skill step for agent runtime
- **#2126** — Validate markdown quality for agent consumption
- **#2141** — Add fixture-backed tests (partially done — fixtures now exist)

### Lower priority (expansion)
- **#2103** — Extend ingestion to AQWA/BEMRosetta docs
- **#2124** — Extend ingestion to Orcina resources/examples/training
- **#2283-2286** — Execute standards promotions (YAML records created, wiki pages not yet generated)

## Cron install reminder

The new `weekly-governance-check` entry was added to `schedule-tasks.yaml` but crontab has not been updated. Run:

```bash
bash scripts/cron/setup-cron.sh
```

to install the new Monday 04:45 UTC schedule on dev-primary.
