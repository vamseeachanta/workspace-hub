---
name: crossprovider codex asserting-zero-references-via-grepping-missing-f
description: Asserting zero references via grepping missing files is invalid
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [code-review, verification, adversarial-review]
---

Using `grep -c pattern missing_file.py 2>/dev/null → 0` to confirm zero references is circular: the missing file + stderr suppression both return zero. Test instead with existence checks first, then grep only if the file is present. Otherwise, missing file + zero-reference claim become indistinguishable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
