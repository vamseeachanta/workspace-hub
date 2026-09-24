---
name: crossprovider codex email-extraction-pipeline-must-distinguish-raw-a
description: Email extraction pipeline must distinguish raw archiving from structured extraction with legal gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [email-automation, data-modeling, legal-compliance]
---

Shifting from 'save full email bodies to repos' to 'extract structured fields (amount, vendor, deadline) then legal-scan before commit' is a paradigm change, not a refactor. It affects state modeling (when can we delete?), deletion logic (grace periods), and downstream consumers. Plans must explicitly show the old/new contrast.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
