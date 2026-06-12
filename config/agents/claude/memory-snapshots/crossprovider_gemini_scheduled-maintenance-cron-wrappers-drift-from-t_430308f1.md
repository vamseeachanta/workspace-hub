---
name: crossprovider gemini scheduled-maintenance-cron-wrappers-drift-from-t
description: Scheduled maintenance cron wrappers drift from test contracts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cron, automation, testing, maintenance]
---

Long-running cron tasks (skills-curation, staleness-scan) often become implemented as free-form prompt wrappers that don't produce deterministic JSON/Markdown artifacts, while their test suites expect explicit artifact paths and validated output schemas. Test failures accumulate as drift indicator.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
