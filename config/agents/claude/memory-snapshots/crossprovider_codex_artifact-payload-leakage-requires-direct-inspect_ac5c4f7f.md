---
name: crossprovider codex artifact-payload-leakage-requires-direct-inspect
description: Artifact payload leakage requires direct inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-safety, payload-leakage, generated-content, verification]
---

Generated artifacts claiming to avoid paths or sensitive data must be scanned directly in the JSON/HTML output—not caught by reviewing source code alone. Check for repo paths, script paths, manifest references, and pattern leakage in the actual generated payloads.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
