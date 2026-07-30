---
name: crossprovider codex acceptance-tests-must-bind-directly-to-issue-del
description: Acceptance tests must bind directly to issue deliverables, not just artifact structure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, acceptance-criteria, requirements-traceability]
---

Tests that check for section anchors, file presence, or JSON keys can pass without delivering the actual issue outcome. Each acceptance criterion must tie one or more tests to a specific deliverable named in the issue body (e.g., "lifecycle page" → artifact path + content expectations, not just `test_render_report_contains_section`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
