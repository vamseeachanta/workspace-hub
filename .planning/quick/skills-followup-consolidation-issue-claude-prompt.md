You are working in /mnt/local-analysis/workspace-hub.

Task
Create a follow-up GitHub issue draft for the next high-ROI skills consolidation wave after #2280/#2281/#2282 landed.

Hard constraints
- Do NOT modify tracked repo files outside .planning/quick/.
- Do NOT create or edit GitHub issues directly.
- Do NOT touch docs/plans/, config/, scripts/, tests/, or .claude/skills/.
- Stay focused on drafting one issue only.
- Use the current weekly audit findings as the primary evidence source.

Available evidence
Current weekly audit findings from /tmp/skills-audit-verify/logs/maintenance/skills-curation/2026-04-15.json:
1. exact-duplicate | gmail-data-extraction | email/_archived/gmail-data-extraction/SKILL.md; email/gmail-data-extraction/SKILL.md
2. exact-duplicate | cross-agent-skill-audit | coordination/cross-agent-skill-audit/SKILL.md; cross-agent-skill-audit/SKILL.md
3. exact-duplicate | github-code-review | development/github/code-review/SKILL.md; github/github-code-review/SKILL.md
4. exact-duplicate | obsidian | business/productivity/obsidian/SKILL.md; note-taking/obsidian/SKILL.md
5. exact-duplicate | corporate-tax-strategic-planning | business-finance/corporate-tax-strategic-planning/SKILL.md; corporate-tax-strategic-planning/SKILL.md
6. exact-duplicate | gmail-email-to-repo-extraction | email/_archived/gmail-email-to-repo-extraction/SKILL.md; email/gmail-email-to-repo-extraction/SKILL.md
7. exact-duplicate | gmail-unsubscribe | email/_archived/gmail-unsubscribe/SKILL.md; email/gmail-unsubscribe/SKILL.md
8. exact-duplicate | writing-plans | development/planning/writing-plans/SKILL.md; software-development/writing-plans/SKILL.md
9. exact-duplicate | gmail-touchbase | email/_archived/gmail-touchbase/SKILL.md; email/gmail-touchbase/SKILL.md
10. exact-duplicate | dspy | ai/prompting/dspy/SKILL.md; mlops/research/dspy/SKILL.md
11. exact-duplicate | session-corpus-audit | coordination/session-corpus-audit/SKILL.md; workspace-hub/session-corpus-audit/SKILL.md
12. exact-duplicate | gmail-extract-and-clean | email/_archived/gmail-extract-and-clean/SKILL.md; email/gmail-extract-and-clean/SKILL.md
13. exact-duplicate | gmail-extract-archive | email/_archived/gmail-extract-archive/SKILL.md; email/gmail-extract-archive/SKILL.md
14. exact-duplicate | systematic-debugging | development/systematic-debugging/SKILL.md; software-development/systematic-debugging/SKILL.md
15. generic-leaf-collision | competitive-analysis, product-competitive-analysis | business/marketing/competitive-analysis/SKILL.md; business/product/competitive-analysis/SKILL.md
16. generic-leaf-collision | ops-pyproject-toml, pyproject-toml | development/devtools/pyproject-toml/SKILL.md; operations/devtools/pyproject-toml/SKILL.md
17. generic-leaf-collision | doc-extraction-naval-architecture, naval-architecture | engineering/doc-extraction/naval-architecture/SKILL.md; engineering/marine-offshore/naval-architecture/SKILL.md
18. adjacent-specialization | openfoam-analysis, orcawave-analysis | engineering/cfd/openfoam/analysis/SKILL.md; engineering/marine-offshore/orcawave/analysis/SKILL.md
19. generic-leaf-collision | github-sync, sync | development/github/sync/SKILL.md; workspace-hub/sync/SKILL.md
20. generic-leaf-collision | code-review, github-code-review | development/github/code-review/SKILL.md; software-development/code-review/SKILL.md
21. generic-leaf-collision | ops-uv-package-manager, uv-package-manager | development/devtools/uv-package-manager/SKILL.md; operations/devtools/uv-package-manager/SKILL.md

Nearby existing open issues already covering some slices:
- #2083 chore(skills): reconcile duplicate session-corpus-audit
- #2019 chore: Consolidate email skill sprawl — 12 skills → 4-5 workflow-aligned skills
- #2214 docs(ai): split current architecture guidance from legacy wrapper redirects

What to do
1. Inspect the repo paths implicated by the findings if needed.
2. Decide the best next issue scope that avoids duplicating #2083, #2019, or #2214.
3. Draft a single GitHub issue body with:
   - Summary
   - Why
   - Scope
   - Deliverables
   - Acceptance Criteria
   - Explicit out-of-scope / non-goals
   - Related Issues
4. Also propose:
   - issue title
   - suggested labels
   - 3-8 highest-ROI findings to include in the issue
5. Save the output to:
   .planning/quick/skills-followup-consolidation-issue-draft.md

Preferred shape
- One concrete issue, not an umbrella.
- Focus on exact duplicates and the most actionable collisions not already covered.
- Prefer a bounded, high-signal wave over a huge omnibus cleanup.
- Make the body ready for `gh issue create --body-file ...` with minimal editing.

When done
- Print a short terminal summary naming the chosen scope, proposed title, and output file path.