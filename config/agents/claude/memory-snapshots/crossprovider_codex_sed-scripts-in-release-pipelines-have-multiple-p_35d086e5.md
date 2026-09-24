---
name: crossprovider codex sed-scripts-in-release-pipelines-have-multiple-p
description: sed scripts in release pipelines have multiple portability hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripts, release, cross-platform, correctness]
---

Version strings with dots are not escaped in sed regex (treating '.' as wildcard), multi-line sed insertions break if changelog_entry contains backslashes, and GNU sed -i is not portable to BSD/macOS. Cross-platform release scripts need escaping or use of platform-agnostic text tools (awk, perl, or Python).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
