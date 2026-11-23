# Session Handoff — Terminal 2: Doc Staleness Scanner + Stale Doc Refresh

**Date:** 2026-04-02
**Model:** claude-opus-4-6 via Hermes
**Issues:** #1568 (scanner), #1571 (stale doc refresh)

---

## What Was Done

### TASK 1: Doc Staleness Scanner (#1568) — COMPLETE

**New files:**
- `scripts/quality/doc-staleness-scanner.py` — scans docs/ for .md files, classifies by age
- `tests/quality/test_doc_staleness_scanner.py` — 16 TDD tests (all passing)

**How it works:**
- Scans 6 directories: docs/, docs/assessments/, docs/modules/, docs/research/, docs/standards/, docs/vision/
- Primary date: `git log -1 --format=%aI`; fallback: YAML frontmatter date; last resort: filesystem mtime
- Classification: current (<90d), stale (90-180d), critical (>180d)
- Outputs: JSON report to `.claude/state/doc-staleness/YYYY-MM-DD.json` + ASCII dashboard
- Run: `uv run --no-project python scripts/quality/doc-staleness-scanner.py`

**First scan result:** 225 docs, all current (repo reorganized Feb 24, 2026)

**Commit:** `940c13d1`

### TASK 2: Stale Doc Refresh (#1571) — COMPLETE (4 commits)

1. **WORKSPACE_HUB_CAPABILITIES_SUMMARY.md** (`2af99ad3`)
   - Removed 927 lines of stale content (Claude Flow, SPARC, .agent-os, droid, Flow-Nexus, consensus agents)
   - Added 118 lines reflecting: Control-Plane Contract, GSD workflow, provider adapter model
   - Updated skill counts: 2,734 total (568 active, 2,166 archived)

2. **SKILLS_INDEX.md** (`ec23837c`)
   - Regenerated from actual `.claude/skills/` tree
   - Updated from 51 → 2,734 skills (568 active across 12 categories + 57 GSD commands)
   - Fixed `/mnt/github/` → correct paths
   - Removed references to sparc-workflow, agent-orchestration

3. **TIER2_REPOSITORY_INDEX.md** (`ffdb1728`)
   - Marked 2 repos as REMOVED: `energy`, `ai-native-traditional-eng` (no longer in workspace)
   - Updated stats: 10 present + 2 removed
   - Updated date

4. **workspace-hub-structure.md** (`96f85a4c`)
   - Complete Mermaid diagram rewrite for current architecture
   - Removed: .agent-os, Claude Flow, SPARC, consensus agents, Flow-Nexus, swarm diagrams
   - Added: Provider adapter model, GSD workflow, actual directory tree (52 top-level dirs)

**Follow-up fixes (second pass):**
- SKILLS_INDEX.md (`a744896a`): marked sparc subcategory as "legacy — retained for reference only"
- TIER2_REPOSITORY_INDEX.md (`0a66ec02`): adjusted config requirements 52h→43h for 10 active repos
- workspace-hub-structure.md (`0ca43cd8`): removed last `.agent-os` literal reference from notes

**Net:** ~1,420 lines stale content removed, ~478 lines current content added

---

## GitHub Issue Comments

- #1568: Commented with scanner implementation summary and first scan results
- #1571: Commented with all 4 commit summaries and net line change stats

---

## What's Next

- The staleness scanner should be added to quality check-all.sh or cron
- Consider running scanner weekly via schedule-tasks.yaml
- The scanner currently shows all 225 docs as "current" — this will become useful as time passes and docs age past 90/180 day thresholds
- Some docs in _archive/ or other directories outside the 6 scanned dirs may also need staleness tracking
