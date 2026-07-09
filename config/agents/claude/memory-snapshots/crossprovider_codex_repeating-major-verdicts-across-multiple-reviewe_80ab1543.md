---
name: crossprovider codex repeating-major-verdicts-across-multiple-reviewe
description: Repeating MAJOR verdicts across multiple reviewers + "patch attempt recorded; re-review required" signals plan/review loop misconfiguration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [codex, adversarial-review, planning, review-loop, MAJOR-verdict]
---

When adversarial reviews yield MAJOR verdicts across independent reviewers (Claude, Codex) in successive rounds (r1-r9) with identical core findings (wave-class mapping, #62 interface, evidence gaps) and each round logs "patch attempt recorded; re-review required," this indicates either: (1) patches aren't actually being applied between reviews, (2) the plan has a fundamental structural flaw requiring root-cause rework (not incremental patches), or (3) the review loop is auto-triggering without human gate. Escalate to root-cause investigation before continuing cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
