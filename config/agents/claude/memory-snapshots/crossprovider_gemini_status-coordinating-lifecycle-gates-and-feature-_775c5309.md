---
name: crossprovider gemini status-coordinating-lifecycle-gates-and-feature-
description: Status:coordinating lifecycle gates and feature-specific filters
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [status, lifecycle, work-queue]
---

Feature WRKs transition working→coordinating when children are scaffolded (new-feature.sh sets it). Coordinating items bypass category/subcategory filters in whats-next.sh. validate-queue-state.sh allows coordinating in working/ folder (exemption). Coordinating is not a terminal state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
