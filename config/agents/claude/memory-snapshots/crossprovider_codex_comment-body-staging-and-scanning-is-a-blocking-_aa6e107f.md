---
name: crossprovider codex comment-body-staging-and-scanning-is-a-blocking-
description: Comment-body staging and scanning is a blocking requirement before posting
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [privacy-enforcement, comment-safety, batch-routing]
---

When batch systems emit issue comments with data from private/sensitive batches, the exact comment body must be staged as an artifact, scanned for leaks against the batch's denial list, and that scan must pass before the comment is posted to GitHub. Test coverage for report/section leaks is necessary but not sufficient; tests must also cover the final comment body.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
