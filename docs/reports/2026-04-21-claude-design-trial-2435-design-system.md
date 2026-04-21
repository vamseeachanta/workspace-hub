# Claude Design trial — aceengineer.com design system

**Issue**: #2435 (design system setup) under epic #2434 → #2426
**Protocol**: #2432
**Date**: 2026-04-21
**Trial started (Generate clicked)**: 2026-04-21T14:55 UTC (approx)
**Status**: GENERATION COMPLETE — awaiting user review of 25 cards + 4 design decisions

## Outcome summary (strong positive)

Claude Design genuinely read the linked repo and surfaced real design debt beyond a visual mockup:
- **Noticed color divergence** — three oranges in the codebase (`#b84315` favicon vs `#d35400`/`#e67e22` Bootstrap alerts) → proposed consolidation on `#c85a2a`
- **Noticed font availability** — Inter self-hosted at `assets/fonts/inter/`, Ubuntu not self-hosted → kept Inter primary, loaded Ubuntu from Google Fonts (CDN fallback)
- **Correctly scoped** — recognized aceengineer.com is a single product (no app, no docs site), produced one UI kit instead of speculating about multiple surfaces
- **Asked specific questions** (not vague "what do you think?") — 4 clear asks:
  1. Confirm primary orange: `#c85a2a` vs favicon `#b84315`
  2. Send 2–3 real project photos (marketing UI kit is photo-less)
  3. Pick icon direction: Lucide substitution, custom SVG, or existing sprite in repo
  4. Copy tone tweaks before locking

### Verdict on the "brief vs. repo conflict" trial dimension
**Hybrid, weighted toward repo truth.** The text brief informed tone/constraints; the repo code informed font stack, color palette, and product scope. When in tension, repo facts won (Ubuntu inclusion from `assets/fonts/ubuntu-*.woff2` presence, not from the brief which said Inter primary).

## Inputs provided to Claude Design

### Company blurb
> A&CE (AceEngineer): AI-native offshore/subsea engineering consulting. Static marketing + technical showcase website at aceengineer.com featuring engineering calculators (fatigue life, S-N curves, NPV field-development), case studies, methodology pages, and 5 parametric demos. Primary client-acquisition funnel. Stack: static HTML/CSS/JS deployed on Vercel, Inter typeface. Target audience: offshore/marine/energy engineering managers evaluating consulting partners.

### GitHub repo linked
`vamseeachanta/aceengineer-website` (via OAuth — pre-authorized from prior session, no consent popup)

### Design notes (guardrails)
> Audience: offshore/marine/energy engineering managers — credibility over flair. Avoid generic SaaS aesthetics. Favor precision, technical authority, clean hierarchy.
> Typography: Inter variable (primary), Ubuntu fallback. Heading 600-700, body 400.
> Color: neutral base, single strong accent. Not a rainbow palette.
> Key components: calculator input forms, case study cards, methodology step diagrams, CTAs for capability-summary-v1.pdf download, result tables.
> Layout: content-dense, generous whitespace around figures, desktop-first.
> Avoid: marketing emoji, cartoon illustrations, testimonial carousels, "As seen in" logo walls, pricing/plans cards.

### NOT provided (tool limitations)
- Inter `.woff2` files at `assets/fonts/inter/` — `upload_image` tool in claude-in-chrome accepts only screenshots
- `favicon.svg` — same limitation
- `.fig` file — none exists in repo

## Baseline — current aceengineer.com design (pre-trial)

Observed on live site 2026-04-21 via browser screenshot:

