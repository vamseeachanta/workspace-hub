# Future Work Recommendations — WRK-678

wrk_id: WRK-678
captured_at: 2026-03-02T19:00:00Z
captured_by: claude

## Follow-up WRKs

| Priority | WRK-ID | Title | Status | Rationale |
|----------|--------|-------|--------|-----------|
| P1 | WRK-679 | Standardize execute gate variation tests | pending | Next governance gate item in sequence |
| P2 | WRK-680 | Strengthen archive gate validation | pending | Archive gate currently has no validator check |
| P3 | WRK-681 | Add anti-pattern sections to agent skills | pending | Skill quality improvement follow-on |

## Team Decisions

- Future-work gate is WARN when absent (backward compatible) and FAIL when present-but-invalid.
  This allows legacy WRK-669/670/671 to close without needing the artifact, while enforcing
  the standard for all new orchestrator runs from WRK-678 onward.
- Template uses `no_follow_ups_rationale:` as escape hatch for items with no natural follow-ons.
