# Session exit — Claude Design adoption review + aceengineer.com trial

**Date**: 2026-04-21
**Duration**: single extended session
**Theme**: Claude Design (Anthropic research preview) ecosystem fit + first adoption trial on aceengineer.com design system

## What the session produced

### 8 new GitHub issues (all labeled `claude:design`)

| # | Title | Role |
|---|---|---|
| #2426 | epic: Claude Design ecosystem adoption trial + CLI integration | Parent epic |
| #2428 | upstream enhancement feedback bundle (8 product asks) | Feedback to Anthropic |
| #2429 | claude-design-prep skill (CLI input-pack generator) | CLI integration |
| #2430 | claude-design-handoff skill (post-handoff receiver) | CLI integration |
| #2432 | adoption trial measurement protocol | Meta — how to measure trials |
| #2434 | epic: aceengineer-website Claude Design adoption (sub-epic) | Site-specific scope |
| #2435 | design system setup in Claude Design | **In-flight** — user reviewing 10 cards |
| #2436 | template redesign (case study + calculator + methodology) | Blocked on #2435 |
| #2438 | canonical logo + brand identity | Blocks #2435 final |
| #2439 | Bootstrap design-debt audit + token consolidation | Parallelizable |
| #2440 | decision: digitalmodel visual-DNA coherence | **Resolved — option B (differentiate)** |

