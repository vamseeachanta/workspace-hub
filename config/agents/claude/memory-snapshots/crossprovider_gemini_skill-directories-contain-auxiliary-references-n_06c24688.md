---
name: crossprovider gemini skill-directories-contain-auxiliary-references-n
description: Skill directories contain auxiliary references, not SKILL.md only
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, file-inventory, deletion-safety]
---

Skills have `references/*.md`, `docs/`, or other auxiliary files alongside `SKILL.md`. Directory-level inventory required before deletion. Simple `rm -rf <skill>` risks losing supporting documentation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
