---
name: crossprovider hermes harness-update-patches-survive-git-pulls-via-ded
description: Harness update patches survive git pulls via dedicated patch directory
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [harness, patches, update-strategy, infrastructure]
---

Custom patches to vendored harnesses (e.g. Hermes) can be preserved across updates by saving them to config/agents/<harness>/patches/ and having the harness-update.sh apply them after git pull. This allows local customizations (skill dir exclusion, config extensions) to survive harness version upgrades without manual re-application.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
