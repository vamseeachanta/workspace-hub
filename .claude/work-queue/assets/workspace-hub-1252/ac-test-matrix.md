# WRK-5104 AC Test Matrix

| AC | Description | Test | Result | Evidence |
|----|-------------|------|--------|----------|
| AC-1 | Every stage exit posts completion comment | Exit stage 4 → check issue comments | PASS | Stage 4 DONE comment visible on #1252 |
| AC-2 | Human gate stages post AWAITING APPROVAL | Exit stage 5 → check issue comments | PASS | AWAITING APPROVAL comment posted on #1252 |
| AC-3 | enforce-human-gate.sh reads GitHub comments | Run hook with approval on issue | PASS | Hook exits 0 after finding approval |
| AC-4 | Offline fallback works | SKIP_GATE_GITHUB_CHECK=1 | PASS | Falls through to local evidence check |
| AC-5 | No regression on issue body updates | Run --update after changes | PASS | Issue #1252 body correctly rendered |
| AC-6 | wait-for-approval.sh detects approval | Run against #1252 with existing approval | PASS | Script exits 0 immediately |
| AC-7 | Quoted replies don't match AWAITING | jq startswith filter | PASS | Only "## Stage" prefixed comments match |
| AC-8 | "approve" (not just "approved") matches | User commented "I approve stage 5" | PASS | jq \bapprove pattern matches |
