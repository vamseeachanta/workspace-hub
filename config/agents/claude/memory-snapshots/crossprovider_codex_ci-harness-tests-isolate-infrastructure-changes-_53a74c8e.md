---
name: crossprovider codex ci-harness-tests-isolate-infrastructure-changes-
description: CI harness tests isolate infrastructure changes from domain matrix
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci, infrastructure, test-architecture]
---

CI detector/harness logic runs in its own job before the domain matrix, with layered detection: (1) skip NO_DOMAIN_PATHS to avoid false positives on infrastructure files, (2) check explicit DOMAIN_PATHS mappings, (3) fall back to domain.roots. Prevents untested changes to CI itself.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
