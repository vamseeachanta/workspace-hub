# Execution Routing Policy View

This is a derived policy view for #2728. The canonical machine identity and capability source is `config/workstations/registry.yaml`.

## Registry keys referenced

- `dev-primary`
- `dev-secondary`
- `licensed-win-1`
- `licensed-win-2`
- `macbook-portable`

This document intentionally references registry keys only. It must not duplicate machine identity, network, operating-system, role, provider, or capability fields. When those facts are needed, read the registry.

## Routing posture

- Control-plane documentation and architecture tests default to `dev-primary`.
- Open-source simulation or heavy engineering stacks route by registry capability to a capable Linux worker when approved.
- Licensed Windows execution remains registry-routed and cannot be assumed reachable by SSH.
- Provider tools are capabilities of a machine, not standalone source-of-truth records.

## Open dependencies

#2119, #1838, and #2089 remain open dependencies. This view does not treat them as approved policy and does not replace their future routing contracts.
