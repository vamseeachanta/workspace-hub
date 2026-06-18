---
name: crossprovider codex verification-commands-should-only-claim-what-the
description: Verification commands should only claim what they actually check
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [verification, testing, accuracy, documentation]
---

A command claiming to verify 'no source filenames' but only scanning for `/mnt/`, `source_pdf`, and `full-text-part` is an overclaim. Either extend the marker list or narrow the claim text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
