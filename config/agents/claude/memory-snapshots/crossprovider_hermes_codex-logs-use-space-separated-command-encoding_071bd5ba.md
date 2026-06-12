---
name: crossprovider hermes codex-logs-use-space-separated-command-encoding
description: Codex logs use space-separated command encoding
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, command-logging, audit-normalization]
---

Codex encodes individual command characters separated by single spaces; original shell separators become 3+ space runs. Normalization should map 1–2 spaces to nothing and 3+ spaces to single space; the current re.sub(r"\s+", "") destroys separators, turning "s e d   - n" into "sed-n" instead of "sed -n". Lightweight decoder using space-run heuristic reconstructs pipes, &&, ||, redirects, and heredocs correctly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
