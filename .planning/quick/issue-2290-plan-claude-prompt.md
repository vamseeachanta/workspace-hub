You are working in /mnt/local-analysis/workspace-hub.

Task
Draft the canonical planning artifact for GitHub issue #2290 and update the plan index, but do NOT implement the issue.

Hard constraints
- Planning only. No implementation changes to .claude/skills/, config/, scripts/, or tests.
- Allowed write paths only:
  - docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md
  - docs/plans/README.md
  - optional .planning/quick/* scratch notes only if absolutely needed
- Do NOT create review artifacts yet.
- Do NOT change GitHub labels or create/close issues.
- Do NOT touch any file outside the allowed write paths.

Required outputs
1. Create the plan file at:
   docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md
2. Add a row for #2290 to docs/plans/README.md

Plan requirements
- Follow docs/plans/_template-issue-plan.md structure closely.
- Status must be draft.
- Complexity should be T2 unless the evidence proves otherwise.
- The plan must explicitly note that actual implementation is blocked pending adversarial review + user approval.
- The plan must separate current-scope work from follow-up/future work already covered by #2019, #2083, and #2214.
- The plan must include TDD/validation steps for the eventual implementation.

Evidence you should incorporate
Issue
- #2290: chore(skills): deduplicate 7 exact-copy skills and reconcile 3 dev/ops leaf collisions
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2290

Relevant planning/template sources
- docs/plans/_template-issue-plan.md
- docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md
- docs/plans/README.md

Existing related issues / boundaries
- #2019 covers email skill consolidation; keep it out of scope
- #2083 covers session-corpus-audit dedup; keep it out of scope
- #2214 covers architecture doc split / legacy wrapper redirects; keep it out of scope
- #2280 / #2281 / #2282 are prior landed audit/planning dependencies and should be cited as prior work

Current audit findings to cite as evidence
- exact-duplicate: cross-agent-skill-audit
  paths: coordination/cross-agent-skill-audit/SKILL.md ; cross-agent-skill-audit/SKILL.md
- exact-duplicate: github-code-review
  paths: development/github/code-review/SKILL.md ; github/github-code-review/SKILL.md
- exact-duplicate: obsidian
  paths: business/productivity/obsidian/SKILL.md ; note-taking/obsidian/SKILL.md
- exact-duplicate: corporate-tax-strategic-planning
  paths: business-finance/corporate-tax-strategic-planning/SKILL.md ; corporate-tax-strategic-planning/SKILL.md
- exact-duplicate: writing-plans
  paths: development/planning/writing-plans/SKILL.md ; software-development/writing-plans/SKILL.md
- exact-duplicate: dspy
  paths: ai/prompting/dspy/SKILL.md ; mlops/research/dspy/SKILL.md
- exact-duplicate: systematic-debugging
  paths: development/systematic-debugging/SKILL.md ; software-development/systematic-debugging/SKILL.md
- generic-leaf-collision: code-review / github-code-review
  paths: development/github/code-review/SKILL.md ; software-development/code-review/SKILL.md
- generic-leaf-collision: pyproject-toml
  paths: development/devtools/pyproject-toml/SKILL.md ; operations/devtools/pyproject-toml/SKILL.md
- generic-leaf-collision: uv-package-manager
  paths: development/devtools/uv-package-manager/SKILL.md ; operations/devtools/uv-package-manager/SKILL.md

Important nuance from live repo inspection
- Do NOT claim all seven duplicate pairs are byte-identical copies.
- Live sha256 checks show some pairs are identical (for example corporate-tax-strategic-planning), but several are not byte-identical despite sharing canonical names.
- Therefore the plan should frame the exact-duplicate work as canonical-name duplicate reconciliation, with diff/compare before delete where needed.

Extra evidence from live inspection
- scheduler wrapper exists at scripts/cron/skills-curation.sh
- policy and audit were landed under #2281/#2282
- audit JSON example used earlier: /tmp/skills-audit-verify/logs/maintenance/skills-curation/2026-04-15.json

What good looks like
- Resource Intelligence Summary cites concrete files/issues and specific findings.
- Artifact Map includes this plan, likely skill paths, future tests/validation targets, and future review artifact placeholders.
- Files to Change names likely skill paths for future implementation, plus docs/plans/README.md already updated now.
- TDD Test List includes focused tests for audit regression + path/reference verification, even if some exact test files may need to be created later.
- Acceptance Criteria are measurable and aligned with issue #2290.
- Risks/Open Questions mention the canonical-name-vs-byte-identical nuance and the possibility of unique content in some duplicate pairs.

When done
- Print a concise summary with:
  - created plan path
  - whether docs/plans/README.md was updated
  - any important planning nuance discovered
