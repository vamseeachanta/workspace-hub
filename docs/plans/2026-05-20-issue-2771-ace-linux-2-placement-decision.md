# Plan for #2771: decision(workstations): choose tier-1 repo placement for ace-linux-2

> **Status:** draft — decision recorded; adversarial review not yet run; no implementation approval
> **Complexity:** T1
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2771
> **Review artifacts:** pending if this decision issue is promoted to `status:plan-review`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/workstations/registry.yaml` — `dev-secondary` declares `hostname: ace-linux-2`, `workspace_root: /mnt/local-analysis/workspace-hub`, `storage.local: /mnt/dde`, and current `repos: [digitalmodel, worldenergydata]`.
- Found: `docs/plans/2026-05-20-issue-2755-ace-linux-2-secondary-linux-worker-baseline.md` — broader plan-review artifact for ace-linux-2 worker readiness already exists and covers registry/readiness implementation scope.
- Gap: #2771 itself needs the user placement decision captured and linked to #2755/#future setup work without approving clone/move/delete/sync actions.

### Standards

| Governance source | Status | Source |
|---|---|---|
| Issue planning workflow | applicable | `docs/plans/README.md` hard gate. |
| Per-machine placement outcome contract | applicable | `.claude/skills/coordination/issue-planning-mode/references/per-machine-repo-placement-outcome-contract.md`. |
| Repo location contract | applicable | `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md`. |

### LLM Wiki pages consulted

- N/A — placement decision issue.

### Documents and issues consulted

- Issue #2771 comments — live SSH facts and user decision are already posted.
- Issue #2755 plan — ace-linux-2 broader readiness plan is already at plan-review and should absorb implementation details.
- `config/workstations/registry.yaml` — registry currently diverges from the #2771 decision because it lacks `workspace-hub` and `assetutilities` in `dev-secondary.repos`, and it treats `worldenergydata` as registered while #2771 makes it optional/code-only.

### Gaps identified

- Need a concise decision closeout path for #2771 once the user confirms no further placement changes.
- Need registry reconciliation in the implementation issue/plan (#2755 or a child) before any local clone/setup is performed.

### Evidence (embedded verification)

**User decision in #2771** (posted 2026-05-20):

```text
required: workspace-hub, digitalmodel, assetutilities
optional: worldenergydata, llm-wiki
reference-only: shared data/reference access through /mnt/remote/ace-linux-1/ace where appropriate
not planned: assethold, aceengineer-website, aceengineer-strategy
repo root: prefer /mnt/local-analysis for local Git checkouts unless approved plan changes it
```

**Live remote facts in #2771**:

```text
ace-linux-2 reachable over SSH
/mnt/local-analysis/workspace-hub present and dirty
/mnt/dde present
/mnt/remote/ace-linux-1/ace mounted
hermes/claude/codex/gemini missing from SSH PATH during probe
```

**Reproduction proofs**: N/A — decision/governance issue.

Distinct sources consulted: #2771 comments, #2755 plan, registry file, repo-location planning reference.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2771-ace-linux-2-placement-decision.md` |
| Existing implementation plan | `docs/plans/2026-05-20-issue-2755-ace-linux-2-secondary-linux-worker-baseline.md` |
| Registry authority | `config/workstations/registry.yaml` |
| GitHub decision thread | #2771 |

---

## Deliverable

A closed-loop ace-linux-2 placement decision record that links implementation to #2755 and prevents repo setup work from being mistaken as approved by the decision comment.

---

## Pseudocode

Trivial — decision issue. Implementation belongs in #2755 or a follow-on setup issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-20-issue-2771-ace-linux-2-placement-decision.md` | Durable decision plan/closeout artifact. |
| Update | `docs/plans/README.md` | Index this plan. |
| No direct implementation | `config/workstations/registry.yaml` | Registry changes belong to approved #2755/#follow-on implementation. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| N/A | Decision-only issue; no implementation in #2771. | #2771 decision comment. | Implementation remains linked to #2755/follow-on plan. |

---

## Acceptance Criteria

- [ ] #2771 decision classes are durable and linked from the issue thread.
- [ ] #2771 does not authorize clone/move/delete/sync/setup work.
- [ ] #2755 or a follow-on approved issue owns registry, readiness, and setup implementation for ace-linux-2.
- [ ] Large `/mnt/ace` data is not duplicated to ace-linux-2 by default; shared/reference access remains through `/mnt/remote/ace-linux-1/ace` unless separately approved.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending/not required for decision closeout unless moving to plan-review |  |
| Codex | pending/not required for decision closeout unless moving to plan-review |  |
| Gemini | pending/not required for decision closeout unless moving to plan-review |  |

**Overall result:** draft decision artifact; implementation remains blocked elsewhere.

---

## Risks and Open Questions

- **Risk:** Keeping both #2755 and #2771 open can create duplicate ace-linux-2 registry plans. Preferred next action is to treat #2771 as decision-complete and leave implementation to #2755/follow-on setup.
- **Open:** Whether the user wants `worldenergydata` code clone optional or required-code-only on ace-linux-2.

---

## Complexity: T1

T1 because #2771 is a decision/traceability issue; technical implementation is already covered by #2755.
