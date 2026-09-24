---
name: crossprovider codex upstream-plan-artifacts-not-reliably-findable-ac
description: Upstream plan artifacts not reliably findable across issues
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-issue-dependency, artifact-tracking, plan-coupling]
---

Plans that depend on prior-issue plan artifacts (e.g., #605 depends on #500 plan files) assume those files exist in standard locations (docs/plans/NNNN-*). When prior issues are in different repos or archived, the dependency chain breaks invisibly. Document explicit fallback retrieval or absolute paths to approval artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
