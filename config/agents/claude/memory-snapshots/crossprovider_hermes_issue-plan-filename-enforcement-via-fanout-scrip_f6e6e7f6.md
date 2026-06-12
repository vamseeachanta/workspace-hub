---
name: crossprovider hermes issue-plan-filename-enforcement-via-fanout-scrip
description: Issue plan filename enforcement via fanout script
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naming-convention, automation, plan-artifact]
---

Plan artifact location `docs/plans/YYYY-MM-DD-issue-NNN-slug.md` is automatically enforced by `scripts/review/plan-review-fanout.sh` parsing filename shape. Non-conformant paths fail fanout dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
