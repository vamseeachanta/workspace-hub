# Plan for digitalmodel#1456: Close the 10 section one-pager PDF gaps (#1444 reference index)

> **Status:** adversarial-reviewed (r1 Claude MINOR/4 repo-verified @ dm 3ecb97b1 + r2 Codex MAJOR/10 → r3 inline patch, this revision)
> **Complexity:** T2 — 10 authored SPECS entries + scoped PDF builds + a coverage ratchet; no engine code.
> **Date:** 2026-07-06
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/1456 (repo: **digitalmodel** — attestation-vs-repo mismatch is a known tooling artifact)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-dm1456-claude.md | ...-codex.md (local-only by convention)

---

## Resource Intelligence Summary

### Existing repo state (probed on origin/main 2026-07-06; intel also posted on the issue)
- **Gap set (machine-derived, #1444 `capabilities-inventory.json:pdf_gaps`)**: `fatigue, cfd, wall-thickness, viv, field-development, naval-architecture, geotechnical, production-engineering, drilling-engineering, cathodic`. Nuance: `wall-thickness`/`cathodic` have explorer-level PDFs (work-kind); the gap is the **`kind="section"`** one-pager the reference index keys on.
- **SPECS entry shape** (`scripts/capabilities/build_onepagers.py` L51+): `dict(id="sec-<anchor>", kind="section", title, std="<standards line>", path="capabilities/#<anchor>", blurb, figures=[(num,label)×~3], bullets=[×~5])`. In-script guards: duplicate-id assert, unknown-CLI-id exit. **Scoped builds**: `build_onepagers.py sec-fatigue …` builds only named ids (keeps the 10-PDF diff scoped).
- **Build mechanics** (per #1411 + #1444 sessions): headless Chrome `--print-to-pdf` (agent runs need the sandbox-override pattern; `CHROME=` env override exists); module reads `assets/logo/digitalmodel_logo_compact.svg` at import (sparse worktrees must include `assets/logo`); the moored-mark logo is portable-by-construction but every produced PDF still gets the **`pdftocairo -png` Cairo check** per `.claude/rules/svg-pdf-portability.md`.
- **Completion signal already exists**: the #1444 `--check` freshness gate (CI: `tests-capabilities` via DOMAINS + quality-gates registries) FAILS after SPECS changes until `capabilities-inventory.json` + spec MD are regenerated — regeneration is part of this lane, and afterward `pdf_gaps` must be `[]`.
- **Content sources for authoring**: each section's own cards/text in `docs/api/capabilities/index.html` + the linked engine/explorer pages. **Overclaim precedent**: the #1391 fatigue section was flagged in verify for standards overclaim and fixed by grep-matching every standard named in `std`/bullets to a linked implementation file — that discipline is a correctness rule here.
- PDFs are committed artifacts — CI never renders them (no Chrome-in-CI dependency).

### Standards / LLM Wiki
The one-pagers NAME standards (API/DNV/ASME lines) but introduce no standards-derived constants — calc-citation contract not triggered. Every named standard must be grounded (rule 2). No wiki content.

### Documents consulted
dm#1456 (contract + intel comment) · #1444 spec/inventory (gap source) · #1411 (one-pager program precedent + Chrome/sandbox lesson) · #1391 (fatigue overclaim lesson) · `.claude/rules/svg-pdf-portability.md` · memory `project_dm_capabilities_page_expansion` · drive-file index ("capability one-pager pdf brochure", `--caller plan-resource-intel`): no relevant documents.

### Gaps identified
10 SPECS section entries + 10 PDFs + inventory regeneration + a coverage RATCHET test (post-close, `pdf_gaps == []` becomes the permanent contract: a future section without its one-pager fails CI).

### Evidence (embedded verification)
- Issue states: dm#1456 OPEN (intel comment 4899384413); #1444 CLOSED (merged #1455); #1411/#1391 precedents merged.
- SPECS shape/guards/scoped-CLI: quoted from origin/main in this session (sec-ffs full entry, main() L770+).
- **Reproduction proofs: N/A — additive content/artifact issue; no alleged failure.** The gap list is machine-derived and re-derivable.
- Parallel-work check at implementation start (capabilities content lanes #144x churn section interiors; SPECS/build_onepagers is a distinct file — low collision; single-lane sparse worktree incl. `assets/logo`).

## Artifact Map
| Artifact | Kind | Path (digitalmodel) |
|---|---|---|
| 10 SPECS entries | edit | `scripts/capabilities/build_onepagers.py` (section-kind, `sec-<anchor>` ids) |
| 10 PDFs | generated+committed | `docs/api/capabilities/pdf/sec-<anchor>.pdf` |
| Inventory + spec regen | generated | `docs/capability-map/capabilities-inventory.json` + `capabilities-ia-spec-1444.md` |
| Ratchet + grounding tests | edit | `tests/capabilities/test_capabilities_inventory.py` (+2 tests) |

## Deliverable
1. **10 authored `kind="section"` SPECS entries** — title/std/blurb/figures/bullets per section, authored FROM the section's own cards and its linked engine pages. **Grounding is a CI TEST, not PR prose** (r2 F1, r1 F3): `test_specs_standards_grounded` extracts standards tokens from each section-kind `std` line, resolves the section's linked files (from the #1444 inventory), and FAILS on any token with zero grep evidence (r1 verified mechanizable: fatigue→`sn_library.py` 17× RP-C203; cfd→runnable verification pages). Bullets beyond named standards stay descriptive-of-linked-cards only; PR body carries the per-section evidence table as secondary human-review aid. Figures reuse numbers already published on the page/explorers (no new claims).
2. **10 PDFs** built via scoped `build_onepagers.py sec-… ×10`; each verified with `pdftocairo -png` (Cairo) before commit; diff scoped to exactly the 10 new PDFs + the SPECS edit + regenerated capability-map artifacts.
3. **Inventory + spec regenerated** — `pdf_gaps: []`; the #1444 `--check` gate green.
4. **Coverage ratchet**: new test asserts (a) every section-kind SPECS id maps to a live section anchor (no orphan `sec-*` entries), and (b) **every live section has a section-kind SPECS entry AND its committed PDF exists**. Full bijection is justified by repo reality, not aspiration: r1 verified `sec-validation` + its committed PDF already exist, so ALL 12 current sections carry one-pagers — total coverage IS the established practice (refutes the exclusion-list concern, r2 F2). Escape hatch for future structural work (r2 F3): the test reads an `onepager_exempt: []` list from `capabilities-clusters.yml` (EMPTY today; adding to it is a reviewable diff, not a silent bypass). NOTE (r1 F1): `pdf_gaps == []` in the inventory is a SPECS-presence signal only — `load_pdf_specs` never checks disk; ratchet test (b) is the sole closure of that hole, which is exactly why it exists.

### Correctness rules
1. **No overclaim**: std/bullet grounding per #1391 (grep evidence recorded in the PR body per section).
2. **Cairo-verified PDFs** (svg-pdf-portability rule); render check with Liberation-Sans substitution only for the throwaway raster.
3. **Scoped builds only** (named ids) — never a full rebuild that churns existing PDFs.
4. **dm env**: `.venv/bin/python`; Chrome sandbox override documented; no `uv run`.
5. **Single-PR, single-push sequencing** (r1 F2, r2 F4): the lane is verified fully green LOCALLY (all tests incl. ratchet + freshness) before the one branch push — no intermediate red pushes (the freshness gate goes red the moment SPECS changes, so partial pushes are forbidden by rule, and the ecosystem's push-immediately discipline is explicitly suspended for this lane's intermediate states).
6. **Diff hygiene enforced, not assumed** (r1 F4, r2 F5/F6/F8): scoped builds verified by `git status --short` against an expected-path allowlist (exactly 10 new `sec-*.pdf` + SPECS + 2 capability-map artifacts + test file; r1 verified scoped section builds emit PDFs only — `api/` assets are work-kind-gated). NEVER run argless `build_onepagers.py` (Chrome timestamps would churn all 49 committed PDFs). Per-file size sanity < 2 MB; rebuild-churn accepted as a known property (committed-PDF practice is established: 12 `sec-*.pdf` already in-tree), mitigated by the scoped-only rule.
7. **Content check beyond renderability** (r2 F10): each new PDF passes `pdftotext`-based title/anchor spot-check (section title present, non-empty text, expected page count 1) in addition to the Cairo raster.

## Pseudocode
n/a — content authoring + existing pipeline invocation; the only new code is the two tests:
```python
def test_specs_section_ids_biject_live_sections()  # sec-* set == live anchor set (both directions)
def test_every_section_pdf_committed()             # pdf file exists per section-kind entry
```

## TDD Test List
1. `test_specs_section_ids_biject_live_sections` — RED now (10 missing), GREEN after entries land; fails on orphan `sec-*`; honors the (empty) `onepager_exempt` list.
2. `test_every_section_pdf_committed` — RED until the 10 PDFs are committed (the real closure of the pdf_gaps hole, r1 F1).
3. `test_specs_standards_grounded` — standards tokens in section-kind `std` lines grep-matched against the section's linked files; RED for any ungrounded claim (r2 F1).
4. Existing suite stays green; `test_committed_inventory_is_fresh` forces the regeneration step (single-push rule keeps CI green throughout).

## Acceptance Criteria (mirrors dm#1456)
- [ ] 10 section-kind SPECS entries + committed `sec-<anchor>.pdf` each; diff contains no unrelated PDF churn
- [ ] Per-section grounding evidence (standard → linked file) recorded in the PR body
- [ ] Every PDF passes the Cairo (`pdftocairo`) render check
- [ ] Inventory + spec regenerated: `pdf_gaps == []`; tests-capabilities CI green including the new ratchet
- [ ] Card-wiring on index.html explicitly DEFERRED to the revamp lane (spec-only boundary from #1444 still applies; note in PR)
- [ ] **Domain-accuracy review by the owner** (r2 F7): the authored engineering claims (fatigue/CFD/VIV/geotech/drilling summaries) are owner-reviewed at the PR — grounding tests prove standards presence, not summary accuracy; the owner IS the domain engineer and his merge follows an explicit content pass (AC checkbox in the PR body)
- [ ] Diff-hygiene check recorded in the PR: `git status` allowlist match + per-PDF size + pdftotext title checks all green

## Risks
1. **Content overclaim** — the main risk; mitigated by rule 1 + PR-body evidence + adversarial code review at PR stage.
2. Binary diff size (10 PDFs) — expected; scoped build keeps it minimal.
3. Chrome/sandbox variance on the build box — documented override; PDFs are deterministic enough for commit (font substitution differences acceptable; not golden-tested).
4. Ratchet may bite the NEXT section author — intended (that is the point); DOMAINS test docstring says so and points at this plan.
5. Full worktree checkout timeout — sparse set: `scripts/capabilities docs/api docs/capability-map tests .claude assets/logo`.

## Adversarial Review Summary
- **r1 (Claude subagent, repo-verified @ dm 3ecb97b1): MINOR/4.** Decisive verifications: gap set exact (22−12=10); zero orphan `sec-*`; **`sec-validation` + PDF already committed** (total coverage = established practice); scoped builds emit PDFs only; 12 committed `sec-*.pdf` precedent; grounding mechanizable.
- **r2 (Codex): MAJOR/10** — several MAJORs refuted by r1's repo facts (ratchet over-breadth F2, api-asset side-effects F8); the surviving substance patched.
- **r3 (this revision, inline per `feedback_r3_inline_loop_break_pattern`):** grounding → CI test (r2 F1, r1 F3); `onepager_exempt` escape hatch, empty today (r2 F3); pdf_gaps-is-SPECS-only note + ratchet as the true closure (r1 F1); single-PR/single-push green sequencing (r1 F2, r2 F4); diff-hygiene allowlist + size + no-argless-rebuild (r1 F4, r2 F5/F6/F8); pdftotext content check (r2 F10); owner domain-review AC (r2 F7); issue-state claims repo-qualified (r2 F9 — the attestation resolves #1456 against workspace-hub; the dm issue is OPEN).
- Awaiting user approval; not self-labeled.
