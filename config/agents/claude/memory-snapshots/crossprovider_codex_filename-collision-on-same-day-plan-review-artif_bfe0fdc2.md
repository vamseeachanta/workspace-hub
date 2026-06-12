---
name: crossprovider codex filename-collision-on-same-day-plan-review-artif
description: Filename collision on same-day plan-review artifact reruns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-artifact-filenames, plan-review-fanout, collision-prevention]
---

plan-review-fanout.sh currently writes to `YYYY-MM-DD-plan-NNN-<provider>.md`, overwriting same-day reruns. Must switch to collision-free timestamped form like `YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md` while retaining backward-compat parsing for legacy `YYYY-MM-DD` artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
