# Deckhand File Inventory

Generated from `rg --files | rg -i 'deckhand' | sort` on branch `docs/deckhand-knowledge-map-2944`. Repo column is `workspace-hub` for every tracked file listed.

## Plugin

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py` | Live Hermes plugin registering `/scope`, `/whoami`, and `pre_tool_call` enforcement. | workspace-hub | plugin / scope authorization / hook / audit / rate-limit |
| `scripts/deckhand/hermes-plugin/deckhand-scope/plugin.yaml` | Hermes plugin manifest naming the Deckhand scope plugin entrypoint. | workspace-hub | plugin |

## Shims

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `scripts/deckhand/shims/git` | PATH wrapper for `git`; resolves active scope and injects scoped PAT via `GIT_ASKPASS`. | workspace-hub | scoped PAT boundary |
| `scripts/deckhand/shims/gh` | PATH wrapper for `gh`; resolves active scope and exports scoped `GH_TOKEN`/`GITHUB_TOKEN`. | workspace-hub | scoped PAT boundary |
| `scripts/deckhand/shims/hub` | PATH wrapper for `hub`; resolves active scope and exports scoped `GH_TOKEN`/`GITHUB_TOKEN`. | workspace-hub | scoped PAT boundary |

## Source

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `src/deckhand/__init__.py` | Package export for the pure decision engine. | workspace-hub | source |
| `src/deckhand/audit.py` | Append-only raw audit writer and redacted summary HTML helpers. | workspace-hub | audit |
| `src/deckhand/engine.py` | Config-driven authorization engine for scopes, operators, repos, destructive ops, risk gates, and reply visibility. | workspace-hub | scope authorization / no-destructive |
| `src/deckhand/hook.py` | Shell/Python command classifier and pre-engine git/gh/hub guard. | workspace-hub | hook / no-destructive |
| `src/deckhand/pipeline.py` | End-to-end dry-run evaluator wiring hook, runtime, executor, rate store, and audit. | workspace-hub | pipeline |
| `src/deckhand/ratelimit.py` | File-backed live write limiter with operator, scope, and duplicate request caps. | workspace-hub | rate-limit |
| `src/deckhand/runtime.py` | Stateful authorize-rate-limit-execute-audit orchestration with PENDING/FINAL audit records. | workspace-hub | runtime / audit / rate-limit |
| `src/deckhand/shim_resolve.py` | Resolves active scope to a `pat_env` name for shims from Hermes session env and scope config. | workspace-hub | scoped PAT boundary / scope resolution |

## Config

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `config/deckhand/README.md` | Explains the Deckhand config surface and no-secrets/fail-closed rules. | workspace-hub | docs / config |
| `config/deckhand/platforms.yml` | Platform enablement and credential env-var references for Telegram, WhatsApp, Teams, Signal, and fanout. | workspace-hub | config / platform |
| `config/deckhand/policy.yml` | Global enforcement policy: fail-closed, destructive denylist, audit sinks, enforcement switches, rate limits, elevation. | workspace-hub | config / policy |
| `config/deckhand/scopes.yml` | Per-scope repositories, operators, `pat_env`, bindings, group authorization, and origin-bound default. | workspace-hub | config / scopes |

## Patches

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `patches/hermes/01-path-shim-prepend.patch` | Local Hermes patch to prepend the Deckhand shim directory to tool PATH. | workspace-hub | Hermes core patch / shim routing |
| `patches/hermes/02-scope-command-session-env.patch` | Local Hermes patch to expose session env to plugin slash commands. | workspace-hub | Hermes core patch / identity |

## Scripts

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `scripts/deckhand/README.md` | Setup-script overview and PAT provisioning notes. | workspace-hub | docs / scripts |
| `scripts/deckhand/add-member.sh` | Adds Telegram/WhatsApp member IDs to closed-gateway allowlists and optional scope operators. | workspace-hub | gateway allowlist / onboarding |
| `scripts/deckhand/install-hermes-b2.sh` | Dry-run/apply installer for B2 shims and Hermes local patches. | workspace-hub | install / Hermes patch |
| `scripts/deckhand/protect-and-verify.sh` | Repo ruleset, PAT scope verification, and destructive-event alarm deployment tool. | workspace-hub | no-destructive / scoped PAT verification |
| `scripts/deckhand/templates/deckhand-destructive-alarm.yml` | GitHub Actions workflow template that opens an issue on delete or force-push events. | workspace-hub | detective control |
| `scripts/deckhand/verify-hermes-b2.sh` | Verifies shim install, PATH resolution, resolver output, and ambient token absence. | workspace-hub | install verification |

## Tests

10 test files under `tests/deckhand/`; `tests/deckhand/__pycache__/` exists locally but is not a source file.

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `tests/deckhand/test_add_member.sh` | Tests member ID validation, allowlist edits, WhatsApp/Telegram welcome routing, and external-scope guardrails. | workspace-hub | tests / onboarding |
| `tests/deckhand/test_audit.py` | Tests raw audit append, PENDING/FINAL IDs, sensitive raw preservation, redacted summaries, and HTML rendering. | workspace-hub | tests / audit |
| `tests/deckhand/test_hermes_plugin.py` | Tests plugin loading, `/scope`, `/whoami`, scope state, terminal hook decisions, group authorization, and rate-limit wiring. | workspace-hub | tests / plugin |
| `tests/deckhand/test_hook.py` | Tests git/gh/hub command classification, destructive denial, suspicious shell fail-closed behavior, and Python re-entry scanning. | workspace-hub | tests / hook |
| `tests/deckhand/test_pipeline.py` | Tests dry-run evaluation across hook, runtime, real config loading, audit, and denied suspicious commands. | workspace-hub | tests / pipeline |
| `tests/deckhand/test_ratelimit.py` | Tests per-operator caps, per-scope caps, duplicate suppression, window expiry, and store-error fail-closed behavior. | workspace-hub | tests / rate-limit |
| `tests/deckhand/test_runtime.py` | Tests runtime executor calls, deny-without-execute, PENDING/FINAL audit, redaction, rate denial, and executor failure audit. | workspace-hub | tests / runtime |
| `tests/deckhand/test_scope_decision_engine.py` | Tests pure decision engine for scope auth, repo allowlists, read-only repos, external-disabled scope, origin default, risk gates, and kill switches. | workspace-hub | tests / engine |
| `tests/deckhand/test_shim_pat_read.sh` | Tests live shim `read_pat_value`: secrets-file precedence, `.env` fallback, quoted values, invalid key rejection, and missing-key fail-closed behavior. | workspace-hub | tests / shims |
| `tests/deckhand/test_shim_resolve.py` | Tests active-scope and channel-binding `pat_env` resolution, missing identity, CLI exit behavior, and Route B group binding. | workspace-hub | tests / shim resolver |

## Docs

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `docs/deckhand/ARCHITECTURE.md` | Architecture map for enforcement layers, plugin flow, shims, config, runtime state, and platform status. | workspace-hub | docs / architecture |
| `docs/deckhand/DEPLOYMENT.md` | From-scratch deployment/operator guide for new scopes or machines. | workspace-hub | docs / deployment |
| `docs/deckhand/FILE-INVENTORY.md` | Exhaustive Deckhand file inventory grouped by area. | workspace-hub | docs / inventory |
| `docs/deckhand/ISSUE-AND-DECISION-MAP.md` | Cross-map of Deckhand issues and decisions, owned by another documentation lane. | workspace-hub | docs / map |
| `docs/deckhand/ONBOARDING.md` | Living member onboarding guide for Telegram, WhatsApp, Signal stub, and Teams stub. | workspace-hub | docs / onboarding |
| `docs/deckhand/REPO-DOMAIN-MAP.md` | Repo/domain knowledge map, owned by another documentation lane. | workspace-hub | docs / map |
| `docs/reports/deckhand-dashboard.html` | HTML dashboard tracking Deckhand work status, decisions, reviews, and board state. | workspace-hub | docs / report |
| `docs/session-handoffs/2026-06-01-deckhand-chatbot-board-exit-handoff.md` | Session handoff preserving board state, issue status, live conclusions, and next checkpoint. | workspace-hub | docs / handoff |

## Governance

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md` | Decision record establishing enforcement below the model with command hooks, scoped PATs, and audit. | workspace-hub | governance |
| `docs/governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md` | Decision record separating scope from routing and coupling only through sensitivity clearance. | workspace-hub | governance |
| `docs/governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md` | Strategy note for Telegram-led GTM and demand-driven WhatsApp/Teams rollout. | workspace-hub | governance / GTM |

