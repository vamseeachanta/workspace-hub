---
name: crossprovider codex file-type-blocking-by-extension-alone-is-bypassa
description: File-type blocking by extension alone is bypassable; use container sniffing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [security, file-validation, container]
---

Checking only filename suffix (e.g., `.xlsx`, `.xls`) to block workbook types is defeated by renaming a ZIP-based OpenXML workbook to `.payload`. Require magic-byte or ZIP-container inspection to confirm file class regardless of extension.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
