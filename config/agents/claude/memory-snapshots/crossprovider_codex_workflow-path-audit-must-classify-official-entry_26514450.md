---
name: crossprovider codex workflow-path-audit-must-classify-official-entry
description: Workflow path audit must classify official entrypoints vs downstream validators vs manual mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-audit, path-classification, compliance-enforcement]
---

When auditing workflow compliance, categorize each path: official entrypoint (e.g., scripts/agents/plan.sh), downstream validator (e.g., verify-gate-evidence.py), or out-of-band manual mutation (direct frontmatter edits). Fix must block bypass modes at the official entrypoint; validators and mutations are separate concerns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
