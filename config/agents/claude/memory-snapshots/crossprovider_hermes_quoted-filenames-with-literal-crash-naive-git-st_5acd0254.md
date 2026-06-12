---
name: crossprovider hermes quoted-filenames-with-literal-crash-naive-git-st
description: Quoted filenames with literal ` -> ` crash naive git-status parsers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, shell-parsing, error-handling]
---

Splitting on `" -> "` before proper quote-aware parsing breaks on legitimate filenames like `a -> b.txt`. assethold#49 `_split_status_path()` crashes with 'No closing quotation' on such files. Use shlex or structured git output; never split on delimiters inside quoted strings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
