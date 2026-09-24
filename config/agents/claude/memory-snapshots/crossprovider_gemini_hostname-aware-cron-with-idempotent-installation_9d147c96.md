---
name: crossprovider gemini hostname-aware-cron-with-idempotent-installation
description: Hostname-aware cron with idempotent installation enables safe deployments across contexts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [operations, automation, deployment]
---

setup-cron.sh maps hostname to cron_variant (ace-linux-1=full, ace-linux-2=contribute, Windows=Task Scheduler fallback). Duplicate detection via script name prevents re-installs. This pattern supports multi-machine workflows without manual variant selection.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
