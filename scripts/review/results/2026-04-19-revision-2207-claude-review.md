# In-Run Adversarial Review: 2026-04-19 revision of #2207 Provenance + Reuse Contract

> **Reviewer:** Claude (adversarial stance, per planning-skill reviewer-stance contract)
> **Date:** 2026-04-19
> **Deliverable under review:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (revised 2026-04-19)
> **Revision dispatch prompt:** `docs/plans/2026-04-19-revision-dispatch-prompt-2207-provenance-reuse-contract.md`
> **Prior findings reviewed:** 11 combined (7 Claude + 4 Codex) from 2026-04-17 reviews
> **Parent amendments checked:** #2205 Sections 2, 3, 8.1 (amended 2026-04-19)

## Stance declaration

This review assumes the revision has defects until proven otherwise. Empty-findings sections are failures. The revision touched identity rules, status enums, field semantics, and frontmatter authority simultaneously — four independent axes where internal inconsistency is the default failure mode. I verified each claim against live repo state and the amended parent rather than against the revision's own internal logic.

## Verdict: **MINOR** — approval-ready with documented residuals

No MAJOR defects remain. Three MINOR observations worth noting but not blocking.

---

## Compliance audits

### Parent-section compliance (amendments A–E)

| Amendment | Parent section | Compliance evidence in the revised contract |
|---|---|---|
| A. `<algorithm>:<hex>` identity | #2205 §3 | §3.1 adopts verbatim; §3.2 forbids cross-namespace joins; §8.5 rewritten accordingly |
| B. Status vocabulary | #2205 §3 | §4.1.3 table is the parent superset verbatim; §5.1 branches on every value |
| C. `merged_at` rename | #2205 §3 | §4.1 + §4.1.2 + §4.2 use `merged_at`; readers accept `discovered`; code-side rename deferred (Open Q3) |
| D. Frontmatter authority | #2205 §8.1 | §6.3 restates baseline floor, delegates binding to wiki `CLAUDE.md`, labels `source_ref`/`domain`/`promoted_from` as recommendations |
| E. Cross-references | — | §2 updated; amendment comment linked |

All five amendments are fully applied. Internal consistency checked: `merged_at` appears 11 times; `discovered` appears only in legacy/backward-compat contexts (6 times, all qualified); no mixed usage found in normative claims.

### Finding disposition vs. the revision-dispatch contract

