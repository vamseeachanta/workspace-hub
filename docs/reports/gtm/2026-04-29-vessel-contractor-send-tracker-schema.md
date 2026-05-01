# Vessel-Contractor Outbound Send Tracker — Schema

> **Issue:** #2556
> **Companion document:** `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
> **Status:** schema (planning artifact). The runtime `send-tracker.public.yaml` and `send-tracker.private.yaml` files materialize at `docs/gtm/intake/` after `status:plan-approved` per the issue-planning-mode workflow.
> **Date:** 2026-04-29

---

## 1. Purpose

Track every outbound brochure send and the contractor's downstream response, while keeping personally-identifying contact details (name, email, phone, LinkedIn URL) out of the public repo. The schema is split across two files:

| File | Path | Tracked in git? | Carries PII? |
|---|---|---|---|
| Public tracker | `docs/gtm/intake/send-tracker.public.yaml` | yes | **no** |
| Private companion | `docs/gtm/intake/send-tracker.private.yaml` | **no** (gitignored) | yes |

Public rows reference private rows by `prospect_id_hash` (a salted SHA-256). The public file is sufficient for review of campaign progress, response rates, and tier coverage. The private file is required only at send-time and remains on the operator's local filesystem.

This tracker is for **outbound sends** only. The existing `docs/gtm/deliveries-log.md` continues to track inbound prospect-demo deliveries (per `docs/gtm/prospect-demo-sop.md`); the two surfaces are deliberately separate.

## 2. `prospect_id_hash` derivation

```
prospect_id_hash = sha256(salt + ":" + canonical_email).hexdigest()[:16]
```

- `salt` is read from an environment variable (`GTM_TRACKER_SALT`) and is never committed.
- `canonical_email` is the contact's email address normalized to lowercase + stripped of "+suffix" Gmail aliases.
- The 16-char prefix gives ~10^19 collision space; collisions raise an explicit error rather than silently merging.
- The hash is **non-reversible without the original email + salt**. Even if the salt leaks, an attacker still needs the contact's address.

## 3. Public file schema (`send-tracker.public.yaml`)

YAML chosen for tooling-friendliness and because the existing `docs/gtm/intake/canonical-vessels/*.yaml` neighborhood is already YAML.

```yaml
# docs/gtm/intake/send-tracker.public.yaml
# Public outbound send tracker. NO PII permitted in this file.
# Companion private file: docs/gtm/intake/send-tracker.private.yaml (gitignored).
schema_version: 1
issue: 2556
generated_utc: 2026-04-29T00:00:00Z   # set on each rewrite

rows:
  - prospect_id_hash: "9f3a2b7d12c4e8f0"   # 16-char salted-sha256 prefix
    contractor: "Subsea7"                   # public company name only
    tier: 1                                 # 1 | 2 | 3 — matches #2554 matrix
    segment: "heavy_lift_pipelay"           # see segment enum below
    target_role_class: "engineering_manager" # see role-class enum; NOT a person
    evidence_source_url: "https://www.subsea7.com/en/our-fleet.html"  # public, verified
    personalization_hook: "Seven Borealis fleet expansion in GoM 2026Q1"  # short, public-facts only
    artifact_id: "brochure_v1_tier1"        # see artifact-id enum
    send_channel: "email_personal"          # email_personal | linkedin
    send_state: "SCHEDULED"                 # see state enum below
    send_date_utc: null                     # ISO 8601 UTC; populated on SENT
    followup_due_utc: null                  # populated on SENT (Day 3 / 7 / 14 / 30)
    response_class: null                    # populated on REPLIED / NEUTRAL / NEGATIVE / NO_REPLY
    fallback_applied: null                  # F1..F5 (mirrors prospect-demo-sop.md) or null
    last_legal_scan_utc: null               # required to be non-null before state -> SENT
    notes_public: null                      # short public-safe annotation; default null
```

### 3.1 Forbidden fields in the public file

The following keys MUST NOT appear in `send-tracker.public.yaml`:

- `contact_name`, `name`, `first_name`, `last_name`
- `contact_email`, `email`, `email_address`, `to_address`
- `contact_phone`, `phone`, `mobile`
- `contact_linkedin_url`, `linkedin`, `linkedin_url`
- `cv_link`, `resume_link`
- Any free-text field that quotes a private email, phone number, or full personal name.

A pre-commit check (future issue scope) greps the public file for these keys and rejects commits that introduce them.

### 3.2 Enums

```yaml
send_state_enum:
  - SCHEDULED            # row created, not yet sent
  - SENT                 # send dispatched; legal scan was passed
  - REPLIED              # any reply received; classify response_class next
  - MEETING_SCHEDULED    # call/Calendly slot booked
  - CLOSED_WON           # paid engagement initiated
  - CLOSED_LOST          # explicit no, opt-out, or after Template 6 break-up + Day 30 silence
  - FAILED_SEND          # SMTP/LinkedIn delivery failure (terminal — see prospect-demo-sop.md analog)

response_class_enum:
  - POSITIVE
  - NEUTRAL
  - NEGATIVE
  - NO_REPLY            # set after Day 30 if no response

send_channel_enum:
  - email_personal       # via authorized personal email (per email-outreach-templates.md §Usage Notes)
  - linkedin             # connection note + DM via personal LinkedIn

tier_enum: [1, 2, 3]    # matches #2554 contractor-matrix tier classification

segment_enum:
  - heavy_lift
  - heavy_lift_pipelay
  - pipelay
  - subsea_construction
  - imr_light_construction
  - offshore_wind_installation
  - regional_niche
  - other

target_role_class_enum:
  # Role families only — never a person's name. The private file carries the person.
  - engineering_manager
  - vp_engineering
  - cto
  - operations_director
  - tender_manager
  - fleet_manager
  - business_development
  - independent_advisor

artifact_id_enum:
  # Versioned artifact IDs the brochure outline can produce.
  - brochure_v1_tier1
  - brochure_v1_tier2
  - brochure_v1_tier3
  - methodology_note_v1
  - demo3_mudmat_screening
  - demo5_rigid_jumper

fallback_applied_enum:
  # Mirrors docs/gtm/prospect-demo-sop.md F1-F5 codes for consistency.
  - F1   # refuse + email back
  - F2   # closest canonical vessel
  - F3   # canonical-default field
  - F4   # one clarification email
  - F5   # reduced-scope analysis
```

## 4. Private companion schema (`send-tracker.private.yaml`)

This file is **gitignored**. It must never be committed. The schema is the public schema **plus** the contact-detail fields:

```yaml
# docs/gtm/intake/send-tracker.private.yaml
# Private outbound send tracker. PII permitted ONLY here.
# Path is enforced by .gitignore. Never `git add -f` this file.
schema_version: 1
issue: 2556
generated_utc: 2026-04-29T00:00:00Z

rows:
  - prospect_id_hash: "9f3a2b7d12c4e8f0"        # joins to public file
    # All public-row fields repeat here (so the private file is self-contained
    # for send-time use). Then the private-only fields below:
    contact_name: "<full name>"
    contact_email: "<email>"
    contact_phone: null                          # optional
    contact_linkedin_url: "<url>"                # optional
    source_of_contact: "<how you got the contact: company website, conf, intro>"
    last_human_touch_notes: |
      <free-text private notes only the operator sees; e.g. "Met at OTC 2025"
       or "intro by <person>"; ALL personal references stay here>
```

### 4.1 Gitignore enforcement

`.gitignore` adds:

```gitignore
# Outbound send-tracker private companion (#2556) — NEVER commit.
docs/gtm/intake/send-tracker.private.yaml
docs/gtm/intake/*.private.yaml
docs/gtm/intake/*.private.yml
```

The plan TDD checklist confirms `git check-ignore` matches the path. A reviewer can quickly audit whether the file is properly gitignored without inspecting its contents.

### 4.2 Recovery / loss tolerance

The private file is local-only and not backed up by git. Operator responsibility:

- Keep a local encrypted backup (e.g., `~/.local/state/gtm/send-tracker.private.yaml.gpg`).
- Never `scp` the private file unencrypted between machines.
- Loss of the private file does not break the public ledger — public state remains valid; only the contact join is lost. Reconstruction requires re-collecting contact details from the source-of-record (LinkedIn / contact_export).

## 5. Lifecycle and state transitions

```
SCHEDULED ──────► SENT ──┬──► REPLIED ──┬──► MEETING_SCHEDULED ──► CLOSED_WON
                          │              │
                          │              ├──► CLOSED_LOST
                          │              │
                          │              └──► (stay in REPLIED until classified)
                          │
                          ├──► NO_REPLY (auto after Day 30) ──► CLOSED_LOST
                          │
                          └──► FAILED_SEND (terminal)

Any state ──► UNSUBSCRIBED  (immediate; record reason; never revert)
```

Required gates before each transition:

| From → To | Gate |
|---|---|
| SCHEDULED → SENT | `last_legal_scan_utc` is non-null AND scan exit-code 0 within 24 h |
| SENT → REPLIED | manual operator entry or Gmail-triage signal (#1971) |
| REPLIED → MEETING_SCHEDULED | calendar artifact exists |
| Any → UNSUBSCRIBED | recipient explicit request; remove from sequence per `email-outreach-templates.md` §Usage Notes |

## 6. Legal-sanity gate (mandatory before any SENT transition)

Mirrors `docs/BUSINESS_BRAIN.md` "Legal Sanity Gates for Public Artifacts":

```
require: artifact provenance recorded (artifact_id resolves to a versioned brochure file)
require: public-vs-private inputs identified (this schema is the contract)
require: methodology citations attached (brochure has citations per outline §5)
require: scripts/legal/legal-sanity-scan.sh --diff-only on brochure source: exit 0
require: no client-identifying content in artifact (visual + grep verified)
=> if all true: set last_legal_scan_utc = now_utc; allow state -> SENT
=> else: stay in SCHEDULED; record blocker in notes_public
```

## 7. Reporting / dashboards (out of scope, but schema supports)

The schema is intentionally simple-to-aggregate so a downstream issue can produce:

- response rate by tier (SENT-count / REPLIED-count grouped by `tier`)
- segment coverage (`segment` distribution across SENT)
- followup overdue (`followup_due_utc < now_utc AND send_state IN [SENT, REPLIED]`)
- artifact-version performance (`response_class` grouped by `artifact_id`)

Implementing the dashboard is **not** in this issue's scope; the schema must just not preclude it.

## 8. Migration path from inbound `deliveries-log.md`

`docs/gtm/deliveries-log.md` is for inbound prospect-demo deliveries (NDA, dual-channel publish, demo report URL). It is **not** replaced by this tracker. Cross-link patterns:

- An outbound send (this tracker) that produces a positive reply may trigger an inbound demo delivery (`deliveries-log.md`); the prospect_id_hash carries forward, so the two ledgers can be joined offline.
- The `fallback_applied` enum in this tracker uses the same F1–F5 codes as `deliveries-log.md` to keep operator vocabulary consistent.

## 9. Open questions for plan-review

1. Salt management: store in `~/.config/gtm/tracker.env` per machine vs in `1Password`? Default proposal: `1Password` reference + machine-local cache.
2. Should send-state transitions be append-only (event-log) or in-place edits to YAML rows? Default proposal: in-place for the active table; append-only for an `events` sub-list per row to retain audit history.
3. Should `notes_public` allow free-text at all, or only enum'd reason codes? Default proposal: free-text but pre-commit grep blocks any field that looks like an email/phone.
4. Cross-machine sync: the private file is per-machine. Do we accept that the home-win machine can't initiate sends if the file lives on ace-linux-1? Default proposal: yes — sends originate from a single operator-authorized machine, default ace-linux-1 (per `BUSINESS_BRAIN.md` machine table).

## 10. Cross-references

- Brochure outline (companion): `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
- Plan: `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`
- Inbound demo SOP (analogous infrastructure): `docs/gtm/prospect-demo-sop.md`
- Inbound delivery log: `docs/gtm/deliveries-log.md`
- Email templates: `docs/gtm/email-outreach-templates.md`
- Business-Brain legal-sanity gates: `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts"
