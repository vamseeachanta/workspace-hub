# Plan for #2024: gmail-extract-and-act pipeline — rewrite gmail-archive-extract.py for extract-first, delete-later queue model

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2024
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/email/gmail-archive-extract.py` is the current implementation (~470 lines) and currently fetches full Gmail messages, routes by sender domain via `email-routing.yaml`, saves raw markdown/email artifacts into repo paths, optionally parses spreadsheets, and can delete messages via `--delete`.
- Found: `scripts/email/email-routing.yaml` already defines the current routing policy, including explicit CRE listing routes to `assethold/data/cre-listings` and delete/review actions.
- Found: `scripts/email/templates/cre-listing.yaml` already exists as a structured extraction template and explicitly says it is intended for `scripts/email/gmail-extract-and-act.py (planned)`.
- Found: the current script already contains a legal scan surface and deny-list handling, so the new pipeline should reuse and strengthen that rather than invent a second legal gate path.
- Gap: no `gmail-extract-and-act.py` implementation exists yet, no local state file contract is defined, and the existing script is built around raw email archiving rather than structured extraction + queue state transitions.

### Standards
N/A — email/data-pipeline/workflow task

### Documents consulted
- GitHub issue #2024 — required migration from raw archive model to extract-first queue model.
- `scripts/email/gmail-archive-extract.py` — current behavior and reusable Gmail/OAuth/extraction helpers.
- `scripts/email/email-routing.yaml` — current sender routing and delete/review policy.
- `scripts/email/templates/cre-listing.yaml` — existing structured extraction template and legal-scan requirement.
- Parent issue #2017 — Email-as-Queue workflow parent context from #2024 body.

### Gaps identified
- No canonical state-file schema for thread lifecycle (`extracted`, `awaiting-reply`, `completed`).
- No explicit deletion state machine yet replaces the current `--delete` flag behavior.
- No plan yet defines which parts of `gmail-archive-extract.py` are retained, wrapped, or replaced.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2024-gmail-extract-and-act-pipeline.md` |
| Existing script to replace/refactor | `scripts/email/gmail-archive-extract.py` |
| New pipeline script | `scripts/email/gmail-extract-and-act.py` |
| Routing rules | `scripts/email/email-routing.yaml` |
| Extraction templates | `scripts/email/templates/` |
| State file | `~/.hermes/email-state.yaml` |
| Tests | `tests/email/` (exact files to be created by implementation) |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A T3 implementation plan for a stateful Gmail extract-and-act pipeline that replaces raw email archiving with structured extraction, thread-state tracking, safe deletion/re-activation logic, and domain-template-driven output.

---

## Pseudocode

```text
load routing rules and extraction templates
query Gmail for candidate messages/threads
for each message/thread:
    classify sender/domain and select template/action
    if action == DELETE:
        mark/delete per policy
    elif action == REVIEW:
        label and defer
    else:
        extract structured fields from subject/body/attachments
        write structured output to target repo path
        update local state file with thread status and metadata
        apply legal scan before commit/writeback
periodically:
    inspect completed threads for grace-period deletion
    inspect completed/awaiting threads for new replies and reactivate when needed
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-13-issue-2024-gmail-extract-and-act-pipeline.md` | canonical plan artifact |
| Create | `scripts/email/gmail-extract-and-act.py` | new extract-first queue pipeline |
| Modify | `scripts/email/gmail-archive-extract.py` | slim, deprecate, or wrap existing behavior as needed |
| Modify | `scripts/email/email-routing.yaml` | align routing semantics with new queue actions if needed |
| Add/Modify | `scripts/email/templates/` | domain-specific extraction templates |
| Create | `tests/email/` | state-machine and extraction tests |
| Update | `docs/plans/README.md` | add plan row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_template_selection_by_sender | correct template/action selected from routing rules | sender domain fixture | expected template/action |
| test_structured_extraction_cre_listing | CRE listing email becomes structured YAML/JSON fields | Sands/LoopNet style fixture | populated structured record |
| test_state_file_transition_extracted_to_completed | thread state changes correctly | extracted thread fixture | completed status |
| test_completed_thread_grace_period_delete | deletion only happens after grace period | completed thread older than threshold | delete action |
| test_new_reply_reactivates_thread | new reply moves thread back to active state | completed/awaiting thread with new message | reactivated state |
| test_no_raw_body_archive_written | new pipeline does not dump full raw email bodies into repo docs paths | normal extraction fixture | structured output only |
| test_legal_scan_blocks_disallowed_output | legal/deny-list hit prevents unsafe write | flagged content fixture | blocked result |

---

## Acceptance Criteria

- [ ] Canonical local plan exists for #2024.
- [ ] Plan defines the state model for extracted / awaiting-reply / completed threads.
- [ ] Plan defines how deletion and re-activation replace the old `--delete` flag semantics.
- [ ] Plan makes explicit whether `gmail-archive-extract.py` is replaced, wrapped, or partially reused.
- [ ] Plan is ready for adversarial review before implementation begins.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Pending | — | Review not yet run |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** legal/compliance rules may require stronger guarantees than the current deny-list approach when structured extraction writes into repo paths.
- **Risk:** Gmail thread semantics can be tricky if deletion/re-activation is modeled at message level instead of thread level.
- **Open:** should the first implementation store state per message or per thread as the canonical unit?
- **Open:** should attachments be persisted selectively, transformed, or merely referenced in state/output metadata?

---

## Complexity: T3

**T3** — new stateful pipeline replacing a live extraction script, with routing, templates, legal scanning, and lifecycle state transitions.
