---
name: crossprovider codex pdfplumber-availability-may-live-in-an-existing-
description: pdfplumber availability: may live in an existing sandbox venv
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tooling-quirk, pdfplumber, environment]
---

pdfplumber may not be on the default Python path but could exist in /tmp venv or sandboxed environment. When default import fails, check local venv paths before assuming the tool is unavailable. Source control matters: use the available tool even if installed in a non-standard location.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
