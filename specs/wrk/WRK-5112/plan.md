# WRK-5112: Redistribute Scripts to Stage Folders

## Mission

Move stage-specific scripts from flat `scripts/work-queue/` into their corresponding `stage-NN-name/scripts/` folder-skill directories. Keep shared/orchestration scripts in place.

## Script Classification

### Stage-Specific Scripts (to move)

| Script | Target Stage | Reason |
|--------|-------------|--------|
| wait-for-approval.sh | stage-01-capture | Stage 1 pre-exit hook |
| create-resource-pack.sh | stage-02-resource-intelligence | Creates resource pack for stage 2 |
| infer-category.py | stage-03-triage | Triage-specific categorization |
| assign-categories.py | stage-03-triage | Category assignment during triage |
| assign-workstations.py | stage-03-triage | Workstation assignment during triage |
| urgency_score.py | stage-03-triage | Priority scoring during triage |
| stage5-plan-dispatch.sh | stage-05-user-review-plan-draft | Stage 5 specific dispatch |
| bootstrap-stage5-gate.sh | stage-05-user-review-plan-draft | Stage 5 gate bootstrap |
| log-user-review-browser-open.sh | stage-05-user-review-plan-draft | Stage 5 user review logging |
| log-user-review-publish.sh | stage-05-user-review-plan-draft | Stage 5 review publish |
| check-p1-resolved.sh | stage-06-cross-review | Cross-review P1 check |
| claim-item.sh | stage-08-claim-activation | Claim/activation logic |
| stage_dispatch.py | stage-09-routing | Routing dispatch |
| feature-status.sh | stage-10-work-execution | Feature child status tracking |
| feature-close-check.sh | stage-10-work-execution | Feature child completion check |
| feature-auto-close.sh | stage-10-work-execution | Feature auto-close when children done |
| check-acs-pass.sh | stage-12-tdd-eval | AC verification for eval stage |
| scan-future-work.py | stage-15-future-work | Future work synthesis |
| close-item.sh | stage-19-close | Close stage logic |
| archive-item.sh | stage-20-archive | Archive stage logic |

### Shared/Orchestration Scripts (keep in place)

| Script | Reason |
|--------|--------|
| dispatch-run.sh | Central dispatcher — calls all stages |
| start_stage.py | Stage start machinery — all stages |
| exit_stage.py | Stage exit machinery — all stages |
| run-plan.sh | Group runner — stages 1-4 |
| run-review-plan.sh | Group runner — stages 5-7 |
| run-execute.sh | Group runner — stages 8-16 |
| run-close.sh | Group runner — stages 17-20 |
| run_hooks.py | Hook runner — all stages |
| run_log.py | Log writer — all stages |
| verify_checklist.py | Checklist verifier — all stages |
| verify-gate-evidence.py | Gate evidence verifier — all stages |
| verify-log-presence.sh | Log presence check — all stages |
| stage_exit_checks.py | Exit validation — all stages |
| gate_check.py | Gate check — all stages |
| gate_checks_extra.py | Extended gate checks — all stages |
| gate_checks_archive.py | Archive gate checks — stages 19-20 |
| update-stage-evidence.py | Stage evidence updater — all stages |
| checkpoint.sh | Checkpoint writer — all stages |
| checkpoint_writer.py | Checkpoint writer — all stages |
| set-active-wrk.sh | Session state — all stages |
| clear-active-wrk.sh | Session state — all stages |
| start-wrk.sh | WRK lifecycle — all stages |
| is-human-gate.sh | Gate config — all stages |
| check-gates-green.sh | Gate check — all stages |
| log-gate-event.sh | Gate logging — all stages |
| print-gate-passed.sh | Gate output — all stages |
| validate-wrk-frontmatter.sh | Validation — all stages |
| whats-next.sh | Queue management utility |
| queue-status.sh | Queue reporting |
| queue-report.sh | Queue reporting |
| next-id.sh | ID generation |
| gh-next-id.sh | GitHub ID generation |
| find-items.sh | Queue search |
| new-feature.sh | Feature WRK creation |
| new-spec.sh | Spec creation |
| create-spinoff-wrk.sh | Spinoff creation |
| wrk-progress.sh | Progress tracking |
| rebuild-wrk-index.sh | Index management |
| update-wrk-index.sh | Index management |
| dep_graph.py | Dependency visualization |
| generate_transition_table.py | Reference generation |
| backfill-categories.py | Maintenance/migration |
| backfill-github-refs.sh | Maintenance/migration |
| backfill-stage-evidence.py | Maintenance/migration |
| migrate-queue.py | Migration utility |
| migrate-stage-rules.py | Migration utility |
| migrate-stage-to-folder.sh | Migration utility |
| validate-folder-skill.sh | Validation utility |
| validate-stage-gate-policy.py | Validation utility |
| promote-local-ids.sh | ID management |
| scan-ghost-pending.sh | Queue cleanup |
| auto-unblock.sh | Queue automation |
| check-claude-md-limits.sh | CLAUDE.md validation |
| audit_micro_skill_scripts.py | Auditing |
| audit-session-signal-coverage.py | Auditing |
| build-session-gate-analysis.py | Analysis |
| remediation-report.py | Reporting |

## Acceptance Criteria

- [ ] AC1: Script-to-stage mapping YAML at `scripts/work-queue/script-stage-mapping.yaml`
- [ ] AC2: 20+ stage-specific scripts moved to `stage-NN-name/scripts/`
- [ ] AC3: Shared scripts remain in `scripts/work-queue/`
- [ ] AC4: Symlinks from old locations to new (backward compat for in-flight WRKs)
- [ ] AC5: `validate-folder-skill.sh` updated to check for scripts/ subdirectory
- [ ] AC6: All existing tests pass

## Scripts to Create

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| redistribute-scripts.sh | Move scripts per mapping YAML | script-stage-mapping.yaml | Moved files + symlinks |

## Test Plan

| What | Type | Expected |
|------|------|----------|
| Scripts accessible at new paths | happy | All moved scripts importable/callable |
| Symlinks point to correct targets | happy | Old paths resolve to new locations |
| dispatch-run.sh still works | happy | Full lifecycle test passes |
| Shared scripts not moved | edge | scripts/work-queue/ still has all shared scripts |
| validate-folder-skill.sh passes all stages | integration | 20/20 PASS |

## Pseudocode

```
1. Parse script-stage-mapping.yaml → dict[script_name, target_stage]
2. For each stage-specific script:
   a. mkdir -p stage-NN-name/scripts/
   b. mv scripts/work-queue/<script> → stage-NN-name/scripts/<script>
   c. ln -s (relative path) scripts/work-queue/<script> → new location (backward compat)
3. Update validate-folder-skill.sh to check scripts/ existence
4. Run validate-folder-skill.sh for all 20 stages
5. Run dispatch-run.sh smoke test
```

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-23T18:25:00Z
decision: passed
