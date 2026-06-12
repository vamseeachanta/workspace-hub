---
name: crossprovider hermes monkeypatch-checker-load-failures-to-test-fallba
description: Monkeypatch checker load failures to test fallback determinism
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, monkeypatch, determinism]
---

Force `_load_repo_placement_checker()` to raise; verify exception path honors same time source as success path. Catches non-deterministic fallbacks that live tests miss. Pattern: stub external dependency, verify time injection flows through all paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
