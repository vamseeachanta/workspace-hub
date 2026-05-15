# Email-as-Queue Workflow

> **Email is a QUEUE, not an ARCHIVE.** Per GitHub #2017.

## At a glance

```
INBOUND → TRIAGE → EXTRACT DATA → ACT → DELETE
                                      ↓
                          Topic completed? → DELETE email
                          Awaiting reply?  → KEEP (live)
                          New reply arrives → RE-ACTIVATE
```

## Key Rules

1. Do NOT save all emails — extract only actionable data/information
2. Delete the email when the topic is completed
3. Keep email alive when awaiting response
4. Re-activate on new reply (thread comes back to inbox)
5. Learn from patterns — improve routing/extraction over time

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `gmail-triage` | Daily inbox scan, classify, digest | Active — queue model |
| `gmail-extract-and-act` | Extract structured data, track state, delete when done | Active — queue action engine |
| `gmail-operations` | Class-level Gmail/email operations: triage, extraction, attachments, outreach, and state handling | Active — aggregator |
| `gmail-outreach` | Touchbase messages + batch unsubscribe | Active — replaces old touchbase/unsubscribe flows |
| `gmail-multi-account` | Foundation — 3 accounts, OAuth, himalaya | Active |
| `gmail-attachment-to-document` | Parse attachments, save structured data | Active |
| `gmail-data-extraction` | Historical extraction patterns and code reference | Active — reference/pattern skill |
| `contact-manager` | Normalize/classify contact databases | Active |
| `himalaya` | CLI reference for email operations | Active — reference only |
| `gmail-headless-oauth` | Manual OAuth2 token exchange | Active — infra utility |

## Routing Rules

`scripts/email/email-routing.yaml` — Sender domain → extraction target or DELETE/REVIEW.

## State Tracking

- Gmail labels: `wh-email/extracted`, `wh-email/awaiting-reply`, `wh-email/completed`, `wh-email/noise`
- Local state: `~/.hermes/email-state.yaml` (authoritative tracker; credentials/config values must stay out of docs)
- Label semantics: `docs/email/email-skill-state-labels.md`
- Grace period: 7 days for completed threads before deletion

## Cron Jobs

| Job | Schedule | Status |
|---|---|---|
| `gmail-daily-digest` | Daily 12 PM CT | Scheduled (first run pending) |

## Issues

| Issue | Description | Status |
|---|---|---|
| #2017 | Email-as-Queue workflow design | Open |
| #2019 | Consolidate skill sprawl | Open |
| #2024 | Rewrite extraction pipeline | Open |
| #2025 | Per-domain extraction templates | Open |
| #2026 | State tracking system | Open |
| #1963 | Multi-account Gmail management (parent) | Open |
| #1987 | Email cleanup pipeline | Open (needs rewrite) |
| #1968 | Personal triage | Open |
| #1969 | SKEstates triage | Open |
| #1971 | ACE triage | Open |
