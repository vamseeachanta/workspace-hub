wrk_id: WRK-1154
reviewed: true
approved: true
confirmed_by: vamsee
confirmed_at: 2026-03-12T11:01:00Z
decision: passed

# Plan: Stage-01 Frontmatter Validator Script

## Route A Inline Plan

1. Create `scripts/work-queue/validate-wrk-frontmatter.sh WRK-NNN`
2. Use awk to extract YAML frontmatter fields from WRK markdown files
3. Validate 12 required fields: id, title, status, priority, complexity, created_at, target_repos, computer, plan_workstations, execution_workstations, category, subcategory
4. Exit 0 if all present+non-empty; exit 1 with list of missing fields
5. TDD: write test script first, then implementation
