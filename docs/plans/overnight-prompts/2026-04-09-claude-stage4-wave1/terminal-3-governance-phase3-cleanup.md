We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2057 — Session Governance Phase 3 (Skill Restoration)
Status: deliverable skill files already exist; remaining work is cleanup hygiene.

Context:
- Existing coordination skills:
  - `.claude/skills/coordination/session-start-routine/SKILL.md`
  - `.claude/skills/coordination/session-corpus-audit/SKILL.md`
  - `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md`
  - `.claude/skills/coordination/cross-review-policy/SKILL.md`
- Broken links exist under `.claude/skills/_internal/meta/`.
- Duplicate `session-corpus-audit` exists under `.claude/skills/workspace-hub/`.
- `docs/governance/SESSION-GOVERNANCE.md` needs a #2057 section.

Tasks:
1. Find and fix all broken `session-start-routine` links under `.claude/skills/_internal/meta/` so they point to `.claude/skills/coordination/session-start-routine/SKILL.md`.
2. Reconcile duplicate `session-corpus-audit` content:
   - compare coordination and workspace-hub versions
   - merge unique value into the coordination version if needed
   - otherwise remove the redundant workspace-hub copy
3. Add a #2057 section to `docs/governance/SESSION-GOVERNANCE.md` documenting the restored Phase 3 skills.
4. Add smoke tests at `tests/governance/test_phase3_skill_smoke.py` verifying each skill file has parseable YAML frontmatter and non-empty markdown body.
5. Run:
   - `uv run pytest tests/governance/test_phase3_skill_smoke.py -v`
6. Post a GitHub issue comment on #2057 summarizing cleanup work.

Allowed write paths:
- `.claude/skills/_internal/meta/**/*.md` (link fixes only)
- `.claude/skills/coordination/session-corpus-audit/SKILL.md`
- `.claude/skills/workspace-hub/session-corpus-audit/` (delete only if redundant)
- `docs/governance/SESSION-GOVERNANCE.md`
- `tests/governance/test_phase3_skill_smoke.py`
- `tests/governance/__init__.py`

Negative write boundaries:
- `.claude/skills/coordination/session-start-routine/SKILL.md`
- `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md`
- `.claude/skills/coordination/cross-review-policy/SKILL.md`
- `.claude/settings.json`
- `.claude/hooks/`
- any file under `digitalmodel/` or `worldenergydata/`

Cross-review: not required.

End state:
- broken links fixed
- smoke test passes
- governance doc updated
- issue comment posted
