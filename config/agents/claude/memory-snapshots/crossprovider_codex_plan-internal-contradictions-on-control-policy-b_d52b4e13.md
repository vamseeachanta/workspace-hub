---
name: crossprovider codex plan-internal-contradictions-on-control-policy-b
description: Plan internal contradictions on control policy block approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, approval-gate, policy-consistency]
---

Plans that state mutually exclusive policies (e.g., 'whole-host exclusions are prohibited' in acceptance criteria, but 'add rotted host to exclude list' in risk mitigation) cannot be approved until internally consistent. This pattern appeared in #2443 markdownlint plan where lychee gate policy contradicted itself.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
