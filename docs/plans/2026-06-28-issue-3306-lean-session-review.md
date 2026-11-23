# Plan for #3306: Lean reference-layer session-review doc

> **Status:** plan-approved (design forks resolved by user in-window 2026-06-28; see below)
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3306
> **Client:** N/A
> **Lane:** lane:claude
> **Refines:** #3298 (shipped v1)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/workflow/build_session_review.py` (#3298, in main) — v1 renderer RESTATES content inline (`summary`, `kpis[]`, prose `decisions[]`/`artifacts[]`/`next_steps[]`, PR descriptions). This is what makes the page heavy.
- Found: `scripts/workflow/session_review_sanitize.py` — fail-closed sanitizer; unchanged by this issue.
- Found: `scripts/build_pages.py::build_sessions()` — publish path; unchanged (still copies index + manifest pages).
- Found canonical homes already in repo: `docs/plans/` (plans), `docs/governance/*-decision.md` (durable decisions; 6+ exist), `docs/session-handoffs/` (handoffs), `.claude/state/sessions/` (raw logs), `docs/reports/` (reports).
- Gap: no reference-based payload schema; renderer holds prose instead of pointers.

### Standards / Wiki
Not applicable (harness artifact; out of wiki-sibling scope).

### Documents consulted
- #3306 (source), #3298 (v1), #2110 (machine-readable session-close — **NOT yet implemented**, so the page references artifacts directly, never via #2110).
- `.legal-deny-list.yaml` + `scripts/legal/check-client-pii.py` (the CI PII gate that caught v1's own leak — lean labels reduce leak surface).
- `config/agents/claude/SOUL.runtime.md` (HTML-default #2663; legal gate).

## Design forks (RESOLVED by user 2026-06-28)
- **Decisions home = where decided (issue/PR).** The page links the GitHub issue/PR comment where a decision was made; durable/architectural forks additionally link `docs/governance/<date>-<slug>-decision.md`. No new per-session decisions file.
- **Session log home = the handoff doc IS the log.** `docs/session-handoffs/<date>-<slug>.md` is the single canonical per-session record (handoff + log + decisions narrative). The page links it once as the "record".

## Target page shape (lean)
A grouped link-index — one line/label per artifact, no restated prose beyond an optional one-line `headline`:
```
Session — <title>           2026-06-28 · lane:claude
Issues     #3306 · #2110
PRs        #3299 · #3304
Plans      docs/plans/2026-06-28-issue-3306-…md
Decisions  publish-mode=sanitized-public → #3298 (comment)
Record     docs/session-handoffs/2026-06-28-…md   (handoff = log = decisions)
Reports    docs/reports/sessions/…
```

## Implementation (TDD)
1. **Payload v2 = reference entries.** `refs: [{type, label, num?|path?|href?}]`, `type ∈ {issue,pr,commit,plan,decision,handoff,report,link}`. Plus optional one-line `headline`. Deprecate inline `summary/kpis/decisions/artifacts/next_steps` (renderer ignores them; v1 payloads still render via a thin back-compat shim that maps known fields → refs). *(tests: schema acceptance; v1→v2 shim)*
2. **Link resolution** in the renderer:
   - `num` + type issue/pr/commit → `REPO/issues|pull|commit/{num}`.
   - `path` → `REPO/blob/main/{path}` AND verified to exist at build time (missing → rendered with a ⚠ marker + logged, never silently broken).
   - `href` → used verbatim.
   *(tests: each type resolves; missing path flagged)*
3. **Lean render.** Group refs by type into a compact link list; drop KPI tiles and prose sections. Keep self-contained inline CSS + the sanitize-then-`assert_clean` gate (labels only → smaller leak surface). *(tests: no prose blocks; grouped links present; self-contained; sanitized)*
4. **Regenerate** this session's page from a v2 payload (lean) so main carries a worked example.
5. **Docs.** Update `SESSION-GOVERNANCE.md`: payload is reference-only; decisions→issue/PR(+governance), log=handoff doc.

## Acceptance criteria
- Page is a grouped link-index; zero restated prose beyond one `headline`.
- Every ref resolves (GitHub URL or `blob/main` path); path refs verified present at build (missing → visible ⚠, not silent).
- Decisions link the issue/PR (or governance decision); the handoff doc is linked as the session record.
- Sanitized-public gate + `check-client-pii` still pass; tests cover the reference schema, link resolution, and the v1→v2 shim.

## Out of scope
- #2110 machine-readable report (separate; not a dependency).
- Auto-emitting the handoff/log (separate session-close hook work).
