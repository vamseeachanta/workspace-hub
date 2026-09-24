---
name: crossprovider codex privacy-scans-for-private-safe-indexing-need-spe
description: Privacy scans for private-safe indexing need specific token categories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, privacy-scan, security-tokens]
---

Check for raw paths (`/mnt/`, `/home/`, `/tmp/`), raw identifiers, filenames, account/client/project names, source bodies/excerpts, and `password=`/`token=`/`secret=` patterns. For HTML reports, explicitly show upload/body/mutation control flags so readers can verify the safety constraints are visible. Monkeypatch `Path.read_text()` in tests to catch hidden source-body reads.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
