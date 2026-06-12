---
name: crossprovider gemini file-iteration-loops-must-cover-the-stated-scope
description: File iteration loops must cover the stated scope completely or it silently breaks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [completeness, file-patterns, hidden-scope-gaps]
---

Plans claiming scope `.{yaml,json}` but implementing only `*.yaml` loops will silently ignore half the inputs. Verification gaps appear as 'missing coverage' only in integration tests. Loop scope must match prose scope exactly, and acceptance criteria must test both branches.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
