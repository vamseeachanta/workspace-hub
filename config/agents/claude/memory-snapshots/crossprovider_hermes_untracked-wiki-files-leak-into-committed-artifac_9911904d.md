---
name: crossprovider hermes untracked-wiki-files-leak-into-committed-artifac
description: Untracked wiki files leak into committed artifacts when normalizer allows repo-local paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tracking-boundary, git-discipline, artifact-leakage]
---

Generator limiting node inventory to git-tracked files, but `_normalise_link()` accepting any existing repo-local public path, causes untracked filenames to appear in `unresolved_targets`. Validator explicitly allows unresolved targets, so filenames leak as evidence without triggering failure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
