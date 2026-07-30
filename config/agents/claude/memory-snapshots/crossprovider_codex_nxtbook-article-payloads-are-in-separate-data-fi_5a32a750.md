---
name: crossprovider codex nxtbook-article-payloads-are-in-separate-data-fi
description: NXTBook article payloads are in separate data files, not the page shell
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [web-ingest, nxtbook, data-fetch]
---

Direct page fetches hit a metadata shell; full article body is in a separate data file keyed via `book.json` manifest. Extract the manifest first, then fetch `data/<article-id>.html` by path, not by parsing rendered HTML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
