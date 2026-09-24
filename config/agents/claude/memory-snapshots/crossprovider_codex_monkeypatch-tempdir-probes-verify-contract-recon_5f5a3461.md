---
name: crossprovider codex monkeypatch-tempdir-probes-verify-contract-recon
description: Monkeypatch tempdir probes verify contract reconciliation safely
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, contracts, fixtures, monkeypatch]
---

To test config/contract reconciliation without worktree edits, use tempdir + monkeypatch: create temporary config files, monkeypatch file-path lookups, run validators. This isolates contract behavior from live repo state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
