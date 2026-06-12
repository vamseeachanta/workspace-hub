---
name: crossprovider hermes ignored-tests-require-documented-rationale
description: Ignored tests require documented rationale
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci, hygiene]
---

Silent test suppression (conftest ignores, @pytest.mark.skip without reason) creates hidden risk in CI matrices. Every ignore rule needs documented reason, target policy (reenable/quarantine/permanent), and regression note if status changes. CI commands must explicitly reflect included vs excluded test suites.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
