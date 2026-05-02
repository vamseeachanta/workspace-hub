# Agent Execution Operations

Repo-owned launch/readiness scripts for multi-machine AI worker orchestration.

## Scripts

- `ace2-readiness.sh` — remote login-shell probe for ace-linux-2 AI/tool/GitHub readiness.
- `launch-2518-finalizer.sh` — launches the #2518 Claude Code finalizer from the repo-owned finalizer prompt.
- `launch-ace1-control-plane.sh` — launches the ace-linux-1 control-plane Claude worker from the repo-owned execution prompt.
- `launch-ace2-overflow-worker.sh` — copies repo-owned prompts to ace-linux-2 and starts the overflow Claude worker in remote tmux.

## Prompt sources

The scripts use prompt artifacts under:

- `docs/plans/machine-prompts/2026-04-27/`
- `docs/plans/machine-prompts/2026-04-27/execution/`

## Safety defaults

- No force-push behavior is encoded.
- Launchers fail if the target tmux session already exists.
- ace-linux-2 is treated as an overflow worker; GitHub mutation remains on ace-linux-1 unless fresh auth is verified.
- Long-running workers log under `/mnt/local-analysis/...` runtime directories; those logs are operational artifacts, not committed repo content.
