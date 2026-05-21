# Plan for #2772: decision(workstations): choose tier-1 repo placement for licensed-win-1

> **Status:** draft — registry-based/GUI-verification-needed decision artifact; no implementation approval
> **Complexity:** T1
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2772
> **Review artifacts:** pending if this decision issue is promoted to `status:plan-review`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/workstations/registry.yaml` — `licensed-win-1` is registered as Windows, `workspace_root: D:\workspace-hub`, `ssh: null`, `telegram_mode: desktop-status-only`, `dispatch_enabled: false`, current repo list `OGManufacturing`.
- Found: issue #2772 comments — registry-based memo plus user placement decision are posted; live GUI verification is still needed because hostname/SSH probe from ace-linux-1 cannot access the host.
- Found: `docs/plans/2026-05-20-issue-2756-licensed-win-1-solver-status-lane-baseline.md` — existing draft baseline for licensed-win-1; its required set needs alignment with newer #2772 decision that makes `assetutilities` required.
- Gap: no GUI-captured evidence artifact currently proves actual Windows checkout paths, Git Bash/Hermes/provider auth, solver executable/license state, or Task Scheduler readiness.

### Standards

| Governance source | Status | Source |
|---|---|---|
| Issue planning workflow | applicable | `docs/plans/README.md` hard gate. |
| Per-machine placement outcome contract | applicable | `.claude/skills/coordination/issue-planning-mode/references/per-machine-repo-placement-outcome-contract.md`. |
| Repo location contract | applicable with Windows path adaptation | `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md`. |

### LLM Wiki pages consulted

- N/A — placement decision issue.

### Documents and issues consulted

- Issue #2772 comments — user placement decision and registry-based memo.
- `config/workstations/registry.yaml` lines for `licensed-win-1` — current role/path/access posture.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` — Windows machines are desktop/status-only for MVP; no unattended dispatch until separately approved.
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — Windows machines are licensed solver hosts; Linux should not mount/mutate Windows solver workspaces.

### Gaps identified

- Need GUI verification checklist/evidence capture before any registry implementation or solver queue claims.
- Need to classify `OGManufacturing` as existing non-tier-1 machine state, not a substitute for `workspace-hub` / `digitalmodel` / `assetutilities`.
- Need to keep `licensed-win-1` status-only/manual until Windows dispatch parity is separately approved.

### Evidence (embedded verification)

**User decision in #2772** (posted 2026-05-20):

```text
required: workspace-hub, digitalmodel, assetutilities
optional/reference-only: worldenergydata, llm-wiki
not planned by default: assethold, aceengineer-website, aceengineer-strategy
existing non-tier1: OGManufacturing unless separately promoted
access: registry-based / needs GUI verification
```

**Registry evidence**:

```yaml
licensed-win-1:
  os: windows
  workspace_root: 'D:\workspace-hub'
  ssh: null
  telegram_hermes:
    dispatch_enabled: false
    telegram_mode: desktop-status-only
```

**Reproduction proofs**: N/A — decision/governance issue; live GUI verification is the planned evidence gap.

Distinct sources consulted: #2772 comments, registry file, Windows ops/control-plane docs, prior licensed-win plan pattern.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2772-licensed-win-1-placement-decision.md` |
| Registry authority | `config/workstations/registry.yaml` |
| Future GUI evidence | `docs/reports/licensed-win-1-tier1-gui-verification.md` |
| GitHub decision thread | #2772 |

---

## Deliverable

A durable `licensed-win-1` repo-placement decision record plus a bounded GUI-verification checklist, with all setup/registry changes blocked until a reviewed and user-approved implementation plan.

---

## Pseudocode

Trivial — decision issue. Implementation belongs in a future approved Windows registry/readiness/GUI-verification plan.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-20-issue-2772-licensed-win-1-placement-decision.md` | Durable decision artifact. |
| Update | `docs/plans/README.md` | Index this plan. |
| Future create | `docs/reports/licensed-win-1-tier1-gui-verification.md` | Manual evidence checklist after approval. |
| No direct implementation | `config/workstations/registry.yaml` | Registry updates require approved implementation plan. |

---

## GUI Verification Checklist

Capture manually on `licensed-win-1` before any dispatch or setup claims:

1. Confirm `D:\workspace-hub` exists and is a git checkout of `vamseeachanta/workspace-hub`.
2. Confirm whether `D:\digitalmodel` or approved equivalent exists; record remote, branch, dirty/ahead/behind.
3. Confirm whether `D:\assetutilities` or approved equivalent exists; record remote, branch, dirty/ahead/behind.
4. Record whether `worldenergydata` and `llm-wiki` are absent, reference-only, or present on-demand.
5. Record existing `OGManufacturing` path and classify as non-tier-1 unless separately approved.
6. Confirm Git Bash command availability: `git`, `gh`, `uv` if present, `hermes` if present, provider CLIs if present.
7. Confirm auth state without exposing secrets: `gh auth status`, Hermes profile availability, provider CLI login state.
8. Confirm solver state: OrcaFlex/OrcaWave/ANSYS executable presence and license availability if safe to query.
9. Confirm Task Scheduler queue/readiness if solver queue work is proposed.
10. Leave `dispatch_enabled=false` unless a later Windows dispatch parity plan is approved.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| N/A | Decision-only issue; no implementation in #2772. | #2772 decision comment and GUI checklist. | Implementation remains future/blocked. |

---

## Acceptance Criteria

- [ ] #2772 decision classes are durable and linked from the issue thread.
- [ ] Required repos for `licensed-win-1` are `workspace-hub`, `digitalmodel`, and `assetutilities`.
- [ ] `worldenergydata` and `llm-wiki` are optional/reference-only; `assethold`, `aceengineer-website`, and `aceengineer-strategy` are not planned by default.
- [ ] `OGManufacturing` is classified as existing non-tier-1 state, not a tier-1 substitute.
- [ ] GUI verification checklist exists before any claim that `licensed-win-1` is ready.
- [ ] `licensed-win-1` remains desktop/status-only/manual; no unattended dispatch, clone/move/delete/sync, or solver execution is authorized by this decision issue.
- [ ] Completion reuses the same workstation registry authority/schema pattern established by ace-linux-1.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending/not required for decision closeout unless moving to plan-review |  |
| Codex | pending/not required for decision closeout unless moving to plan-review |  |
| Gemini | pending/not required for decision closeout unless moving to plan-review |  |

**Overall result:** draft decision artifact; implementation remains blocked.

---

## Risks and Open Questions

- **Risk:** Registry is not live evidence. GUI verification can contradict the registry and must be treated as newer evidence.
- **Risk:** Windows path and shell semantics differ from Linux; no `/mnt/...` assumptions should be used for Windows checkout placement.
- **Open:** Exact approved Windows repo root convention: `D:\<repo>` sibling checkouts versus another explicitly approved root.

---

## Complexity: T1

T1 because #2772 is a decision/traceability and GUI-evidence checklist issue. Registry/checker/solver queue implementation must be separately planned and approved.
