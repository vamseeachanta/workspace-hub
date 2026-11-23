---
name: agent-teams-decision-matrix-team-vs-sequential
description: 'Sub-skill of agent-teams: Decision Matrix: Team vs Sequential.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Decision Matrix: Team vs Sequential

## Decision Matrix: Team vs Sequential


| Task profile | Use team? | Rationale |
|-------------|-----------|-----------|
| < 5 files, single domain | **No** | Sequential is faster than team overhead |
| Writing WRK items / skills | **No** | Small, sequential, ~minutes each |
| 3+ independent workstreams > 20 min each | **Yes** | Parallelism pays off |
| Bulk file transforms (50+ files) | **Yes** | Bash agent per batch |
| Research + implementation (separate concerns) | **Yes** | Explore agent + Bash agent |
| Cross-repo changes (each repo independent) | **Yes** | One agent per repo |
| WRK-205 knowledge graph (115 files) | **Yes** | 3 parallel streams |

**Rule of thumb**: If you would finish faster doing it yourself than explaining
it to a teammate, do it yourself.
