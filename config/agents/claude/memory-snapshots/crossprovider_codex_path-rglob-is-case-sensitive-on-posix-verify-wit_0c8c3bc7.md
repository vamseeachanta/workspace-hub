---
name: crossprovider codex path-rglob-is-case-sensitive-on-posix-verify-wit
description: Path.rglob() is case-sensitive on POSIX; verify with independent find
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [file-globbing, posix-behavior, testing-independence]
---

Python's `Path.rglob('*.pdf')` uses case-sensitive matching on POSIX filesystems, missing uppercase `.PDF` extensions. When claiming corpus completeness (e.g., "only 1 PDF exists"), verify independently with `find -iname '*.pdf'` (case-insensitive) rather than relying on the code under test. Pre-existing uppercase files in the corpus would falsify the claim.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
