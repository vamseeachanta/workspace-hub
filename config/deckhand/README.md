# Deckhand configuration surface

All Deckhand behavior is driven by **externalized YAML config** here — reviewable,
editable, version-tracked. **No Deckhand config is embedded in code.** This is a
deliberate industry-grade choice: onboarding a new client/tenant or member is an edit
to these files, not a code change. `acma` / `doris` are example instances.

> Status: **PROPOSED** — inert until the approved build (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md`) wires it. Gate: owner applies `status:plan-approved` on [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931).

| File | Holds | Tenant-specific? |
|---|---|---|
| `policy.yml` | Global enforcement: destructive ops, action/diff-risk gate, reply clearance, audit rules + sinks, enforcement layers, kill switches, rate limits, elevation | No — generic |
| `scopes.yml` | **One self-contained section per client/scope**: repos (+ typed flags), `pat_env`, operators, sensitivity, data root, channel→repo bindings; plus origin-bound default | Examples (acma/doris) |
| `platforms.yml` | Messaging platform enablement + credential-by-reference (env var names) | No — generic |

Per-client config lives as a **section in `scopes.yml`** (not split across files) so a client can be reviewed/edited in one place. Adding a client = add a section.

## Rules

- **No secrets here.** Tokens/credentials live in env (`~/.hermes/.env`) and are referenced by env-var *name* only.
- **Fail-closed.** Unknown scope, repo absent from a scope allowlist, unparseable/missing file, or unrecognized operator → DENY (`policy.yml: fail_closed`).
- **Stable IDs only.** Operators are platform IDs (Telegram numeric id, Teams AAD oid, WhatsApp E.164) — never display names.
- **Generic over specific.** If a value would differ per company, it belongs in `scopes.yml`/`operators.yml`/`data-locations.yml`, never in `policy.yml` or code.

## Decisions
- [`docs/governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md`](../../docs/governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md)
- [`docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md`](../../docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md)
- Glossary: [`CONTEXT.md`](../../CONTEXT.md)
