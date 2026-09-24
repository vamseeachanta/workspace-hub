---
name: crossprovider gemini contract-tests-must-fail-on-missing-apis-not-ski
description: Contract tests must fail on missing APIs, not skip
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, api-stability]
---

Consumer-side contract tests should fail when upstream APIs are missing or broken—never silently skip. Skipping defeats the purpose of catching breaking changes early. Use assertions or pytest.fail(), never pytest.skip() or importorskip() for API availability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
