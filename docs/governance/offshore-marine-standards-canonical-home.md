# Offshore-Marine Standards Canonical Home — Phase 1 Decision

> **Status:** Phase 1 LOCKED. Phase 2 (populate DNV-OS-E301 + API RP 2SK) PENDING.
> **Date:** 2026-04-26
> **Authority:** User-approved via aceengineer-strategy [#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) `status:plan-approved` (label flipped 2026-04-26) + decision-panel licensing-posture acceptance. Local approval marker: `.planning/plan-approved/aces-4.md` (revision-bound to plan SHA `7af80b652`).
> **Plan:** [`docs/plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md`](../plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md)
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)

---

## 1. Audit of Current Dispersion (per Phase 1 §1 of plan)

| Path | Content type | Suitability for canonical home |
|---|---|---|
| `data/standards/promoted/` | Raw promoted standards artifacts (binary/PDF references) | Not suitable — `data/` is for raw payloads, not LLM-citable wiki content |
| `docs/standards/` | **Mislabeled.** Contains governance/policy docs (HARD-STOP-POLICY, REVIEW_GATE_BYPASS_POLICY, etc.), NOT actual engineering standards content | Not suitable — already serves a different purpose; renaming would be disruptive |
| `knowledge/wikis/marine-engineering/wiki/` | LLM-maintained markdown with sanctioned schema (per `knowledge/wikis/marine-engineering/CLAUDE.md`); subdirs `entities/`, `concepts/`, `sources/`, `comparisons/`, `visualizations/` | **Strongest candidate** — schema authority is already in place; aligns with `project_wiki_standards_path_decision.md` routing principle |
| `knowledge/wikis/marine-engineering/wiki/standards/` | Does not yet exist; no content | Path-name aligns with sanctioned routing principle; this is the home being decided |

## 2. Decision — Canonical Path

**`knowledge/wikis/marine-engineering/wiki/standards/<publisher>/<code-id>/`**

Examples:
- `knowledge/wikis/marine-engineering/wiki/standards/dnv/os-e301/<clause-slug>.md`
- `knowledge/wikis/marine-engineering/wiki/standards/api/rp-2sk/<clause-slug>.md`

Rationale:
- Aligns with the existing schema at `knowledge/wikis/marine-engineering/CLAUDE.md` (auto-generated 2026-04-07 by `llm-wiki init`); keeps standards as a first-class peer of `entities/`, `concepts/`, `sources/`.
- Consistent with the routing principle in workspace-hub memory `project_wiki_standards_path_decision.md` (sanctioned across marine-engineering, engineering, naval-architecture wikis).
- Adjacent to (not in conflict with) workspace-hub [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) which is scoped strictly to CSA Z276; aces-#4 establishes the *general* substrate and CSA can land within it whenever #2471 closes.
- The two-level `<publisher>/<code-id>/` nesting (rather than `<publisher>-<code-id>.md` or flat) supports clause-level pages without name collisions when DNV and API have similarly-named clauses.

## 3. Frontmatter Schema (Phase 1 lock — Phase 2 populates per-page)

Required fields on every standards page:

