> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_email_cross_noise.md

---
name: Email cross-noise — someone else's account emails misrouted to user's Gmail
description: Pattern where third parties sign up for services using the user's Gmail by mistake, causing account/overdue/statement emails from those services to arrive for a non-existent relationship
type: feedback
originSessionId: 512141a1-fd1b-4872-bcc8-66a1e93059d6
---
The user has at least one confirmed case of **email cross-noise**: third parties sign up for services (observed: Tata Capital in India) using his Gmail address by mistake, and account-related emails (overdue EMI reminders, statements) arrive in his inbox even though he has no account with that service.

**Why this matters:**
- Standard unsubscribe flows FAIL — unsub pages require authenticating as the account holder, which the user is not.
- These emails look superficially actionable ("EMI overdue") and can waste user's attention during triage.
- Sender-domain DELETE rules in routing config may be the only reliable mitigation from the user's side.

**How to apply during triage:**
1. When user reports "this doesn't belong to me" for a financial/account notification, classify the thread as `noise / email-cross-noise` rather than `actionable`.
2. Add the sender domain to `scripts/email/email-routing.yaml` DELETE list (the pipeline will auto-delete future mail from that sender, regardless of subject).
3. DO NOT draft outreach to the sender asking them to remove the user's email — that assumes the user has standing with the sender, which he does not. The real account holder is someone else; user has no relationship to invoke.
4. For Gmail-side UI: recommend the user use "Block sender" in Gmail, which filters future mail from that exact sender domain, independent of the pipeline.

**Known cases (2026-04-21):**
- Tata Capital (financial services, India) — EMI overdue reminders. User is not a customer. Sender probably added his address during signup error.

**For #2017 Step 2 pipeline design:** add `email-cross-noise` as a possible classification, distinct from standard spam. Heuristics:
- Sender claims a financial/account relationship ("your loan", "your account", "overdue")
- User has marked similar prior emails from same sender as cross-noise
- No prior outbound mail to the sender domain in the user's sent folder

The classification should route to DELETE (same as other noise) but the reason field should distinguish it for the quarterly learning review so patterns of repeat-offender senders can be flagged.
