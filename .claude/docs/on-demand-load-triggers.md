# On-Demand Load Triggers

Files removed from CLAUDE.md @imports (WRK-1384). Load explicitly when needed.

## cross-repo-graph.yaml (38 lines)

Path: `config/deps/cross-repo-graph.yaml`

| When to load | Script/context |
|---|---|
| Running cross-repo contract tests | `scripts/testing/run-cross-repo-integration.sh` (auto-reads) |
| Checking downstream dependencies before a breaking change | Agent reads manually |
| Adding a new repo to the dependency graph | Agent reads + edits |

Not needed for: single-repo WRK items, planning stages, reviews, archival.

## repo-map.yaml (60 lines)

Path: `config/onboarding/repo-map.yaml`

| When to load | Script/context |
|---|---|
| Running tests in a specific repo | Stage 10/12 micro-skills reference it; agent reads for test command |
| Nightly smoke tests | `scripts/cron/nightly-smoke-tests.sh` (auto-reads) |
| Onboarding a new repo | `scripts/onboarding/generate-repo-map.py` regenerates it |
| Dark intelligence implementation | `dark-intelligence-workflow/step-6-implement` references it |
| Research literature domain mapping | `scripts/data/research-literature/research-domain.py` uses domain variant |

Not needed for: planning stages, reviews, git operations, archival, non-code WRKs.
