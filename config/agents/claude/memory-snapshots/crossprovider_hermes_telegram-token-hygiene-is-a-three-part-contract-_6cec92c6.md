---
name: crossprovider hermes telegram-token-hygiene-is-a-three-part-contract-
description: Telegram token hygiene is a three-part contract, not just file permissions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [credential-hygiene, readiness-gates]
---

Token safety requires: (1) file mode 0600, (2) owner vamsee:vamsee, AND (3) env var names scoped to `TELEGRAM_HERMES_*` (not generic bot-token keys). Readiness scripts must check all three, not just "key exists". Legacy generic keys (e.g., `BOT_TOKEN=...`) pass (1)+(2) but fail (3); readiness should fail-closed on mismatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
