# Deckhand improvement roadmap (zoom-out synthesis, 2026-06-01)

> Synthesis of two independent zoom-out reviews — Claude (inline) + codex
> (`scripts/review/results/2026-06-01-deckhand-zoomout-codex.md`). Both converge on one
> theme: **the pure core is solid; the next leverage is turning the pieces into a single
> audited live enforcement gateway with typed config and live bypass proofs — not more
> classifier work.** Host: ace-linux-2. Gate: changes touching the reviewed core are
> planned + reviewed before landing.

## Tier 1 — do before any live external test
1. **Single audited enforcement seam.** One entry point (`DeckhandGateway.authorize_and_execute(manifest)`) that runs hook classify → engine decide → rate-limit → audit PENDING → executor → audit FINAL. The `~/.hermes` shim must call *this*, never `hook.inspect()` raw (raw hook denials are unaudited — breaks the every-decision-audited contract). *(both reviews #1)*
2. **Prove live runtime integration / the 7 bypass paths.** The hook is moot unless the wiring forces *all* git/gh (incl. `execute_code`, MCP, `webhook.py` direct `gh`, checkpoint, `cli.py`, release script) through the seam. Add live integration tests, not just pure-core tests. *(both #4; Claude #1)*
3. **Executor uses the scope PAT, not ambient `gh`.** The box's `gh` is the owner (full access); the executor must run with `GH_TOKEN=<scope PAT>` in a clean credential context, or scoping is bypassed. Add an effective-permission test. *(tracked on `t_3c0e3ddd`)*
4. **Private-repo compensation (stay-Free).** PR-only enforced as a boundary, not an intention: PATs cannot push default branches; all writes via ephemeral non-default branches → PR; **a canary that attempts a direct default-branch push with the Deckhand token and expects failure**; plus the detective alarm (built). *(codex #7; #2741)*

## Tier 2 — foundation hardening
5. **Typed, versioned config loader.** Replace the three duplicated `_load_config()`s (engine/runtime/pipeline) with one validated `DeckhandConfig`: schema + version check, `${...}` expansion, glob snapshot, repo canonicalization, operator-registry views, config-hash stamped into every audit record. *(both #2)*
6. **Unify the destructive taxonomy.** One config-owned taxonomy (named irreversible ops · generic high-risk families · parser sentinels) instead of engine-policy names + hook generic `"destructive"` as two systems. *(both #3)*
7. **Cross-platform operator/person registry.** `person_id` + per-platform identities + tenant memberships + internal/external + clearance + disabled + elevation-eligibility — replaces per-scope bare-string lists and the `_is_internal_operator` approvers-proxy. *(both #5; `t_7f640411`)*
8. **Dry-run vs live as policy mode**, not an executor default: `mode: dry_run|live` with fail-closed startup + audit label. *(both #6)*
9. **`ecosystem` glob = unresolved dangerous scope.** `_repo_in_scope` accepts any `vamseeachanta/*` prefix — not a snapshot. Resolve+pin+audit at load; treat unbounded glob as deny-by-default. *(codex #9)*
10. **Elevation workflow.** TTL enforcement, evidence capture, approver≠requester, two-person rule for risky edits, audit linkage. *(codex; `t_7f640411`)*
11. **Real diff-risk implementation.** Engine consumes precomputed booleans; needs an actual diff parser (rename/binary/submodule/generated-file) + PR preflight. *(codex)*

## Tier 3 — industry / multi-tenant (beyond POC)
Threat model + trust boundaries · tenant isolation (per-tenant worktrees/temp/audit, no shared rate-store in multi-worker) · credential lifecycle (rotation/revocation/attestation/break-glass) · policy schema + migration + config hash · immutable execution manifest · idempotency/outbox for fanout · observability + incident runbook + audit-integrity + canary schedule · data governance (classification/retention/export, what-to-which-model) · gateway identity hardening (account linking, device state, revocation propagation, spoofing controls) · deployment topology + startup checks gating live mode · formal onboarding/offboarding · supply-chain/plugin allowlist (MCP/tools).

## Already addressed this session
Glossary origin-visibility inconsistency fixed in `CONTEXT.md`; detective alarm built (`scripts/deckhand/templates/deckhand-destructive-alarm.yml` + `deploy-detective`); hook hardened fail-closed (~60 bypasses); per-decision audit; fail-closed config verified.
