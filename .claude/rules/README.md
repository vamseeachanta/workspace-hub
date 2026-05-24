# Rules
Universal constraints only. Stage-specific rules live in micro-skills (`.claude/skills/workspace-hub/stages/`).

Files:
- `coding-style.md` — edit safety, path handling, harness file size
- `patterns.md` — enforcement gradient (prose → script → hook)
- `calc-citation-contract.md` — citation emission for standards-derived constants (per [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685))
- `codes-standards-data-routing.md` — vendor-licensed codes/standards data → private `vamseeachanta/llm-wiki` (post 2026-05-20 visibility flip)
- `wiki-sibling-routing.md` — `llm-wiki` + `llm-wiki-<client>` data/knowledge/result routing contract (suffix form, one-sibling-per-client, projects-as-folders; enforced by Level-2 `scripts/enforcement/check-wiki-sibling-frontmatter.py`; per [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778))
- `goal-invocation.md` — `/goal` invocation contract; consult [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) catalog before invoking
