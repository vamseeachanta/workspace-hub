# Terminal 4 — Gemini — Doc Staleness Scanner + Doc Refresh

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to main and push after each task. Do not branch.
Run `git pull origin main` before every push.
TDD: write tests before implementation.
Do NOT ask the user any questions — make reasonable decisions and document them.

IMPORTANT: Do NOT write to docs/architecture/, docs/roadmaps/, docs/document-intelligence/,
or scripts/document-intelligence/ — those are owned by other terminals.
Only write to: scripts/docs/, docs/dashboards/, docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md,
docs/SKILLS_INDEX.md, docs/modules/tiers/TIER2_REPOSITORY_INDEX.md.

## TASK 1: Automated Doc Staleness Scanner (GH #1568)

### Context
Issue #1568 needs an automated doc staleness scanner. Many docs drift silently:
- docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md — STALE (Oct 2025)
- docs/SKILLS_INDEX.md — STALE (Dec 2025)
- docs/modules/tiers/TIER2_REPOSITORY_INDEX.md — STALE (Jan 2026)
- docs/research/engineering-capability-map.md — Moderate (Feb 2026)

The scanner should check git last-modified dates and content-based freshness signals.

### What to do
1. Write tests first: tests/docs/test_staleness_scanner.py
   - test_detects_stale_files (mock git log output)
   - test_freshness_thresholds (30/60/90 day buckets)
   - test_yaml_output_format
   - test_handles_missing_files
2. Implement scripts/docs/staleness-scanner.py that:
   - Walks all .md files under docs/
   - Gets last git commit date for each file via `git log -1 --format=%aI -- <file>`
   - Classifies: FRESH (<30 days), MODERATE (30-90 days), STALE (>90 days)
   - Checks for date stamps in file content (e.g., "Updated: YYYY-MM-DD")
   - Outputs YAML report + summary table
3. Run the scanner and save output to docs/dashboards/doc-freshness-dashboard.md
4. Run: `uv run pytest tests/docs/test_staleness_scanner.py -v`

### Acceptance criteria
- scripts/docs/staleness-scanner.py exists and runs
- tests/docs/test_staleness_scanner.py has at least 4 tests, all pass
- docs/dashboards/doc-freshness-dashboard.md shows all docs with staleness status
- Dashboard has summary: "N FRESH, M MODERATE, P STALE"

### Commit message
feat(docs): automated doc staleness scanner and freshness dashboard (#1568)

---

## TASK 2: Refresh CAPABILITIES_SUMMARY (GH #1571, part 1)

### Context
docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md is from Oct 2025 — 6 months stale.
The workspace-hub has grown significantly since then. Current state:
- 25+ repos (see docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md for current list)
- digitalmodel has 31+ packages, 1594 source files
- Document intelligence pipeline is new (post Oct 2025)
- OrcaWave/OrcaFlex pipeline, solver queue, hull library — all new
- Continuous architecture intelligence features (#1567) — new

### What to do
1. Read the current docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md
2. Read docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md (current as of 2026-03-31)
3. Read docs/document-intelligence/data-intelligence-map.md
4. Read docs/research/engineering-capability-map.md
5. Rewrite CAPABILITIES_SUMMARY to reflect current state:
   - Ecosystem overview (repo count, package count, test count)
   - Engineering capabilities (solvers, hull library, OrcaWave/OrcaFlex)
   - Document intelligence capabilities
   - AI orchestration capabilities
   - Infrastructure & operations
   - Add "Last updated: 2026-04-02" at the top

### Acceptance criteria
- docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md is fully rewritten
- References all major capabilities added since Oct 2025
- Has "Last updated: 2026-04-02" header

### Commit message
docs: refresh WORKSPACE_HUB_CAPABILITIES_SUMMARY.md — Oct 2025 → Apr 2026 (#1571)

---

## TASK 3: Refresh SKILLS_INDEX and TIER2_REPOSITORY_INDEX (GH #1571, parts 2+3)

### What to do

Part A — SKILLS_INDEX:
1. Read current docs/SKILLS_INDEX.md
2. List all Hermes skills by reading the skills directory if accessible, or scan
   docs/ and scripts/ for skill references
3. Update the index to reflect current skills inventory
4. Add "Last updated: 2026-04-02"

Part B — TIER2_REPOSITORY_INDEX:
1. Read docs/modules/tiers/TIER2_REPOSITORY_INDEX.md
2. Read docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md for current tier-2 repos
3. Update index with any new tier-2 repos, remove any that have been promoted/archived
4. Add "Last updated: 2026-04-02"

### Acceptance criteria
- Both docs updated with current content
- Both have "Last updated: 2026-04-02" headers
- No stale repo references remain

### Commit message
docs: refresh SKILLS_INDEX + TIER2_REPOSITORY_INDEX — current as of Apr 2026 (#1571)

---

## After all tasks
Post a brief progress comment on GitHub issues #1568 and #1571 in repo vamseeachanta/workspace-hub:
"Overnight agent run (2026-04-01): [artifact] committed. See [path]."
