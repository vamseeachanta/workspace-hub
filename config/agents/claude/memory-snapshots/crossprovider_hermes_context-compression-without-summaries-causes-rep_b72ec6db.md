---
name: crossprovider hermes context-compression-without-summaries-causes-rep
description: Context compression without summaries causes repeated validation cycles
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-management, context-loss, work-duplication]
---

10+ Hermes sessions compacted without summaries → repeated validation, re-reviews, and re-fixes of the same blockers (symlink scan, unresolved targets, content field safety). Preserved task lists help, but full work context is lost across compressions. Plan and MAJOR findings need explicit persistence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
