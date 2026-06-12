---
name: crossprovider hermes numpy-int64-serialization-bug-in-comparison-fram
description: numpy int64 serialization bug in comparison_framework.py blocks export_report() JSON dump
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [serialization-bug, numpy-compatibility, test-blocker]
---

comparison_framework.py:450-451 tries to json.dump() numpy int64 tuple (max_magnitude_diff_location), fails with TypeError. Blocks test coverage work on comparison APIs. Real source code bug, not test-infra issue. Workaround: skip json.dump tests or convert numpy ints to Python ints before serialization.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
