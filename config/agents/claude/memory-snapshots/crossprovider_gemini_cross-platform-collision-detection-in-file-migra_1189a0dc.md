---
name: crossprovider gemini cross-platform-collision-detection-in-file-migra
description: Cross-platform collision detection in file migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, cross-platform, preflight-gate]
---

File migrations must include case-insensitive preflight collision checks as a required gate before apply; Unicode normalization collision handling (NFC/NFD) can be deferred to later waves if out-of-scope.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
