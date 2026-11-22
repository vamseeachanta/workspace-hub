# Implementation authority without separate plan approval

The originating task request or established standing authorization covers
implementation within its scope. Planning depth and adversarial review follow
the actual effects of the change. A separate approval of the plan is not a
prerequisite for authorized substantial implementation.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add a reproducible authority example and distinguish review from permission. |

## Sources and method

The governing sources are [shared authorization](../../config/agents/SHARED_SOUL.md#authorization)
and the [risk policy](HARD-STOP-POLICY.md), particularly “Plan and execute without
repeated approval”. These are repository policy rules; no engineering equations,
coefficients or acceptance limits apply to this example.

Read the task and establish its provenance and current scope. Check whether the
request is planning-only, whether a domain decision is unresolved, and whether
the proposed action has consequential effects. Prepare a proportionate plan,
obtain adversarial review, resolve blocking findings and follow TDD. Material
scope changes require matching authority; reuse authority already established
within unchanged scope.

The optional `scripts/governance/workflow_decision.py` CLI only assesses the
supplied context. It cannot authenticate a task request, perform an operation,
grant permission or replace review. A label, marker, receipt or handoff cannot
establish authority by itself. Historical approval records remain intact and
maintainer-controlled; never self-apply `status:plan-approved`.

## Worked example

Input: a request to update provider guidance substantially, with bounded scope and a
reference to the originating implementation task. All identities below are
synthetic. Save this input as `request.json` in an authorized temporary folder:

```json
{
  "schema_version": "1",
  "provider": "codex",
  "operation_kind": "edit",
  "scope": {
    "repository_id": "example-repository",
    "task_id": "example-task",
    "operation_id": "update-guidance",
    "bounded": true
  },
  "changed_paths": ["config/agents/hermes/SOUL.md"],
  "effects": ["local-reversible", "substantial-change"],
  "authorization_reference": "originating-task-request"
}
```

From the repository root, using an environment with the CLI's `pyyaml` and
`jsonschema` dependencies:

```sh
uv run --no-project --with pyyaml --with jsonschema python scripts/governance/workflow_decision.py < request.json
```

Method: the substantial effect selects the substantial route in the shared
authorization table. The shared-instruction path also requires protected-change
scrutiny under the same source. The task reference requires independent provenance and
scope verification; it does not become authenticated through JSON. The absence
of consequential effects means this assessment does not request a separate
approval. The expected answer, derived from those rules, is:

```json
{
  "risk_class": "substantial",
  "authorization_assessment": "unverified-reference",
  "action_boundary": "verify-task-authority",
  "metric_advice": "not-requested",
  "reuse_assessment": "not-requested",
  "reason_codes": ["PROTECTED_CHANGE", "TASK_AUTHORITY_REQUIRED", "UNVERIFIED_AUTHORITY"]
}
```

After independently verifying the task, proceed with implementation, tests and
review without another plan-approval request. The CLI output alone does not
establish that the independent verification occurred.

## Boundary cases

| Changed input or circumstance | Expected route and reason |
| --- | --- |
| Another provider performs the same assessment | Same route; provider identity does not grant authority. |
| The task reference is absent | `needs-context`; missing provenance must be resolved. |
| Publication, destruction or access change is added | `approval-required`; verify explicit authority matching the action and destination. |
| Engineering basis change is added | `approval-required`; the existing consequential engineering check remains. |
| The request asks only for a plan | Continue planning and review; implementation requires matching task scope. |
| A required domain decision or blocking review finding is unresolved | Pause the affected work and continue independent authorized work. |
| A historical approval label or local marker is absent | Discover current authority; absence does not revoke established authorization. |

The example and executable boundary cases are checked by
`tests/governance/test_authorization_guidance_routes.py`. That suite also checks
the complete generated provider artifacts, including provider-specific content,
and the active engineering and ecosystem workflow references. Generated content
parity does not establish installed loading on other systems. Queue selection
and dispatch authentication are separate from this advisory example; no live
dispatch, installed runtime or external state is changed by it.
