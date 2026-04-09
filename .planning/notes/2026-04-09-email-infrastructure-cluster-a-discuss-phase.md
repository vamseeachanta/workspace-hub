# Discuss Phase — Cluster A Email Infrastructure

Date: 2026-04-09
Anchor issue: #1963
Related issues: #2017, #1987, #2024, #2025, #2026

## Scope reviewed

GitHub issues reviewed:
- #1963 — multi-account Gmail management parent
- #2017 — email-as-queue design
- #1987 — legacy cleanup/archive pipeline
- #2024 — rewrite extraction pipeline
- #2025 — per-domain extraction templates
- #2026 — state tracking system

Repo code reviewed:
- scripts/email/gmail-archive-extract.py
- scripts/email/gmail-digest.py
- scripts/email/contact-normalizer.py
- scripts/email/email-routing.yaml
- docs/email/WORKFLOW.md
- scripts/legal/legal-sanity-scan.sh (location verified)

## Current architecture reality

1. Infra foundation exists
- OAuth-backed multi-account support is wired into existing scripts.
- Contact databases exist for ace, personal, and skestates.
- Daily digest script exists.
- Routing config exists.

2. Core mismatch still exists
- The implemented extraction script is archive-first, not queue-first.
- `gmail-archive-extract.py` routes emails into `docs/email/...` and can delete immediately with `--delete`.
- This conflicts with #2017 and docs/email/WORKFLOW.md, which define:
  INBOUND -> TRIAGE -> EXTRACT DATA -> ACT -> DELETE

3. Planning split is already visible in issues
- #2024 = extraction/action pipeline rewrite
- #2025 = template registry
- #2026 = thread state system
- #1987 = legacy issue that must be reframed, not followed literally
- #1963 = parent cluster / operating envelope

## Existing code findings

### scripts/email/gmail-archive-extract.py
Observed behavior:
- fetches full Gmail messages and attachments
- extracts body text
- writes raw/near-raw markdown artifacts into repo paths driven by `email-routing.yaml`
- optionally deletes messages directly with `--delete`
- has no queue-state machine
- has no Gmail label lifecycle
- has no structured template engine

Implication:
- This script is the main implementation obstacle to the new design.
- It should not be extended in-place as archive-first logic; it should be replaced or heavily refactored under #2024.

### scripts/email/gmail-digest.py
Observed behavior:
- scans unread and recent messages across 3 accounts
- classifies by contact DB and keyword heuristics
- produces a digest-style prioritization view

Implication:
- Useful as triage entry point.
- Needs eventual integration with queue state / Gmail labels so digest reflects active thread lifecycle, not just unread/recent heuristics.

### scripts/email/email-routing.yaml
Observed behavior:
- maps domains to DELETE / REVIEW / repo archive destinations
- many destinations still point at `docs/email/...`
- CRE routes already point closer to structured data targets (`assethold/data/...`) but still under an email-oriented path

Implication:
- Routing must be migrated from archive destinations to extraction destinations.
- Routing should become template-aware and state-aware rather than a pure path map.

### scripts/email/contact-normalizer.py
Observed behavior:
- contact normalization/classification exists and is usable as upstream context for triage

Implication:
- contact work is not the first blocker for Cluster A planning.
- queue model should consume this as enrichment, not re-solve normalization first.

## Design decisions from discuss phase

### 1. Thread state tracking
Decision: use a hybrid model.
- Primary operational state: Gmail labels
  - wh-email/extracted
  - wh-email/awaiting-reply
  - wh-email/completed
  - wh-email/noise
- Durable/local mirror: `~/.hermes/email-state.yaml`

Why:
- labels give operator visibility and Gmail-native filtering
- local YAML gives deterministic cron-safe bookkeeping and deletion windows
- this matches #2026 and docs/email/WORKFLOW.md

### 2. Extraction format
Decision: structured YAML as the default persisted artifact, with optional markdown summaries only where human review materially benefits.

Why:
- #2025 already defines YAML template direction
- YAML is easy to diff, inspect, and post-process
- raw email body dumps should be explicitly out of scope

### 3. Deletion policy
Decision: conservative queue lifecycle.
- `noise` can be deleted immediately after classification rules are trusted
- `completed` gets 7-day grace period
- `awaiting-reply` is never auto-deleted
- first production rollouts should default to dry-run or review mode per domain batch

Why:
- preserves safety while still honoring the queue model
- aligns with #2017 and #2026

### 4. Learning loop
Decision: template-and-exception feedback loop.
- known domains use explicit templates
- unknown/unclassified emails are surfaced in digest/report output
- user corrections feed routing/template changes
- periodic review should compare keep/delete/extract outcomes

Why:
- avoids over-fitting on day one
- gives an iterative improvement path without restoring archive-everything behavior

## Proposed architecture for Cluster A

Layer A — Triage
- continue using digest-style scanning as entry point
- enrich each message with contact match, domain class, and current queue state

Layer B — Extraction
- replace archive dumps with template-driven field extraction
- first extraction target: CRE listings (`sandsig.com`) because volume is high and fields are structured

Layer C — State machine
- create/read Gmail labels
- maintain local `email-state.yaml`
- support transitions:
  - inbox -> extracted
  - extracted -> awaiting-reply
  - extracted/awaiting-reply -> completed
  - completed -> delete after grace period
  - completed/awaiting-reply -> inbox on new reply

Layer D — Routing
- convert routing from `domain -> archive path` into `domain -> template + destination`
- preserve REVIEW / DELETE controls, but make destination paths structured-data-first

Layer E — Safety and commit discipline
- legal scan before commit
- dry-run support on all destructive actions
- no raw email archiving to repos

## Recommended execution order

1. Plan Cluster A at the parent level under #1963
2. Treat #2017 as the governing design contract
3. Make #2024 the first implementation issue
4. Make #2025 and #2026 parallelizable after #2024 interface decisions are fixed
5. Mark #1987 as legacy/superseded in plan narrative so implementation does not follow archive-first behavior

## Dependencies / constraints

Verified present:
- scripts/email/gmail-archive-extract.py
- scripts/email/gmail-digest.py
- scripts/email/email-routing.yaml
- contact CSV outputs for ace, personal, skestates
- scripts/legal/legal-sanity-scan.sh

Still needing explicit implementation during execution:
- new extraction/action script
- template registry directory under scripts/email/templates/
- tests for extraction, state transitions, and deletion guardrails
- routing migration away from docs/email archival destinations
- issue comment / label workflow after plan review

## Planning conclusion

Cluster A should be planned as an architecture migration, not a small feature.

Parent framing:
- #1963 owns the cluster and operator surface
Design contract:
- #2017 defines the correct workflow
Implementation stream:
- #2024 pipeline rewrite
- #2025 template registry
- #2026 state tracking
Legacy stream to constrain:
- #1987 must not drive implementation as written

Recommended complexity for the plan: T3
Reason: multi-account workflow, destructive operations, cross-repo data routing, new state machine, and test-first requirements.