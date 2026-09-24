---
name: crossprovider codex shell-enforcement-script-path-scoping-test-patte
description: Shell enforcement script path-scoping test pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, enforcement, shell-scripts, path-scoping]
---

To add a `--paths` argument to shell enforcement scripts (e.g., legal-sanity-scan), use: create temp git repo in test, copy script in, write local config, run with `subprocess.run(..., cwd=repo, capture_output=True)`, assert return codes and scoped stderr/stdout. Verify the script rejects unrelated untracked files outside supplied scope while still catching denied content inside scoped paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
