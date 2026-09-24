---
name: crossprovider codex email-thread-state-machines-need-re-activation-l
description: Email thread state machines need re-activation logic for multi-surface state tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [email-automation, state-management, lifecycle]
---

Email automation tracking states across Gmail labels ('extracted', 'awaiting-reply', 'completed') and local state files requires explicit re-activation: periodic checks for new replies on 'completed'/'awaiting-reply' threads, with a clear state-transition diagram. Leaving this implicit causes premature deletions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
