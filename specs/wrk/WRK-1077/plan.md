# WRK-1077 Plan — licensed-win-1 workstation readiness setup

## Objective
Get licensed-win-1 to pass workspace-hub readiness checks and participate in the work queue.

## Acceptance Criteria
- verify-setup.sh: 0 FAIL, minimal WARN
- dev-env-check.sh: OGManufacturing repo OK; ANSYS detected
- All git hooks installed and current
- Claude/Codex/Gemini CLIs functional

## 7-Step Runbook (Route A — execute on licensed-win-1)
1. Run baseline: `PYTHONIOENCODING=utf-8 bash scripts/setup/verify-setup.sh`
2. Fix claim-item.sh re.sub lambda (Windows backslash escape bug)
3. Fix dev-env-check.sh hostname lowercase
4. Fix verify-setup.sh keybindings Python (uv + cygpath)
5. Fix manifest workspace_root (D: path)
6. Fix Python section in verify-setup.sh (uv preference, statusLine check)
7. Add windows_exe_paths probe to dev-env-check.sh for ANSYS

## Final Result
15 PASS, 3 WARN, 0 FAIL. All ACs met.
