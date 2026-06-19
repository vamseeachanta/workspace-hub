---
name: crossprovider codex prior-art-specificity-must-transfer-to-downstrea
description: Prior-art specificity must transfer to downstream issues
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [patterns, requirements, testing]
---

When a prior issue (#732) established concrete patterns (e.g., no-body-read, no-mutation tests, symlink behavior, monkeypatch strategy), downstream issues (#730) should carry equivalent specificity, not abstract equivalents. Session 5/6: #730 plan had broad test names but lacked concrete API constraints, filesystem guards, and strategy details that #732 prior art had nailed. Copy the rigor, not the idea.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
