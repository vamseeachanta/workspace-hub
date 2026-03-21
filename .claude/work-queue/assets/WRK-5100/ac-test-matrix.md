# AC Test Matrix — WRK-5100

| AC | Description | Test | Result |
|----|-------------|------|--------|
| 1 | No lifecycle.html in stage micro-skills | `grep -r 'lifecycle\.html' .claude/skills/workspace-hub/stages/` | PASS |
| 2 | No lifecycle.html in stage YAMLs | `grep -r 'lifecycle\.html' scripts/work-queue/stages/` | PASS |
| 3 | No html_verification_ref in archive template | `grep 'html_verification_ref' scripts/work-queue/templates/archive-tooling-template.yaml` | PASS |
| 4 | No html_verification_ref in validate-queue-state | `grep 'html_verification_ref' scripts/work-queue/validate-queue-state.sh` | PASS |
| 5 | update-github-issue.py renders scope sections | `--dry-run | grep -c '###'` returns ≥2 | PASS (9) |
| 6 | Stage 11 describes evidence audit | No reference to generate-html-review.py | PASS |
| 7 | Ecosystem terminology updated | Lifecycle HTML marked deprecated | PASS |
