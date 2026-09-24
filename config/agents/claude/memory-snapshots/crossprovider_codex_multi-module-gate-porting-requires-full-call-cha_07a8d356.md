---
name: crossprovider codex multi-module-gate-porting-requires-full-call-cha
description: Multi-module gate porting requires full call-chain verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [porting, dependency-discovery, modular-systems]
---

When porting modular gate systems (runner→checker→scorer→renderer) across repositories, verify the complete call chain and all transitively imported modules. A missing intermediate module means the advisory layer fails immediately when used, even if the main entry points were copied.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
