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