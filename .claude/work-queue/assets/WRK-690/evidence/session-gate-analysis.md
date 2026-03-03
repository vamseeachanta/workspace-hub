# Session Gate Analysis (strict + relaxed)

Window: 2026-02-25 to 2026-03-03
- Relaxed sessions: 10
- Strict sessions: 1
- Sources: {'claude-native': 1, 'codex-native': 8, 'gemini-native': 1}

## Gate signal coverage (relaxed)
## Gate signal coverage (ordered by work-queue flow)
| Order | Stage | Signal | Relaxed | Strict | User review | Comments |
|---|---|---|---|---|---|---|
| 1 | Plan / Resource Intelligence | resource_intelligence | 6/10 | 1/1 | PASS (strict) / WARN (relaxed) | Present in strict path; missing in 4 relaxed sessions. |
| 2 | Claim / Session Bootstrap | init | 10/10 | 1/1 | PASS | All qualified sessions include orchestrator init. |
| 3 | Claim -> Work Activation | set_active_wrk | 1/10 | 1/1 | PASS (strict) / FAIL (relaxed) | Primary relaxed gap; explicit WRK activation is mostly absent. |
| 4 | Work-Queue Routing Skill | work_queue_skill | 10/10 | 1/1 | PASS | `/work` or `scripts/agents/work.sh` seen in all qualified sessions. |
| 5 | Work Execution | work_execution | 9/10 | 0/1 | WARN | Execution signal present in most relaxed sessions; strict session does not show explicit `execute.sh` marker. |
| 6 | Artifact Generation | artifact_generation | 10/10 | 1/1 | PASS | Review/HTML artifacts are referenced throughout qualified sessions. |
| 7 | TDD / Eval | tdd_eval | 10/10 | 1/1 | PASS | Test or evaluation evidence markers are present in all qualified sessions. |
| 8 | Verification | verify_gate_evidence | 7/10 | 1/1 | PASS (strict) / WARN (relaxed) | Gate verification command is not universal in relaxed sessions. |
| 9 | User Review (Draft) | plan_html_review_draft | 9/10 | 1/1 | REQUIRED FOR ALL WRKs | Mandatory explicit user review artifact before cross-review. Target compliance: 100%. |
| 10 | Cross-Review | cross_review | 10/10 | 1/1 | PASS | Cross-review scripts are consistently present. |
| 11 | Claim / Evidence Ledger | claim_evidence | 10/10 | 1/1 | PASS | Claim evidence artifacts are referenced across qualified sessions. |
| 12 | User Review (Final) | plan_html_review_final | 9/10 | 1/1 | REQUIRED FOR ALL WRKs | Mandatory explicit user acceptance artifact before close/archive. Target compliance: 100%. |
| 13 | Close Planning | future_work | 4/10 | 0/1 | FAIL | Future-work evidence is frequently missing. |
| 14 | Reclaim | reclaim | 2/10 | 0/1 | WARN | Reclaim is expected only when triggered; mostly absent. |
| 15 | Close / Archive | close_or_archive | 10/10 | 1/1 | PASS | Close/archive signals are present in all qualified sessions. |

## Scripts used (relaxed)
- scripts/agents/session.sh: 6
- scripts/agents/plan.sh: 5
- scripts/review/submit-to-claude.sh: 5
- scripts/work-queue/verify-gate-evidence.py: 5
- scripts/work-queue/close-item.sh: 5
- scripts/work-queue/generate-html-review.py: 5
- scripts/review/submit-to-codex.sh: 4
- scripts/agents/execute.sh: 4
- scripts/review/cross-review.sh: 3
- scripts/review/submit-to-gemini.sh: 3
- scripts/work-queue/log-gate-event.sh: 3
- scripts/agents/work.sh: 3
- scripts/work-queue/assign-workstations.py: 3
- scripts/agents/review.sh: 3
- scripts/legal/legal-sanity-scan.sh: 2

## Skills used (relaxed)
- work: 10
- clear: 8
- comprehensive-learning: 2
- insights: 2
- save: 2
- session-start: 2
- improve: 1
- session-analysis: 1
- session-end: 1

## Tools used (relaxed)
- Bash: 547
- Read: 179
- Edit: 116
- Write: 104
- TaskUpdate: 12
- Glob: 8
- ToolSearch: 8
- TaskCreate: 6
- AskUserQuestion: 6
- TaskOutput: 6
- unknown: 2
- mcp__claude-in-chrome__tabs_context_mcp: 2
- mcp__claude-in-chrome__navigate: 2
- mcp__claude-in-chrome__read_page: 1

## Scripts used (strict)
- scripts/agents/plan.sh: 1
- scripts/agents/session.sh: 1
- scripts/legal/legal-sanity-scan.sh: 1
- scripts/review/cross-review.sh: 1
- scripts/review/submit-to-claude.sh: 1
- scripts/review/submit-to-codex.sh: 1
- scripts/review/submit-to-gemini.sh: 1
- scripts/work-queue/log-gate-event.sh: 1
- scripts/work-queue/set-active-wrk.sh: 1
- scripts/work-queue/verify-gate-evidence.py: 1
- scripts/workflow/refresh-orchestrator-timeline.sh: 1

## Skills used (strict)
- work: 1

## Tools used (strict)
- Bash: 547
- Read: 179
- Edit: 116
- Write: 104
- TaskUpdate: 12
- Glob: 8
- ToolSearch: 8
- TaskCreate: 6
- AskUserQuestion: 6
- TaskOutput: 6
- unknown: 2
- mcp__claude-in-chrome__tabs_context_mcp: 2
- mcp__claude-in-chrome__navigate: 2
- mcp__claude-in-chrome__read_page: 1
