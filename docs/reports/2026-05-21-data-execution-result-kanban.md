# Data → Execution → Result Layer Kanban

Generated: 2026-05-21T05:53:39-05:00

## Flow rule

Work must move in this order:

1. **Data layer**: freeze/inventory/target repo/provenance/ledger.
2. **Execution layer**: only execute approved, non-destructive or explicitly authorized operations with TDD and rollback evidence.
3. **Result layer**: client/report/chatbot outputs consume only reviewed, provenance-backed, residency-cleared data.

Hard gates remain active: no implementation without live `status:plan-approved`; no agent self-applies that label.

## Kanban board

| Column | Layer | Issue | Status | Owner / route | Next checkpoint |
|---|---|---:|---|---|---|
| Ready / dependency input | Data | #2745 freeze ACMA projects and local-only archive posture | `status:plan-approved` | Claude CLI if execution starts | Verify freeze contract before any backup disposition live operation. |
| Ready / dependency input | Data | #2746 create private `llm-wiki-acma` repo target | `status:plan-approved` | Claude CLI preferred; Codex review | Defines private wiki target required by #2747/#2748. |
| Blocked at gate | Data | #2747 raw-to-private-wiki promotion ledger | live label is `status:working`, not `status:plan-approved` | Claude attempted, Codex attempted; both stood down/blocked | Needs user approval reconciliation / live label update before implementation. Codex sandbox currently fails with `bwrap`; Claude correctly refused missing live approval. |
| Waiting on data ledger | Result | #2748 client output scaffolding for reports/chatbots/evidence packs | `status:plan-approved` | Claude CLI after #2747 lands; Codex adversarial review | Plan explicitly blocks implementation on #2747 and #2746/#2389 being landed enough to define contracts. |
| In review / fix loop | Execution / data disposition | #2769 pre-move backup disposition dry-run reporter | `status:working` | Claude implemented; Codex adversarial review | Codex found MAJORs; orchestrator patched output-residency guard + report redaction. Await final review. |
| Needs planning before execution | Data | #2731 inventory/normalize data locations | `status:needs-plan` | planning lane only | Needed for broader canonical data/root taxonomy; do not implement until planned/reviewed/approved. |
| Portfolio / epic | Data | #2744 ACMA client project data-cycle readiness/private llm-wiki launch | open epic | orchestrator | Use as umbrella tracking surface after issue comments are posted. |

## Delegation lanes

### Lane A — Claude CLI: approved local implementation
- Use for write-capable implementation in isolated worktrees when live GitHub label is `status:plan-approved`.
- Current active: #2769 fix verification.
- Next allowed after dependency gate: #2748, but only after #2747 ledger exists.

### Lane B — Codex CLI: adversarial review and connector fallback
- Use for independent review of Claude changes.
- Current limitation: local shell sandbox fails with `bwrap: loopback: Failed RTM_NEWADDR`; Codex can still inspect pushed branches via GitHub connector.
- Current active: #2769 final adversarial review after fixes.

### Lane C — Human approval gate
- #2747 must be reconciled here. Local marker exists, but live issue does not carry `status:plan-approved`; per hard gate, implementation must not proceed.

## Immediate operating order

1. Finish #2769 review/fix/commit/push and leave it ready for integration.
2. Ask user to approve/reconcile #2747 live state if they want ledger execution now.
3. After #2747 lands, execute #2748 result-layer scaffolding with Claude CLI and Codex review.
4. Only then consider live data/archive actions from #2745/#2769.
