# Plan for #3298: Per-session live-link HTML work-review doc

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3298
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** (pending — T2 ⇒ Claude + 1 dispatched provider at code stage)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/build_pages.py` — `HTML_PAGES` explicit allowlist copies pre-rendered standalone HTML verbatim into `public/` → GitHub Pages. This is the live-link publish path (`vamseeachanta.github.io/workspace-hub/<slug>.html`). The session index/latest page hooks here.
- Found: `docs/reports/machine-equality-matrix.html` — precedent for a self-contained, inline-CSS, public-safe HTML artifact published via `HTML_PAGES` (exposes only abstract role-slugs + verdict enums; no hostnames/IPs/paths/client data). The session-review sanitization mode mirrors this discipline.
- Found: `.github/workflows/pages.yml` — builds + deploys `public/`.
- Found: `docs/session-handoffs/*.md` — current session-closeout convention is **Markdown handoffs**, not published HTML and not live-linked. This issue supersedes that for the *quick-review* use case (handoffs remain for deep narrative).
- Gap: no generator that renders a per-session structured payload to a self-contained, public-safe HTML; no sessions index; nothing session-scoped wired into `HTML_PAGES`.

### Standards
Not applicable (harness/governance issue).

### LLM Wiki pages consulted
No relevant wiki pages (workspace-hub-internal harness artifact; out of scope of wiki-sibling routing per `.claude/rules/wiki-sibling-routing.md` §"Do not apply when").

### Documents consulted
- Issue #3298 (this plan's source).
- Issue #2110 — machine-readable session-close structured report (sibling; emits the payload this consumes). `dispatch:ready`, `gate:completeness`.
- `.claude/rules/coding-style.md` — no hardcoded absolute paths (use `$(git rev-parse --show-toplevel)` / `REPO_ROOT`); enforced by `scripts/enforcement/check-no-abs-paths.sh`.
- `config/agents/claude/SOUL.runtime.md` — HTML-default-for-rich-artifacts (#2663); legal-sanity-scan gate (no client identifiers in published code/output).
- Gaps to build from scratch: the generator, the sanitization gate, the sessions index, the `HTML_PAGES` wire-up, and tests.

## Key design decision (REQUIRES USER APPROVAL)

GitHub Pages for `workspace-hub` is **public**. A raw session-review can leak client identifiers (active client / project codenames) and host/path data. Choose the publish mode:

1. **Sanitized public (recommended).** Published page carries only issue/PR numbers (as links), abstract slugs, verdicts, counts, and next-step headers — same public-safe posture as `machine-equality-matrix.html`. Full-fidelity (with names) stays in a local/private copy. Keeps a true live link with zero PII surface. A `legal-sanity-scan` gate runs on the published artifact and fails closed.
2. **Private surface.** Full-fidelity published to an authenticated/private location; no public Pages live-link.
3. **Both.** Sanitized public live-link + private full-fidelity artifact.

Recommendation: **Option 1** for v1 (gets the live link the user asked for, safely); Option 3 as a follow-on if full-fidelity review is needed.

## Implementation steps (TDD — after approval)

1. **Payload contract.** Define a minimal session-review JSON schema (slug, date, summary, issues[], prs[], artifacts[], decisions[], next_steps[]). Reuse #2110's payload fields where they exist; this issue owns only the human-facing render. *(test: schema validation + missing-field tolerance)*
2. **Sanitization gate.** `scripts/workflow/session_review_sanitize.py` — strip/abstract client identifiers (drive from `.legal-deny-list.yaml` + active-client registry), absolute paths, hostnames, IPs. Fail closed if a denied token survives into the public render. *(test: known PII tokens are scrubbed; clean payload passes; `scripts/legal/legal-sanity-scan.sh` green on output)*
3. **Renderer.** `scripts/workflow/build_session_review.py` — payload → self-contained HTML (inline CSS, no external asset refs), public-safe mode applies the sanitization gate. Output `docs/reports/sessions/<date>-<slug>.html`. *(test: self-containment — no `<link>/<script src>` to external; required sections present; issue/PR numbers render as links)*
4. **Index.** `docs/reports/sessions/index.html` — rolling, newest-first list of session reviews with live links. *(test: ordering; entries match files on disk)*
5. **Publish wire-up.** Add the sessions index (slug `sessions`) and the latest per-session page to `build_pages.py` `HTML_PAGES`. *(test: `build_pages.py` includes the slugs; `public/sessions.html` produced)*
6. **Docs.** Update `docs/governance/SESSION-GOVERNANCE.md` (shared with #2110) describing how a session emits its review and where it lands.

## Acceptance criteria
- Session-review HTML generated from structured input, self-contained, public-safe per the approved mode.
- Sessions index reachable at a live Pages URL; newest-first.
- Sanitization gate has a test; `legal-sanity-scan.sh` passes on published output.
- Docs explain the emit→land flow.
- Sibling #2110's payload is consumed (not re-derived) where it exists.

## Out of scope
- A Stop/SessionEnd hook to auto-emit (that is #2110's surface; this consumes its output).
- Full-fidelity private hosting beyond a local copy (follow-on if Option 3 chosen).

## Risks
- **PII leak to public Pages** — mitigated by the fail-closed sanitization gate + legal-sanity-scan (the load-bearing control; reviewed adversarially at code stage).
- **Allowlist drift** — `build_pages.py` is an explicit allowlist by design; adding a per-session latest page must not glob. Keep index static-slug; per-session pages copied by enumeration, not glob.
