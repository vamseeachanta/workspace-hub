---
name: crossprovider codex ad-hoc-pythonpath-wiring-bypasses-real-environme
description: Ad-hoc PYTHONPATH wiring bypasses real environment resolution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pythonpath, package-management, environment-realism]
---

Shell-script PYTHONPATH overlays (e.g., `PYTHONPATH=./src`) skip packaging, dependency resolution, and installed entry points that downstream repos actually use. Contract tests can pass against an invalid dependency mix and miss real API breakages. Use version-controlled package installation (uv run --project) instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