| Dimension | Current state |
|---|---|
| Brand mark | "A&CE" white wordmark in rounded-rect, top-left |
| Nav color | Deep plum/burgundy (~#5E2B3D) with white text |
| Hero BG | Dark slate/navy (~#3A404C) |
| Primary CTA | Rust orange (~#C25A2A) — "Request Pricing", "Get a Free Assessment" |
| Hero headline typography | Display serif (NOT Inter) with italic lowercase accents |
| Body typography | Sans (likely Inter or similar) |
| Section pattern | Alternating dark hero / warm cream body sections |
| Tone | Opinionated and non-generic — "Engineering Calculations You Can Trust. Traceable to International Standards." |
| Existing voice | Strong already — "Tethering timeless engineering to a single source of truth." |

### Critical trial observation
**The site already has an opinionated design** — this is not a blank-slate generation. Claude Design will effectively propose a refresh, not a from-scratch design. The brief guidance I provided (Inter + neutral palette) partially contradicts what's on the live site (serif-display headline + plum/rust palette). This creates a revealing test dimension:

- **Does the linked repo code override the text brief?** → generated output will match current site
- **Does the text brief override the repo code?** → generated output will look like my neutral-Inter brief
- **Does it blend both?** → hybrid

This tells us how Claude Design weights its inputs when they conflict.

## Cost dimensions (per #2432)

| Dimension | Value so far | Final |
|---|---|---|
| Wall-clock in Claude Design (setup) | ~3 min (via CLI automation) | TBD |
| Wall-clock in Claude Design (generation) | self-reported ~5 min | TBD after completion |
| Wall-clock on CLI-side prep | ~2 min (reading repo, drafting blurb + notes) | Final |
| Chat turns to reach acceptable design | 0 (generation started from setup form) | TBD after iteration |
| Inline canvas comments used | 0 | TBD |
| Iteration count | 0 | TBD |

## Value dimensions (per #2432) — TO COMPLETE POST-GENERATION

- [ ] Subjective quality vs. parallel `/gsd:sketch` attempt (not run; would require separate session)
- [ ] Stakeholder readability — does it beat the existing site for the target audience?
- [ ] Did inline canvas comments meaningfully beat chat-only feedback? (need iteration phase to answer)
- [ ] Did Claude Design catch a layout issue a code-only approach would have missed?
- [ ] Did the HTML export integrate cleanly into existing patterns?

## Upstream gaps observed (feed to #2428)

Already aligned with filed upstream asks:
- **Ask #1** (CLI-initiated sessions) — confirmed valuable: setup form-fill via claude-in-chrome was workable but janky; `claude design create --from-repo` would be materially better
- **Ask #3** (git-diffable export format) — not yet tested; will validate on export

New potential gaps to surface after generation:
- Asset-upload path for `.woff2`/`.svg` brand files when browser automation is the UI — the "Drag files here or browse" zone requires a real file picker, which limits agent-driven workflows

## Next actions

- [x] Wait for generation completion — generated in ~3 min (faster than 5 min ETA)
- [x] Capture generated canvas screenshot — 25 cards + 4 clarifying questions captured
- [ ] Await resolution of follow-up issues before completing Value dimensions:
  - [ ] #2438 — canonical logo + brand identity resolution (blocks brief correction)
  - [ ] #2440 — digitalmodel visual-DNA coherence decision (blocks final palette lock)
  - [ ] #2439 — Bootstrap design-debt audit (parallelizable)
- [ ] Rebrief Claude Design and regenerate affected cards (wordmark, palette)
- [ ] Complete 25-card "Looks good / Needs work" review after rebrief
- [ ] On final acceptance: export as standalone HTML, run reconciliation audit
- [ ] Comment final report as link on #2435 and #2426
- [ ] Update #2428 with the new enhancement ask (mid-session brand correction without full regenerate)

## Follow-up issues filed from trial findings

| Issue | Role | Relationship |
|---|---|---|
| #2438 | Canonical logo + brand identity | Blocks #2435 final |
| #2439 | Bootstrap design-debt audit | Parallelizable with #2435 |
| #2440 | digitalmodel visual-DNA decision | Informs #2435 palette |

All carry the `claude:design` label and are linked from the #2434 aceengineer-website umbrella.

## Upstream enhancement asks added during this trial

Started the trial with 7 asks in #2428. Added an **8th** during the review phase:

- **Ask #8 — Bulk card-approval from chat** — Claude Design admitted it can't mark cards as approved from its side because the action lives in the review UI. It attempted a workaround via `register_assets` with `status: "approved"` which **did succeed** server-side (27 pending → 10 pending), but the chat-exposed tool surface should include an explicit approval action for agent-driven workflows.

## Fast-path review outcome

User-selected fast path: auto-approve Type/Spacing/Components/UI Kit cards, review Colors + Brand individually.
- Manual click approvals: 2 (Type · display, Type · body — the latter because it was in "being reviewed" state when batch ran and got skipped)
- Chat-driven batch approvals: 17 cards via Claude's `register_assets` workaround
- Remaining pending for user review: 10 cards
  - **Colors (6)**: Primary color `#c85a2a`, Ink scale, Surfaces, Semantic colors, Palette B (demoted to "explored alternative"), one other color card
  - **Brand (4)**: Brand marks (on-paper / on-dark / on-primary-wash), Voice & tone specimen, Iconography (Lucide substitution note), Imagery placeholders
