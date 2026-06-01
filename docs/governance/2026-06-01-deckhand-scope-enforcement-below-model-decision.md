# Deckhand scope enforcement-below-the-model decision

> **Date:** 2026-06-01
> **Status:** proposed — reached in a `grill-with-docs` design session; NOT yet plan-approved
> **Decision authority:** user (vamsee), pending the formal plan gate for [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (plan → adversarial review → **user approval** → implement)
> **Glossary:** [`CONTEXT.md`](../../CONTEXT.md) (scope, permission level, destructive operation, operator)
> **Related:** [`.claude/rules/patterns.md`](../../.claude/rules/patterns.md) (enforcement gradient), `git-guardrails` skill, [#2741](https://github.com/vamseeachanta/workspace-hub/issues/2741) (destructive-action canary), [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) (platform-parity recon)

## Decision

Per-scope policy — the repo allowlist and the no-destructive rule — is enforced **below the LLM**, in defense in depth, never by system-prompt text:

1. **Layer 1 (model):** the system prompt states the policy. This is *guidance only* and is never the boundary.
2. **Layer 2 (process):** a git/`gh` command interceptor keyed to the active scope blocks destructive operations and any repo outside the scope's allowlist. Extends the existing `git-guardrails` mechanism (already blocks `push --force`, `reset --hard`, `clean`, `branch -D`).
3. **Layer 3 (server):** a per-scope GitHub **fine-grained PAT** provisioned without delete/admin permission, so even a bypass of Layer 2 cannot delete server-side.

Every scope-gated decision (allow **and** deny) is audited: timestamp, operator, platform, scope, target repos, action class, decision + reason — append-only, secrets redacted. The raw trail lives in a durable **private** store (dedicated private repo or backed-up archive) and feeds the #2741 destructive-action canary; a redacted, ID-free summary renders to `docs/reports/` HTML in public workspace-hub.

## Rationale

Deckhand drives an LLM agent. An LLM told "do not delete" in a system prompt *will* eventually delete something — prompt text is not an authorization boundary. The handoff for #2931 is explicit: *"enforcement should be policy-backed, not just prompt text."* The non-obvious part for a future reader is *why three layers* instead of one:

- A command-hook alone (Layer 2) is bypassed by any path that calls the GitHub API directly without going through the wrapper.
- Scoped tokens alone (Layer 3) cannot stop a destructive op the token *does* permit (e.g., a force-push when `contents:write` is granted).
- Together, bypassing any one layer is still caught by the next. This matches the repo's own enforcement-gradient doctrine (`patterns.md`: promote prose → script → hook; "must-never-miss enforcement" fires automatically).

"Destructive" is defined precisely so the boundary is enforceable: repo/branch/tag/release deletion, force-push / history rewrite, `git reset --hard` / `git clean`. A normal commit that removes file lines is a **write** (reviewable in a diff, recoverable via git), not a destructive op.

### Considered options

- **Command-hook only.** Rejected: direct-API path is unguarded.
- **Scoped tokens only.** Rejected: no local guard against permitted-but-destructive ops; no allowlist enforcement at command time.
- **Prompt text only.** Rejected outright: not a boundary; the explicit anti-pattern the handoff names.

## Consequences

- Implementation depends on resource intelligence into how Deckhand currently invokes git/`gh` (#2901 recon) and whether per-scope fine-grained PATs are operationally feasible — recorded as a blocker, not assumed.
- `acma`/`doris` membership must be an explicit, auditable allowlist (fail-closed: unknown repo → deny), not "all repositories as needed" — a recon deliverable before implementation.
- Each scope additionally carries an **operator allowlist** layered on Hermes' gateway allowlist; `ecosystem` (most powerful) gets the tightest operator list. Unknown sender, or known operator not on a scope's list → deny + audit.
- TDD coverage (per #2931 acceptance criteria) must include: scope resolution, repo-allowlist enforcement, no-destructive guardrails at each layer, operator authorization, sensitivity-clearance routing, and audit emission of both allows and denies.
