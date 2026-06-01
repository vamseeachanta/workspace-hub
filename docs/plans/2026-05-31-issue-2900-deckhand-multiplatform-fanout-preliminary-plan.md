# Plan for #2900: Deckhand multi-platform notification fanout

> **Status:** preliminary-draft
> **Complexity:** T3
> **Date:** 2026-05-31
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2900
> **Client:** N/A
> **Review artifacts:** pending — this preliminary plan has not entered adversarial review

---

## Brainstorming outcome

The feature will be treated as **Deckhand**, an operator-facing Hermes chat presence that can send one approved notification to Telegram, WhatsApp, and Microsoft Teams destinations at the same time.

The design will keep two paths separate:

1. **Conversation path:** a user messages Hermes from one platform; Hermes replies only to that origin platform by default.
2. **Notification fanout path:** an explicit notification request uses an approved delivery group to emit text to configured Telegram, WhatsApp, and Teams targets.

The first implementation wave will stay **text-only**. Media, attachments, voice, and cross-platform conversation mirroring will remain deferred until separate planning and security review approve them.

---

## Product framing

- **Display name:** Deckhand
- **Slug / handle candidate:** `deckhand`
- **Role:** practical helper for operator notifications and agent status updates
- **Reasoning:** the name implies crew support rather than command authority. It fits marine/offshore context better than generic "Hermes bot" and avoids the authority/gender problems of names like Toolpusher or Company Man.

---

## Resource Intelligence Summary

### Existing repo / runtime evidence

- Parent issue [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) defines the umbrella scope, safety decisions, architecture drawing, child issues, and explicit no-implementation planning gate.
- Hermes Agent docs at `https://hermes-agent.nousresearch.com/docs/user-guide/messaging/` describe one `hermes gateway` background process that can connect multiple platforms, handle sessions, run cron jobs, expose `/platform list|pause|resume`, and include Telegram, WhatsApp, and Microsoft Teams platform adapters/toolsets.
- Local Hermes version probe returned `Hermes Agent v0.15.1 (2026.5.29)` with project path `/home/vamsee/.hermes/hermes-agent`.
- Local Hermes file discovery found likely implementation surfaces:
  - `/home/vamsee/.hermes/hermes-agent/gateway/delivery.py`
  - `/home/vamsee/.hermes/hermes-agent/tools/send_message_tool.py`
  - `/home/vamsee/.hermes/hermes-agent/gateway/platforms/telegram.py`
  - `/home/vamsee/.hermes/hermes-agent/gateway/platforms/whatsapp.py`
  - Teams gateway/plugin tests under `/home/vamsee/.hermes/hermes-agent/tests/gateway/test_teams.py` and `/home/vamsee/.hermes/hermes-agent/tests/plugins/test_teams_pipeline_plugin.py`
- Existing tests are available for Telegram delivery, WhatsApp formatting/gating, `send_message`, delivery, redelivery dedupe, and Teams runtime wiring.

### Related issue tree

| Issue | Role | Current lane |
|---|---|---|
| [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) | Parent / umbrella | Backlog |
| [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) | Platform parity reconnaissance | Ready for plan drafting |
| [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) | Delivery group + fanout contract | Ready for plan drafting after #2901 starts |
| [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) | Origin-only conversation guardrail | Ready for plan drafting |
| [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) | `send_message` multi-target text fanout | Blocked by #2902 contract |
| [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) | Operator docs and smoke runbook | Follows #2901/#2902 shape |
| [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) | Product naming decision | Decision recorded: Deckhand |

### Constraints

- Delivery groups will be opt-in only.
- Replies will remain origin-only unless a later plan explicitly approves mirroring.
- `all` / `origin,all` expansion will be treated as high-risk because future platform configuration could silently broaden recipients.
- Logs and result artifacts will redact Telegram chat IDs/tokens, WhatsApp phone/JID/session identifiers, Teams conversation/service URLs/tenant IDs, webhook URLs, and `.env` values.
- WhatsApp and Teams readiness will require live deployment verification, not paper parity with Telegram.
- Media fanout will remain blocked until the media-security validation gap is resolved or the implementation remains explicitly text-only.

### Gaps identified

- A shared delivery-group schema and resolver will need to be designed or extracted.
- Interactive `send_message` fanout will need a multi-target result model.
- The origin-only reply policy will need tests that prevent accidental cross-platform mirroring.
- Teams proactive delivery will need conversation-reference setup and operator verification.
- WhatsApp delivery will need bridge/session/recipient verification with a dedicated bot number and opt-in contacts.
- Operator docs will need a single end-to-end guide that covers Telegram, WhatsApp, and Teams together.

---

## Kanban board

> This is the current durable Markdown Kanban. A real GitHub Projects board can be created after `gh` is refreshed with the `project` scope.

### Backlog

- [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) — Parent umbrella / sequencing / synthesis
- Candidate follow-up — Real GitHub Project board automation after auth scope is available
- Candidate follow-up — Media fanout after media-security validation is fixed or explicitly scoped
- Candidate follow-up — Cross-platform conversation mirroring, if ever desired

### Ready for planning

- [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) — Platform parity reconnaissance
- [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) — Origin-only conversation policy guardrails
- [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) — Naming decision closeout

### Planning / draft

- [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) — Shared delivery group and fanout contract
- [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905) — Operator docs and setup guide

### Blocked / dependent

- [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904) — `send_message` multi-target text fanout, blocked until #2902 defines the shared contract
- Media fanout — blocked on media security validation and separate approval
- Teams live bot delivery — blocked until Azure/Bot Framework/tenant/public endpoint requirements are verified
- WhatsApp production delivery — blocked until QR/session persistence, dedicated bot number, and recipient opt-in are verified

