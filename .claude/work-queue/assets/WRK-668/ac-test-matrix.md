# WRK-668 Acceptance Criteria Test Matrix

| AC | Test | Result |
|----|------|--------|
| Archive-tooling requirement matrix defined | archive-tooling-template.yaml with required/optional fields | PASS |
| Machine-checkable archive evidence schema | gate_checks_archive.py validates all schema fields | PASS |
| Validator enforcement for archive-tooling readiness | --phase archive in verify-gate-evidence.py | PASS |
| Spin-off rule: auto-create pending WRK for hard blockers | create-spinoff-wrk.sh scaffolds WRK-NNN.md with context | PASS |
| HTML Archive Readiness section with gate status indicators | _build_archive_readiness_card() in generate-html-review.py | PASS |
| 3 realistic test scenarios: pass, soft, hard | T1 pass, T2 soft-workaround, T3 hard-spinoff | PASS |
