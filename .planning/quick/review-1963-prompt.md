# Adversarial Review Request: Issue #1963

You are an independent adversarial reviewer. Find gaps, risks, missing edge cases, missing retrieval, unclear scope boundaries, unsafe assumptions, and workflow/governance violations. Do NOT rubber-stamp.

Return verdict as one of: APPROVE, MINOR, MAJOR.

Required output format:
1. Verdict
2. Ready for user approval: Yes/No
3. Retrieval adequacy: adequate/insufficient
4. Top blockers (numbered)
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Context:
- Repository: workspace-hub
- Review type: plan-stage adversarial review
- User expectation: strong adversarial review via external providers (Codex and Gemini)
- Mandatory workflow: Issue -> Resource Intel -> Draft Plan -> Adversarial Review -> status:plan-review -> USER APPROVES -> implementation
- Focus on whether the plan is actually approval-ready, not whether the project idea is good.

GitHub issue metadata:
- Issue: #1963
- Title: feat: Multi-account Gmail management — 3 accounts, contact triage, unsubscribe & touchbase automation
- URL: https://github.com/vamseeachanta/workspace-hub/issues/1963
- Labels: enhancement, priority:high, cat:infrastructure

GitHub issue body:
## Overview

Enable unified multi-account Gmail management from the CLI/agent layer. Three accounts, each with distinct purpose, contact base, and handling rules.

## Accounts

| Account | Purpose | Contacts Repo | Domain |
|---|---|---|---|
| `vamsee.achanta@aceengineer.com` | Engineering consulting, GTM, client comms | `aceengineer-admin` (1,306 contacts) | Business/Professional |
| `achantav@gmail.com` | Personal, career networking, subscriptions | `aceengineer-admin` (1,157 contacts) | Personal |
| `skestatesinc@gmail.com` | Real estate LLC, tenant/vendor comms | `sabithaandkrishnaestates` | Business/RE |

## Architecture

### Layer 1: Authentication & Transport
- [ ] Install himalaya CLI (for IMAP/SMTP — lightweight, no OAuth dance)
- [ ] Configure 3 Gmail accounts with App Passwords in `~/.config/himalaya/config.toml`
- [ ] Verify Google Workspace OAuth setup for accounts needing Calendar/Drive/Sheets (aceengineer only)
- [ ] Create `scripts/email/gmail-multi-account.sh` — wrapper that routes `--account` flag

### Layer 2: Contact Management
- [ ] Normalize `aceengineer-admin/admin/contacts/aceengineer_contacts.csv` — clean duplicates, parse names, categorize (client/vendor/recruiter/newsletter)
- [ ] Normalize `aceengineer-admin/admin/contacts/achantav_contacts.csv` — same cleanup
- [ ] Create `sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv` from existing key_contacts.md + fd_corporate_contact_maintenance.md
- [ ] Build `scripts/email/contact-classifier.py` — categorize contacts as: VIP, client, vendor, recruiter, newsletter, spam, unknown
- [ ] Tag contacts with `touchbase` flag (people to maintain relationship with)
- [ ] Tag contacts with `unsubscribe` flag (newsletters/marketing to purge)

### Layer 3: Email Triage Skill
- [ ] Create skill `email/gmail-triage` — multi-account inbox scan, categorize, and recommend actions
  - Scan each inbox for unread
  - Classify: urgent/actionable/FYI/newsletter/spam
  - Cross-reference sender against contacts DB
  - Flag unknown senders for contact-add or unsubscribe
  - Generate daily digest

### Layer 4: Action Handlers
- [ ] Create skill `email/gmail-unsubscribe` — identify and execute unsubscribe from marketing/newsletters
  - Scan for `List-Unsubscribe` headers
  - Batch unsubscribe with confirmation
  - Move to trash after unsubscribe
- [ ] Create skill `email/gmail-touchbase` — periodic outreach to tagged contacts
  - Pull contacts tagged `touchbase`
  - Check last interaction date
  - Draft personalized check-in emails
  - Queue for user approval before sending
- [ ] Create skill `email/gmail-responder` — draft replies for actionable emails
  - Match email context to account domain
  - aceengineer: professional engineering tone
  - achantav: casual/personal tone  
  - skestates: business/formal landlord tone