| Field | Type | Source | Notes |
|---|---|---|---|
| `code_id` | string | locked by workspace-hub [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) calc-citation contract | Globally unique. Convention: `<publisher>-<code>-<clause>`, e.g., `dnv-os-e301-3.5.2`. Smoke-test enforces uniqueness. |
| `publisher` | string | per #2481 | Lowercase, hyphenated. e.g., `dnv`, `api`, `iso`, `abs`, `csa` |
| `revision` | string | per #2481 | Year + edition where present, e.g., `2024-7th`, `2018` |
| `clause_id` | string | new for standards subtree | The clause/section identifier as used in the source document, e.g., `3.5.2`, `Section 4.1` |
| `effective_date` | ISO-8601 date | new for standards subtree | When the revision became effective; useful for legacy-asset compliance lookups |
| `superseded_by` | string or null | new for standards subtree | `code_id` of the superseding clause if revised, else null |
| `license_class` | enum (4 values) | new for standards subtree per [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) F2 patch (extending #2481) | See §5 below; default `summary-only-with-citation` for copyrighted standards |
| `jurisdiction` | string (optional) | optional | e.g., `North Sea`, `GoM`, `global` for transboundary |
| `supersedes` | string (optional) | optional | inverse of `superseded_by` |

Phase 2 populates these for each clause page; Phase 1 locks the schema.

## 4. Crosswalk Index Format

`knowledge/wikis/marine-engineering/wiki/standards/_crosswalk-index.yaml` (file at the standards subtree root, not inside any publisher subdir).

```yaml
# Crosswalk index — DNV ↔ API ↔ ISO ↔ ABS clause equivalence mappings
# Format: each entry maps one source code_id to a relation list

mappings:
  dnv-os-e301-3.5.2:
    - target: api-rp-2sk-5.3
      relation: equivalent  # equivalent | partial-overlap | not-equivalent
      notes: "Both specify factor-of-safety floor for ULS condition"
    - target: iso-19901-7-7.6
      relation: partial-overlap
      notes: "ISO covers a broader scope; only the line-tension subsection overlaps"
  api-rp-2sk-5.3:
    # reverse-direction entries for queryability (not strictly needed but cheap)
    - target: dnv-os-e301-3.5.2
      relation: equivalent
```

Phase 2 populates with at least 5 equivalence/partial-overlap mappings (per plan acceptance criteria).

Smoke test: every `target` resolves to an existing `<publisher>/<code-id>/<clause-slug>.md` page.

## 5. License-Class Handling

Per [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) v2 patch (F2 finding) and decision-panel row 5 (user accepted default), the `license_class` field has exactly four allowed values:

| Value | Use case | Default for | Publication scope |
|---|---|---|---|
| `summary-only-with-citation` | Copyrighted standards (DNV, API, ISO, ABS): page body is our summary + citation; **no verbatim clause text ≥30 consecutive tokens** (enforced by smoke test per F3 patch). | DNV/API/ISO/ABS clause pages | Public per epic #1 |
| `cc-by-publishable` | Content we authored: worked examples, crosswalk metadata, our interpretive notes. | crosswalk index entries; worked examples | Public; requires attribution |
| `public-domain-quoted` | Content from public-domain sources (US government docs, expired copyright). May contain verbatim quotes. | rare for offshore/marine | Public, no restriction |
| `private-derived` | Client-derived under client-opt-out per [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) telemetry agreement. | rare for substrate; common for #6 corpus entries that were opt-out'd | Default-private; expires per opt-out clause |

**Outside-counsel engagement** (user accepted default 2026-04-26): we engage outside counsel for derivative-works review **before** broad rollout beyond the DNV-OS-E301 + API RP 2SK seed pair. The seed pair lands under `summary-only-with-citation` based on industry-typical fair-use guidance (summary + citation, no verbatim ≥30 tokens). Counsel review locks the policy for ISO/ABS expansion and for any verbatim quotes beyond fair-use thresholds.

## 6. Verbatim-Text Threshold

Per F3 patch in plan: **30 consecutive whitespace-tokenized, case-folded, punctuation-stripped tokens.** Source plaintext fixtures live at `tests/standards/fixtures/source-text/<code-id>.txt` (gitignored — fixtures are sourced from licensed PDFs we own access to, never committed). Smoke test SKIPs cleanly if fixture absent.

## 7. Open Items Locked at Phase 2 Execution Time

These were flagged in plan §Risks as locked-at-execution rather than blockers:
- **DNV revision baseline:** propose latest published edition (DNV-OS-E301:2024 if available, else DNV-OS-E301:2021); confirm in Phase 2 first commit.
- **API revision baseline:** API RP 2SK 4th Edition (2024) if available, else 3rd Edition (2008 reaffirmed 2015); confirm in Phase 2 first commit.
- **Crosswalk scope v1:** DNV ↔ API only for v1 seed; ISO 19901-7 + ABS Mooring Guide deferred to v2 (post-counsel review).

## 8. Phase 2 Pre-Conditions

Phase 2 (populate seed standards content) requires:
1. Phase 1 LOCKED — ✅ this artifact.
2. Outside counsel engaged (user-driven, per §5).
3. Source plaintext fixtures provisioned at `tests/standards/fixtures/source-text/{dnv-os-e301,api-rp-2sk}.txt` (gitignored) — required for verbatim-threshold smoke test.
4. Cross-repo workflow per plan §Cross-Repo Workflow for `digitalmodel` (separate `digitalmodel/` branch + cherry-pick to `digitalmodel/main`, mirroring workspace-hub #2481 precedent of cherry-pick `c3be1472`).
5. Recommended: Gemini cross-review on the v2 plan before Phase-2 commits land in digitalmodel (especially F2/F3 specifics). Codex remains UNAVAILABLE per upstream regression.

When all five pre-conditions are met, Phase 2 may proceed under the existing `status:plan-approved` label without re-approval.

## 9. Cross-References

### `cites:` (artifacts this decision relies on)

- `knowledge/wikis/marine-engineering/CLAUDE.md` — schema authority
- workspace-hub [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) (CLOSED — calc-citation contract) — locks `code_id`/`publisher`/`revision` baseline schema this extends
- workspace-hub [#2476](https://github.com/vamseeachanta/workspace-hub/issues/2476) (plan-approved — semantic-equivalence contract) — gates broad rollout
- workspace-hub [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) (CLOSED — llm-wiki ↔ GTM boundary) — sanitization contract for public publication
- workspace-hub [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (OPEN — CSA Z276 routing only) — adjacent decision; CSA can land at `wiki/standards/csa/z276/...` within this canonical home when #2471 closes
- [`flywheel-wedge-decision.md`](./flywheel-wedge-decision.md) — locks why DNV-OS-E301 + API RP 2SK are the seed pair

### `binds:` (issues bound to this decision)

- [aces-#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5) — Public mooring quick-screen calculator (cites standards via `code_id`)
- [aces-#6](https://github.com/vamseeachanta/aceengineer-strategy/issues/6) — Public failure-case browser (cites standards via `code_id`)
- [aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7) — Mooring failure intelligence integration (cites standards in failure-mode taxonomy)
- [aces-#9](https://github.com/vamseeachanta/aceengineer-strategy/issues/9) — Pricing & licensing (the `license_class` enum here informs the public-substrate license terms)

A change to the canonical path (e.g., moving from `wiki/standards/<publisher>/<code-id>/` to a flat structure) would require explicit reconcile of all 4 issues above and any landed Phase 2 content.