| Finding | Disposition claimed | Evidence located in revised contract | Disposition verified |
|---|---|---|---|
| F1 (gap status) | FIXED | §4.1.3 + §5.1 branches | Yes — `gap` present, live-data evidence cited |
| F2 (#8.3 contradiction) | FIXED | §8.3 fully rewritten, §9.3 captures follow-on | Yes — two-field requirement explicit |
| F3 (OCR inconsistency) | FIXED | §3.4 row split, §5.3 aligned | Yes — sidecar vs. re-save disambiguated |
| F4 (L3 owns `wiki_refs`) | FIXED | §4.3 back-link-field definition added | Yes — `wiki_refs` described as materialized at L2 |
| F5 (primary path) | FIXED | §4.1.1 scopes `path` as machine-local | Yes — `provenance[]` named as authoritative list |
| F6 (back-population) | PARTIAL | §9.4 + §10 item 4 + §11 item 3 | Yes — grandfather is now explicit; filing remains open (partial is correct) |
| F7 (cross-provider) | FIXED (out-of-contract) | §12 revision history notes both reviewers | Yes — both 2026-04-17 reviews cited |
| C1 (MD5 legacy) | FIXED | §3.1 + §3.2 + §8.5 | Yes — namespace rule explicit; cross-namespace joins forbidden |
| C2 (summary filename prefix) | FIXED | §4.2 + §6.3 + §6.2 + §8.5 | Yes — all summary-path references show `sha256:<hex>` prefix |
| C3 (status overload) | FIXED | §4.1 + §4.1.3 | Yes — `processing_status` normalized; surfaces enumerated |
| C4 (discovered drift) | FIXED | §4.1.2 + §12 | Yes — `provenance.py:82` live behavior cited; "first-indexed" semantic retracted |

All 11 findings have explicit disposition and supporting evidence in the revised document.

### Scope-drift audit

| Forbidden action per dispatch prompt | Status in revision |
|---|---|
| Modify parent operating model | Not done — parent unchanged |
| Modify #2206 / #2209 deliverables | Not done — adjacent contracts unchanged |
| Modify `data/document-index/*` data files | Not done |
| Modify `scripts/data/document-index/*.py` writers | Not done — rename explicitly deferred (§10 Q3, §11 item 2) |
| Modify `.claude/**`, `.codex/**`, `config/**`, `tests/**` | Not done |
| Touch unrelated dirty/untracked files | Not done (git status unchanged for those) |

No scope drift.

### Frontmatter-authority delegation audit

The revision must make it impossible for a reader to conclude that #2207 binds L3 frontmatter fields.

- §1 out-of-scope table explicitly delegates binding to `CLAUDE.md`
- §2 row for parent §8.1 states "binding happens in the relevant wiki `CLAUDE.md`, not here"
- §6.3 title reads "recommended fields" (not "required")
- §6.3 body: "This contract does not and cannot bind frontmatter fields. What follows are *recommended* fields…"
- §6.3 example block carries the qualifier "Illustrative only. The binding schema is whatever `knowledge/wikis/engineering/CLAUDE.md` declares at the time of page creation."
- §10 Q8 explicitly calls out that wiki `CLAUDE.md` updates are out of scope for this contract.

Delegation is unambiguous.

---

## Remaining observations (MINOR)

### MINOR-R1 — `wiki_refs` still appears in §4.2 recommended-extended-fields table

§4.3 defines `wiki_refs` as a back-link field materialized at L2 from L3 emissions. §4.2 still lists `wiki_refs` in the recommended-extended-fields table with owner layer "Materialized at L2; originates from L3". That is internally consistent with §4.3 but may mislead a skim reader into thinking `wiki_refs` is a standard L2 provenance field like `summary_ref`. Not a defect — §4.3 disambiguates — but the dispatch prompt's "MINOR where cost is low" threshold could support adding a one-line footnote in §4.2 pointing to §4.3. Left as-is; acceptable.

### MINOR-R2 — §11 item 2 describes a rename that Section 10 Q3 also describes

§11 order 2 ("Rename `discovered` → `merged_at` in `provenance.py` emitted records") duplicates Open Question 3. Both explicitly defer to a future code-side issue. The duplication is intentional (follow-on sequence vs. open-question narrative) but a reader might wonder whether one supersedes the other. Not a defect; both point to the same deferred work.

### MINOR-R3 — F6 remains PARTIAL because filing a concrete issue is outside this pass

The revision correctly marks F6 as PARTIAL because ending the grandfather period requires filing a new GitHub issue, which the dispatch prompt forbids (no GitHub-issue creation beyond the §2207 summary comment). The partial disposition is the right call under the dispatch constraints. The user should be aware that fully resolving F6 requires follow-on issue creation.

---

## Verified claims (spot-checks)

- `phase-a-index.py:135-139` does emit `md5:` for 32-char input on `og_standards` source — matches §3.1 evidence citation.
- `provenance.py:82` does stamp `datetime.now(timezone.utc)` at merge time when no upstream value is present — matches §4.1.2 evidence citation.
- `data/document-index/summaries/` contains files with `sha256:<hex>.json` naming — matches §4.2 / §6.3 claims (spot-checked via Codex review artifact; directory structure consistent with 2026-04-17 verification).
- `knowledge/wikis/engineering/CLAUDE.md` currently declares `{title, tags, added, last_updated}` required (does NOT include `doc_key`) — matches §6.3 claim. Adopting the baseline floor will require an edit from the wiki maintainer.
- Parent operating model amendments live at `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` Sections 2, 3, 8.1 — verified.

## Non-defects reconsidered

- The revision retains §3.2 comparison rule "Case-insensitive hex is safe; normalize to lowercase for comparison." This was not in the prior contract. I checked whether live data mixes cases: `phase-a-index.py:135-139` emits whatever content_hash came from the og_standards DB, which historically is lowercase. This is a correct defensive addition, not a drift.

- §9.1 entry for `phase-a-index.py` says "Keep existing namespacing; migration opportunity noted" — I considered whether this under-specifies an actionable change. It does not: parent Section 3 says "No hard sunset; opportunistic upgrade only" verbatim, and the revision inherits that policy faithfully.

## Recommendation

Advance to integrator pass. No MAJOR issues remain. The three MINOR observations above are acceptable residuals given the scope constraints of the revision dispatch.
