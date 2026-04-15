# Skills Consolidation Issue Draft — Wave 2

**Proposed title:** `chore(skills): deduplicate 7 exact-copy skills and reconcile 3 dev/ops leaf collisions`

**Suggested labels:** `enhancement`, `priority:medium`, `cat:skills`, `cat:maintenance`

## Highest-ROI findings included (7 exact duplicates + 3 collisions)

| # | Type | Skill | Canonical path | Stale duplicate |
|---|------|-------|----------------|-----------------|
| 1 | exact-duplicate | cross-agent-skill-audit | `coordination/cross-agent-skill-audit/SKILL.md` | `cross-agent-skill-audit/SKILL.md` |
| 2 | exact-duplicate | github-code-review | `development/github/code-review/SKILL.md` | `github/github-code-review/SKILL.md` |
| 3 | exact-duplicate | obsidian | `business/productivity/obsidian/SKILL.md` | `note-taking/obsidian/SKILL.md` |
| 4 | exact-duplicate | corporate-tax-strategic-planning | `business-finance/corporate-tax-strategic-planning/SKILL.md` | `corporate-tax-strategic-planning/SKILL.md` |
| 5 | exact-duplicate | writing-plans | `development/planning/writing-plans/SKILL.md` | `software-development/writing-plans/SKILL.md` |
| 6 | exact-duplicate | dspy | `ai/prompting/dspy/SKILL.md` | `mlops/research/dspy/SKILL.md` |
| 7 | exact-duplicate | systematic-debugging | `development/systematic-debugging/SKILL.md` | `software-development/systematic-debugging/SKILL.md` |
| 8 | leaf-collision | code-review / github-code-review | `development/github/code-review/SKILL.md` | `software-development/code-review/SKILL.md` |
| 9 | leaf-collision | pyproject-toml (ops vs dev) | `development/devtools/pyproject-toml/SKILL.md` | `operations/devtools/pyproject-toml/SKILL.md` |
| 10 | leaf-collision | uv-package-manager (ops vs dev) | `development/devtools/uv-package-manager/SKILL.md` | `operations/devtools/uv-package-manager/SKILL.md` |

---

## Issue body (ready for `gh issue create --body-file`)

```markdown
## Summary

Deduplicate 7 exact-copy skill pairs and reconcile 3 development-vs-operations
leaf-name collisions identified by the 2026-04-15 weekly skills audit.

This is Wave 2 of post-audit consolidation, following #2280 / #2281 / #2282
which landed the deterministic weekly audit infrastructure and locked the
classification/ranking policy.

## Why

The weekly audit (`scripts/cron/skills-curation.sh`) surfaced 14 exact-duplicate
pairs and 6 active leaf collisions across `.claude/skills/`.
Email-related duplicates are handled by #2019 and session-corpus-audit by #2083.
The remaining 7 exact duplicates and 3 closely related collisions are
unaddressed, meaning:

- Agent skill resolution can non-deterministically pick either copy.
- Edits to one copy silently diverge from the other.
- The `operations/devtools/` and `development/devtools/` trees contain
  functionally identical skills (pyproject-toml, uv-package-manager) under
  different parents, inflating the skill index.

## Scope

### Exact duplicates — delete the stale copy, keep the canonical path

| Skill | Keep | Delete |
|-------|------|--------|
| cross-agent-skill-audit | `coordination/cross-agent-skill-audit/` | `cross-agent-skill-audit/` (root-level orphan) |
| github-code-review | `development/github/code-review/` | `github/github-code-review/` |
| obsidian | `business/productivity/obsidian/` | `note-taking/obsidian/` |
| corporate-tax-strategic-planning | `business-finance/corporate-tax-strategic-planning/` | `corporate-tax-strategic-planning/` (root-level orphan) |
| writing-plans | `development/planning/writing-plans/` | `software-development/writing-plans/` |
| dspy | `ai/prompting/dspy/` | `mlops/research/dspy/` |
| systematic-debugging | `development/systematic-debugging/` | `software-development/systematic-debugging/` |

### Leaf-name collisions — merge content into one canonical location

| Skill | Canonical | Merge-from |
|-------|-----------|------------|
| code-review / github-code-review | `development/github/code-review/` | `software-development/code-review/` |
| pyproject-toml | `development/devtools/pyproject-toml/` | `operations/devtools/pyproject-toml/` |
| uv-package-manager | `development/devtools/uv-package-manager/` | `operations/devtools/uv-package-manager/` |

For each collision: diff the two SKILL.md files, merge any unique content into
the canonical copy, then delete the merge-from directory.

## Deliverables

- [ ] Remove 7 exact-duplicate directories (stale copies)
- [ ] Merge and deduplicate 3 leaf-collision pairs
- [ ] Verify no remaining references (grep for deleted paths in SKILL.md files, scripts, and config)
- [ ] Run weekly audit script; confirm these 10 findings no longer appear
- [ ] If `operations/devtools/` is empty after pyproject-toml + uv-package-manager removal, remove the empty tree

## Acceptance criteria

1. Running `bash scripts/cron/skills-curation.sh` (or the underlying weekly audit flow) produces zero findings for the 10 skill names listed above.
2. No broken cross-references: `grep -r` for every deleted path returns zero hits in `.claude/skills/`, `config/`, and `scripts/`.
3. Canonical copies are content-complete (no information lost from merged collision pairs).
4. PR diff is net-negative in file count (expect -10 SKILL.md files minimum).

## Out of scope / non-goals

- **Email skill consolidation** — covered by #2019.
- **session-corpus-audit dedup** — covered by #2083.
- **Architecture doc split** — covered by #2214.
- **Adjacent-specialization findings** (e.g., openfoam vs orcawave analysis) — these require domain judgment and are not mechanical dedup.
- **Remaining leaf collisions** not listed above (competitive-analysis, naval-architecture, github-sync/sync) — these cross domain boundaries and need separate scoping.
- **Refactoring the top-level directory taxonomy** — this issue removes orphans and merges within existing trees; it does not reorganize the tree.

## Related issues

- #2280 — weekly audit runner (landed)
- #2281 — deterministic weekly audit implementation (landed)
- #2282 — locked classification/ranking policy (landed)
- #2019 — email skill consolidation (open, covers gmail duplicates)
- #2083 — session-corpus-audit dedup (open)
- #2214 — architecture doc split (open)
```
