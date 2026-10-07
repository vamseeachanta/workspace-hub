---
name: taxact-business-c-corp-filing-packet
version: "1.0.0"
category: business_admin
description: "Assemble and execute a packet-first TaxAct Business filing workflow for C-Corp Form 1120 returns using existing repo artifacts, with strict pre-submit gates and human approval."
type: workflow
tags: [tax, taxact, business, c-corp, 1120, 8825, 4562, filing-packet]
scripts_exempt: true
---

# TaxAct Business C-Corp Filing Packet

## Trigger Conditions
Use when:
- the user wants to file or prepare a C-Corp return in TaxAct Business
- the repo already contains corporate tax worksheets, guides, or support docs
- the goal is to get to a deterministic file-now vs blocker decision quickly

Common requests:
- "review the corporate tax packet"
- "get this 1120 ready for TaxAct"
- "prepare the filing workflow for the business return"
- "guide the TaxAct filing session"

## Goal
Convert scattered repo tax artifacts into a compact, filing-ready TaxAct Business packet and run the live session in a strict packet-first order.

## Required mindset
- Do not recompute the whole return from scratch if a vetted worksheet/guide already exists.
- Do not invent values.
- Do not submit anything without explicit user approval.
- Prefer a binary outcome: `READY TO FILE NOW` or `STOP / TRIAGE`.
- If a same-day blocker appears, document it exactly and stop instead of guessing.

## Canonical artifact types to look for
Search likely directories such as:
- `taxes/<YEAR>/`
- `docs/tax/`
- repo-level `Tax/` or `tax/`

Priority files:
1. tax worksheet YAML
2. filing guide / line-by-line entry guide
3. strategy decisions memo
4. reconciliation memos (1099s, reimbursements, deductions)
5. depreciation or cost-seg support
6. state filing notice / state filing data
7. handoff prompt and session notes

Useful filename patterns:
- `*tax-preparation-worksheet*`
- `*form-1120*`
- `*filing-guide*`
- `*tax-strategy*`
- `*reconciliation*`
- `*cost*seg*`
- `*franchise*tax*`
- `*handover*prompt*`

## Workflow

### Phase 1 — Recover the packet
Use `search_files` first and gather the candidate packet.

Minimum read set:
1. worksheet / structured numeric source
2. filing guide
3. strategy memo
4. reconciliation memo(s)
5. depreciation support
6. state filing support

### Phase 2 — Establish source-of-truth order
Declare the packet order explicitly before live filing. Recommended order:
1. worksheet YAML
2. filing guide
3. strategy memo
4. reconciliation memo(s)
5. depreciation support
6. state filing support
7. handoff prompt / session playbook

Treat the worksheet + filing guide as primary numeric truth unless a later file explicitly supersedes them.

### Phase 3 — Produce the compact filing packet
Summarize, at minimum:
1. entity identity
2. tax year and filing deadline
3. expected filing path (TaxAct Business)
4. income components
5. major deductions
6. depreciation posture
7. expected federal result
8. state follow-on filing posture
9. material blockers
10. unresolved but low-impact questions

### Phase 4 — Reconcile only the material categories
Work in this order:
1. gross receipts / 1099 / reimbursement treatment
2. deductible taxes and any basis adjustments
3. insurance / HOA / fees / other major deductions
4. Form 4562 / depreciation / cost-seg support
5. Schedule L / balance sheet support
6. state filing readiness

Avoid broad repo wandering once these are stable.

### Phase 5 — Run the TaxAct session
Use TaxAct Business in this order when possible:
1. entity profile / return setup
2. Form 1120 header facts
3. Form 8825 or rental-income sections if applicable
4. Form 4562 depreciation
5. Schedule K / other information
6. Schedule L / M-1 / M-2
7. final review
8. pre-submit gate
9. user approval
10. submit
11. state filing immediately after federal values are frozen

### Phase 6 — Pre-submit gate
Do not recommend submit until all are true:
- income ties to support
- reimbursement treatment is consistent
- deductible taxes are handled consistently with any basis adjustment
- major deductions tie to support
- depreciation ties to support
- Schedule L balances
- M-1 / M-2 are coherent
- state filing inputs are ready
- user explicitly approves

### Phase 7 — If blocked
Capture:
- exact TaxAct screen or prompt
- field/value conflict
- source document consulted
- whether blocker is material today
- recommended next action

Then produce a short blocker note and updated handoff prompt.

## Deliverables
Minimum:
- user-facing readiness summary
- saved filing packet or session playbook in the repo

Strong optional deliverables:
- `taxact-session-playbook.md`
- `claude-tax-handover-prompt.md`
- session exit note
- post-filing archive checklist
- state filing checklist

## Output style
Be concise and operational:
1. readiness status
2. exact files reviewed
3. bottom-line expected result
4. material blockers only
5. next action options

## Lessons encoded from prior tax sessions
- packet-first beats live exploration
- keep strategy docs separate from execution docs
- use a dedicated handoff prompt rather than restarting from memory
- prefer explicit stop/go decisions over open-ended analysis
- keep CPA handoff or extension as fallback, not default, when the packet is already strong
