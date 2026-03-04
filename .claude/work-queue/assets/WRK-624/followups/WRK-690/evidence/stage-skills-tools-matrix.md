# Stage Skills/Tools Evidence (WRK-690 -> WRK-624 canonical)

Date: 2026-03-03
Source of truth: `.claude/skills/coordination/workspace/work-queue/SKILL.md` (`## Stage Contract` + `## Stage Skills and Tools Matrix`)

## Purpose
Document what happens at each mandatory workflow stage and which skills/tools/scripts are expected, so review can verify enforcement readiness.

## Stage Matrix (Execution Contract)

| Stage | What happens | Primary evidence |
|---|---|---|
| 1. Capture | Create WRK item and baseline frontmatter | WRK file in `pending/` |
| 2. Resource Intelligence | Build pre-plan resource context | `resource-intelligence.yaml` |
| 3. Triage | Set priority/complexity/route/workstations | WRK triage fields |
| 4. Plan Draft | Produce executable draft plan and HTML | draft plan + HTML |
| 5. User Review - Plan (Draft) | User reviews draft plan artifact | review artifact + browser-open proof |
| 6. Cross-Review | Multi-provider review and finding closure | review outputs |
| 7. User Review - Plan (Final) | User approves final plan artifact | final review artifact + browser-open proof |
| 8. Claim / Activation | Claim session ownership and activate WRK | `claim.yaml` + active WRK signal |
| 9. Work-Queue Routing Skill | Enter canonical `/work` route | routing signal in logs |
| 10. Work Execution | Implement scoped work | execution changes + examples |
| 11. Artifact Generation | Generate HTML/report outputs | `review.html` and related artifacts |
| 12. TDD / Eval | Run tests/evals | test/eval outputs |
| 13. Agent Cross-Review | Agent review on implementation outputs | `cross-review-package.md` / provider review notes |
| 14. Verify Gate Evidence | Validate gate ledger | verifier PASS/WARN/FAIL output |
| 15. Future Work Synthesis | Capture deferred/discovered follow-ups | `future-work.yaml` |
| 16. Resource Intelligence Update | Add post-work resource additions | `resource-intelligence-update.yaml` |
| 17. User Review - Implementation | User reviews implementation close package | `user-review-close.yaml` + browser-open proof |
| 18. Reclaim | Re-establish continuity if needed | `reclaim.yaml` |
| 19. Close | Transition WRK to done with gates passing | close script output + done state |
| 20. Archive | Move WRK to archive after sync/merge gates | archive script output + archived state |

## Skills, Scripts, and Tools by Stage

| Stage | Skills/Commands | Scripts | Tools |
|---|---|---|---|
| 1 | `/work` | `migrate-queue.py` (as needed) | queue file ops |
| 2 | `resource-intelligence` | `init-resource-pack.sh` (as needed) | YAML evidence |
| 3 | `/work` triage | `assign-workstations.py` | frontmatter validation |
| 4 | plan flow | `scripts/agents/plan.sh` | HTML generation |
| 5 | user-review gate | n/a | `xdg-open` default browser evidence |
| 6 | cross-review flow | `cross-review.sh`, `submit-to-*.sh` | provider review outputs |
| 7 | user-review gate | n/a | `xdg-open` default browser evidence |
| 8 | claim flow | `claim-item.sh`, `set-active-wrk.sh` | claim ledger |
| 9 | `/work` route | `scripts/agents/work.sh` | route signal |
| 10 | execute flow | `scripts/agents/execute.sh` | implementation artifacts |
| 11 | report flow | `generate-html-review.py` | HTML/report files |
| 12 | test/eval | `uv run --no-project pytest ...` | test outputs |
| 13 | agent cross-review | `cross-review-package.md` | provider review outputs |
| 14 | gate check | `verify-gate-evidence.py` | gate ledger output |
| 15 | follow-up synthesis | n/a | future-work evidence |
| 16 | resource update | n/a | resource-update evidence |
| 17 | implementation close review | n/a | `xdg-open` + review-close evidence |
| 18 | reclaim | n/a | reclaim evidence |
| 19 | close | `close-item.sh` | done-state transition |
| 20 | archive | `archive-item.sh` | archive transition |

## Review Notes
- Browser-open proof is mandatory for all user-review stages (5, 7, 16).
- Verifier is now phase-aware (`--phase claim|close`) and used by claim/close/archive scripts.
- Canonical cross-review pointer for parent item is `.claude/work-queue/assets/WRK-624/cross-review-agent-synthesis.md`.
