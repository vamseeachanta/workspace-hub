---
name: crossprovider hermes policy-tests-focusing-on-schema-fixture-presence
description: Policy tests focusing on schema + fixture presence miss ambiguity; need table-driven tests with concrete signal inputs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-anti-pattern, policy-testing, configuration]
---

#2282 reviews found tests validating YAML structure and fixture rows present, but no tests driving actual classification/ranking on representative multi-signal inputs. Shallow tests pass while policy is contradictory/incomplete. Use table-driven approach: concrete signals → assert bucket/ranking/escalation outcome.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
