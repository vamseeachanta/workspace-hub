# Plan for #9001: Known-good fixture plan for two-fixture plumbing test

> **Status:** fixture
> **Complexity:** T1
> **Date:** 2026-04-17
> **Issue:** fixture-only; not a real issue

## Deliverable

A two-line helper script that prints "hello" and exits 0.

## Acceptance Criteria

- [ ] Script exists at scripts/tmp/hello.sh.
- [ ] Running it prints "hello" on stdout.

This fixture is deliberately simple and self-consistent. It is used only by
`test_two_fixture_plumbing` to verify that the wrapper routes fixture-specific
prompts to fixture-specific artifacts. It is NOT used to verify reviewer
adversarial behavior.
