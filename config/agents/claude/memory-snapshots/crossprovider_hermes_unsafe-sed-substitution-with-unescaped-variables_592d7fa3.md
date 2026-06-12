---
name: crossprovider hermes unsafe-sed-substitution-with-unescaped-variables
description: Unsafe sed substitution with unescaped variables corrupts replacements
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-safety, sed-escaping, injection]
---

Pattern `sed "s|__PATH__|${var}|g"` fails when var contains `&`, `|`, or backslashes. Sed treats `&` as "insert matched string"; backslash escapes the next char. Escape the replacement text first: `escaped=$(printf '%s' "$var" | sed 's/[&\\]/\\&/g'); sed "s|__PATH__|${escaped}|g"`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
