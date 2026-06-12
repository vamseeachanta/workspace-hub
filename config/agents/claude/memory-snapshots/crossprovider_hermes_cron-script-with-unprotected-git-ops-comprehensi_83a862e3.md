---
name: crossprovider hermes cron-script-with-unprotected-git-ops-comprehensi
description: Cron script with unprotected git ops: comprehensive-learning-nightly
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-risk, git-ops, synchronization]
---

comprehensive-learning-nightly.sh (02:00 daily) does git pull, then 10+ phases (~1 hour runtime), then git add/commit/push — zero synchronization, no flock, no retry. Highest risk for contention with gsd-researcher and repo-sync. Runs during peak overlap window 02:00-03:00. Fix: add flock wrapper or pre-run deduplication check.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
