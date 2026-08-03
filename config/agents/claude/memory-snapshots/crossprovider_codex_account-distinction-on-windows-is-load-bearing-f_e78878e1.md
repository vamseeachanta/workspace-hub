---
name: crossprovider codex account-distinction-on-windows-is-load-bearing-f
description: Account distinction on Windows is load-bearing for file server access
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [windows, accounts, architecture, file-server, credentials]
---

Domain account (mkt-a-inc\vamseea) reaches file server (\\mkt-a-file01\Jobs); local account (mkt-a-hou-rds02\administrator) cannot, regardless of SSH setup. Recording 'SSH ✓' without the principal makes the architecture dead on arrival. Stored-credential task must use the domain account.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
