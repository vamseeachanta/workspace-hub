---
name: crossprovider gemini emergency-interaction-limit-lockdown-2026-04-29-
description: Emergency interaction-limit lockdown: 2026-04-29 to 2026-10-29
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [github-security, interaction-limits, project-state]
---

On 2026-04-29, all 10 public `vamseeachanta/*` repos were set to `collaborators_only` interaction mode with `six_months` expiry, terminating 2026-10-29. This requires a scheduled renewal task to avoid the limits expiring without re-authorization. A Hermes cron job was created locally (`renew-github-collaborator-only-interaction-limits`) but remains untracked in the repo.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
