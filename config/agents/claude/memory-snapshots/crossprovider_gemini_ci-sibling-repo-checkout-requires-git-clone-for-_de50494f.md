---
name: crossprovider gemini ci-sibling-repo-checkout-requires-git-clone-for-
description: CI sibling-repo checkout requires git clone for out-of-workspace paths
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, dependencies, github-actions]
---

actions/checkout requires $GITHUB_WORKSPACE; use `git clone --depth 1` for external repos like assetutilities located at ../path.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