### Layer 5: Cron Automation
- [ ] Daily morning inbox scan (all 3 accounts) — cron job delivering digest to Telegram/CLI
- [ ] Weekly touchbase reminder — contacts due for outreach
- [ ] Monthly unsubscribe sweep — identify new newsletter subscriptions

## Account-Specific Rules

### vamsee.achanta@aceengineer.com
- Priority: client emails, RFPs, invoice responses
- Auto-label: GTM prospects, active clients, vendors
- Touchbase: engineering contacts, potential clients from GTM pipeline
- Link to: `aceengineer-strategy/` prospect data

### achantav@gmail.com  
- Priority: personal finance, family, career
- Aggressive unsubscribe: marketing, social media notifications
- Touchbase: close professional network, alumni
- Filter: separate personal from professional spillover

### skestatesinc@gmail.com
- Priority: tenant communications (Family Dollar), tax/legal
- Auto-label: tenant, insurance, tax, maintenance
- Touchbase: property management contacts, tax advisors
- Link to: `sabithaandkrishnaestates/` deal files

## Dependencies
- himalaya CLI installed on ace-linux-1
- Gmail App Passwords generated for all 3 accounts (2FA must be enabled)
- Contact CSVs cleaned and normalized

## Deliverables
1. Working 3-account email access from CLI
2. Cleaned/categorized contact databases
3. `gmail-triage` skill with daily digest
4. `gmail-unsubscribe` skill
5. `gmail-touchbase` skill  
6. Cron jobs for automated monitoring

## Agent Assignment
- **Hermes (ace-linux-1)**: Primary email operator — cron jobs, daily digest, inbox scans
- **Claude Code (CLI)**: Skill creation, contact normalization scripts, code review
- **Codex**: Contact classifier ML/heuristics, unsubscribe pattern detection
- **Gemini**: Research best practices for email automation, touchbase templates

---

## Execution Plan & Issue Dependency Graph

```
PHASE 1 — Infrastructure (Week 1)
  #1964  Install gmail-mcp-multiauth + himalaya        [BLOCKING — everything depends on this]
         Requires: GCP project, OAuth setup, App Passwords
         User action: browser OAuth flow for 3 accounts

PHASE 2 — Contact Normalization (Week 1-2, parallel with Phase 1 partial)
  #1965  Normalize ace contacts (1,306 rows)            [Independent]
  #1966  Normalize personal contacts (1,140 rows)       [Independent]
  #1967  Build skestates contacts (~23 entries)          [Independent]
  #1970  Cross-account dedup (132 overlaps)              [Depends: #1965, #1966]

PHASE 3 — Account-Specific Triage (Week 2-3, after Phase 1+2)
  #1971  ace triage workflow                             [Depends: #1964, #1965]
  #1968  personal triage workflow                        [Depends: #1964, #1966]
  #1969  skestates triage workflow                       [Depends: #1964, #1967]
```

## Child Issues
- #1964 — infra: Install gmail-mcp-multiauth
- #1965 — data: Normalize ace contacts
- #1966 — data: Normalize personal contacts
- #1967 — data: Build skestates contacts
- #1968 — feat: personal triage workflow
- #1969 — feat: skestates triage workflow
- #1970 — feat: Cross-account dedup
- #1971 — feat: ace triage workflow


Plan under review (docs/plans/2026-04-09-issue-1963-email-infrastructure-cluster-a.md):
# Plan for #1963: Email Infrastructure Cluster A

