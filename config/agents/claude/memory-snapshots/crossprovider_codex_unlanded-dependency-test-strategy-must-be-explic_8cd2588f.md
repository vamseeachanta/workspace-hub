---
name: crossprovider codex unlanded-dependency-test-strategy-must-be-explic
description: Unlanded-dependency test strategy must be explicit in plan scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, dependency-management, plan-discipline]
---

Several Ballymore-conversion plans depend on unlanded APIs (#601/#602) without declaring whether tests xfail, skip, mock, or enforce land-order until dependencies materialize. This ambiguity cascades to CI behavior and blocks clear validation timing. Plans with test dependencies on unlanded issues must explicitly specify strategy and CI gating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
