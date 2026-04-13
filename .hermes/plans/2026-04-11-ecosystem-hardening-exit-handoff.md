# Ecosystem hardening exit handoff

Date: 2026-04-11
Repo: /mnt/workspace-hub
Branch: main

## Completed local commits

- 6d5a711f — chore: harden provider health and ecosystem tooling
- 867acc3c — chore: clean codex plugin cache warnings

## Push state

Push to origin/main is currently blocked because local main is behind origin/main.

Last observed state:
- local branch ahead of origin/main by local commits
- remote rejected push with non-fast-forward / fetch-first requirement

## Current provider health

- overall_status: warn
- overall_routing_state: fallback_only

### Claude
- status: warn
- routing_state: fallback_only
- reason: recovered auth drift remains in recent history
- manual recovery if it fails again:
  - run `claude login` in a plain terminal
  - start and exit one clean `claude` session
  - rerun `bash scripts/maintenance/ai-tools-status.sh`

### Codex
- status: ok
- routing_state: eligible
- cleanup completed:
  - archived skills moved out of live root
  - local plugin cache overlong `defaultPrompt` values trimmed

### Gemini
- status: ok
- routing_state: eligible
- cleanup completed:
  - stale temp workspace roots pruned
  - health scoring refined to ignore old residual noise

## Future GitHub issues created

- #2222 — Follow up Claude auth drift hardening with stronger observability, recovery signals, and operator playbook
- #2223 — Plan and execute safe origin/main integration for blocked workspace-hub push while preserving hardening changes
- #2224 — Codex: reduce stale warning churn in provider-health after live cleanup

## Recommended next operator action

1. Sync local main with origin/main safely (issue #2223)
2. Preserve/replay commits 6d5a711f and 867acc3c during sync
3. Push merged/rebased result to origin/main
4. Continue Claude auth observability follow-up under issue #2222

## Files central to the hardening work

- scripts/maintenance/ai-tools-status.sh
- scripts/maintenance/provider-health-check.py
- scripts/maintenance/prune-gemini-tmp.py
- scripts/maintenance/cleanup-codex-plugin-cache.py
- scripts/productivity/sections/ai-usage-summary.sh
- config/ai_agents/provider-health.yaml
- config/ai_agents/ai-tools-status.yaml

## Notes

- A large structural change moved archived skills out of `.claude/skills/_archive` into `.claude/skills-archive` to reduce Codex scan pressure.
- Git push was intentionally not forced.
- Repo should not be considered remotely landed until sync/rebase and push are completed.