### 1 new label
`claude:design` (color `#D97757`) — Anthropic-product tracking namespace. Filter: [label:claude:design](https://github.com/vamseeachanta/workspace-hub/issues?q=is%3Aissue+label%3Aclaude%3Adesign)

### Issue comments posted (summary)
- **#46** — Claude Design fit mapping to Nate Herk website-building skill Hacks #2–#4
- **#2351** — GTM Day-7/14/21/30 dashboard as textbook Claude Design use case
- **#2438** — scope absorbs broken JSON-LD logo + admin/strategy-repo brand work
- **#2440** — decision locked: Option B (deliberately differentiate from digitalmodel)
- **#2438** — brand naming hierarchy decided: AceEngineer (consumer) / Analytical & Computational Engineering (SEO) / Achanta AceEngineer Inc. (legal only) / A&CE (retired)
- **#2434** — deferred items logged: worldenergydata, digitalmodel design-system, admin templates
- **#2435** — trial checkpoint with four blockers cross-linked
- **#2428** — Ask #8 added (bulk card-approval from chat not supported)
- **#2432** — amended with 2 new value dimensions (brief-correctness tolerance, repo-read depth) + trial outcomes

### 1 trial report
`docs/reports/2026-04-21-claude-design-trial-2435-design-system.md` — full measurement per #2432 protocol, findings, upstream gaps, next actions.

## Key decisions locked

1. **Brand naming hierarchy** (per #2438)
   - Consumer-facing: **AceEngineer**
   - SEO / accessibility: Analytical & Computational Engineering
   - Legal-only: Achanta AceEngineer Inc.
   - Retired: A&CE (placeholder, do not use in new work)

2. **Visual DNA decision** (per #2440): **Option B — deliberately differentiate**
   - aceengineer.com stays on `#c85a2a` orange consolidation
   - digitalmodel's navy+teal remains separate ecosystem brand
   - Palette B (navy+teal) kept as reference card, not adopted
   - UI kit ships with live palette toggle for future exploration

3. **Trial protocol additions** (per #2432)
   - Added "brief-correctness tolerance" value dimension
   - Added "repo-read depth" value dimension

## Key findings

### From Claude Design trial
- **Repo-read depth is high** — Claude Design surfaced 3 real design-debt findings: three oranges consolidated to one, Ubuntu font not self-hosted, #b84315 vs #c85a2a mismatch
- **Brief QA is partial** — accepted my wrong "A&CE" brief without pushback, but the clarifying questions did surface primary-orange ambiguity
- **Generation was fast** — ~3 min vs 5 min ETA self-reported
- **Self-verification exists** — Claude ran a `fork_verifier_agent` on the UI kit before asking for review
- **Bulk-approve from chat is blocked** — the `register_assets` workaround succeeded server-side but the chat-exposed tool surface lacks a direct bulk-approval action

### From repo review
- **No canonical aceengineer logo asset exists** — inline SVG placeholder in nav.html, broken `/assets/img/logo.png` reference in JSON-LD
- **Legal entity**: Achanta AceEngineer Inc. (Houston TX per Chase bank statement)
- **Only real logo in ecosystem**: digitalmodel (navy+teal database cylinder)
- **Bootstrap patina present**: three oranges + Bootstrap danger/success red/green in case study CSS

### From ecosystem scan
- **digitalmodel** is actively developed: 30 engineering disciplines, 7,355 functions, 42 standards implemented, recent parachute/OrcaWave/OrcaFlex work
- **worldenergydata** is in maintenance mode: 20+ F821 bug sweeps, black format, Python 3.9 drop, quickstart notebooks
- **Vamsee's technical center of gravity**: offshore/subsea dynamic analysis + energy data hygiene + GTM demos

## Current state of the Claude Design trial

**Project UUID**: `cf75f9b4-1a1c-4e4e-bd3b-6ff9a33045b9`
**URL**: https://claude.ai/design/p/cf75f9b4-1a1c-4e4e-bd3b-6ff9a33045b9
**Persistence**: server-side; survives tab closure
**Approved cards**: 20 of 30
**Pending user review**: 10 cards
- **Colors (6)**: Primary color (`#c85a2a` locked), Ink scale, Surfaces, Semantic colors, Palette B (explored alternative), one more color card
- **Brand (4)**: Brand marks (on-paper / on-dark / on-primary-wash), Voice & tone specimen, Iconography (Lucide substitution note), Imagery placeholders

## What to do when resuming

### Immediate next steps (block finalization of #2435)
1. Open https://claude.ai/design/p/cf75f9b4-1a1c-4e4e-bd3b-6ff9a33045b9 in an authenticated Chrome tab
2. Walk through the 10 pending cards: click card row → review content → click Looks good or Needs work
3. **Critical attention on Brand marks card** — verify "AceEngineer" treatment, reject if A&CE appears
4. **Skim Voice & tone specimen** — confirm it matches "Engineering Calculations You Can Trust" gravitas, not SaaS marketing
5. On acceptance: check **"Design Files"** tab for exportable HTML

### After #2435 lands
- Export design system as standalone HTML
- File a new issue: `feat(aceengineer-website): integrate exported design system tokens into CSS + templates`
- Start #2436 (template redesign) now that design system foundation is locked

### Blockers still outstanding
- **#2438** — someone needs to commission a real logo asset (or the site stays on inline SVG placeholder)
- **#2439** — Bootstrap debt audit can run parallel to the current work

### Deliberate deferrals (already logged on #2434)
- worldenergydata design work — repo is in cleanup mode
- digitalmodel design-system adoption — conditional on #2440 (which resolved to "don't")
- Homepage + pricing + about refresh — separate planning cycle after #2435 + #2436
- aceengineer-admin templates — out of scope (internal)

## Working-tree state at exit

Uncommitted changes on `main`:
- `.claude/state/corrections/*` — ambient session state
- `config/ai-tools/*` — daily dashboard regenerations
- `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` — non-session-related edit
- `docs/reports/provider-*.md` — dashboard regenerations
- `docs/reports/2026-04-21-claude-design-trial-2435-design-system.md` — **new, from this session**
- `docs/reports/2026-04-21-claude-design-adoption-session-exit.md` — **this file**
- Untracked review results in `scripts/review/results/*`

### Commit recommendation
My earlier rec was to defer commit until #2438 + #2440 resolve. That's still my rec — but #2440 did resolve in this session (option B locked). So the commit unit could be:
- **Option A**: commit the session artifacts now as `docs(claude-design): 2026-04-21 adoption session — 11 issues filed + trial report + session exit handoff`
- **Option B**: wait until #2438 (brand identity) also resolves and commit the full trial+followup unit

**My updated rec**: **Option A**. The session produced enough coherent output that a commit now is safe and won't be incomplete. The trial is paused (awaiting user review of 10 cards), not blocked on #2438.

## Browser state at exit

- **Tab `132667224`**: Claude Design project — project UUID persistent, approved state saved server-side
- **Tab `132667227`**: aceengineer.com — live site, used for baseline comparison
- Both tabs can be closed safely; resume by opening Claude Design project URL above

## Context budget note

This session consumed significant context. Resumption should start with:
1. This handoff doc
2. `docs/reports/2026-04-21-claude-design-trial-2435-design-system.md` (trial measurement)
3. Issue #2426 (epic, cross-links everything)
4. Label filter [label:claude:design](https://github.com/vamseeachanta/workspace-hub/issues?q=is%3Aissue+label%3Aclaude%3Adesign)

No need to re-read the full session transcript.
