---
name: crossprovider codex acceptance-criteria-to-test-traceability-gaps-hi
description: Acceptance-criteria-to-test traceability gaps hide AC drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, mandatory-gate]
---

Plans claim 'full AC coverage' but E2E tests, manual checks, and provider-dependent verifications don't have executable test paths. Splits AC into automatable vs manual release-checks without clear separation. Fix: every AC must map to either an automated test or an explicitly named manual release-check; mark both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
