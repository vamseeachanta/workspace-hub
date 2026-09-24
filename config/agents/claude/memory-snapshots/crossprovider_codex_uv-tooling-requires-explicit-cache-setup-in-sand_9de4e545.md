---
name: crossprovider codex uv-tooling-requires-explicit-cache-setup-in-sand
description: UV tooling requires explicit cache setup in sandboxed environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv, python, ci-cd, sandbox-hermiticity, error-handling]
---

When invoking `uv run` in scripts, must export `UV_CACHE_DIR=${REPO_ROOT}/.cache/uv` before execution to ensure hermeticity in sandbox/CI. Absence of this export causes silent failures when the default cache directory (~/.cache/uv) is unreachable, especially when failure modes are masked with `|| echo 0` fallbacks, turning runtime errors into false-negative success reports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
