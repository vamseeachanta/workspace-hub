---
name: crossprovider hermes github-interaction-limits-expire-after-6-months-
description: GitHub interaction limits expire after 6 months and require renewal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, collaboration-management, maintenance]
---

GitHub's API endpoint for restricting interactions to collaborators (`/repos/{owner}/{repo}/interaction-limits`) enforces a 6-month expiration on all limits set. These must be manually reapplied or automated via recurring task every ~150 days, or external interactions revert to unrestricted.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
