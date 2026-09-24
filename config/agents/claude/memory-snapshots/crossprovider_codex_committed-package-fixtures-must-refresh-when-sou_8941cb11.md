---
name: crossprovider codex committed-package-fixtures-must-refresh-when-sou
description: Committed package fixtures must refresh when source-gap transitions to accepted
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-freshness, fixture-sync, acceptance-workflow]
---

When a source-gap field is accepted with a new cited factor, the committed package artifact's metadata file must be regenerated to reflect the new factor and citation. Tests verifying live code can pass while stale committed metadata silently breaks downstream reporting expectations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
