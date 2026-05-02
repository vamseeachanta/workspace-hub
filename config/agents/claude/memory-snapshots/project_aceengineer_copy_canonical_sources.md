---
name: AceEngineer website copy — canonical source priority
description: Priority order of canonical sources when reviewing aceengineer-website copy changes; llm-wiki is out of scope by design, aceengineer-strategy is private with privacy wall.
type: project
originSessionId: d65995dc-088e-41bc-9993-fd21f32743de
---
When reviewing proposed copy changes to `vamseeachanta/aceengineer-website` (especially from A&CE Design System project handoffs), consult canonical sources in this order:

1. **Live `aceengineer-website/*.html`** (public) — already-shipped firm framing, schema.org, meta, capability headings. This is the strongest canonical reference for most copy questions.
2. **`aceengineer-strategy/strategy/*.md`** (**PRIVATE**) — positioning.md, go-to-market.md, ideal-customer.md, competitors.md, pricing-model.md. The TRUE canonical source for firm-level phrasing, but protected by a privacy wall (see `aceengineer-strategy/.claude/CLAUDE.md`). **Paraphrase rules, cite live-site evidence that embodies them. Never quote verbatim in public issues.**
3. **llm-wiki (`knowledge/wikis/`)** — explicitly **OUT OF SCOPE** for firm copy per `engineering/wiki/overview.md` ("how we engineer, not what we engineer"). Only consult for domain/technical claims.
4. Tier-1 repo READMEs for module-count / capability claims.

**Why:** 2026-04-24 A&CE Design System handoff asked for a canonical check against llm-wiki. llm-wiki doesn't have firm copy by design. Real canonical is #1 + #2. Design-system project cannot reach workspace-hub and will keep asking for this check.

**How to apply:** Invoke `.claude/skills/coordination/aceengineer-website-copy-alignment/SKILL.md` whenever a copy-review handoff arrives. Result is always a filed issue on `vamseeachanta/aceengineer-website` tagged `content,design-system` with a Match / Drift / Gap verdict. First execution: issue #6 (2026-04-24, verdict B+C — "consulting practice" drift against live site + gap in llm-wiki).

**Hard rule discovered:** the live `about.html` contains explicit negative constraints ("We deliver automated workflows, not consulting hours"; "AceEngineer is the firm ... not a contractor with a laptop"). Treat live-site negatives as canonical rules — any proposed phrase landing on the forbidden side (e.g. "consulting practice") is drift, not a rephrasing.

**2026-04-24 resolution (first execution):** #6 resolved with Option C + capability naming. Final About lede locks CAP-01 "computational fatigue assessment" + CAP-02 "riser & mooring analysis" + CAP-03 "diffraction analysis" — all three map one-to-one onto existing `engineering.html` headings so no new capability block required. Follow-ups filed: #7 (FPSO + panel-mesh imagery), #8 (engineering.html heading renames, SEO-sensitive), #9 (canonical firm-copy home decision — recommend `brand/copy.yaml` + lint script). Life-extension & integrity management deliberately NOT filed — it's a founder scope-activation call, not a copy task; reintroduce to About lede only after an `engineering.html` block lands first.

**Structural insight for future sessions:** when a CAP span is a genuine NEW capability claim (no live `engineering.html` heading to anchor to), the honest move is usually to swap it for an extant capability rather than defer a Services-page backfill. Deferred backfills rot. The "Services-leads-About" sequencing (Option A) only makes sense when the capability is already delivered somewhere and just needs a page.
