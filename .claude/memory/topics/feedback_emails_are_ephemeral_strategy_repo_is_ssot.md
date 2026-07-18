> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_emails_are_ephemeral_strategy_repo_is_ssot.md

---
name: feedback-emails-are-ephemeral-strategy-repo-is-ssot
description: "Email is transient for the user — once work is done the inbox is cleaned out; anything important is committed to aceengineer-strategy, then move on"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 98f98058-2d4f-4def-b990-4e321d552886
---

The user treats Gmail as a **transient working medium, not a system of record**. Once a piece of work is done, the related emails are deleted / cleaned up — they do not leave threads sitting in the inbox.

**Why:** anything worth keeping (decisions, contacts, one-pagers, strategy, correspondence outcomes) is committed to the **`aceengineer-strategy`** repo, which is the durable SSOT. The inbox is then cleared and they move on. Keeps the mailbox lean and the real record versioned/searchable in git.

**How to apply:**
- When durable info is needed (a contact, a decision, past outreach), look in `aceengineer-strategy` first — not the inbox, which may already be cleaned out.
- Don't assume a missing email means it never existed; it was likely deleted after the work closed (this is exactly why message-search can't find people the user has emailed — see [[reference-gmail-search-no-contacts-autocomplete]]).
- When wrapping outreach/strategy work, the natural close is to persist the important artifact into `aceengineer-strategy` (a clean-lane PR per the repo's plumbing-commit pattern), not to rely on the email thread surviving.
