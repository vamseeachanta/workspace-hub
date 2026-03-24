# WRK-687 Test Results

## test_wrk687_lifecycle.sh (dev-primary, 2026-03-03)

```
[WRK-687 lifecycle] Machine: dev-primary
  Stage A — log write + verify:       PASS
  Stage B — session-analysis dry run: PASS
  Stage C — commit step:              PASS
  Stage D — compilation:              PASS
OVERALL: PASS
```

## verify-log-presence.sh (dev-primary, 2026-03-03)

```
[verify-log-presence] Machine: dev-primary
  claude  OK  (2 file(s), latest: session_20260303.jsonl, valid JSON: 57/57)
  codex   OK  (native: 302 session(s), latest: rollout-2026-03-02T13-53-22-....jsonl; orchestrator: 0 cross-review(s))
  gemini  OK  (native: 772 session(s), latest: session-2026-03-03T05-38-68f52be5.json; orchestrator: 0 cross-review(s))
PASS
```

## dev-secondary (WAIVED)

dev-secondary mounts `/mnt/workspace-hub` via SSHFS from dev-primary
(`vamsee@dev-primary:/mnt/local-analysis/workspace-hub`). Same physical
storage — separate machine run adds no additional coverage.

## licensed-win-1

Pending Git Bash run. Post-close evidence to be added when available.
