---
name: crossprovider codex session-logs-are-unsuitable-for-drift-compliance
description: Session logs are unsuitable for drift/compliance detection — use git state or hook output instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [session-logging, git-validation, drift-detection]
---

Session logs (JSONL format) are lossy: commands truncated to 150 characters. Validating commit-message format or file-path placement from session logs risks both false negatives (incomplete messages) and false positives (harmless examples). Use git commit history, hook output, or live workspace state instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
