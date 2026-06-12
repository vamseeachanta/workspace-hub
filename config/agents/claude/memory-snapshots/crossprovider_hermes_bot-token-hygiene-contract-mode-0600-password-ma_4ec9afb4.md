---
name: crossprovider hermes bot-token-hygiene-contract-mode-0600-password-ma
description: Bot token hygiene contract: mode 0600, password manager, no chat/logs/commits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [bot-token, credential-hygiene, telegram]
---

Telegram/Hermes bot tokens must live in `~/.hermes/.env` with mode 0600, owner `vamsee:vamsee`, backed up in password manager; never paste into GitHub, chat logs, commits, or CLI output. Example: #2728/#2729 audits found token-sensitive readiness script with redaction placeholders. **Why:** credential exposure has no recovery; incident response requires token revocation + branch purge + reflog expiry. **How to apply:** enforce `ls -la ~/.hermes/.env` to check permissions; in scripts use `${TELEGRAM_BOT_TOKEN}` not literal; redact in logs/output; document token location only in runbooks/password manager, never in repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
