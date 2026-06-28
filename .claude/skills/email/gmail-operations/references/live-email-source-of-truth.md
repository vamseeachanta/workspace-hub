# Live Email Source-of-Truth Pattern

Use this when a user asks the agent to check Gmail/email for appointment, coordination, triage, or follow-up clues.

## Durable rule

Current inbox state must come from live authenticated email tooling:

- Gmail API / configured Gmail MCP with current token health
- `himalaya` or another configured local mail client
- an already-open authenticated browser Gmail session, if available

Do not use these as proof of current email state:

- cached `tool-results/mcp-*_Gmail-*` files
- old Claude/Hermes/Codex session logs
- historical session-search snippets
- browser redirects to the Gmail login page
- saved OAuth/token files unless you also perform a live API/mail query

Historical artifacts can guide search terms, but they cannot establish that an email is present, absent, unread, recent, or actionable now.

## Fail-closed response shape

When live access is unavailable:

1. State that the email check is blocked by missing/unauthenticated live email access.
2. Avoid saying “no email found.” Say “not verified.”
3. If the user asked for coordination, create/update the task artifact with a concrete follow-up checklist:
   - check email/portal/texts for confirmation
   - confirm date/time/location/arrival instructions
   - confirm insurance/preauth/deposit/cancellation policy as applicable
   - add calendar/transport assignment
4. Preserve links to any GitHub issue or coordination artifact created.

## Why this exists

A session attempted to recover appointment details after a cron reminder by searching stale local Claude Gmail tool-result files and session logs. That produced historical noise, not live inbox evidence. The correct durable behavior is to treat those files as hints only, verify through live mail tooling, and fail closed when live access is absent.
