# Deckhand Zoom-Out Review

Read-only review. I did not edit files or run tests. Prior `scripts/review/results/2026-06-01-deckhand-zoomout-codex.md` is empty, so this is not just a delta against that artifact.

## 1. Module / Caller Map

| Module | Domain role in glossary vocabulary | Who calls it / should call it |
|---|---|---|
| `src/deckhand/engine.py` | Pure **scope** decision engine: resolves operator, scope, permission level, repo allowlist, destructive operation, sensitivity/clearance visibility, and produces audit payload. | Called by `runtime.handle()` and `hook.inspect()`; should become the only policy decision core. Evidence: `decide()` at `src/deckhand/engine.py:17`, scope resolution at `:106`, audit payload at `:151`. |
| `src/deckhand/hook.py` | **Command-layer enforcement** for git/gh/hub: classifies read/write/destructive shell intent before execution. It is not an audit or runtime seam by itself. | Called by `pipeline.evaluate()` today; intended future caller is Hermes `pre_tool_call`, `execute_code` gate, and PATH shim. Evidence: `inspect()` at `src/deckhand/hook.py:92`, generic destructive deny at `:104`, Python source scan at `:128`. |
| `src/deckhand/runtime.py` | Stateful request lifecycle: engine decision, rate limits, PENDING/FINAL audit, executor call. This is closest to the real **operator → scope → action → audit** seam. | Called by `pipeline.evaluate()`; should be called by every live Deckhand gateway/executor path. Evidence: `handle()` at `src/deckhand/runtime.py:21`, PENDING before executor at `:58`, FINAL after executor at `:81`. |
| `src/deckhand/audit.py` | Append-only raw audit and redacted summary for allow/deny decisions across operators/scopes/sensitivity. | Called by `runtime.handle()` and `pipeline.evaluate()` fallback for hook denies. Evidence: append at `src/deckhand/audit.py:15`, redacted summary at `:37`. |
| `src/deckhand/pipeline.py` | Dry-run composition harness: hook → runtime → audit using a safe executor. This is a test/demo pipeline, not the production gateway. | Called by tests/manual evaluation. Evidence: `evaluate()` at `src/deckhand/pipeline.py:18`, default `dry_run_executor` at `:76`. |
| `config/deckhand/policy.yml` | Global policy: destructive taxonomy, audit, enforcement layers, kill switches, rate limits, elevation. | Loaded by engine/runtime/pipeline; should be loaded once through a shared config object. Evidence: destructive ops at `config/deckhand/policy.yml:17`, enforcement layers at `:75`. |
| `config/deckhand/scopes.yml` | Tenant/scope config: repositories, sensitivity, permission level, PAT env reference, operators, channel bindings. | Loaded by policy engine; should eventually be backed by registry validation and effective-permission attestation. Evidence: `acma` at `config/deckhand/scopes.yml:17`, `doris` at `:34`, `ecosystem` glob at `:49`. |

## 2. Top Architectural Improvements

1. **Make `runtime.handle()` the single enforcement and audit seam.**

   Today `runtime` audits engine decisions, and `pipeline` audits hook-only denies, but `hook.inspect()` itself can deny with `decisions: []` and no audit side effect (`src/deckhand/hook.py:97`, `:104`). If Hermes wires `pre_tool_call` directly to `hook.inspect()`, denials can be correct but unaudited. Production should expose one entry point: `DeckhandGateway.authorize_and_execute(manifest)`, internally running hook classification, engine decision, rate limit, audit PENDING/FINAL, and executor. Risk if not done: bypass paths become a matrix of “some audited, some not,” which breaks the stated every allow/deny audit contract in `docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md:17`.

2. **Centralize config loading into a typed, versioned `DeckhandConfig`.**

   Config loading is duplicated in `engine._load_config()` (`src/deckhand/engine.py:87`), `runtime._load_config()` (`src/deckhand/runtime.py:166`), and `pipeline.load_config()` (`src/deckhand/pipeline.py:91`). This invites inconsistent fail-closed behavior, missing env expansion, missing schema validation, and stale policy snapshots. The shared object should validate schema versions, resolve `${...}` audit paths, snapshot `owner:*/*` globs, canonicalize repos, build operator registry views, and expose a config version/hash for audit. Risk if not done: two modules can make different decisions from the same YAML shape.

3. **Unify the destructive taxonomy.**

   `policy.yml` names specific destructive ops (`repo_delete`, `branch_delete`, `force_push`, etc.) at `config/deckhand/policy.yml:17`, while `hook.py` also has a generic hard-deny class named `"destructive"` (`src/deckhand/hook.py:35`, `:260`, `:288`). That split is pragmatic for shell hardening, but architecturally it creates two policy systems: engine-policy destructive ops and hook-owned generic destructive ops. Make the taxonomy explicit in config: named irreversible operations, generic high-risk command families, and code-owned parser sentinel categories. Risk if not done: future reviewers will add a new `gh`/`git` destructive surface in the hook without policy visibility, audit reporting, or elevation semantics.

