# WRK-1058 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| --docs flag runs ruff D rules | T9, T13, smoke (3181–33692 issues per repo) | PASS |
| README section check (missing sections) | T10, T11, T14 | PASS |
| docs/ presence reported as warning | T12, smoke (docs-dir: PASS all repos) | PASS |
| Output integrated into check-all.sh report | T9, smoke output | PASS |
| --docs additive with --ruff-only | T3+docs combined smoke | PASS |
| --docs additive with --mypy-only | T4+docs combined | PASS |
| Docs checks never raise exit code | T11, T13 (exit 0); smoke exit driven by ruff/mypy | PASS |
| Codex cross-review passes | Stage 13 | PENDING |
