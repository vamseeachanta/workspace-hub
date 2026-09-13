# Hard-Stop Policy — Risk-Based Authorization

> Authority: [SHARED_SOUL.md — Authorization](../../config/agents/SHARED_SOUL.md#authorization).
> Scope: primary issue-planning workflows across providers, including engineering work.
> Tracking: [instruction alignment](https://github.com/vamseeachanta/workspace-hub/issues/3615); [original policy](https://github.com/vamseeachanta/workspace-hub/issues/1839).

## Apply shared authority

Planning depth, permission and verification evidence are separate decisions.
Bounded routine reversible work may proceed under independently established
standing authorization, with proportionate planning, TDD and applicable review.
Substantial work requires explicit approval of the concrete current plan and
implementation scope. Consequential actions require explicit approval matching
the action and destination. Missing scope, effects or provenance requires context
before the affected action proceeds; independent authorized work may continue.

This policy is not an approval service. A label, marker, review verdict, receipt
or handoff cannot authenticate authority. The orchestrator verifies the originating
user/session instruction, scope, limitations and later changes. The optional
workflow decision CLI provides advice, not permission or a mandatory per-tool gate.

## Identify risk from actual effects

Engineering routing indicators include `cat:engineering`,
`cat:engineering-calculations`, `cat:engineering-methodology` and
`cat:data-pipeline`; calculations in digitalmodel, worldenergydata and
assetutilities; and changes based on engineering standards. Repository membership
or a file extension does not establish risk. Absence of an engineering label does
not exempt a change from evaluation.

Changes to engineering basis, qualified inputs, approval/security controls,
shared instructions or deployment configuration require substantive scrutiny.
Harness, infrastructure and documentation changes may require substantial-plan
approval. Publication, deployment, access changes and destructive actions require
matching consequential-action authority. Qualified engineering inputs, licensing,
acceptance criteria and security requirements remain applicable.

## Plan and execute without repeated approval

1. Identify the issue, existing work, intended scope and effects.
2. Prepare proportionate planning and resource intelligence; obtain adversarial review.
3. Verify authority appropriate to the current risk and scope. Obtain explicit approval of a substantial concrete plan when it is not already established. Do not implement the affected work while a required decision is pending.
4. Follow TDD, verify results and obtain code/artifact review.
5. Reassess material scope changes and consequential actions; verify completeness and perform authorized closeout.

Plans identify the intended change, affected paths, tests, acceptance criteria and
risks. Substantial plans use `docs/plans/_template-issue-plan.md`; human-facing rich
plans default to HTML. A bounded routine task may use an issue/session plan under
established standing authorization. Missing local markers or stale historical
metrics do not require repeating verified authorization or unchanged verification.

Only the owner applies `status:plan-approved`; an implementing agent never
self-applies it. The label is a reference to approval, not its authenticated
scope. Do not downgrade labels or delete approval markers because a local file
is missing. Discover current provenance and reconcile records within authorization.

## Interactive, batch and emergency work

Use available interaction when a required decision or missing context changes the
action. Continue independent authorized work while that decision is pending.
Do not request approval again for unchanged scope with verified current authority.

Batch scheduling, elapsed time, posting a plan and handoffs do not grant authority.
Unattended bounded work may proceed under independently verified standing
authorization; unapproved substantial work and consequential actions wait.
Urgency, configuration changes and short duration provide no automatic waiver of
TDD, review, security or data requirements.

## Review and enforcement boundaries

Plan and code/artifact reviews are independent gates. Apply
`docs/standards/AI_REVIEW_ROUTING_POLICY.md`; scale depth without automatically
waiving review for small changes. A blocking finding pauses affected work until
resolved. The finding itself neither grants nor revokes user authorization;
material plan changes require matching approval.

Existing hooks and CI may use legacy marker heuristics and partial tool coverage.
They do not authenticate permission or demonstrate universal enforcement. Report
a blocking mismatch and its source. Do not bypass it with flags, install a
replacement or weaken enforcement under this policy. Consumer migration and
trusted authority transport require their own reviewed scope. These instructions
alone do not change live hooks, settings or provider discovery.
