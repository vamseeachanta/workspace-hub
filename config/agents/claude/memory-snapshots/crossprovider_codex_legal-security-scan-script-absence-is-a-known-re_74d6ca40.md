---
name: crossprovider codex legal-security-scan-script-absence-is-a-known-re
description: Legal/security scan script absence is a known repo-infrastructure gap
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [repo-infrastructure, legal-scan, blocker, technical-debt]
---

Multiple issues (#65, #66, others) remain open at final review stage because `scripts/legal/legal-sanity-scan.sh` does not exist. Issues are functionally complete but cannot close without this script or an explicit deferral. This is a system-level dependency, not a per-issue fix.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
