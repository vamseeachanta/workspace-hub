# WRK-1389 AC Test Matrix

| AC | Test | Result | Evidence |
|----|------|--------|----------|
| All 11 discrepancies categorized with disposition | Count D1-D11 in disposition table | PASS | 11/11 have fix/no-fix/already-fixed decision |
| Fix items captured as new WRKs or appended to existing | Check each "fix" item has WRK reference | PASS | D2-D4,D6-D7: update-github-issue.py/exit_stage.py; D1: new WRK; D8: WRK-1161; D10-D11: runner/wait-for-approval |
| GitHub issue updated with final disposition table | Verify issue #1245 body | PASS | Disposition table present in collapsible section |
