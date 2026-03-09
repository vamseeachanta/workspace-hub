# WRK-1065 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| context-monitor.sh emits log at 70% and 80% thresholds | Test 1 (70%), Test 2 (80%) | PASS |
| Auto-checkpoint fires at 80% for active WRK | Test 2: checkpoint.sh called at 80% | PASS |
| context-warning.yaml written with timestamp and usage level | Test 2: yaml verified | PASS |
| Idempotent — skip if same threshold already triggered | Test 4: duplicate call skipped | PASS |
| No active WRK → logs SKIP, exits 0 | Test 3 | PASS |
| Checkpoint failure non-fatal | Test 5: ERROR logged, exit 0 | PASS |
| Invalid --usage-pct exits 1 | Test 6 | PASS |
| session-chunking.md covers when/how to chunk | Manual: file exists and covers all topics | PASS |
| Stage 10 in work-queue-workflow/SKILL.md notes chunking guidance | Manual: Context Budget block added | PASS |
| Cross-review (Codex) passes | Stage 6: Codex reviewed, P1 addressed | PASS |

All 10 ACs: PASS
Test command: `bash tests/hooks/test-context-monitor.sh`
