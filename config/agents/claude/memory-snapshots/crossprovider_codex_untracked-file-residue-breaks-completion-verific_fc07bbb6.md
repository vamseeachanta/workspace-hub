---
name: crossprovider codex untracked-file-residue-breaks-completion-verific
description: Untracked file residue breaks completion verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [closeout, git-state, artifact-tracking]
---

Implementation artifacts (reports, test files) left untracked after work causes false negatives in 'done' verification. Staged vs. untracked state should be checked at closeout via `git ls-files --error-unmatch <path>` for each expected artifact. Untracked residue is a closeout gate, not a carry-forward.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