### Plan review

- None yet. No issue in this tree should move to `status:plan-review` until the canonical plan and adversarial review artifacts exist.

### Approved / implementation-ready

- None. Implementation remains blocked.

### Done

- Product name decision: **Deckhand** selected as baseline identity and recorded on [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906).

---

## Proposed execution sequence

### Wave 0 — Board and decision hygiene

1. The parent issue will keep the umbrella scope and sequencing authority.
2. [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906) will be updated or closed only after the naming decision is reflected in the parent and downstream docs/plans.
3. A GitHub Projects board will be optional until `gh` has the `project` scope; the Markdown board above will be the current board of record.

### Wave 1 — Readiness reconnaissance

Primary issue: [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)

The plan will verify live and code-level readiness for:

- Telegram current send path and known `send_message` failure risk.
- WhatsApp bridge/session/identifier behavior.
- Teams bot/proactive-send prerequisites.
- Redaction coverage for platform identifiers.
- Day-2 controls: platform pause/resume, circuit breakers, logs, and restart notifications.

Deliverable will be a smoke matrix and blocker classification, not code changes.

### Wave 2 — Shared contract and guardrails

Primary issues: [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902), [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903)

The delivery group contract will define:

- Target grammar and explicit group expansion.
- Fail-closed preflight for invalid, unauthorized, or unsafe targets.
- Per-target result envelope.
- Redacted audit/event output.
- Text-only scope in the first implementation.

The conversation policy plan will add tests and guardrails so normal replies remain origin-only.

### Wave 3 — Interactive fanout

Primary issue: [#2904](https://github.com/vamseeachanta/workspace-hub/issues/2904)

After the shared contract exists, `send_message` will be planned to accept an approved delivery group or explicit target list and return a per-target status report. Partial success will apply only after full preflight succeeds; validation failures will abort before any platform send.

### Wave 4 — Operator documentation and smoke operations

Primary issue: [#2905](https://github.com/vamseeachanta/workspace-hub/issues/2905)

The operator guide will cover:

- Platform setup prerequisites.
- Dedicated WhatsApp bot-number guidance.
- Teams Bot Framework / Azure / tenant requirements.
- Safe delivery-group configuration examples.
- Smoke tests for Telegram-only, Telegram+WhatsApp, Telegram+Teams, and all-three text fanout.
- Troubleshooting for paused adapters, circuit breakers, unavailable platforms, and redacted logs.

---

## Artifact Map

| Artifact | Path / target |
|---|---|
| Preliminary plan | `docs/plans/2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md` |
| Parent issue | https://github.com/vamseeachanta/workspace-hub/issues/2900 |
| Naming issue | https://github.com/vamseeachanta/workspace-hub/issues/2906 |
| Canonical child plans | `docs/plans/YYYY-MM-DD-issue-2901-*.md` through `docs/plans/YYYY-MM-DD-issue-2905-*.md` |
| Review artifacts | `scripts/review/results/YYYY-MM-DD-plan-290X-{claude,codex,gemini}.md` |
| Hermes implementation candidates | `/home/vamsee/.hermes/hermes-agent/gateway/delivery.py`, `/home/vamsee/.hermes/hermes-agent/tools/send_message_tool.py`, platform adapters under `/home/vamsee/.hermes/hermes-agent/gateway/platforms/` |
| Workspace-hub operator docs candidate | `docs/hermes/` or `docs/operations/` path to be finalized in #2905 |

---

## Preliminary TDD / verification checklist

Each child implementation plan will define exact tests before any code changes. The expected test themes are:

| Theme | Tests will verify |
|---|---|
| Delivery group parsing | explicit targets and groups resolve deterministically; unknown groups fail closed |
| Authorization | unauthorized targets abort before any send |
| Preflight atomicity | invalid target in a multi-target request prevents all sends |
| Partial transport failure | one platform failure reports failure without hiding successes after preflight succeeds |
| Redaction | chat IDs, JIDs, phone numbers, tenant/conversation/service URLs, tokens, and env values do not leak |
| Origin-only replies | inbound Telegram/WhatsApp/Teams conversations reply only to their source platform by default |
| `send_message` contract | multi-target text calls return a per-target result envelope |
| Operator smoke | platform-disabled or paused adapters produce predictable, non-secret failure reports |

---

## Acceptance criteria for the planning tree

- [ ] The parent issue will link the board, preliminary plan, child issues, and Deckhand decision.
- [ ] Each child issue will receive a canonical plan under `docs/plans/` before implementation.
- [ ] Each implementation plan will receive adversarial review before `status:plan-review`.
- [ ] No child will be implemented until the user explicitly approves it with `status:plan-approved`.
- [ ] The first implementation wave will remain text-only.
- [ ] Platform-specific live-readiness blockers will be classified before any all-three fanout claim.
- [ ] Operator-facing results/logs will redact platform identifiers and credentials.

---

## Open decisions

1. Whether to create a real GitHub Projects board after refreshing `gh` with `project` scope.
2. Whether Deckhand should be only an internal/operator-facing name or also visible to clients.
3. Whether the first delivery-group syntax should mirror current cron `deliver` comma-list behavior or introduce a separate named-group config surface.
4. Whether Teams should start with Bot Framework only or allow a clearly labeled webhook-only demo mode.

---

## Next recommended action

Draft [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) first. It will produce the platform readiness matrix that determines whether #2902 and #2904 can safely plan all-three fanout or must sequence Telegram-first with WhatsApp/Teams behind readiness gates.

Implementation remains blocked until child plans are reviewed and explicitly approved.
