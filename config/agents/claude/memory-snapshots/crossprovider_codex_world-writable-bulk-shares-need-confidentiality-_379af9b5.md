---
name: crossprovider codex world-writable-bulk-shares-need-confidentiality-
description: World-writable bulk shares need confidentiality warnings
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [operations, security, data-safety]
---

When bulk storage is exported as 777 nobody:nogroup with guest Samba access and browseable, it is effectively a public LAN share. Preservation records and cleanup procedures must warn against sending client-confidential data there.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
