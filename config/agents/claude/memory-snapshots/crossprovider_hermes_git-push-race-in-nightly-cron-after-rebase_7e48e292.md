---
name: crossprovider hermes git-push-race-in-nightly-cron-after-rebase
description: Git push race in nightly cron after rebase
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-race, cron-contention, gsd-researcher]
---

gsd-researcher script does git pull --rebase then git push, but another process (repo-sync, other cron) can push between rebase and push, causing 'remote rejected: is at X but expected Y' errors. Observed in 5 of 8 days (62.5% failure rate). Fix: either retry logic on push failure, pre-push rebase+pull, or global flock covering both pull and push phases atomically.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
