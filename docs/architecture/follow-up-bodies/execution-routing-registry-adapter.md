# feat(execution): add machine/provider routing registry adapter

Parent: #2728

Expose a read-only adapter over `config/workstations/registry.yaml` for execution routing decisions without duplicating workstation truth in architecture docs.

The adapter should support:

- machine/provider capability lookup
- execution residency constraints
- missing-machine fail-closed behavior
- explicit blocked states for unresolved dependencies #2119, #1838, and #2089

Acceptance criteria:

- adapter has TDD coverage for known machines and unknown-machine rejection
- adapter returns structured routing metadata consumable by execution manifests
- architecture docs reference the adapter instead of duplicating machine details
- unresolved dependency states are represented explicitly and cannot be treated as ready
