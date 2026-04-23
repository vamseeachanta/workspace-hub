# Plan for #9002: Known-broken fixture plan for two-fixture plumbing test

> **Status:** fixture
> **Complexity:** T1
> **Date:** 2026-04-17
> **Issue:** fixture-only; not a real issue

## Deliverable

A script at scripts/nonexistent/foo.sh that will never exist.

## Acceptance Criteria

- [ ] Fictional script references a fictional dir.
- [ ] Plan claims compatibility with kernel 2.6, which is EOL.
- [ ] Pseudocode below is syntactically invalid bash.

```bash
if then while do () echo "broken"
```

This fixture is deliberately broken. Paired with `known-good-plan.md` it
proves the wrapper's plumbing passes fixture-specific prompts through to
per-provider artifacts without cross-contamination. The review quality of
the paired mocks is NOT tested by this pair — only the routing.
