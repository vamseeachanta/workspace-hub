---
name: crossprovider codex dual-guard-output-redaction-deny-list-plus-locat
description: Dual-guard output redaction: deny-list plus location checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [output-safety, data-redaction, llm-wiki-pattern, security]
---

Use unsafe-token deny-list (grep for `/mnt/`, `/home/`, `token=`, `password=`, raw filenames) before report write. Also require output-location guard: all generated reports must resolve outside source roots. Together these prevent path leakage, secrets exposure, and raw private content in metadata artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
