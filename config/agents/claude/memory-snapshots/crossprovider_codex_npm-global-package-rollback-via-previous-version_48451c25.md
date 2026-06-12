---
name: crossprovider codex npm-global-package-rollback-via-previous-version
description: npm global package rollback via previous version is unreliable without pre-state verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [npm, rollback, package-management, transaction-safety]
---

npm install -g pkg@previous does not guarantee restoration of the exact prior state: transitive dependencies may differ, cache may be stale, postinstall scripts may behave differently. Reliable rollback requires recording pre-update state (lock file, file hashes, or manifest snapshot) and validating post-rollback equivalence, not trusting version strings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
