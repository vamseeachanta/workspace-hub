---
name: shared-risk-workflow
description: Assess bounded agent operations and prior verification evidence through the shared advisory CLI. Use for Claude or Codex workflow decisions; does not execute work, authenticate approval, install profiles or replace live gates.
---

# Shared risk workflow

Read the [request and receipt contract](../../../../docs/governance/evidence-threshold/README.md#shared-workflow-assessment).
Resolve the repository root and call `scripts/governance/workflow_decision.py`
with the bounded JSON request on stdin. Use the documented pinned dependencies.
Explicitly loading this file establishes only explicit loading, not native discovery.

Describe the actual operation, exact paths including both rename endpoints,
effects and repository/task/operation identity. If those facts cannot be established,
report missing context rather than inventing a routine label. Supply an existing
authorization reference only when it identifies evidence available for independent
verification. Preserve the user's standing authorization and its scope.

Report all six output fields: `risk_class`, `authorization_assessment`,
`action_boundary`, `metric_advice`, `reuse_assessment`, `reason_codes`.
Exit 0 means an assessment was produced; it is not permission. Historical metrics
do not grant or revoke authority. An unverified reference never satisfies an
approval gate by itself. Substantial unapproved work and consequential actions
require independently established matching authorization before execution.

When comparing prior verification, supply complete dependency keys and actual
evidence content through the documented receipt input. Treat
`candidate-pending-live-validation` as a candidate only: independently validate
dependency completeness, evidence provenance, current access, rights, revocation,
freshness and action authority. Do not rerun solely because an unrelated timestamp
or locator changed; do not reuse when governing inputs changed or remain unknown.

The CLI performs assessment only. This skill grants no authority to modify live
hooks, user settings, installed skill roots, generated runtimes or remote state.
