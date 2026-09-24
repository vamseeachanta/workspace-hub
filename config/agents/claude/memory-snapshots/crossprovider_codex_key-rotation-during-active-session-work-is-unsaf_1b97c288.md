---
name: crossprovider codex key-rotation-during-active-session-work-is-unsaf
description: Key rotation during active session work is unsafe
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, key-management, secrets, credentials]
---

When rotating encryption keys during live session work, both the old and new keys can end up in session transcripts if the replacement key is generated and used in the same session. Rotate keys offline or ensure a full re-encryption cycle completes before resuming live work to prevent key material leakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