4. **Prove live runtime integration, not just pure-core correctness.**

   The plan names seven bypass paths not contained by the hook: `execute_code`, MCP stdio tools, direct webhook `gh`, checkpoint git, CLI destructive git, internal probes, release script (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md:158`). Current tests exercise the dry-run pipeline (`tests/deckhand/test_pipeline.py:70`) and shell classifier hardening, but not Hermes gateway wiring, PATH shim installation, scoped PAT usage, or the seven bypass paths as live integration tests. Risk if not done: the hook can be excellent and still moot.

5. **Replace per-scope operator string lists with a cross-platform person registry.**

   `scopes.yml` has `operators: []` per scope (`config/deckhand/scopes.yml:24`, `:43`, `:54`), while `policy.yml` only says stable platform IDs are required (`config/deckhand/policy.yml:47`). That does not model a person with multiple platform identities, revocation, internal/external status, clearance, tenant memberships, MFA/paired-device state, or audit-friendly display metadata. Build `operators.yml` as person registry: `person_id`, platform identities, tenant memberships, internal/external, clearances, disabled flag, elevation eligibility. Risk if not done: one human becomes N unrelated strings, offboarding misses one platform, and “internal operator” remains incorrectly proxied through elevation approvers (`src/deckhand/engine.py:234`).

6. **Make dry-run/live an explicit policy mode, not a code-path default.**

   `pipeline.evaluate()` defaults to `dry_run_executor` (`src/deckhand/pipeline.py:55`), and tests assert `dry_run` output (`tests/deckhand/test_pipeline.py:83`). That is good for safety, but production needs a config-controlled execution mode with fail-closed startup: `mode: dry_run | live`, permitted scopes, required PAT attestations, and audit label. Risk if not done: a caller can switch behavior by passing an executor, outside policy review.

7. **Add compensating control for private-repo branch-protection limits.**

   The plan’s guardrail floor assumes “PR-only; no direct/protected branch pushes” (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md:141`). If private-repo branch protection is unavailable or not reliable under the active GitHub plan, architecture must compensate below the model: fine-grained PATs must not have permission to push default branches, all writes must use ephemeral non-default branches, PR creation only, CI/status checks as merge gate where available, and a server-side canary that attempts direct default-branch push with the Deckhand token and expects failure. Risk if not done: “PR-only” is an intention in local code, not an enforceable boundary.

8. **Resolve the glossary/plan inconsistency on origin visibility.**

   `CONTEXT.md` says “the origin chat is always allowed” for sensitivity/clearance (`CONTEXT.md:47`), but the plan later fixes that as unsafe and allows full detail only in DMs or cleared channels (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md:128`). The code follows the safer direction for private scopes (`src/deckhand/engine.py:239`). Risk if not fixed: future routing/fanout work may reintroduce the shared-group leak because the glossary still encodes the older rule.

9. **Treat `owner:vamseeachanta/*` as a dangerous unresolved scope, not an allowlist.**

   `ecosystem.repositories` is a glob with a comment “snapshot-audited glob” (`config/deckhand/scopes.yml:53`), but `_repo_in_scope()` simply accepts any `vamseeachanta/…` string prefix (`src/deckhand/engine.py:194`). That is not a snapshot, not audited, and not bounded against new repos appearing later. Risk if not done: `ecosystem` silently expands over time without explicit authorization.

## 3. Missing Entirely for Safe Multi-Tenant / Industry-Grade Use

- **Threat model and trust boundaries:** explicit attacker model for malicious operator, compromised platform account, prompt injection from repo content, malicious PR diff, compromised PAT, and direct GitHub API bypass.
- **Tenant isolation contract:** per-tenant worktrees, per-tenant temp dirs, per-tenant audit/log sinks, no shared cwd assumptions, no shared rate-store dict in multi-worker mode.
- **Credential lifecycle:** token creation, scoped permission attestation, rotation, revocation, secret storage, least-privilege proof, and break-glass disable.
- **Effective-permission tests:** live checks that the active token cannot delete repo, force-push, mutate protected/default branch, access another tenant repo, or call forbidden GitHub API endpoints.
- **Policy schema and migration:** JSON Schema or Pydantic-style validation for `policy.yml`, `scopes.yml`, `platforms.yml`; unknown-key handling; version migrations; config hash in every audit record.
- **Immutable execution manifest:** the plan names this (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md:131`), but code does not yet model it. Every command should carry operator id, scope id/version, repo node id, worktree path, token id, action class, dry-run/live mode, and request id.
- **Durable idempotency/outbox:** fanout and operator replies need request IDs, delivery IDs, retry policy, duplicate suppression across restarts, and per-channel result records.
- **Approval/elevation workflow:** current `_valid_elevation()` only checks membership (`src/deckhand/engine.py:225`). Missing TTL enforcement, evidence capture, two-person rule for risky edits, approver cannot approve own request, and audit linkage.
- **Diff-risk implementation:** policy declares protected paths and mass deletion (`config/deckhand/policy.yml:30`), but the engine consumes precomputed booleans/counts (`src/deckhand/engine.py:211`). Missing actual diff parser, rename/binary/submodule handling, generated-file treatment, and PR preflight.
- **Observability and incident response:** metrics, alerts, audit integrity checks, canary schedule, failed audit-write behavior, emergency kill-switch drills, and incident runbook.
- **Data governance:** raw client data roots are in `scopes.yml` (`config/deckhand/scopes.yml:25`, `:44`) but there is no data classification, retention, backup, legal hold, export controls, or “what can be sent to which model/platform” policy.
- **Gateway identity hardening:** platform allowlists are necessary but insufficient. Need account linking, device/session state, revocation propagation, group membership drift detection, and platform-specific spoofing controls.
- **Deployment model:** no service topology: single process vs workers, where PATH shim lives, how Hermes loads hook, how config reloads, how rollback works, and what startup checks block live mode.
- **Formal tenant onboarding/offboarding:** add scope, provision PAT, register operators, verify channel bindings, run canary, document evidence; reverse process for offboarding.
- **Supply-chain / plugin control:** MCP stdio and plugin surfaces are listed as bypass paths, but there is no allowlist of tools/plugins that may execute under Deckhand or policy for unknown tools.

Bottom line: the pure core is directionally solid for a POC, especially after hook hardening. The highest leverage next move is not more classifier work; it is turning the current pieces into one audited live enforcement gateway, with typed config and live bypass proofs.
