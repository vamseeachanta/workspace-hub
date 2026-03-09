# WRK-1055 Plan Review — Claude

**Reviewer**: Claude (Sonnet 4.6)
**Date**: 2026-03-09
**Plan ref**: assets/WRK-1055/wrk-1055-engineering-mcp-servers.md

## Verdict: APPROVE

## Strengths

1. **Correct sequencing** — catalog file first, then install, then evaluate additional servers.
   This ensures the config artifact exists before the server is wired in.
2. **Supply-chain risk addressed** — commit SHA pinning requirement is explicit in Phase 2.
   Trust assessment checklist in Phase 4 doc is appropriate.
3. **Scope boundary clear** — out-of-scope section explicitly calls out WRK-578, arXiv/BSEE
   wrappers, Codex/ace-linux-2. Prevents scope creep.
4. **Tests per phase** — each phase has a concrete test condition, not just "verify manually".
5. **Route B appropriate** — 2 new files + 1 install + Codex cross-review. Not over-engineered.

## Concerns

1. **Phase 2 install command uncertainty** — `claude mcp add` scoping (`-s user` vs `-s project`)
   needs to be confirmed at execution time. User-scoped means all Claude sessions; project-scoped
   means only this workspace. Recommend starting with `-s project` (lower blast radius).
2. **Phase 3 registry query** — `registry.modelcontextprotocol.io` programmatic API endpoint
   not confirmed live. Execution should fall back to `mcpmarket.com` browse if API is unavailable.
3. **No rollback plan** — if Semantic Scholar MCP causes context issues (slow, noisy, or
   permissions overreach), removal is `claude mcp remove`. Should be documented in Phase 4 doc.

## Minor Suggestions

- Phase 4 doc should include `claude mcp remove <name>` as the removal pattern.
- `mcp-servers.yaml` should include a `removed_at` field schema for servers that get uninstalled.

## Conclusion

Plan is sound, well-scoped, and executable. Concerns are implementation details to handle
at execution time, not plan-level blockers.
