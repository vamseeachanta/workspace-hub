---
name: crossprovider codex table-parse-status-defaults-to-provisional-raw-n
description: Table parse_status defaults to provisional/raw; never verified without independent validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [table-extraction, parse-status, quality-assurance]
---

Tables extracted from PDFs without pdfplumber (often unavailable in worktrees) marked provisional-unverified or raw-unverified. NEVER claim verified parse_status unless independently validated. The _verification-queue.csv is the deferral layer where extracted tables await human or secondary verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
