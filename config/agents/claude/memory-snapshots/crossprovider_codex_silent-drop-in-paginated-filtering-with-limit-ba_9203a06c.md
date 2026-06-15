---
name: crossprovider codex silent-drop-in-paginated-filtering-with-limit-ba
description: Silent drop in paginated filtering with limit-based collection
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [github-api, filtering, silent-failure, issue-259]
---

When filtering large paginated API responses (e.g., GitHub issues), applying the filter AFTER the limit allows requested items to silently disappear while the query reports success. Issue #259: fetching 100 issues, filtering to --issues 259, returns empty queue with complete=true if issue #259 is beyond position 100. Fix: apply filter before limit, or fetch until the requested item is found.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
