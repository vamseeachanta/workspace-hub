---
name: work-queue-stage-contracts-summary
description: 'Sub-skill of work-queue: Stage Contracts (summary).'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Stage Contracts (summary)

## Stage Contracts (summary)


| Stage | Key exit artifact(s) | Gate |
|-------|----------------------|------|
| 1 | `evidence/user-review-capture.yaml` (`scope_approved: true`) | HARD |
| 2 | `evidence/resource-intelligence.yaml` | — |
| 3 | WRK frontmatter triage fields | — |
| 4a | `EnterPlanMode` + explicit coverage instruction → text draft → `ExitPlanMode` | — |
| 4b | Draft plan spec + self-verification pass + HTML artifact | — |
| 5 | `evidence/user-review-plan-draft.yaml`; HTML opened in browser | **HARD — user must respond** |
| 6 | Multi-provider review outputs (`cross-review-*.md`) | — |
| 7 | `evidence/plan-final-review.yaml` (`confirmed_by` human) | **HARD — R-25** |
| 8 | `claim-evidence.yaml` + `activation.yaml` | HARD — R-26 |
| 9 | Routing log | — |
| 10 | Execution commits; `execute.yaml` | — |
| 11 | Lifecycle HTML | — |
| 12 | `ac-test-matrix.md` (≥3 PASS, 0 FAIL) | — |
| 13 | Cross-review finding closure notes | — |
| 14 | `gate-evidence-summary.{md,json}` (PASS) | — |
| 15 | `future-work.yaml` | — |
| 16 | `resource-intelligence-update.yaml` | — |
| 17 | `evidence/user-review-close.yaml` (`reviewer` human) | **HARD — R-27** |
| 18 | `reclaim.yaml` (if continuity broke) | — |
| 19 | `scripts/work-queue/close-item.sh WRK-NNN <hash>` | — |
| 20 | `scripts/work-queue/archive-item.sh WRK-NNN` | — |

Stage 5 exit (ALL required before Stage 6): HTML opened (`xdg-open`) + pushed; section walk-through done; user explicitly responded; `user-review-plan-draft.yaml` written; plan artifacts updated.
Stage 7 exit (ALL required before Stage 8): HTML opened + pushed; `plan-final-review.yaml` written; `confirmed_by` in allowlist; `claim-item.sh --stage7-check` → PASS.
Stage 17 exit (ALL required before Stage 19): HTML opened + pushed; `user-review-close.yaml` written; `reviewer` in allowlist; `close-item.sh --stage17-check` → PASS.
