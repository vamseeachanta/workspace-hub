---
name: crossprovider codex url-shape-validation-does-not-constitute-retriev
description: URL-shape validation does not constitute retrieval-backed evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [evidence-verification, security, test-coverage]
---

Verifying that a source URL matches a pattern (e.g. `https://osha.gov/...`) is not sufficient for 'official source verified.' Real verification requires: fetch the URL, check HTTP status, extract and store content digest, timestamp retrieval, quote specific evidence passages, reject query/fragment variants. Tests that only check rejection paths ("non-OSHA URLs fail") miss acceptance-path bypasses ("bogus OSHA URLs pass").

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
