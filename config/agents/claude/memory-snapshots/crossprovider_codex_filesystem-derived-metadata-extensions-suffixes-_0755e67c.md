---
name: crossprovider codex filesystem-derived-metadata-extensions-suffixes-
description: Filesystem-derived metadata (extensions, suffixes) bypasses field allowlists
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy-patterns, metadata-filtering, implementation-gaps]
---

Allowlisting 'safe fields' from source roots (extension_mix) did not prevent leakage of unintended timestamp-like suffixes. Raw filesystem metadata needs explicit redaction/filtering rules, not just allowlisting of field names. A separate filter layer (e.g., reject extensions matching date patterns) is needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
