---
name: crossprovider codex github-tarball-lacks-git-directory-tests-calling
description: GitHub tarball lacks .git/ directory; tests calling git ls-files fail
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [github, ci, git-metadata]
---

Tarballs downloaded from GitHub intentionally omit `.git/` metadata. Tests that call `git ls-files` will fail even though the extracted content is correct. Workaround: initialize a scratch Git index over the extracted files with `git init` to supply Git metadata without altering content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