## GTM

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `docs/gtm/deckhand-teams-enterprise-connectivity.html` | Client-facing Teams connectivity/GTM draft explaining security posture and rollout decisions. | workspace-hub | GTM / Teams |

## Plans

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `docs/plans/2026-05-31-issue-2900-deckhand-board-level-plan.md` | Board-level Deckhand multi-platform fanout planning artifact for [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900). | workspace-hub | plan |
| `docs/plans/2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md` | Preliminary plan for Deckhand multi-platform fanout under [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900). | workspace-hub | plan |
| `docs/plans/2026-06-01-deckhand-delegation-plan.md` | Deckhand delegation plan artifact. | workspace-hub | plan |
| `docs/plans/2026-06-01-deckhand-improvement-roadmap.md` | Deckhand improvement roadmap artifact. | workspace-hub | plan |
| `docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md` | Message-lifecycle POC plan for [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931). | workspace-hub | plan |
| `docs/plans/2026-06-01-issue-2941-deckhand-teams-connect.md` | Teams connection plan for [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941). | workspace-hub | plan / Teams |

## Review Results

| path | one-line purpose | repo | layer |
|---|---|---|---|
| `scripts/review/results/2026-06-01-deckhand-audit-code-review.md` | Review result for Deckhand audit code. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-b2-plan-codex.md` | Codex review result for the B2 shim/core-patch plan. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-delegation-codex.md` | Codex review result for Deckhand delegation. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-engine-code-review.md` | Review result for Deckhand engine code. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-hook-adversarial-codex.md` | Adversarial Codex review result for hook hardening. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-hook-hardening-verification.md` | Verification artifact for Deckhand hook hardening. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-onboarding-plan-codex.md` | Codex review result for Deckhand onboarding plan. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-pipeline-code-review.md` | Review result for Deckhand pipeline code. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-platform-connectivity-and-terminology-codex.md` | Codex review/recon result for platform connectivity and terminology. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-runtime-code-review.md` | Review result for Deckhand runtime code. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-whatsapp-identity-recon.md` | Recon artifact for WhatsApp identity and operating risk. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-wiring-recon-codex.md` | Codex recon artifact for Deckhand wiring. | workspace-hub | review-results |
| `scripts/review/results/2026-06-01-deckhand-zoomout-codex.md` | Codex zoom-out review result for Deckhand architecture/work direction. | workspace-hub | review-results |

## Runtime/Host Artifacts (Not In Repo)

These are live on `ace-linux-2` and must not be committed:

```text
~/.hermes/.env
~/.hermes/deckhand/secrets.env
~/.hermes/deckhand/shims/{git,gh,hub}
~/.hermes/plugins/deckhand-scope
~/.hermes/whatsapp/session
~/.hermes/deckhand/active-scope/<platform>/<chat>/<operator>.json
~/.hermes/deckhand/ratelimit/
${DECKHAND_AUDIT_DIR:-/mnt/dde/deckhand/audit}/decisions.ndjson  # abs-path-allowed
```
