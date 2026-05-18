# Telegram/Hermes control-surface issue-tree decomposition

Use this reference when a multi-machine Telegram/Hermes audit concludes that dispatch is not ready and the user wants to persevere toward a working control-surface machine. The durable pattern is to convert readiness blockers into a plan-gated GitHub issue tree rather than starting ad hoc operational changes.

## Trigger

- User asks whether Telegram + Hermes can connect to all available machines.
- Audit produces mixed classifications: coordinator blocked, first worker blocked, status-only/manual hosts, and not-onboarded hosts.
- User asks for feature/subissues or a path to enable dispatch from a control surface machine.

## Issue tree shape

Create one umbrella feature plus side-effect-separated subissues:

1. **Umbrella feature** — enable Telegram/Hermes control-surface dispatch across approved machines.
2. **Coordinator hardening** — first dispatch coordinator, usually the currently reachable Linux host running `hermes-gateway`.
3. **First worker promotion** — the nearest realistic worker with SSH/workspace potential; require host-local readiness evidence.
4. **Readiness evidence and registry gates** — formalize freshness, env-var pointer names, dispatch-enabled vs status-only classification, and evidence directory contract.
5. **Smoke/destructive canary tests** — Telegram `/status`, harmless dispatch, and approval-gated destructive canary after coordinator + worker pass readiness.
6. **Cross-platform parity planning** — Windows/macOS stay status-only/manual until an approved parity plan exists.
7. **New host onboarding** — machines without workspace/Hermes/network path are onboarding plans, not failed dispatch hosts.

Keep this tree operationally sequenced: coordinator hardening gates worker promotion; worker promotion gates smoke/canary validation; parity/onboarding are expansion tracks, not MVP blockers.

## Labels and gates

- Use existing repo taxonomy; do not invent labels if matching `cat:*`, `domain:*`, `priority:*`, and `status:*` labels already exist.
- Start all implementation-affecting issues at `status:needs-plan`.
- Embed the hard gate in every issue body: resource intel → plan document → adversarial review → `status:plan-review` → user approval → `status:plan-approved` → TDD implementation → code review/verification → close.
- Link prior closed design issues as context, but create a new operational issue tree when the old issue was design/planning-only and the current work is live enablement.

## Verification checklist after issue creation

1. `gh issue view <parent> --json number,title,url,state,labels,body` confirms parent exists, is open, and references all children.
2. `gh issue view <child> --json comments` confirms each child links back to the parent.
3. Parent body contains explicit child issue numbers/URLs.
4. Every child has the intended labels and `status:needs-plan`.
5. No secret values appear in issue bodies or comments; env-var names are allowed, raw values are not.

## Operator closeout shape

Report only the verified issue tree and the next recommended planning target. Do not imply dispatch works. Example next order:

1. Plan coordinator hardening first.
2. Then first worker promotion.
3. Then readiness evidence/gates if not already covered.
4. Then Telegram smoke/canary validation.
5. Keep parity/onboarding issues as expansion planning.
