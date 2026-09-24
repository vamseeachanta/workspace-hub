---
name: crossprovider codex vague-test-wording-is-not-fail-closed-validation
description: Vague test wording is not fail-closed validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, privacy, acceptance-criteria]
---

Acceptance criteria like 'without repeating sensitive labels where unnecessary' do not enforce fail-closed behavior. Equivalent prior work used exact validation tests, allowlist/denylist specifications, and monkeypatch strategies. New plans must match that specificity or inherit the test suite by reference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
