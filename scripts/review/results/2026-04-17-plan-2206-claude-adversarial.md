# Adversarial Review: #2206 Pyramid Conformance Checks Design

> **Reviewer:** Claude (adversarial stance, per planning-skill reviewer-stance contract)
> **Date:** 2026-04-17
> **Deliverable under review:** `docs/document-intelligence/pyramid-conformance-checks.md` (created 2026-04-11)
> **Plan under review:** `docs/plans/2026-04-16-issue-2206-pyramid-conformance-checks.md`
> **Prior reviews consulted:** `2026-04-11-issue-2206-claude-review.md`, `2026-04-11-issue-2206-final-review.md`, `2026-04-16-plan-2206-claude-overnight.md` — all Claude.

## Stance declaration

Same stance as #2207 and #2209 sibling reviews: assume defects until proven otherwise; no praise; no restatement; evidence required. #2206 is structurally exposed because it consumes rules from the other two contracts — defects in #2207 (e.g., status enum, MD5 namespace, summary filename pattern) propagate into #2206 as checks that would either falsely fail on shipped data or vacuously pass on missing inputs. This review hunts for those propagation defects in particular.

## Verdict: **MAJOR** — not approval-ready

Five MAJOR findings: four contract-vs-reality conflicts (the conformance checks would behave incorrectly against today's repo) plus the same MAJOR cross-provider-gap process defect as #2207 and #2209. The check design also commits the exact violation it is supposed to detect — child-issue redefinition of parent vocabulary.

---

## Finding 1 — MAJOR: DT-1 wiki-frontmatter check requires fields that contradict the contracts it claims to enforce

**Claim under review (Section 5.4 DT-1, "Pass signal"):** "Every wiki page has `title`, `tags`, `sources`, `last_updated` in frontmatter."

**Conflicting source authority — #2209 GR-1 + GR-4 (the rules DT-1 claims to validate per Appendix A):** GR-1 requires "frontmatter linking to its sources (`doc_key`, issue number, or external citation)." GR-4 requires `last_updated` and `sources` field updates on any wiki edit. Neither GR-1 nor GR-4 mandates `title` or `tags` as conformance-required.

**Conflicting source authority — #2207 Section 6.3 (frontmatter example):** Shows `title, doc_key, source_ref, domain, promoted_from, last_updated`. No `tags` field. No `sources` field (uses `source_ref` instead).

**Why this is a defect:** #2206 invents a third frontmatter contract that aligns with neither sibling. An implementer building DT-1 from this design will mass-flag wiki pages following #2207's frontmatter example as non-conformant, and will allow wiki pages without source traceability through if they happen to have `title`, `tags`, `sources`, `last_updated` — even when `sources` is empty or stale. The check is simultaneously over-strict (rejects #2207-shaped frontmatter) and under-strict (passes pages with nominal but empty `sources`).

**Required fix:** DT-1 must be redefined to exactly match the union of GR-1 and GR-4: pass = `last_updated` present AND `sources` (or equivalent #2207 field `source_ref`) present and non-empty. Drop the `title`/`tags` requirement unless a sibling contract is amended to include them.

---

## Finding 2 — MAJOR: ID-1 and ID-3 checks would falsely fail on 100% of currently-shipped storage

**Claim under review (Section 5.2 ID-1, "Pass signal"):** "Every record has a `content_hash` or `doc_key` field with a 64-character hex value."
**Claim under review (Section 5.2 ID-3, "Pass signal"):** "All identity comparisons use bare 64-char hex (no `sha256:` prefix in lookup keys)."

**Conflicting live-repo evidence (verified during the #2207 Codex review, 2026-04-17):**
- `scripts/data/document-index/phase-a-index.py:135-137` writes `md5:`-prefixed 32-char identities for legacy `og_standards` records. ID-1 would fail every such record (32 ≠ 64) even though the record is conformant to current writer behavior.
- `data/document-index/summaries/` contains files named `sha256:<hex>.json` (verified: `ls` showed three such files in sequence). ID-3 would flag the entire summaries directory as non-conformant (prefixed lookup keys are the actual storage convention).

**Why this is a defect:** #2206 cannot, without coordination with #2207, define an ID check whose pass signal is "no `sha256:` prefix" while #2207's storage layer uses prefixed keys. If #2206 ships with these checks unchanged, the first run would emit thousands of false-positive failures and developers would mute the checks — exactly the CF-2 ("check proliferation → alert fatigue") anti-pattern the design itself warns against.

**Required fix:** Defer ID-1/ID-3 to Phase 4 alongside FLOW-1 etc. ("requires future tooling"), with the explicit dependency that #2207 must first reconcile the MD5/SHA-256 namespace and bare-hex-vs-prefixed convention. Until that reconciliation, the checks are unimplementable in a way that produces useful signal.

---

## Finding 3 — MAJOR: Retention checks (DT-2/DT-3/DT-4/DT-5) contradict #2209's own "advisory only" admission

**Claim under review (Section 5.4 DT-2 through DT-5, "Pass signal"):** Each defines a hard date threshold (handoff > 30 days, planning > issue-closure + 14 days, signals > 7 days, reviews > 90 days) and a pass/fail signal.

**Conflicting source authority — #2209 Section 11 item 1:** "This policy defines retention periods but does not implement the cleanup automation. Until a transient-artifact cleanup script exists, **retention is advisory only**. Risk: transient artifacts accumulate indefinitely."

**Why this is a defect:** #2206 designs four hard-fail conformance checks against retention rules that the source contract explicitly admits are advisory pending follow-on tooling. Section 11 item 4 of #2206 attempts to address this by saying "retention check failures should auto-create cleanup issues" — but that only escalates the problem (every weekly review would auto-create dozens of cleanup issues from the existing accumulated transient artifacts).

**Required fix:** Mark DT-2 through DT-5 as **conditional checks** that activate only when (a) the cleanup workflow (#2237) ships and (b) #2209 promotes retention from advisory to enforceable. Until then, they should be in Section 8 ("intentionally manual") rather than Section 5 ("automatable now").

---

## Finding 4 — MAJOR: Section 7.3 commits the exact violation GUARD-1 is supposed to detect

**Claim under review (Section 7.3, directory-to-layer mapping):** "`docs/document-intelligence/` → L3-adjacent normative docs only."

**Conflicting source authority — #2205 Section 2:** Defines layers L1–L6 only. There is no "L3-adjacent" layer.

**Conflicting source authority — #2206's own GUARD-1 check (Section 5.6):** "Detect child artifacts that define their own layer model. Pass signal: Child docs reference parent layer definitions without redefining them. Fail signal: Child doc contains a layer table that contradicts #2205 Section 2."

**Why this is a defect:** #2206 is a child artifact under #2205. Section 7.3 introduces the term "L3-adjacent" — a new layer classification not present in the parent. By GUARD-1's own definition, #2206 itself fails GUARD-1. This is the same defect pattern as #2209's "between L5 and L6 — recurring-operational" finding. Both child contracts invent classifications outside the parent's six-layer model and then hope nobody notices.

This is meta-inconsistency: a conformance-check design cannot validly check rule X if its own text violates rule X. An implementer applying GUARD-1 strictly would reject #2206 as non-conformant.

**Required fix:** Either (a) reclassify `docs/document-intelligence/` under an existing layer (most likely L3 since it contains durable normative knowledge documents), OR (b) propose a #2205 amendment to add a formal classification for normative architecture documents. (a) is the parent-respecting path; (b) is bigger surgery.

---

## Finding 5 — MINOR: Section 5 conformance-check definitions hardcode targets that exist as moving paths

**Claim under review (Sections 5.1–5.6 throughout):** Multiple checks reference specific paths as inputs: `data/document-index/index.jsonl`, `knowledge/wikis/*/wiki/**/*.md`, `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`, etc.

**Conflicting source authority — #2206's own Section 11 item 5:** "Several checks reference specific file paths ... If these files are renamed, checks will fail spuriously. Mitigation: checks should emit a distinct 'target missing' error."

**Why this is a defect:** Section 11 item 5 acknowledges the brittleness but doesn't apply the mitigation in Section 5's check definitions themselves. None of the per-check tables in 5.1–5.6 specify how the "target missing" error class is distinguished from a conformance failure in the script's exit code or output. An implementer following Section 5 alone would build checks that conflate "target moved" with "check failed."

**Required fix:** Add a per-check "target precondition" row to the matrices in 5.1–5.6 that specifies what the check does when its input file is missing (recommend: emit a "target-missing" warning to stderr and exit 2, distinct from pass=0 / fail=1).

---

## Finding 6 — MINOR: Phase 3.3 depends on #1839 which is OPEN and may not converge

**Claim under review (Section 10, Phase 3.3):** "Add label/doc consistency check to plan-gated workflow [depends on] Phase 2.5, plan-gate workflow (#1839)."

**Conflicting live-repo evidence:** Issue #1839 ("Workflow hard-stops and session governance — Hermes-orchestrated lifecycle with enforced gates") is OPEN as of 2026-04-17.

**Why this is a defect (minor):** Phase 3 of #2206 has a hard dependency on an open, unsequenced parent issue. The conformance design treats #1839 as if it were a fixed ordering constraint, but #1839 has no committed delivery date. Risk: Phase 3 becomes perpetually deferred.

**Required fix:** Either (a) decouple Phase 3.3 from #1839 by defining a minimum interface the conformance check needs (so it can be built against any plan-gate implementation, not just #1839's), or (b) explicitly mark Phase 3.3 as gated and accept it may not happen in the milestone window.

---

## Finding 7 — MINOR: CF-3 anti-pattern conflicts with the harness's existing enforcement model

**Claim under review (Section 9.1, CF-3):** "Start all checks as reporting-only. Promote to blocking (pre-commit or CI gate) only after at least 30 days of reporting with < 5% false positive rate."

**Conflicting source authority — `issue-planning-mode/SKILL.md:300-303`:** The harness already has enforcement-first patterns:
- `PreToolUse hook`: `.claude/hooks/plan-approval-gate.sh` blocks writes without approval marker
- `Pre-commit hook`: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits

**Why this is a defect (design philosophy):** The harness enforces immediately, accepting some false-positive cost in exchange for strong guarantees. #2206's CF-3 prescribes 30 days of reporting before blocking — which is opposite to the existing pattern. An implementer following CF-3 would hold conformance checks in reporting mode for a month even when the rule being checked is binary and unambiguous (e.g., "child must not redefine `doc_key`"). The design and the existing harness will collide on enforcement timing.

**Required fix:** Distinguish two check classes: (a) binary, unambiguous, low-false-positive checks (e.g., GUARD-2 prefix-check, ACC-3 backlink) that can ship enforcement-first like the harness pattern, and (b) heuristic checks (e.g., OWN-1 keyword scan) that genuinely need the 30-day reporting period. CF-3's blanket rule is too coarse.

---

## Finding 8 — MAJOR (process): Cross-provider adversarial review is absent

**Same as #2207 Finding 7 and #2209 Finding 7.** Three Claude reviews, zero Codex/Gemini. Planning skill Step 3 mandates 2+ providers. The 2026-04-16 overnight review's "no issues found" pattern is suspect by skill rule. Codex review on this issue is now in flight in parallel with this review.

---

## Verified claims

- `docs/README.md` exists and contains 4 references to intelligence ecosystem paths — ACC-1 would pass today.
- `docs/document-intelligence/README.md` exists — ACC-2 would pass today.
- `data/document-index/index.jsonl` exists and contains records — ID-1 has its input.
- `phase-a-index.py:135-137` writes `md5:` prefixes — verified during the #2207 Codex review on this same date.
- `data/document-index/summaries/sha256:<hex>.json` filename pattern — verified during the #2207 Codex review.
- Issue #1839 is OPEN — Phase 3.3 dependency is unblocked by no other party.
- The check-to-source traceability in Appendix A correctly maps each check to a source rule (no fabricated rule citations were found).

## Cross-issue dependency observation

Findings 2, 4, and 7 are not independent — they are downstream consequences of unresolved defects in #2207 (identity namespace) and #2209 (layer classification). Fixing #2207 and #2209 first is a prerequisite for #2206's checks to be correctly specified. The dependency order in #2205 Section 9 (#2207 → #2209 → #2206) reflects this; the existing draft of #2206 ignores it and defines checks against an unsettled foundation.

## Recommendation

Stay at `status:plan-review`. Findings 1–4 and 8 are MAJOR. Recommend a single coordinated revision pass across #2207, #2209, and #2206 — fix #2207 first (identity), then #2209 (layer classification), then update #2206's checks to match the reconciled foundation. Do not implement any check from Section 5 until #2207 and #2209 revisions land, otherwise the implementation would have to be redone.
