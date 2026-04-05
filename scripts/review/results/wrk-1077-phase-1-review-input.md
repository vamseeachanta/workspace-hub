# WRK-1077 Cross-Review Input — Phase 1

## Item
WRK-1077: acma-ansys05 workstation readiness setup

## Route
A (simple) — manual execution runbook, no code changes

## Plan (inline in WRK file)
1. `git pull` on acma-ansys05 to get latest repo
2. `bash scripts/setup/install-all-hooks.sh` — installs pre-commit/post-merge/post-rewrite
3. Append `source /c/workspace-hub/config/shell/bashrc-snippets.sh` to `~/.bash_profile`
4. `claude config set statusBarEnabled true`
5. `cp config/claude/keybindings.json ~/.claude/keybindings.json`
6. `bash scripts/setup/verify-setup.sh` — target 0 FAIL
7. `bash scripts/operations/system/dev-env-check.sh` — confirm manifest loads

## Risks
- Step 3: on Windows Git Bash, RC file is `~/.bash_profile` NOT `~/.bashrc` — verify-setup.sh auto-detects this correctly
- Step 6: cron/SSH WARNs are expected and acceptable per ACs

## Artifacts checked
- `specs/modules/hardware-inventory/manifests/acma-ansys05.yml` — EXISTS
- `scripts/setup/install-all-hooks.sh` — EXISTS, idempotent
- `config/shell/bashrc-snippets.sh` — EXISTS
- `config/claude/keybindings.json` — EXISTS

## Verdict request
Does this plan correctly address all ACs? Any gaps or risks?
