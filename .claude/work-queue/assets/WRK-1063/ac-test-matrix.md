# WRK-1063 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| 1 | 4 templates in specs/templates/ | `ls specs/templates/route-c-*.md` — 4 files present | PASS |
| 2 | Each has mission skeleton, domain checklist, standards references | Manual inspection of all 4 templates | PASS |
| 3 | Templates reference .claude/docs/ and .claude/rules/ | Grep for `.claude/rules/` and `.claude/docs/` in templates | PASS |
| 4 | new-spec.sh copies right template for all domains | `bash new-spec.sh WRK-9999 structural/marine/energy/generic` each created correct spec.md | PASS |
| 5 | new-spec.sh rejects unknown domain | `bash new-spec.sh WRK-9999 unknown` exits with error + valid domain list | PASS |
| 6 | Codex cross-review passes | cross-review-implementation-codex.md: Verdict MINOR, all P2 fixed | PASS |
