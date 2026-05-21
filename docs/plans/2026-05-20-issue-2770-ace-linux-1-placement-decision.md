# Plan for #2770: decision(workstations): choose tier-1 repo placement for ace-linux-1

> **Status:** draft — decision recorded; adversarial review not yet run; no implementation approval
> **Complexity:** T1
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2770
> **Review artifacts:** pending if this decision issue is promoted to `status:plan-review`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/workstations/registry.yaml` — `dev-primary` already declares `hostname: ace-linux-1`, `workspace_root: /mnt/local-analysis/workspace-hub`, `tier1_repo_root: /mnt/local-analysis`, `repo_layout: sibling`, and current repos `worldenergydata`, `digitalmodel`, `assetutilities`, `assethold`, `workspace-hub`, `OGManufacturing`.
- Found: `docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md` — execution/normalization plan created to implement the decision through registry/checker/readiness work after review and approval.
- Found: issue #2766 comments — nested direct git repositories were relocated to sibling paths and #2770 decision is linked back to the normalization issue.
- Gap: #2770 itself should remain a decision/traceability issue; registry/checker implementation belongs to #2766 or a follow-on approved plan.

### Standards

| Governance source | Status | Source |
|---|---|---|
| Issue planning workflow | applicable | `docs/plans/README.md` hard gate. |
| Per-machine placement outcome contract | applicable | `.claude/skills/coordination/issue-planning-mode/references/per-machine-repo-placement-outcome-contract.md`. |
| Repo location contract | applicable | `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md`. |

### LLM Wiki pages consulted

- N/A — placement decision issue. `llm-wiki` is part of the repo-placement classification, not a domain knowledge source for this decision.

### Documents and issues consulted

- Issue #2770 comments — live ace-linux-1 sibling inventory and user placement decision.
- Issue #2766 — physical relocation/normalization execution surface.
- `docs/plans/2026-05-19-issue-2754-ace-linux-1-throughput-lane-tier1-baseline.md` — prior throughput-lane baseline; #2770 updates it by making `assethold` required.
- `config/workstations/registry.yaml` — current authority still needs explicit `tier1_baseline` / repo role projection.

### Gaps identified

- Need registry reconciliation so `llm-wiki`, `aceengineer-website`, and `aceengineer-strategy` are represented explicitly for ace-linux-1 instead of relying on comments.
- Need a single reusable schema for subsequent machines, not an ace-linux-1-only convention.
- Need no further filesystem moves until an approved implementation plan authorizes them.

### Evidence (embedded verification)

**User decision in #2770** (posted 2026-05-20):

```text
required: workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold
optional: aceengineer-website, aceengineer-strategy
separate/non-tier1: OGManufacturing unless later promoted by an explicit plan
repo root: /mnt/local-analysis sibling checkouts; workspace-hub remains control plane
```

**Live checkout evidence from latest local probe** (2026-05-20T22:25:46Z):

```text
nested git repos under workspace-hub: 0
/mnt/local-analysis first-level git repos include:
workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold, aceengineer-website, aceengineer-strategy
```

**Reproduction proofs**: N/A — decision/governance issue.

Distinct sources consulted: #2770 comments, #2766 comments, #2754 plan, registry file, live filesystem/git probe.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2770-ace-linux-1-placement-decision.md` |
| Execution plan | `docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md` |
| Registry authority | `config/workstations/registry.yaml` |
| GitHub decision thread | #2770 |

---

## Deliverable

A durable ace-linux-1 repo-placement decision record that #2766 can implement through registry/checker/readiness changes after adversarial review and user approval.

---

## Pseudocode

Trivial — decision issue. Implementation belongs in #2766 or a follow-on approved issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-20-issue-2770-ace-linux-1-placement-decision.md` | Durable decision artifact. |
| Update | `docs/plans/README.md` | Index this plan. |
| No direct implementation | `config/workstations/registry.yaml` | Registry updates belong to approved #2766 implementation. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| N/A | Decision-only issue; no implementation in #2770. | #2770 decision comment. | Implementation remains linked to #2766/follow-on plan. |

---

## Acceptance Criteria

- [ ] #2770 decision classes are durable and linked from the issue thread.
- [ ] #2770 does not authorize clone/move/delete/sync/setup work.
- [ ] #2766 owns registry, checker, readiness, and normalization implementation after review and explicit user approval.
- [ ] Completion leaves a reusable machine-placement pattern for subsequent workstation issues through the single workstation registry authority.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending/not required for decision closeout unless moving to plan-review |  |
| Codex | pending/not required for decision closeout unless moving to plan-review |  |
| Gemini | pending/not required for decision closeout unless moving to plan-review |  |

**Overall result:** draft decision artifact; implementation remains blocked in #2766.

---

## Risks and Open Questions

- **Risk:** #2754 and #2770 differ on `assethold` required/optional status. Treat #2770 as the newer machine placement decision and revise implementation plans accordingly.
- **Open:** Whether `OGManufacturing` remains non-tier-1 machine-access only or needs its own separate placement decision later.

---

## Complexity: T1

T1 because #2770 is a decision/traceability issue; technical implementation is covered by #2766.
