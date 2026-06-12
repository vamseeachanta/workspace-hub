---
name: crossprovider codex path-parent-math-in-tests-breaks-silently-on-lay
description: Path.parent math in tests breaks silently on layout changes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, file-paths, robustness]
---

Path(__file__).parents[N] for finding repo root is fragile—if directory structure changes, the hardcoded index silently points to the wrong place. Safer: explicit assertion that parents[N] contains a known marker file, or use env-var (REPO_ROOT) fallback. Silently wrong paths hide test failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
