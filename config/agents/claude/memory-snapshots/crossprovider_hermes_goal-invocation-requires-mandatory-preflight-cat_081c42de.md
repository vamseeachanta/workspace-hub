---
name: crossprovider hermes goal-invocation-requires-mandatory-preflight-cat
description: /goal invocation requires mandatory preflight: catalog + picklist + status + runner check
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [/goal-skill, workflow-rules, hermes-routing]
---

Per `.claude/rules/goal-invocation.md`, `/goal` is blocked until: (1) fetch #2695 catalog body, (2) fetch latest weekly picklist comments, (3) validate issue status labels match catalog, (4) check `status:plan-approved` label, (5) validate runner/quota allocation. Skipping preflight causes work to restart; multiple sessions show repeated `/goal` failures due to stale preflight.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
