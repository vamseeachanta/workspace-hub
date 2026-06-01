# Plan for [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900): Deckhand board-level multi-platform fanout sequencing

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-05-31
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2900
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** pending — this board-level plan has not entered adversarial review

---

## Resource Intelligence Summary

### Existing repo code

- Found: `/home/vamsee/.hermes/hermes-agent/gateway/delivery.py` — existing gateway delivery surface includes Telegram-specific target parsing and delivery functions; it is the likely extraction point for shared target parsing / fanout preflight.
- Found: `/home/vamsee/.hermes/hermes-agent/tools/send_message_tool.py` — existing interactive `send_message` tool has a single-target-oriented surface and platform-specific target resolution; it is the likely implementation surface for later multi-target operator fanout.
- Found: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/telegram.py` — Telegram adapter exists and is the currently working conversational path.
- Found: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py` — WhatsApp adapter exists, but production fanout will need bridge/session/recipient-readiness verification before all-three fanout can be claimed.
- Found: `/home/vamsee/.hermes/hermes-agent/tests/gateway/test_teams.py` and `/home/vamsee/.hermes/hermes-agent/tests/plugins/test_teams_pipeline_plugin.py` — Teams test surfaces exist, but live proactive bot delivery will still require Bot Framework / Azure / tenant / public endpoint readiness evidence.
- Gap: there is no board-level canonical plan that sequences the parent issue and child issues [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)-[#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) as one reviewable GitHub planning tree.

### Standards

Not applicable — this is workflow / integration planning, not an engineering standards calculation issue.

### LLM Wiki pages consulted

No relevant wiki pages were required for this board-level planning artifact. The work concerns Hermes messaging/runtime integration and workspace-hub GitHub issue governance.

### Documents and issues consulted

- Parent issue [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) — defines the umbrella safety boundary: explicit notification fanout only, origin-only conversations by default, text-first scope, and no implementation before canonical plans + adversarial review + user approval.
- Child issue [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) — scopes platform parity reconnaissance and blocker classification for Telegram, WhatsApp, Teams, and Signal.
- Child issue [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) — scopes the shared delivery-group / fanout contract.
- Child issue [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) — scopes the origin-only conversation policy guardrail.
- Child issue [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) — scopes `send_message` multi-target text fanout, blocked until the [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) contract exists.
- Child issue [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) — scopes operator setup docs and smoke tests.
- Child issue [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) — records the product/operator-facing name decision: **Deckhand** with slug `deckhand`.
- Preliminary artifact `docs/plans/2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md` — provides initial brainstorming, Markdown Kanban, and safety framing. This canonical plan will supersede it as the board-level control artifact.
- `docs/plans/_template-issue-plan.md` — confirms required fields for canonical issue plans.
- `docs/plans/README.md` — is the local plan index that will link this board-level plan.

### Gaps identified

- The child issues will need separate canonical plans before implementation.
- The first implementation plan will need real platform readiness evidence before claiming Telegram/WhatsApp/Teams/Signal simultaneous delivery.
- The shared contract will need fail-closed target parsing, group authorization, deduplication, and redacted per-target result reporting.
- The conversation path will need tests that prove default replies stay origin-only.
- The operator documentation will need a smoke path that separates local/demo readiness from real Teams bot and WhatsApp bridge readiness.

### Evidence

**Issue statuses** (verified 2026-05-31T10:58:07Z via `gh issue view`):

| Issue | State | Labels | Finding |
|---|---|---|---|
| [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Parent still needs a canonical plan and review; no implementation is authorized. |
| [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Platform parity reconnaissance child exists and is not approved. |
| [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Delivery-group contract child exists and is not approved. |
| [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Origin-only guardrail child exists and is not approved. |
| [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | `send_message` fanout child exists and is blocked by the [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) contract. |
| [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Operator-docs child exists and depends on the readiness/contract shape. |
| [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) | OPEN | `status:needs-plan`, `enhancement`, `priority:medium`, `cat:ai-orchestration`, `domain:integrations` | Naming decision is recorded in comments and body; governance closeout remains available. |

**File existence** (verified 2026-05-31T10:58:07Z):

- EXISTS: `/home/vamsee/.hermes/hermes-agent/gateway/delivery.py`
- EXISTS: `/home/vamsee/.hermes/hermes-agent/tools/send_message_tool.py`
- EXISTS: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/telegram.py`
- EXISTS: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py`
- EXISTS: `/home/vamsee/.hermes/hermes-agent/tests/gateway/test_teams.py`
- EXISTS: `/home/vamsee/.hermes/hermes-agent/tests/plugins/test_teams_pipeline_plugin.py`
- EXISTS: `docs/plans/2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md`
- NEW: `docs/plans/2026-05-31-issue-2900-deckhand-board-level-plan.md`

**Reproduction proofs**:

N/A — this parent issue is governance / architecture planning. It does not allege a runtime failure that can be reproduced directly. Child issue [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) will reproduce or classify the listed platform bugs before implementation planning claims readiness.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This canonical board-level plan | `docs/plans/2026-05-31-issue-2900-deckhand-board-level-plan.md` |
| Preliminary brainstorming artifact | `docs/plans/2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md` |
| Plan index | `docs/plans/README.md` |
| Parent issue | https://github.com/vamseeachanta/workspace-hub/issues/2900 |
| Child issues | [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901), [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902), [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903), [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904), [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905), [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) |
| Future plan reviews | `scripts/review/results/YYYY-MM-DD-plan-2900-{claude,codex,gemini}.md` |
| Candidate Hermes implementation surfaces | `/home/vamsee/.hermes/hermes-agent/gateway/delivery.py`, `/home/vamsee/.hermes/hermes-agent/tools/send_message_tool.py`, `/home/vamsee/.hermes/hermes-agent/gateway/platforms/` |

---

## Deliverable

A canonical board-level control plan will exist for [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900), sequencing child issues [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)-[#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) and defining the approval gates for Deckhand Telegram/WhatsApp/Teams/Signal notification fanout.

---

## Board-level architecture contract

### Path A — conversation replies

Inbound messages from Telegram, WhatsApp, Teams, or Signal will route through the originating adapter and receive replies only on the originating platform/chat by default. This path will not reuse notification delivery groups unless a future privacy/security plan explicitly approves conversation mirroring.

### Path B — explicit notification fanout

An operator or scheduled/proactive workflow will request a notification to an approved delivery group. The resolver will preflight every target, validate authorization, deduplicate targets, reject unsupported media, redact identifiers, and then send text to each configured destination. A validation failure will abort before any send; a transport failure after preflight may produce partial failure with per-target details.

### Text-first boundary

The first implementation wave will be text-only. Media, attachments, voice, and cross-platform live conversation mirroring will stay out of scope unless separate plans pass adversarial review and user approval.

---

## Kanban board of record

### Backlog

- [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) — parent sequencing and review-state authority.
- Candidate follow-up — real GitHub Projects board after `gh` has `project` scope.
- Candidate follow-up — media fanout after media-security validation is fixed or explicitly scoped.
- Candidate follow-up — cross-platform conversation mirroring, if ever desired.

### Ready for planning

- [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) — platform parity reconnaissance.
- [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) — origin-only conversation policy guardrails.
- [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) — naming decision governance closeout.

### Planning / draft

- [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) — this board-level plan.
- [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) — shared delivery group and fanout contract; it can start after [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) begins, but final readiness claims must consume [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) findings.
- [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) — operator docs and setup guide; final docs will follow [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)/[#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) contract decisions.

### Blocked / dependent

- [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) — `send_message` multi-target text fanout; blocked until [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) defines the shared contract.
- Teams live bot delivery — blocked until Azure/Bot Framework/tenant/public endpoint and conversation-reference readiness are verified.
- WhatsApp production delivery — blocked until QR/session persistence, dedicated bot number, bridge health, and recipient opt-in are verified.
- Signal delivery — blocked until adapter availability, QR/session/linking flow, session persistence, recipient/group identifiers, and redaction coverage are verified.
- Media fanout — blocked until media security validation is complete or media remains explicitly out of scope.

### Plan review

- None yet. No issue in this tree will move to `status:plan-review` until its canonical plan and adversarial review artifacts exist.

### Approved / implementation-ready

- None. Implementation remains blocked.

### Done / decision recorded

- [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) — Deckhand selected as the baseline product/operator-facing name; issue can be closed after downstream plan/docs references are confirmed.

---

## Sequencing plan

### Wave 0 — Board and governance hygiene

1. This parent issue will keep the umbrella scope, board lanes, and dependency order.
2. `docs/plans/README.md` will point at this canonical board-level plan rather than treating the preliminary artifact as approval-ready.
3. The parent issue will receive a comment linking this plan and stating that the tree remains `status:needs-plan` until adversarial review runs.
4. [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) will either stay open as the naming decision record or close after the user confirms no further naming review is needed.

### Wave 1 — Platform parity reconnaissance

Primary issue: [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)

This plan will produce the readiness matrix before shared fanout implementation is approved. It will classify:

- Telegram text send path and known `send_message` failure risk.
- WhatsApp bridge/session/identifier/group-DM behavior.
- Teams Bot Framework / Azure / tenant / HTTPS endpoint / proactive conversation-reference requirements.
- Signal adapter/setup readiness, recipient identifiers, QR/session behavior, linked-device persistence, and group/DM behavior.
- Redaction coverage for Telegram chat IDs, WhatsApp phone/JID/session identifiers, Teams tenant/conversation/service URLs, Signal numbers/UUIDs/session artifacts, webhook URLs, tokens, and `.env` values.
- Existing related bugs as blocker / limitation / dependency / out-of-scope.

### Wave 2 — Shared contract and conversation guardrails

Primary issues: [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) and [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903)

The [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) plan will define a shared text delivery contract:

- target grammar and reserved names (`origin`, `all`, explicit platform targets, named groups),
- delivery-group config schema,
- authorization / allowlist behavior,
- fail-closed preflight,
- deterministic deduplication,
- redacted per-target result envelope,
- backward compatibility with existing cron/proactive delivery strings.

The [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) plan will define the conversation safety guardrail:

- default `origin_only` replies,
- no implicit cross-platform mirroring,
- no reuse of source-specific thread/topic metadata for unrelated notification targets,
- regression tests for Telegram/WhatsApp/Teams/Signal origin-only reply behavior.

### Wave 3 — Interactive/operator `send_message` text fanout

Primary issue: [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904)

This plan will begin only after the shared contract is available. It will extend `send_message` to support approved explicit target lists or named delivery groups while preserving single-target behavior. It will return structured per-target results, abort atomically on validation failures, and reject multi-target media until a separate media-security plan approves it.

### Wave 4 — Operator documentation and smoke operations

Primary issue: [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905)

This plan will produce operator docs that explain:

- Deckhand naming and the Hermes Gateway relationship,
- Telegram bot/home-channel setup,
- WhatsApp bridge QR/session/dedicated-number requirements,
- Teams Bot Framework / Azure / tenant / public endpoint requirements,
- Signal app QR/linking/session-persistence requirements,
- onboarding flow: auto-select the platform when the QR is scanned inside a known app flow; require explicit operator platform selection when a generic QR scanner is used,
- technical example scope areas where Deckhand can help, starting with GTM workflows and then repo-ecosystem operations,
- explicit out-of-scope areas, including no commitment to preliminary responses within 24 hours unless a separate support/SLA workflow is planned and approved,
- safe delivery-group examples with redacted identifiers,
- text-only smoke tests for Telegram-only, Telegram+WhatsApp, Telegram+Teams, Telegram+Signal, and all-configured fanout,
- troubleshooting for paused adapters, circuit breakers, unavailable platforms, and redacted failure reports.

---

## Pseudocode

```text
function plan_deckhand_tree():
    keep [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) as parent board and safety authority
    mark all child implementation issues as not-approved until their own plans pass review
    run [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) read-only readiness reconnaissance first
    use [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) findings to constrain [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) target grammar and platform support claims
    draft [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) origin-only policy in parallel with [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) because it protects a separate path
    block [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) until [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) defines validation, fanout, and result contracts
    block [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) final smoke docs until [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)/[#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) decide real setup and syntax
    keep media and conversation mirroring out of scope until separate plans are approved
```

```text
function safe_notification_fanout_contract(request):
    resolve explicit targets or named group
    validate every target and group authorization before sending anything
    reject unsupported media for multi-target requests
    deduplicate platform + target + thread/topic keys
    redact sensitive identifiers in logs and results
    send text to each target only after preflight passes
    return success, partial_failure, failed, or validation_failed with per-target records
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-31-issue-2900-deckhand-board-level-plan.md` | Canonical parent board-level plan. |
| Modify | `docs/plans/README.md` | Point plan index at canonical board-level plan and mark status as draft. |
| Comment | [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) | Link canonical plan and current gate status. |
| Future create | `docs/plans/YYYY-MM-DD-issue-2901-*.md` | Platform parity reconnaissance child plan. |
| Future create | `docs/plans/YYYY-MM-DD-issue-2902-*.md` | Shared delivery group / fanout contract child plan. |
| Future create | `docs/plans/YYYY-MM-DD-issue-2903-*.md` | Conversation policy guardrail child plan. |
| Future create | `docs/plans/YYYY-MM-DD-issue-2904-*.md` | `send_message` text fanout child plan. |
| Future create | `docs/plans/YYYY-MM-DD-issue-2905-*.md` | Operator docs child plan. |

---

## TDD Test List

This parent plan is governance / sequencing work and will not implement runtime code. Child implementation plans will include test-first requirements. Expected test themes are:

| Future child | Test theme | What it will verify |
|---|---|---|
| [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) | Readiness smoke matrix | Platform-specific send/readiness checks are classified with evidence and redacted outputs. |
| [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) | Delivery group parsing | Explicit targets and named groups resolve deterministically; unknown groups/platforms fail closed. |
| [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) | Preflight atomicity | Invalid or unauthorized target aborts before any platform send. |
| [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) | Result envelope | Per-target status is returned with redacted identifiers and retryable/unsupported-media flags. |
| [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) | Origin-only replies | Inbound Telegram/WhatsApp/Teams/Signal conversations reply only to the source platform by default. |
| [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) | Backward compatibility | Single-target `send_message` behavior remains unchanged. |
| [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) | Text fanout | Approved multi-target text fanout sends to configured targets and reports per-target outcomes. |
| [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) | Operator smoke | Docs provide runnable smoke tests and do not claim media/mirroring parity. |

---

## Acceptance Criteria

- [ ] This canonical board-level plan is indexed in `docs/plans/README.md`.
- [ ] [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) has a comment linking this plan and stating current gate status.
- [ ] All issue references in the plan render as Markdown links.
- [ ] The board separates ready, draft, blocked, plan-review, approved, and done lanes.
- [ ] [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) remains explicitly blocked by the [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) contract.
- [ ] The first implementation wave remains text-only.
- [ ] Cross-platform conversation mirroring remains out of scope unless separately planned, reviewed, and approved.
- [ ] No issue in the tree is moved to `status:plan-review` until plan review artifacts exist.
- [ ] No issue in the tree is moved to `status:plan-approved` by the agent.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not yet dispatched. |
| Codex | PENDING | Not yet dispatched. |
| Gemini | PENDING | Not yet dispatched. |

**Overall result:** PENDING — this board-level plan is a draft and is not approval-ready until adversarial review completes and any findings are resolved.

---

## Risks and Open Questions

- **Risk:** WhatsApp, Teams, and Signal may have code/test surfaces but still fail live bot delivery without bridge/session/Azure/tenant/public-endpoint setup. [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) will classify this before implementation.
- **Risk:** `all` / `origin,all` expansion can become unsafe if new platforms are added later. The shared contract will default sensitive sends to explicit approved targets.
- **Risk:** Media fanout can leak or mis-handle unsupported attachments. The first implementation wave will stay text-only.
- **Risk:** Operator docs may overclaim readiness if they blur demo/incoming-webhook behavior with real Teams bot behavior. [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) will separate these modes.
- **Open:** Whether a real GitHub Projects board should be created later after `gh` has `project` scope.
- **Open:** Whether Deckhand should remain operator/internal-facing only or also appear in client-facing copy.

---

## Complexity: T3

**T3** — multi-platform messaging including Signal as an additional channel, privacy-sensitive target routing, multiple dependent child issues, cross-provider adversarial review requirement, and separate implementation surfaces across Hermes Gateway, platform adapters, `send_message`, cron/proactive delivery, and operator docs.
