> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gmail_override_filters_silent_defeat.md

---
name: Gmail "Override filters" silently defeats Skip-Inbox rules
description: Gmail Inbox importance-override setting nullifies Skip-Inbox filters for any sender flagged as "important"; flip to "Don't override" before installing filters
type: feedback
originSessionId: aff40e1f-c80c-4f6d-9797-cba4ecc59a84
---
Gmail's Inbox setting **"For messages classified as important: Override filters"** silently defeats Skip-Inbox filter rules for any sender Gmail's importance heuristic flags. Must flip to **"Don't override filters"** before installing any Skip-Inbox filter.

**Why:** Discovered 2026-04-24 on the ace account. `from:(collide.io)` filter existed and was enabled, yet collide.io mail kept reaching Inbox because Gmail had marked the sender "important." The 87% inbox reduction from the 2026-04-24 sweep depended as much on flipping this setting as on the filter rules themselves — filters alone weren't enough.

**How to apply:** Before any Gmail filter-install session, navigate to `Settings → Inbox → "For messages classified as important"` and select **"Don't override filters."** Verify via reading the radio-button state (don't assume from the label). This is step 1 of any Gmail hygiene automation — filter-install without it produces silent partial failures. See `docs/sessions/2026-04-24-gmail-ace-sweep.md` and commit `07e73c2ec` for the reference workflow.
