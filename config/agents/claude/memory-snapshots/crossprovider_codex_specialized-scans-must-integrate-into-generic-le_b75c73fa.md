---
name: crossprovider codex specialized-scans-must-integrate-into-generic-le
description: Specialized scans must integrate into generic leak scans
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [security, scanning, architecture]
---

Reports enumerating sensitive hits (hash/provenance rationales, redaction decisions) are themselves high-risk artifacts. They must be included in generic leak scans, not only specialized classifier tests—otherwise the scanning framework creates a new leak surface at the summary level.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
