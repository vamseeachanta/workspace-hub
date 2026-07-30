---
name: crossprovider codex route-conjunction-tests-need-exhaustive-predicat
description: Route conjunction tests need exhaustive predicate mutation, not subset coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, tdd, test-design]
---

Test named `test_each_route_conjunction_predicate_is_required` must generate one-field mutations for every route+predicate combination. Subset coverage hides bypasses. Include both positive (valid routes) and negative (route-specific rejections).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
