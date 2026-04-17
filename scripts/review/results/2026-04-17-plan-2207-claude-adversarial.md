# Adversarial Review: #2207 Standards/Codes Provenance + Reuse Contract

> **Reviewer:** Claude (adversarial stance, per planning-skill reviewer-stance contract)
> **Date:** 2026-04-17
> **Deliverable under review:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (created 2026-04-11, 27,391 bytes)
> **Plan under review:** `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md`
> **Prior reviews consulted:** `2026-04-11-issue-2207-claude-review.md`, `2026-04-11-issue-2207-final-review.md`, `2026-04-16-plan-2207-claude-overnight.md` — all Claude, all APPROVE, all charitable.

## Stance declaration

This review assumes the deliverable has defects until proven otherwise. Prior reviews produced either pure PASS verdicts or empty-findings sections; per the planning skill's reviewer-stance contract ("empty reviews are failures"), they are suspect. This review re-examines the contract against live repository evidence, not only against internal consistency.

## Verdict: **MAJOR** — not approval-ready

Two correctness-critical defects contradict live data or the contract's own text. Cross-provider review (Codex, Gemini) is also absent, violating planning-skill Step 3.

---

## Finding 1 — MAJOR: Status enum omits the status value that dominates real data

**Claim under review:** Section 4.1 defines `status` as enum `indexed | summarized | extracted | promoted`. Section 5.1's entire reuse-vs-reparse decision tree branches on this enum.

**Evidence against:** Sampling the first 2,000 records of `data/document-index/index.jsonl` yields `status: gap` for **2000/2000** records. The value `gap` is nowhere in the contract's enum or decision tree.

```
$ head -2000 data/document-index/index.jsonl | jq -r '.status' | sort -u
gap
```

**Why this is a defect:** The contract is normative ("Status: Normative — approved provenance and reuse contract"). A decision tree that doesn't cover the status value held by 100% of currently-indexed documents is not operational. Any implementation following Section 5.1 literally would hit the decision tree's fall-through case (treat as indexed-only) for every real document, forcing reparse of documents that may already have richer upstream artifacts — the exact anti-pattern 8.1 forbids.

**Required fix:** Either (a) audit all live `status` values in the intelligence ecosystem and expand the enum to cover them, or (b) define `gap` as a semantic synonym of `indexed` and add it to the enum. Option (a) is safer; this should not be a one-line patch without looking at all phase-A/B/C/E writer code.

**Files to audit for the full status vocabulary:**
- `scripts/data/document-index/phase-a-index.py`
- `scripts/data/document-index/phase-b-claude-worker.py`
- `scripts/data/document-index/phase-c-classify.py`
- `scripts/data/document-index/reclassify-audit.py`
- `scripts/data/document-index/subcategory-classify.py`

---

## Finding 2 — MAJOR: Section 8.3 contradicts Section 3.1 on what the promoter `# content-hash:` comment actually traces

**Claim under review (Section 8.3, "correct approach"):** "The current promoter pattern (`# content-hash: <hash>` or `# content_hash: <hash>`) satisfies [the requirement for promoted artifacts to link back to the source document]."

**Direct contradiction (Section 3.1 last row):** "`content_hash()` function ... NOT a `doc_key`. This hashes the promoted *output content*, not the source document. It is a content-integrity stamp for promoted artifacts, not a document identity."

**Evidence against:** Every promoter emits a hash of the output body, not the source:

| Promoter | Code | Input to hash |
|---|---|---|
| `constants.py:105-107` | `h = content_hash(body); return f"# content-hash: {h}\n{body}"` | output body |
| `curves.py:53-54` | `h = content_hash(body); return f'# content-hash: {h}\n{body}'` | output body |
| `definitions.py:50-53` | `chash = content_hash(body); lines.append(f"# content_hash: {chash}")` | output body |
| `equations.py:185` | `f"# content-hash: {content_hash(body)}\n"` | output body |
| `procedures.py:74-86` | `body_hash = content_hash(steps_block); f"content_hash: {body_hash}"` | steps block (output) |
| `requirements.py:65` | `f"# content-hash: {content_hash(body)}\n"` | output body |

**Why this is a defect:** The contract asserts that existing `# content-hash:` comments already provide traceability to source. They do not — they provide output-integrity stamps. An implementer reading Section 8.3 and believing traceability is already satisfied will close the gap without actually threading the source `doc_key` through the promoter pipeline. Anti-pattern 8.3 ("broken lineage") would remain present despite the contract claiming it is mitigated.

**Required fix:** Section 8.3's "correct approach" must be rewritten to acknowledge that a separate `# doc_key:` (or equivalent `source_doc_key`) field is required in promoter output, alongside the existing `# content-hash:` output-integrity stamp. The two serve different purposes and one cannot substitute for the other.

---

## Finding 3 — MINOR: OCR-vs-PDF-rewrite rule is internally inconsistent

**Claim under review (Section 5.3):** "OCR does NOT change the `doc_key`. The source file is unchanged; OCR produces a derived text artifact."

