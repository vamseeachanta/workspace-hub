---
name: crossprovider codex cli-path-independence-via-context-inference
description: CLI path independence via context inference
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cli, path-handling, portability]
---

CLI tools that accept path arguments should infer context (repo root, config dir) from the supplied paths, not Path.cwd(), to remain usable outside the invoking directory. When a manifest or config lives under a known location (e.g., `data/document-index`), derive `repo_root = manifest_path.parent.parent` and add a regression test that runs the CLI from a temp directory with absolute paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
