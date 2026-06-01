# Deckhand scope/routing orthogonality decision

> **Date:** 2026-06-01
> **Status:** proposed — reached in a `grill-with-docs` design session; NOT yet plan-approved
> **Decision authority:** user (vamsee), pending the formal plan gate for [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (plan → adversarial review → **user approval** → implement)
> **Glossary:** [`CONTEXT.md`](../../CONTEXT.md) (scope, channel, delivery group, sensitivity/clearance)
> **Related issues:** [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (scope policy), [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) (delivery-group contract), [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) (reply-policy guardrails), [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) (fanout board)

## Decision

A Deckhand **scope** (`ecosystem`, `acma`, `doris`) is a named set of repositories plus the permission policy over them. It is **orthogonal to routing**: a scope answers *"which repos, and read/write/destructive?"* and says nothing about which messaging platform output goes to. Where output goes is a separate **delivery group** (or, by default, the origin chat).

The two concepts are coupled by exactly one constraint: **sensitivity clearance**. A scope declares a sensitivity (`acma` = private, `ecosystem` = internal); a delivery group declares which sensitivities it may receive. Output produced under a scope may fan out only to delivery groups cleared for that scope's sensitivity. The origin chat is always allowed (the operator already saw the request).

## Rationale

Issue #2931's wording fuses the two — *"named channels that can route to Telegram/WhatsApp/Teams while preserving authorization boundaries and repo-write safety."* Read literally, a "named channel" would bundle a routing target set **and** a repo-scope ACL into one object. That is the surprising-without-context part: a future reader sees `scope` and `delivery group` as separate types and will ask why they weren't one "channel."

They were deliberately split for two reasons:

1. **The word "channel" is already taken.** `gateway/channel_directory.py` defines a *channel* as a reachable messaging destination (Telegram chat, Slack `#channel`, Discord channel). #2902 already defines *delivery group* as a named set of those. Reusing "channel" for a repo-scope ACL would overload one word across three concepts.
2. **Fusing them creates a silent-fanout footgun.** If a scope carried its own routing, a casual DM command (`scope=acma, fix and push`) could broadcast private-repo activity to whatever channel set the scope bundled — without the operator choosing to. Keeping routing explicit means replies default to origin (consistent with the #2903 origin-only guardrail) and fanout is opt-in.

### Considered options

- **Scope = routing too (one fused "named channel").** Rejected: overloads "channel"; silent fanout from a DM; couples authorization to delivery.
- **Scope carries a *default* delivery group.** Rejected: still routes output somewhere the operator didn't name from a DM; couples authorization to routing.
- **Fully orthogonal, no coupling at all.** Rejected: a fat-fingered delivery group would leak `acma`/`doris` private-repo activity to a general audience — the exact `client → other-client` leak the [`wiki-sibling-routing`](../../.claude/rules/wiki-sibling-routing.md) rule forbids. Hence the single sensitivity-clearance coupling.

## Consequences

- A command resolves two independent parameters: an **active scope** (default: origin-bound — see below) and a **delivery target** (default: origin chat).
- The delivery-group contract (#2902) must carry a `clearance` field; the reply-policy guardrails (#2903) enforce origin-only-by-default. #2931 hands them the clearance requirement.
- "Origin-bound default scope" resolves the active scope from explicit context only (a channel→repo binding, or a repo the operator named) — never inferred from message prose — permits read+write but no destructive ops, must be contained within a scope the operator is authorized for, and rejects writes when no origin repo is resolvable.
