---
name: crossprovider codex legal-and-security-deny-lists-need-explicit-mach
description: Legal and security deny-lists need explicit machine-readable schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [security, legal, schema, automation]
---

Rather than describing legal/security scanning behavior in prose, define concrete JSON/YAML schema and parser rules repo-locally. This lets automated validators check plan compliance without human interpretation, and allows reviewers to verify the schema exists and is enforced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
