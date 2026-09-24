---
name: crossprovider codex hardcoded-domain-path-mappings-require-exhaustiv
description: Hardcoded domain path mappings require exhaustive regression test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-testing, domain-detection, mapping-coverage, regression-testing]
---

When hardcoding domain/path mappings (e.g., `DOMAIN_PATHS` tuples), each mapping must have a dedicated regression test (e.g., `test_known_src_change_outputs_matching_domain`, `test_specific_test_override_wins_over_broad_domain_root`). Without these, future refactors may silently break domain detection without triggering test failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
