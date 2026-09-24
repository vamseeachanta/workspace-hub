---
name: crossprovider gemini phase-0-pilot-single-repo-before-multi-repo-roll
description: Phase 0 pilot (single repo) before multi-repo rollout catches integration issues
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [rollout, pilot, risk-management, orchestration]
---

When rolling out infrastructure changes across multiple repos, start with a single end-to-end pilot (Phase 0) before broader rollout. This surfaces integration issues, config problems, and test gaps in one repo before duplicating failures across five.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