> Status: draft
> Complexity: T3
> Date: 2026-04-09
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/1963
> Review artifacts: pending — adversarial plan review not yet run

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/email/gmail-archive-extract.py` — current Gmail extraction implementation, but archive-first and delete-flag-driven.
- Found: `scripts/email/gmail-digest.py` — multi-account digest scan with contact enrichment and priority heuristics.
- Found: `scripts/email/contact-normalizer.py` — canonical contact normalization pipeline for ace and personal contacts.
- Found: `scripts/email/email-routing.yaml` — domain routing table with `DELETE`, `REVIEW`, and repo destinations.
- Found: `docs/email/WORKFLOW.md` — already documents the target queue model from #2017.
- Found: `scripts/legal/legal-sanity-scan.sh` — legal gate available for pre-commit / pre-write workflow.

### GitHub issues consulted
- #1963 — parent: multi-account Gmail management
- #2017 — governing design: email-as-queue
- #1987 — legacy cleanup pipeline; conflicts with queue-first design and must be treated as superseded guidance
- #2024 — extraction/action pipeline rewrite
- #2025 — per-domain extraction templates
- #2026 — state tracking system

### Documents consulted
- `.planning/notes/2026-04-09-email-infrastructure-cluster-a-discuss-phase.md`
- `docs/email/WORKFLOW.md`
- `docs/plans/README.md`
- `docs/handoffs/session-2026-04-08-strict-planning-workflow.md`
- `knowledge/wikis/engineering/wiki/entities/gsd-framework.md`
- Session recall: 2026-04-07 email infrastructure restructuring session

### Gaps identified
- No queue-native extraction pipeline exists yet.
- No `scripts/email/templates/` registry exists yet.
- No test suite exists for email extraction/state logic.
- Routing still points primarily to archive-style `docs/email/...` destinations.
- No implemented Gmail label lifecycle or local `~/.hermes/email-state.yaml` state machine exists.
- Daily digest is not yet state-aware.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Discuss-phase notes | `.planning/notes/2026-04-09-email-infrastructure-cluster-a-discuss-phase.md` |
| This plan | `docs/plans/2026-04-09-issue-1963-email-infrastructure-cluster-a.md` |
| Plans index update | `docs/plans/README.md` |
| Existing workflow doc | `docs/email/WORKFLOW.md` |
| Existing extraction script | `scripts/email/gmail-archive-extract.py` |
| Existing digest script | `scripts/email/gmail-digest.py` |
| Existing routing config | `scripts/email/email-routing.yaml` |
| Planned new pipeline | `scripts/email/gmail-extract-and-act.py` |
| Planned template registry | `scripts/email/templates/*.yaml` |
| Planned tests | `tests/email/test_gmail_extract_and_act.py` |
| Planned tests | `tests/email/test_email_state_machine.py` |
| Planned tests | `tests/email/test_email_templates.py` |

---

## Deliverable

A queue-first, multi-account email architecture plan for Cluster A that replaces archive-first behavior with template-driven extraction, Gmail-label-plus-local state tracking, and safe delete-later lifecycle rules, anchored by #1963 and decomposed into #2024, #2025, and #2026.

---

## Pseudocode

```text
function triage_account(account):
    load contact database for account
    fetch unread/recent Gmail messages
    enrich with sender, domain, contact match, and current thread state
    classify into actionable, awaiting-reply, completed, noise, or review-needed
    return triage batch

function extract_and_act(message, template_registry):
    select template by domain/account/message type
    parse structured fields from subject/body/attachments
    validate required extracted fields
    write structured YAML artifact to destination repo/path
    run legal-sanity-scan before commit
    apply Gmail label and local state transition to extracted

function transition_thread(thread, event):
    if event == operator_replied:
        move extracted -> awaiting-reply
    if event == topic_resolved:
        move extracted|awaiting-reply -> completed
    if event == new_inbound_reply:
        move awaiting-reply|completed -> inbox
    if event == noise_detected:
        move inbox -> noise

function deletion_sweep(state_log, gmail):
    for each thread in state_log:
        if state == noise:
            delete immediately once policy confidence allows
        if state == completed and grace_period_elapsed and no new reply:
            delete from Gmail and log deletion
        if state == awaiting-reply:
            never auto-delete

function daily_digest(account):
    summarize triage results, unknown domains, pending replies, and threads eligible for deletion
    include exceptions requiring template or routing updates
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/email/test_gmail_extract_and_act.py` | TDD for extraction pipeline behavior |
| Create | `tests/email/test_email_state_machine.py` | TDD for label/state transitions and grace-period rules |
| Create | `tests/email/test_email_templates.py` | TDD for template parsing and validation |
| Create | `scripts/email/gmail-extract-and-act.py` | queue-first extraction/action pipeline |
| Create | `scripts/email/templates/cre-listings.yaml` | first structured extraction template |
| Create | `scripts/email/templates/client-email.yaml` | client/project extraction template |
| Create | `scripts/email/templates/tenant-property.yaml` | tenant/property extraction template |
| Create | `scripts/email/templates/tax-financial.yaml` | tax/financial extraction template |
| Create | `scripts/email/templates/invoice-payment.yaml` | invoice/payment extraction template |
| Modify | `scripts/email/gmail-digest.py` | make digest state-aware and exception-aware |
| Modify | `scripts/email/email-routing.yaml` | migrate from archive destinations to template + structured destination semantics |
| Deprecate/replace | `scripts/email/gmail-archive-extract.py` | retire archive-first behavior after parity is reached |
| Update | `docs/email/WORKFLOW.md` | align docs with final implementation details |
| Update | `docs/plans/README.md` | add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_selects_cre_template_for_sandsig_domain` | domain/template matching works | account=`ace`, domain=`sandsig.com` | `cre-listings` template selected |
| `test_extracts_core_cre_fields_from_listing_email` | structured extraction parses known listing fields | representative Sands IG subject/body fixture | YAML payload with tenant, price, cap_rate, state, building_sf |
| `test_rejects_template_with_insufficient_fields` | template validation enforces minimum field count | malformed template fixture | validation error |
| `test_marks_thread_extracted_after_successful_write` | successful extraction updates state | extracted message fixture | Gmail/local state = `extracted` |
| `test_transition_to_awaiting_reply_after_operator_response` | reply lifecycle transition works | thread in `extracted` + reply event | state = `awaiting-reply` |
| `test_completed_thread_respects_grace_period` | delete-later safety is enforced | completed thread, age < 7 days | not deleted |
| `test_completed_thread_deletes_after_grace_without_new_reply` | eligible deletions are permitted | completed thread, age >= 7 days, no reply | delete action scheduled/executed |
| `test_new_reply_reactivates_completed_thread` | reactivation works | completed thread + new inbound reply | state returns to inbox/active |
| `test_noise_thread_can_be_deleted_without_repo_write` | noise flow bypasses extraction | marketing/newsletter fixture | deletion path, no artifact write |
| `test_digest_reports_unknown_domains_for_learning_loop` | digest surfaces learning backlog | messages from untemplated domains | unknown-domain exception list |
| `test_archive_script_path_is_not_used_for_new_extractions` | raw archive behavior is blocked in new path | extraction run fixture | no raw markdown dump written |

---

## Acceptance Criteria

- [ ] Plan approved by user after adversarial review
- [ ] All new tests pass: `uv run pytest tests/email -v`
- [ ] Queue-first pipeline exists in `scripts/email/gmail-extract-and-act.py`
- [ ] No new workflow writes raw email body archives to repo destinations
- [ ] Gmail-label plus local-state lifecycle is implemented and covered by tests
- [ ] Template registry exists with at least 5 domain/type templates
- [ ] `gmail-digest.py` surfaces state-aware queue information and unknown-template exceptions
- [ ] `email-routing.yaml` no longer treats archive destinations as the primary workflow contract
- [ ] `docs/email/WORKFLOW.md` matches implemented behavior
- [ ] Legal scan is part of the extraction commit path

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | not yet run |
| Codex | pending | not yet run |
| Gemini | pending | not yet run |

Overall result: pending

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- Risk: archive-first code may be accidentally extended instead of replaced; enforce #2017 as the governing contract.
- Risk: deletion behavior is destructive; all destructive actions need dry-run and state-gated tests first.
- Risk: routing migration spans multiple destination repos and may surface path/ownership issues.
- Risk: template extraction quality for heterogeneous client emails may lag behind structured CRE listing emails.
- Open: whether `email-routing.yaml` should remain a simple YAML config or evolve into a richer template registry index.
- Open: whether immediate deletion for `noise` should be enabled from day one or only after confidence thresholds are proven with dry runs.
- Open: whether `gmail-archive-extract.py` should be renamed in place or replaced by a new script with a later cutover.

---

## Complexity: T3

T3 — This is a cross-cutting architecture migration affecting triage, extraction, routing, state tracking, deletion safety, tests, and documentation across multiple accounts and dependent issues.

Review questions — address ALL:
1. Is the plan specific enough to execute without hidden design decisions surfacing during implementation?
2. Does the resource intelligence satisfy the repo's planning contract, or are important sources missing?
3. Are TDD scope, acceptance criteria, files-to-change, and risks concrete and falsifiable?
4. Are there unmade decisions that should be resolved before user approval?
5. Are there sequencing/dependency problems relative to child issues, parent issues, or migration risk?
6. Should this plan be approved as-is, revised, or split?