**Conflicting claim (Section 3.4 table):** "PDF re-saved with different metadata but identical visible content — **Yes** [new `doc_key`] — The `doc_key` is computed from file bytes. A re-save that changes metadata changes the hash."

**Why this is a defect:** A common OCR workflow (e.g., `ocrmypdf --output-type pdf`) re-saves the PDF with an added text layer — producing a new PDF with new bytes but identical visible content. Under Section 5.3 this "OCR" event produces no new `doc_key`. Under Section 3.4 the re-save produces a new `doc_key`. Both rules apply simultaneously.

**Required fix:** Section 5.3 should disambiguate: "OCR that emits a sidecar text artifact leaves the source `doc_key` unchanged. OCR that re-saves the PDF produces a new `doc_key` linked to the original via `superseded_by` lineage."

---

## Finding 4 — MINOR: Section 4.3 assigns a provenance field to a layer that #2205 says does not own provenance

**Claim under review (Section 4.3 table, L3 row):** "L3 Durable knowledge owns `wiki_refs` (back-links from wiki pages to their source `doc_key`)."

**Conflicting parent rule (#2205 Section 2, L3 row, "Must NOT own"):** "Live execution state, source-of-truth provenance records."

**Why this is a defect (ambiguity, not outright violation):** `wiki_refs` is a back-link field, not a provenance record — but the contract never defines the distinction. A reader implementing the registry could reasonably conclude that because L3 "owns" `wiki_refs`, other provenance fields can also live at L3. The rule-boundary between "back-link" and "provenance record" is load-bearing but undefined.

**Required fix:** Either remove `wiki_refs` from the L3-owned row and note that wiki pages emit references that are *materialized* at L2, or add an explicit definition: "back-link fields (pointers from higher layers to lower) are not provenance and may be owned by the originating layer."

---

## Finding 5 — MINOR: "Primary path" is undefined across machines

**Claim under review (Section 4.1):** "`path` — Primary file path (the highest-priority alias)."

**Why this is a defect:** "Highest-priority" is not defined. When the same `doc_key` appears at `/mnt/ace/.../X.pdf` on machine A and `/mnt/dev-secondary/.../X.pdf` on machine B, which is primary? The contract delegates cross-machine path normalization to #2136 (parent Section 12 Q4), but Section 4.1 still requires a primary path without saying what rule selects it. A registry populated from machine A will disagree with a registry populated from machine B.

**Required fix:** Either (a) explicitly mark `path` as machine-local and rename to `primary_path_for_host`, or (b) defer the entire concept of primary path to #2136 and require only `doc_paths[]` + `provenance[]` at this layer.

---

## Finding 6 — MINOR: Back-population has no scoped work

**Claim under review (Section 10 item 3):** "Populating `doc_key` requires hashing source files, which requires mount access. This should be a Phase E back-population task."

**Why this is a defect:** "Phase E back-population" is named but no issue exists, no owner is assigned, no estimate is given, and there is no rule for entries whose sources are on permanently unreachable mounts. Section 4.1 lists `doc_key` as a *required* field. An existing ledger row without `doc_key` is, per the contract's own rule, non-conformant — but the contract provides no transition plan to reconcile that.

**Required fix:** Either file a concrete follow-on issue for the back-population task (with an ownership assignment) or explicitly mark pre-existing ledger entries without `doc_key` as "legacy — grandfathered until Phase E" so #2206 conformance checks don't flag them.

---

## Finding 7 — MAJOR (process): Cross-provider adversarial review is absent

**Claim under review (plan file line 106-109):** The plan lists Claude reviews only. No Codex, no Gemini, no documented provider-unavailability record.

**Conflicting rule (planning skill Step 3):** "Route the plan to 2+ AI providers for review. Each gives: APPROVE | MINOR | MAJOR. If any MAJOR: revise and re-review."

**Why this is a defect:** #2205 workstream is architectural governance — arguably the most review-sensitive work in the ecosystem. Three Claude-only passes with APPROVE verdicts does not satisfy cross-provider review. Per the reviewer-stance contract, "empty reviews are failures" — the 2026-04-16 overnight review's "no issues found" section is itself suspect and should be re-run.

**Required fix:** Route the deliverable to Codex (via the available `codex:rescue` skill) and Gemini. Do not advance this issue to `status:plan-approved` until at least one non-Claude provider has independently reviewed and either accepted the findings above or raised new ones.

---

## Summary of verified claims

- `data/document-index/index.jsonl` has `status: gap` for 2000/2000 sampled records. (Finding 1)
- Every promoter under `scripts/data/doc_intelligence/promoters/*.py` hashes the output body, not the source. (Finding 2)
- Parent operating model `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` Section 2 lists L3 as forbidden from owning provenance. (Finding 4)
- `config.yaml:182` sets `primary_key: content_hash` — consistent with Section 3.1 mapping, not contradicted.
- Deliverable exists at the stated path at 27,391 bytes, matching prior reviews. (No new defect.)

## Recommendation

Return to **status:plan-review** (already there; do not advance). Apply fixes to Findings 1, 2 in the deliverable. Apply fixes to Findings 3–6 or explicitly defer each with written rationale. Route revised deliverable to Codex and Gemini before user approval.
