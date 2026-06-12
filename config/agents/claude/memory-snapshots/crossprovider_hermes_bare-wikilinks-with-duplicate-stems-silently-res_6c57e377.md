---
name: crossprovider hermes bare-wikilinks-with-duplicate-stems-silently-res
description: Bare wikilinks with duplicate stems silently resolve to wrong page
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, wikilink-resolution, ambiguity]
---

When multiple public pages share the same stem (e.g., `wikis/a/wiki/concepts/shared.md` and `wikis/b/wiki/concepts/shared.md`), bare `[[shared]]` links resolve to the first match after lexicographic sorting of full paths, not alphabetically last or closest. The resolution is deterministic but wrong because it depends on iteration order, not semantic intent. Fix: require fully-qualified links or emit unresolved when ambiguous.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
