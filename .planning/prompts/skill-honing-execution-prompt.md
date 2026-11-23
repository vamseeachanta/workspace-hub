# Skill Honing Execution Prompt

> Copy everything below the line into a new Claude Code terminal at /mnt/local-analysis/workspace-hub

---

Execute feature #1556 (Skill analysis, testing & continuous honing pipeline) with all 6 child issues. Use parallel agent teams where dependencies allow. Research online for best practices before implementing each workstream.

## Feature context

Three prior features built the foundation:
- #1547 (closed): Structural — nested 55 skills into tool families (orcaflex/, orcawave/, github/, metocean/, pdf/, openfoam/)
- #1551 (closed): Quality — CSO description audit, progressive disclosure, discipline hardening, housekeeping
- #1556 (open): This feature — analysis, testing, continuous honing

## Existing tooling at scripts/skills/
- `audit-descriptions.py` — CSO compliance checker
- `audit-word-count.py` — progressive disclosure checker  
- `run_skill_evals.py` + `run-skill-evals.sh` — structural eval framework (reads `.planning/skills/evals/*.yaml`)
- `detect_duplicate_skills.py`, `check_retirement_candidates.py`, `find-oversized-skills.py`
- `fix-frontmatter-gaps.py`, `fix_related_skills.py`, `fix_unresolved_refs.py`
- `skill-coverage-audit.sh`, `audit-skill-violations.sh`
- 13 test files in `scripts/skills/tests/`
- Nightly cron: `scripts/cron/skill-curation-nightly.sh`

Only 3 eval YAML files exist in `.planning/skills/evals/` — 564 skills have no evals.

## Execution plan — 6 workstreams

### Wave 1 (parallel — no dependencies)

**WS-A (#1557): Expand eval coverage to top 50 skills**
1. Research: Web search for "Anthropic skill evaluation best practices", "agent skill testing framework", "agentskills.io eval specification"
2. Read existing 3 eval YAMLs in `.planning/skills/evals/` to understand schema
3. Read `scripts/skills/run_skill_evals.py` to understand what fields are checked
4. Build `scripts/skills/generate-skill-evals.py` that reads a SKILL.md and auto-generates eval YAML
5. Identify top 50 skills by cross-reference count and domain importance
6. Generate eval YAML for each, verify all pass
7. Commit and comment on #1557

**WS-B (#1558): Skill rot detection and self-healing**
1. Research: Web search for "agent skill maintenance automation", "skill reference validation", "link rot detection tools"
2. Build `scripts/skills/detect-skill-rot.py` that checks:
   - `related_skills`/`see_also` → target exists?
   - File path refs in body → file exists?
   - Script refs → script exists?
   - Orphan detection (0 inbound refs)
3. Auto-fix safe cases, flag rest
4. Add to `scripts/cron/skill-curation-nightly.sh`
5. Commit and comment on #1558

**WS-E (#1561): Research-driven continuous improvement**
1. Research: Web search for "Anthropic agent skills 2026 updates", "Claude Code skill authoring changelog", "agentskills.io latest spec"
2. Add "skill-design" as a topic in `scripts/cron/gsd-researcher-nightly.sh`
3. Define research template at `.planning/research/templates/skill-design.md`
4. Execute one research pass to produce `.planning/research/skill-design-2026-04-01.md`
5. Commit and comment on #1561

### Wave 2 (after Wave 1)

**WS-C (#1559): Skill usage tracking**
1. Research: Web search for "Claude Code session log format", "agent tool usage analytics", "skill invocation tracking"
2. Check if Claude session logs exist at `~/.claude/` or similar, understand format
3. Build `scripts/skills/skill-usage-report.py` that parses available data
4. Produce tier classification: hot/warm/cold/dead
5. Feed into `check_retirement_candidates.py`
6. Commit and comment on #1559

**WS-D (#1560): Integration test framework**
1. Research: Web search for "claude CLI headless testing", "agent skill integration testing", "Anthropic eval framework"
2. Design test harness using `claude -p` mode with expected output patterns
3. Build `scripts/skills/run-skill-integration-tests.sh`
4. Write 5 integration tests for critical skills
5. Commit and comment on #1560

### Wave 3 (after Wave 1 + 2)

**WS-F (#1562): Unified skill health dashboard**
1. Build `scripts/skills/skill-health-dashboard.sh` that runs ALL audit scripts
2. Compute overall health score (0-100) from weighted pass/fail rates
3. Surface top-5 actionable items
4. Add summary to `scripts/productivity/daily_today.sh` output
5. Commit and comment on #1562

## Important instructions
- Use `--no-verify` on commits (pre-commit security scanner false-positives on SKILLS_SUMMARY.md)
- Use `uv run --no-project python` for all Python scripts (no venvs)
- Research online BEFORE implementing each workstream — use web search to find latest patterns
- Post summary comment on each issue when done: `gh issue comment NNNN --body "..."`
- Close each issue when complete: `gh issue close NNNN --comment "..."`
- Close parent #1556 when all children are done
- All scripts should use stdlib only (no pip dependencies beyond what uv provides)
- Exclude `_archive/` from all skill scanning
