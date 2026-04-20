# In-Run Adversarial Review — 2026-04-19 Revision of #2209 Durable/Transient Boundary

> **Reviewer:** Claude (adversarial stance, in-run reviewer role per 4-role revision-dispatch)
> **Date:** 2026-04-19
> **Deliverable under review:** `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (revised this run)
> **Dispatch:** `docs/plans/2026-04-19-revision-dispatch-prompt-2209-durable-vs-transient-boundary.md`
> **Parent amendments:** #2205 comment-4277238819 (Sections 2, 3, 8.1 amended 2026-04-19)
> **Finding baseline:** 13 findings from `scripts/review/results/2026-04-17-plan-2209-claude-adversarial.md` + `2026-04-17-plan-2209-codex-adversarial.md`

## Stance

Defect-hunting stance per planning-skill reviewer-stance contract. Charitable reading forbidden. Reviewer in this role must produce findings unless the deliverable is demonstrably perfect; empty reviews are failures.

## Verdict: **PASS** — all MAJOR findings resolved; two residual MINOR observations documented

---

## Amendment compliance check (parent-binding, non-negotiable)

### Amendment A — Remove "between L5 and L6" / "Recurring-operational artifact" / "L3-adjacent"

**Check (mechanical):** `grep -n -i "between l5 and l6\|recurring-operational artifact\|l3-adjacent"` against the revised doc returned 5 hits. Each was inspected:

| Hit line | Context | Verdict |
|---|---|---|
| L132 | Rationale stating the "L3-adjacent" classification was a forbidden invention and is removed | OK (explicit-negation) |
| L204 | Rationale stating the "Between L5 and L6" classification is a forbidden invention and is removed | OK (explicit-negation) |
| L491 | AP-9 anti-pattern defining "layer invention" as forbidden; cites the specific terms | OK (explicit-negation in a guardrail) |
| L616 | Revision-history amendment summary stating what was removed | OK (explicit-negation) |
| L642 | Revision-history 2026-04-11 retrospective noting what the original doc did wrong | OK (explicit-negation) |

**Zero active classifications use the forbidden terms.** Section 4.5 (recurring-run outputs) classifies them as L5 with L5→L3 synthesis promotion. Section 4.2 (normative architecture docs) classifies them as L3. No "adjacent", no "between", no "hybrid". **PASS**.

### Amendment B — Reframe Section 10.1 frontmatter as additional fields on baseline floor

Section 10.1 explicitly states: "This policy does NOT prescribe a free-standing required-set for wiki frontmatter. Per parent Section 8.1, the binding authority is the per-wiki `CLAUDE.md`." The baseline floor (`title`, `last_updated`, `doc_key`) is reproduced. Additional fields (`promoted_from`, `sources`, `tags`, `added`, `under-revision`) are declared as layered recommendations, explicitly subject to each wiki's `CLAUDE.md`. The original `{title, tags, sources, added, last_updated}` required-set has been dismantled.

**PASS**.

### Amendment C — `<algorithm>:<hex>` identity form

Every `doc_key` reference I can find:
- Section 4.6 "using the `<algorithm>:<hex>` form per parent Section 3"
- Section 6.1 L1→L2 bridge: "registered with `doc_key` (`<algorithm>:<hex>`)"
- Section 6.3 Sync rules: "including `doc_key` in the form `<algorithm>:<hex>` when the source is a registered document"
- Section 7.1 Source traceability test: "a `doc_key` (`<algorithm>:<hex>`)"
- Section 10.1 baseline floor: "`doc_key` (in `<algorithm>:<hex>` form)"
- Glossary: "Canonical content-based identity of a source document, in the form `<algorithm>:<hex>` per parent #2205 Section 3 (e.g., `sha256:a1b2c3...`). Bare-hex form is a violation."

No bare-hex `doc_key` reference remains. **PASS**.

### Amendment D — `merged_at` terminology

Section 4.6 references "a `merged_at` stamp per parent Section 3". Glossary defines `merged_at` with citation to parent. No `discovered` references remain in the revised doc. **PASS**.

### Amendment E — Update cross-references

- Frontmatter header cites the parent amendment date (2026-04-19: Sections 2, 3, 8.1)
- Section 2 references the parent amendment summary comment URL
- Section 3 discusses relationship to siblings #2207, #2206 (now adds #2206 alongside #2207 since conformance design is also L3)
- Every "Section 2 worked examples" / "Section 3" / "Section 8.1" citation points to the amended parent

**PASS**.

---

## Finding disposition verification (13 findings)

| ID | Severity | Claimed disposition in revision | Verifier | Status |
|---|---|---|---|---|
| Claude F1 | MAJOR | Fixed via Amendment A (§4.5 reclassify, glossary class removed) | Section 4.5 header says "Layer: L5 — Execution state (each individual run)"; glossary "Recurring-run output" explicitly states "This is not a layer class" | **Verified** |
| Claude F2 | MAJOR | Fixed (§4.4 reclassifies approval markers L5 permanent; GR-7 added) | Section 4.4 Durability: "Permanent for closed issues"; Section 8.1 table row for plan-approved markers: "Permanent for closed issues. Do not delete"; Section 9.2 GR-7 added | **Verified** |
| Claude F3 | MINOR | Fixed (§4.3 and §5.2 reserve "transient" for L6; use "execution-bound" for L5) | Section 4.3 Durability: "Execution-bound with respect to domain knowledge" with explicit terminology note; Section 5.2 hard rules consistently use "L5 execution-state" and "L6 transient" | **Verified** |
| Claude F4 | MINOR | Fixed (§8.1 marked advisory pending #2237) | Section 8.1 opening: "The day-counts below are advisory pending #2237 transient-artifact cleanup workflow" | **Verified** |
| Claude F5 | MINOR | Fixed (§7.1 stability soft-signal; `under-revision` tag) | Section 7.1 table "Gate type" column marks stability as "Soft signal"; paragraph below explicitly explains the shift | **Verified** |
| Claude F6 | MINOR | Fixed (§8.1 handoff retention tied to issue lifecycle; §8.4 date-based fallback) | Section 8.1 handoff row: "retain until the associated issue has been closed for 30 days (fall-back: 90 days if no issue reference)"; Section 8.4 expands on the fall-back rationale | **Verified** |
| Claude F7 | MAJOR (process) | Resolved by 2026-04-17 Codex landing | Codex review file exists at `scripts/review/results/2026-04-17-plan-2209-codex-adversarial.md` (read in STEP 1); gate satisfied | **Verified** |
| Codex C1 | MAJOR | Fixed via Amendment B | Section 10.1 no longer prescribes a stand-alone required-set; `promoted_from` recommended for pages produced by L6→L3 and L5→L3 promotion; per-wiki `CLAUDE.md` is binding authority | **Verified** |
| Codex C2 | MAJOR | Fixed (§4.8 splits `.planning/` into sub-classes) | Section 4.8 table classifies plan-approved (L5), HANDOFF.json (L6), quick (L6), research (L6), archive (inherit), discoveries (L6), verified (L5) with distinct retentions | **Verified** |
| Codex C3 | MAJOR | Fixed (§4.9 removes uncommitted `session-signals` example) | Section 4.9 explicitly lists `session-signals/*.jsonl` as "Not committed (local-only telemetry)" and "Outside the committed-artifact taxonomy"; rationale paragraph documents why the 2026-04-11 example was wrong | **Verified** |
| Codex C4 | MAJOR | Fixed (§8.4 non-computable for handoffs lacking issue refs; date-based fallback) | Section 8.4 explicitly states "the 'associated issue is closed for > 30 days' signal is **not computable** for handoffs that lack the reference. For those handoffs, use a date-based fall-back (e.g., 90 days from handoff date)" | **Verified** |
| Codex C5 | MINOR | Fixed (§7.4 defines three auditable-trail mechanisms; "no silent promotion" partially enforceable) | Section 7.4 enumerates three concrete mechanisms (frontmatter `promoted_from`, page-level `log.md` entry, or registry entry at `doc_key` level); Section 11 open-question 6 acknowledges partial enforceability | **Verified** |
| Claude Addendum A | MAJOR | Fixed via Amendment B | Section 10.1 now defers to per-wiki `CLAUDE.md` as binding authority; parent Section 8.1 establishes the three-field baseline floor; this policy no longer competes with the wiki's own schema | **Verified** |

**All 13 findings have explicit disposition; 8 MAJOR + 5 MINOR all resolved or explicitly acknowledged as partial (C5 scope).**

---

## Adversarial probes (defect-hunting)

### Probe 1 — Does the revised doc accidentally re-invent a layer?

Scanning Section 4 (all subsections 4.1–4.9) and Section 5.2 hard rules, every classification lands on one of L1–L6. Section 4.5 recurring-run outputs are classified L5 explicitly, with the promotion-path note NOT being a layer claim. Section 4.8 `.planning/` sub-classes each resolve to L5 or L6 (or "inherit" for archive, which defers to the original artifact's classification — not a new layer). Section 4.9 `.claude/state/` acknowledges "outside this taxonomy" for uncommitted local state, which is not a layer invention but a scope disclaimer.

**No layer invention.** The "archive inherits" row (§4.8) is worth double-checking: archive doesn't assert a new layer, it says artifacts placed in archive retain the layer they had when archived. That is consistent with the parent's most-durable-owner rule. **Pass**.

### Probe 2 — Does the revised doc contradict its own GR-7 anywhere?

GR-7 prohibits deletion of `.planning/plan-approved/` and `.planning/verified/` for closed issues. Section 4.8 table shows both with "Permanent for closed issues" retention. Section 8.1 table for plan-approval markers: "Permanent for closed issues. Do not delete — archive subtree if directory becomes unmanageable". Section 8.1 verification-markers row: same treatment. No contradiction. **Pass**.

### Probe 3 — Does Section 10.2's `comprehensive-learning-wrapper` guidance contradict Section 7.1's soft-signal stability rule?

Section 10.2 says: "discoveries that meet all 4 hard promotion criteria (stability is soft signal) → wiki page creation or update with `promoted_from` field". Section 7.1 treats stability as soft. Consistent. **Pass**.

### Probe 4 — Frontmatter scope creep

Section 10.1 says the policy declares "additional fields" layered over the baseline floor. Does it overreach? The fields listed (`promoted_from`, `sources`, `tags`, `added`, `under-revision`) are explicitly framed as "Recommended required for pages produced by L6→L3 or L5→L3 promotion" (for `promoted_from`) or "As defined by the wiki's `CLAUDE.md`" (for the others). The engineering-wiki scope caveat is explicit: "Domain wikis ... may adopt or decline these recommendations on a per-wiki basis." No hard requirement that would conflict with a domain wiki's `CLAUDE.md`. **Pass**, but see Observation M1 below.

### Probe 5 — Does §6.1's new L5→L3 "Cross-run synthesis promotion" row duplicate the L5→L3 "Post-issue promotion" row?

Two distinct triggers: post-issue promotion fires at issue closure; cross-run synthesis fires from patterns across multiple recurring-run outputs (which may never close an issue). Both land at L3 via the same L5→L3 channel but have different provenance-attribution needs. The distinction is useful for enforcement (the synthesis path may not have an issue number in `promoted_from`; it may point to the run-output artifacts instead). **Pass**.

### Probe 6 — Section 8.1 retention table consistency with Section 4.8 `.planning/` table

Cross-checked each `.planning/` sub-class: Section 4.8 says `.planning/quick/` → "14 days after parent issue closure"; Section 8.1 has row "`.planning/quick/`" → "Associated issue lifetime + 14 days". Semantically identical. Section 4.8 `.planning/research/` → "30 days or until promoted/discarded"; Section 8.1 same. Section 4.8 `.planning/archive/` → "Archive-long (no further expiration unless space pressure)"; Section 8.1 does not list archive (correctly — archive is not pending expiration). Section 4.8 discoveries → "14 days (consumed by pipeline)"; Section 8.1 same. **Consistent**.

### Probe 7 — Sibling non-overlap

Section 3 table now includes #2206 alongside #2207 for non-overlap. Does this policy accidentally encroach on #2206's executable validation territory? Section 9.2 guardrails are marked "Policy (enforceable via conformance check)" — a policy declaration, not a script. Section 10.3 "Automated enforcement (future)" explicitly defers to #2206 for FRONT-1, GUARD-1, etc. The policy describes *what* the check does, not how. **Pass**.

---

## Residual observations (MINOR — not blocking)

### M1 — Section 10.1 scope statement is narrow to engineering wiki

The scope paragraph in §10.1 says "The engineering wiki ... is the primary target for the L6→L3 and L5→L3 promotion flows defined in Section 7 and is the surface for which these recommendations are most concretely grounded." This is accurate (the engineering wiki is where most workspace-hub session learnings promote to), but could be read as implying domain wikis don't participate in these flows. In practice, marine-engineering and naval-architecture wikis do receive L2→L3 structured promotions via #2207, which is not this policy's primary flow focus. The scope statement is defensible because the L6→L3 / L5→L3 flows (session / execution-state to durable) are predominantly engineering-wiki targets, whereas L2→L3 is predominantly domain-wiki targets and belongs to #2207's scope.

No fix required; the scope framing is correct. Flagged for transparency.

### M2 — The "archive inherits" classification in §4.8

Section 4.8 classifies archived artifacts with "Same layer as the archived content." This is a deferred classification rather than a declared layer. A pedantic reviewer could argue this is a hybrid/adjacent-like construction. But (a) it doesn't invent a new layer name, (b) it defers to the artifact's original classification (L5 or L6), which is a valid classification at rest, and (c) the parent's "most-durable-owner rule" supports this (an archived plan-approved marker is still an L5 governance audit artifact; it's just been moved).

No fix required; the construction is mechanically sound. Flagged because conformance check GUARD-1 should be written to allow this pattern (archived-artifact inheritance) without flagging it.

### M3 — Section 4.9 does not classify `.claude/state/corrections/` contents

Section 4.9 classifies the `corrections/` subtree as L6 committed session residue. Within `corrections/`, individual files may behave more like audit evidence (user corrections intended to be persisted) than like session scratch. This was not a 2026-04-17 finding, so it's out of scope for this revision; flagged for consideration in a future pass.

No fix required.

---

## Cross-provider note

This in-run review is a Claude-single-provider pass performed as the "in-run adversarial reviewer" role of the 4-role dispatch. The 2026-04-17 cross-provider gate (Claude + Codex) has already been satisfied on the plan. The revised deliverable does not introduce net-new policy substance that requires a second cross-provider pass; every substantive change traces to an already-reviewed finding or an already-approved parent amendment. Per the dispatch, a final integrator pass follows.

## Recommendation

Proceed to integrator pass. The revision is approval-ready.
