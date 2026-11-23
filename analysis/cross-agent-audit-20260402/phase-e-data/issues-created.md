# Issues Created from Cross-Agent Audit (Terminal 3)

**Date**: 2026-04-02
**Parent Issue**: #1720

## Issues by Priority

### Priority: HIGH
| # | Issue | Labels | Source |
|---|-------|--------|--------|
| #1728 | fix: resolve 6 CLAUDE.md merge conflicts across repos | bug, priority:high, cat:harness | Phase G §3 |
| #1729 | chore: add AGENTS.md to CAD-DEVELOPMENTS | enhancement, priority:high, cat:harness | Phase G §2 |

### Priority: MEDIUM
| # | Issue | Labels | Source |
|---|-------|--------|--------|
| #1730 | chore: update routing-config.yaml and provider-capabilities.yaml | enhancement, priority:medium, cat:ai-orchestration | Phase E §5-7 |
| #1731 | chore: clean up 15 stale command references | bug, priority:medium, cat:harness | Phase G §4 |
| #1733 | chore: promote 5 domain-critical skills from CAD-DEVELOPMENTS | enhancement, priority:medium, cat:skills | Phase G §5 |
| #1734 | chore: add domain skills to assethold (tier-1, 0 skills) | enhancement, priority:medium, cat:skills | Phase G §6 |
| #1735 | chore: add skills/commands to aceengineer-website (111 commits, 0 skills) | enhancement, priority:medium, cat:harness | Phase G §6 |

### Priority: LOW
| # | Issue | Labels | Source |
|---|-------|--------|--------|
| #1732 | chore: deduplicate 13 skills in achantas-data | enhancement, priority:low, cat:skills | Phase G §5 |
| #1736 | chore: standardize cross-review verdict format | enhancement, priority:low, cat:ai-orchestration | Phase E §4 |
| #1737 | fix: OGManufacturing test_command but 0 test files | bug, priority:low, cat:harness | Phase G §2 |
| #1738 | chore: triage 54 pending WQ items in CAD-DEVELOPMENTS | enhancement, priority:low, cat:work-queue-infrastructure | Phase G §1 |

## Dependency Map
- #1728 (merge conflicts) should be resolved BEFORE #1734 (assethold skills)
- #1729 (CAD-DEVELOPMENTS AGENTS.md) is independent
- #1733 (skill promotion) depends on #1729 for context
- #1730 (routing config) is independent and can be done anytime
