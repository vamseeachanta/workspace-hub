---
name: crossprovider hermes telegram-hermes-token-hygiene-pattern-tdd-with-t
description: Telegram-Hermes token hygiene pattern: TDD with tempfile fakes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [token-hygiene, tdd-pattern, telegram-hermes, readiness-verification]
---

Bot token lives only in ~/.hermes/.env (mode 0600), readiness scripts redact values, and coordinator verifier uses TDD with safe tempfile-based fake command scripts to avoid chmod/permission issues. Fakes mock systemctl output/pgrep patterns without requiring shell script permissions changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
