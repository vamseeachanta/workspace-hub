# Per-machine repo placement outcome contract

Use when drafting or revising workstation/machine tier-1 repo placement plans.

## Trigger

A plan decides which tier-1 repos belong on a specific machine, or adds readiness gates for a workstation lane.

## Required outcome language

Do not let the first machine issue become a one-off convention. The plan must state that completion establishes a repeatable pattern for subsequent machines:

- consistent tier-1 repo folder structure,
- methodical primary/reference checkout role decisions,
- repo harness/file ecosystem handling through one repo-tracked authority,
- no duplicated per-machine truth sources or local-only conventions.

## Placement authority rule

Prefer extending the existing workstation registry/control-plane artifact over creating a new machine-specific config file. If a separate file is proposed, the plan must explain why it is not duplicating authority and how it is linked from the canonical registry.

## Acceptance criteria to include

Add an explicit AC equivalent to:

> Completion leaves a reusable machine-placement pattern for subsequent workstation issues: consistent tier-1 repo folder structure, methodical primary/reference repo placement decisions, and repo harness/file ecosystem handling all routed through the single workstation registry authority.

## Sequencing

For a machine sequence such as ace-linux-1 -> ace-linux-2 -> licensed-win-1 -> licensed-win-2, treat the first machine as the baseline pattern. Later machine issues should inherit the same schema and only vary the repo set, machine constraints, and dispatch role.
