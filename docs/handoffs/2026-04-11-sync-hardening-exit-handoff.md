# Sync Hardening Exit Handoff — 2026-04-11

## Completed this session

### Core hardening work
- Hardened `scripts/_core/sync-agent-configs.sh` across Codex, JSON, and Hermes helper paths.
- Fixed recurring Codex TOML corruption caused by root keys (`model`, `model_reasoning_effort`) leaking into non-root TOML tables such as `[features]`.
- Replaced fragile line-based TOML handling with Python-assisted sanitation/validation for the Codex path.
- Added broader helper hardening for:
  - JSON validation before install
  - Hermes YAML validation before install
  - literal-safe Hermes `__WS_HUB_PATH__` rendering
  - temp-file + rename write pattern in more paths
  - cleanup on failure
  - fallback from broken `python3` to `uv`
  - preservation of machine-local Hermes overrides for `terminal.backend` and `terminal.cwd`
- Fixed the last concrete leak found in final adversarial review: JSON update-path temp-file cleanup on `jq` failure.

### Tests added / expanded
- `scripts/_core/tests/test_sync_agent_configs.sh`
  - Codex TOML root-scope enforcement
  - multiline-string preservation
  - inline-table sanitization
  - commented `[status_line]` replacement
  - dry-run no-side-effects
  - invalid-template atomic failure behavior
- `scripts/_core/tests/test_sync_agent_helpers.sh`
  - Hermes placeholder rendering with `&` in workspace path
  - Hermes terminal override preservation
  - invalid JSON create-path failure
  - invalid JSON create-path failure without `jq`
  - invalid YAML create-path failure
  - invalid JSON update-path cleanup/preservation
  - fallback from broken `python3` to `uv`

## Verification completed
- `bash scripts/_core/tests/test_sync_agent_configs.sh`
  - result: `21 PASS, 0 FAIL`
- `bash scripts/_core/tests/test_sync_agent_helpers.sh`
  - result: `13 PASS, 0 FAIL`
- `bash scripts/_core/sync-agent-configs.sh`
  - result: success
- `codex --version`
  - result: `codex-cli 0.120.0`

## Future issues created
- #2210 — `chore(harness): add ws_hub fallback regression coverage for sync-agent-configs`
- #2211 — `chore(harness): add dry-run existing-target regression coverage for sync helpers`
- #2212 — `chore(harness): add invalid-update atomicity regression coverage for sync helpers`

## Current changed files of interest
- `scripts/_core/sync-agent-configs.sh` — modified, not committed
- `scripts/_core/tests/test_sync_agent_helpers.sh` — new, not committed
- `scripts/_core/tests/test_sync_agent_configs.sh` — touched earlier in session as part of Codex hardening/verification
- `docs/handoffs/2026-04-11-sync-hardening-exit-handoff.md` — this handoff

## Notes
- Final Claude adversarial review completed after broader helper hardening.
- Final Claude finding (JSON merge-path temp leak) was fixed and regression-tested.
- Remaining items are future coverage improvements, not active known defects in the hardened path.
- There are unrelated local repo changes outside this sync-hardening scope; do not assume a globally clean working tree.

## Suggested next session start
1. Review newly created follow-up issues #2210, #2211, and #2212.
2. Decide whether to commit the sync-hardening diff as one changeset or split into Codex-vs-helper commits.
3. Run `git diff --check` / prepare commit message and push if desired.
