# In-run Adversarial Review — #2206 Revision (2026-04-19)

> **Reviewer:** Claude (adversarial stance per planning-skill reviewer-stance contract)
> **Date:** 2026-04-19
> **Deliverable under review:** `docs/document-intelligence/pyramid-conformance-checks.md` (revision pass 2026-04-19)
> **Revision dispatch prompt:** `docs/plans/2026-04-19-revision-dispatch-prompt-2206-pyramid-conformance-checks.md`
> **Parent amendment driving revision:** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` Sections 2, 3, 8.1 (amended 2026-04-19)
> **Prior review pass:** `scripts/review/results/2026-04-17-plan-2206-claude-adversarial.md`, `scripts/review/results/2026-04-17-plan-2206-codex-adversarial.md`

## Stance declaration

Assume defects until proven otherwise. The revision is in the same document family where the 2026-04-17 cross-provider pass found 14 findings (10 MAJOR + 4 MINOR). The revision must not introduce new defects while fixing old ones. Particular attention to: (a) did Amendment A actually remove the L3-adjacent classification everywhere, or only in some places? (b) does strengthened GUARD-1 now match this document itself? (c) are FRONT-1, identity-namespace, status, and `merged_at` checks concrete enough for an implementer? (d) did any finding disposition quietly drop a claim without addressing it?

## Verdict: **APPROVE with MINOR residuals**

All four amendment-mandated verifications from the dispatch prompt STEP 3 pass. Ten of the fourteen 2026-04-17 findings are fully addressed by edits in Section 5 or 7. Four are addressed by explicit classification changes (retention → advisory; ID-5 → cross-repo; CF-3 → two-class; target-precondition → new column). The document no longer classifies any artifact as "L3-adjacent." GUARD-1 has a scoping note that prevents self-match. No new MAJOR defects found.

Residual items are MINOR and do not block approval; they are documented below for follow-up visibility.

---

## Amendment verifications (from dispatch prompt STEP 3)

### A1 — `docs/document-intelligence/` is now classified as L3 (not L3-adjacent)

**Verified.** Section 7.3 directory-to-layer mapping row now reads: "`docs/document-intelligence/` → **L3** (durable architectural knowledge per Section 2 worked examples — no longer 'L3-adjacent')". Section 4.1 concrete-examples note describes the prior defect in past tense. The document contains 10 occurrences of "adjacent" total; all are either (a) quoted citations of the forbidden pattern for GUARD-1 detection, (b) references to the prior defect in revision-history context, or (c) the regex pattern itself (`\bL[0-9]+-adjacent\b`). Zero are used as a classification of any artifact.

### A2 — GUARD-1 is strong enough to catch the prior violations

**Verified.** GUARD-1 pass signal now reads: "**Zero** occurrences of the regex patterns `\bL[0-9]+-adjacent\b`, `\bbetween L[0-9]+ and L[0-9]+\b`, `\bhybrid layer\b` in any child doc." The three regexes directly match the parent Section 2 forbidden-invention list verbatim. A correctly-scoped run against the 2026-04-17 pre-revision text of this document would have matched both "L3-adjacent" and "between L5 and L6" (the latter from #2209's pre-revision text). Adversarially probed: a minor concern that GUARD-1 might self-match on this document. Mitigation: the new scoping note under Section 5.6 explicitly requires the implementation to exclude backtick-delimited inline code, fenced code blocks, the Section 5.6 / Section 12 pattern-definition rows, and URLs. This converts a latent meta-issue into a documented implementation constraint. Acceptable.

### A3 — FRONT-1, namespace, status, and `merged_at` checks are concrete and testable

**Verified each:**

- **FRONT-1** Section 5.4 row specifies: inputs = `knowledge/wikis/*/CLAUDE.md`; pass = each file's Frontmatter-Schema section lists `title`, `last_updated`, `doc_key` with "required" marking; fail = missing or downgraded; target precondition = glob empty → `target-missing`. An implementer can write a YAML-table parser that checks the Required column values. **Concrete.**
- **Identity namespace (ID-3)** Section 5.2 row specifies: regex `^(sha256|md5):[0-9a-f]+$`; `md5:` permitted only on `og_standards` records; bare-hex emits warning; unknown prefix fails. Directly testable against `data/document-index/index.jsonl`. Grounded in `phase-a-index.py:135-137` (verified 2026-04-19). **Concrete.**
- **Status vocabulary (FLOW-6)** Section 5.3 row specifies: enum `{gap, indexed, summarized, extracted, promoted, superseded, unreachable}`; violation = any value outside. Directly testable against `index.jsonl`; matches parent Section 3 superset exactly. Live-data sample showed `status: "gap"` — in-enum. **Concrete.**
- **`merged_at` migration (ID-7)** Section 5.2 row specifies: post-2026-04-19 writes use `merged_at`; pre-amendment writes may use `discovered` (informational only). Grounded in `scripts/data/document-index/provenance.py:82` (verified — field is currently `discovered`). The check correctly handles backward compatibility. **Concrete.**

---

## Finding-disposition audit (2026-04-17 cross-provider — 14 items)

Each 2026-04-17 finding is cross-checked against the revised document.

| # | Finding | Disposition in revision | Verified? |
|---|---|---|---|
| Claude-1 | DT-1 frontmatter contradicts siblings | Amendment D: DT-1 reframed to defer required-set to wiki `CLAUDE.md` (Section 5.4 row, Section 3 commentary). Hardcoded `{title, tags, sources, last_updated}` is gone. | Yes |
| Claude-2 | ID-1/ID-3 false-fail on 100% of shipped storage | Amendment E: ID-3 renamed to Identity-namespace-conformance; accepts `sha256:`/`md5:` prefixes; bare-hex emits warning rather than hard-fail. Grounded in `phase-a-index.py:135-137`. | Yes |
| Claude-3 | DT-2/3/4/5 retention contradicts #2209's advisory admission | Retention checks explicitly marked **advisory-only** in Section 5.4, Phase 1.8, and Residual Risks item 2. Promotion gated on #2209 updating its own policy. | Yes |
| Claude-4 | Section 7.3 commits GUARD-1 violation it detects | Amendment A + B. Section 7.3 now classifies `docs/document-intelligence/` as L3. GUARD-1 has regex + scoping note. Self-contradiction resolved. | Yes |
| Claude-5 | Section 5 hardcoded targets with no missing-input handling | Every automatable check in 5.1–5.6 now has a **Target precondition** column. `target-missing` is distinct exit code (exit 2) per Section 7.6 and CF-5. | Yes |
| Claude-6 | Phase 3.3 depends on OPEN #1839 | Phase 3.2 (previously 3.3) now decoupled — "minimum plan-gate interface" instead of hard #1839 dependency. | Yes |
| Claude-7 | CF-3 collides with enforcement-first harness | CF-3 split into binary-vs-heuristic two-class policy. Phase 1 table annotates each work-item's mode (enforcement-first vs reporting-only). | Yes |
| Claude-8 | Process: cross-provider review absent | Resolved at source — Codex review present at `scripts/review/results/2026-04-17-plan-2206-codex-adversarial.md`. Now a historical process item. | Yes |
| Codex-1 | DT-1 false positives across live wiki frontmatter shapes | Amendment D resolves. Per-wiki authority accommodates `{domain, created, last_updated, page_count}` index frontmatter, `source` (singular) variants, and any other per-wiki declared shape. | Yes |
| Codex-2 | DT-3 assumes `.planning/` is issue-addressable | DT-3 row explicitly scopes to `.planning/plan-approved/<issue-number>.md` and `.planning/issue-<number>/**`. Non-issue artifacts (`.continue-here.md`, `STATE.md`, `session.md`) explicitly excluded. | Yes |
| Codex-3 | Runner contract incompatible with both hook surfaces | Section 7.6 defines two modes: hook-mode (stdout JSON + exit 0) and cli/pre-commit-mode (text/JSON + exit 0/1/2). Grounded in the two existing scripts by filename + line numbers. | Yes |
| Codex-4 | ID-5 cross-repo treated as local | ID-5 reclassified as **manual (cross-repo)** in Section 5.2. Section 7.7 defines an invocation contract (sibling location, branch state, failure ownership, never-block rule). | Yes |
| Codex-5 | ACC-6 references untracked targets | ACC-6 revised to require git-tracked membership (`git ls-files`). ACC-7 added for the related header-vs-content count-drift class (15-vs-25 cross-links). | Yes |
| Codex-6 | DT-2/DT-5 mtime-based retention unstable | Retention checks specify embedded frontmatter/filename dates, not `mtime`. CF-7 anti-pattern codifies the rule. | Yes |

All 14 findings have explicit disposition. No finding was silently dropped.

---

## Adversarial probes (defects hunted for, findings reported)

### Probe 1 — Does the revised document still classify any artifact as "L3-adjacent" anywhere?

Grep result: 10 occurrences of "adjacent" in the document; each reviewed individually. Zero occurrences are classifications of an artifact. All are either regex-pattern citations, forbidden-pattern enumerations in GUARD-1 context, or revision-history descriptions of the prior defect. **No defect.**

### Probe 2 — Does GUARD-1 self-match?

A naive regex would match "L3-adjacent" in GUARD-1's own row. The revision adds an explicit scoping note under Section 5.6 requiring the implementation to exclude (a) backticks, (b) fenced code blocks, (c) the Section 5.6 / Section 12 pattern-definition rows, (d) URLs. This converts the meta-issue into an implementation constraint, and the constraint is explicit enough that a follow-on implementation issue can enforce it. **Addressed; MINOR residual below.**

### Probe 3 — Does the retention-advisory classification match the runtime data?

Retention checks are now advisory-only. But the revision-history row for Amendment-driver "Claude-3" says "promotion gated on #2209 promoting its own policy." This creates a two-way dependency: DT-2/3/4/5 can't become enforceable until #2209 updates, and #2209 wouldn't update without conformance pressure. Realistic risk: retention remains advisory-forever. Residual item 2 in Section 11 explicitly names the 6-month retirement clause as mitigation — but the clause only retires the advisories, it doesn't force promotion. **Acceptable as designed; MINOR residual below.**

### Probe 4 — Does FRONT-1 run cleanly on the current 5 wiki `CLAUDE.md` files?

Checked all 5. **None** currently declare `doc_key` as required. `engineering/CLAUDE.md` declares `{title, tags, added, last_updated}` required (no `doc_key`). `marine-engineering/CLAUDE.md`, `maritime-law/CLAUDE.md`, `naval-architecture/CLAUDE.md`, `personal/CLAUDE.md` all similar. **FRONT-1 will fail on all 5 wikis on day 1.** This is the intended behavior — the check is designed to surface the gap the amendment created. Residual item 1 of Section 11 explicitly acknowledges this. The dispatch prompt's forbidden paths prevent this revision from updating wiki `CLAUDE.md` files. **Expected failure mode; documented; acceptable.**

### Probe 5 — Does ID-3 handle the concrete sample records?

Sample `content_hash: "sha256:0d75d96f237eb621b360267e00a0f0de"` has 32 hex chars prefixed with `sha256:`. That is technically an MD5-length digest prefixed as SHA-256 — a subtle defect in the writer. The ID-3 regex `^(sha256|md5):[0-9a-f]+$` matches both 32-char and 64-char hex, so the check would not flag the record itself. But the check does not validate the hex length matches the prefix's expected digest length. **MINOR residual below** — noted for follow-up, not blocking.

### Probe 6 — Does any finding disposition quietly drop an adversarial claim?

Cross-checked each 2026-04-17 finding against Section 12 disposition table and the actual body of the revised document. Two concerns:

- **Claude Finding 7 (CF-3 two-class)**: The binary/heuristic split is documented in CF-3 and tagged in the Phase 1 work-item table, but "binary" is not rigorously defined. An implementer could argue OWN-3 (glob for session-handoff filenames) is binary, while another could argue it's heuristic (what about a legitimate file named `session-handoff-wiki-schema.md`?). **MINOR residual** — could use a tighter "binary" definition.
- **Codex Finding 5 (navigation-count drift)**: The revision adds ACC-7. However, ACC-7's pass/fail signal ("counts agree") doesn't specify what to do when a navigation doc has prose counts but the target file has no structured counter. **MINOR residual** — spec gap.

### Probe 7 — Are all quality-bar items from dispatch prompt met?

Quality bar items (from prompt):
1. Zero occurrences of "L3-adjacent" classification anywhere — **MET** (10 occurrences all in quoted/regex/historical context; zero classifications).
2. GUARD-1 explicitly enumerates forbidden-invention patterns — **MET** (three regexes listed in the pass-signal column).
3. FRONT-1 concrete enough to implement without re-deriving schema-authority rule — **MET** (pass signal, fail signal, inputs, target-precondition all specified).
4. Status, namespace, `merged_at` checks reference live writers — **MET** (ID-3 cites `phase-a-index.py:135-137`; ID-7 grounded in `provenance.py:82`; FLOW-6 grounded in live `index.jsonl` sample).
5. Every 2026-04-17 finding has explicit disposition — **MET** (Section 12 table).
6. No drift into implementing scripts — **MET** (checks specify inputs/pass/fail; no executable code, no registry schemas, no CI pipeline definitions).

---

## Residual items (MINOR, do not block approval)

### R1 — GUARD-1 scoping note is prose, not machine-testable

The scoping requirement for GUARD-1 ("skip backticks, fenced blocks, pattern-definition rows, URLs") is written as prose under Section 5.6. A future implementer must interpret this correctly. This is acceptable because (a) the scoping is a well-known text-processing pattern and (b) the design-vs-implementation boundary of this document prohibits specifying the exact parser. Mitigation: the follow-on implementation issue should cite the scoping note verbatim and include a test case that this document's own Section 5.6 row passes cleanly.

### R2 — Retention advisory may accumulate indefinitely

Section 11 item 2 describes a 6-month retirement clause as mitigation. The clause retires advisories but does not force retention promotion. In practice, if #2209 doesn't promote within 6 months, DT-2/3/4/5 signals disappear entirely — which may hide real accumulation. Acceptable trade-off: better to retire a noisy never-actioned signal than to leave it polluting weekly review.

### R3 — ID-3 doesn't cross-validate hex length against prefix

Sample data shows `sha256:<32-char hex>` — a subtle writer defect where an MD5-length digest carries the `sha256:` prefix. ID-3 regex accepts it. A stricter check would require `sha256:[0-9a-f]{64}$` and `md5:[0-9a-f]{32}$`. Proposed: add as a follow-on tightening after ID-3 ships and runs clean with the lenient regex. Not blocking because the primary defect class (unknown prefix, bare-hex, cross-source `md5:`) is caught.

### R4 — "Binary" vs "heuristic" classification in CF-3 is under-specified

An implementer could disagree on whether a given check is binary or heuristic. Acceptable because Phase 1 explicitly annotates each work-item's mode — the annotations are the operative classification, not a general rule. Follow-on: if more checks are added in a later revision, each must be annotated at introduction.

### R5 — ACC-7 under-specifies the "counter field" shape

ACC-7 checks navigation-count prose against target-file counter fields (e.g., `total_cross_references: 15`). The revision does not specify what to do when the target file lacks any structured counter field. Acceptable because ACC-7 is triggered by navigation docs containing count claims — if a navigation doc cites a count that has no corresponding counter, the check can either emit a warning ("counter not found, cannot verify") or fail. Implementer choice at implementation time, acceptable at design time.

---

## Summary

**Verdict: APPROVE with MINOR residuals.**

All dispatch-prompt STEP 3 verifications pass. All 14 cross-provider findings have explicit disposition and are addressed in the revised document. Zero new MAJOR defects introduced. Five MINOR residuals documented for follow-up visibility; none block approval.

The revision correctly treats itself as a revision pass (not a rewrite): preserved content includes all six conformance target classes, the tiered implementation phases, Appendix A traceability, and the anti-pattern taxonomy. Changes are surgical where possible and systemic where the amendments require (target-precondition column, runner-contract mode split, retention advisory reclassification).

Recommend proceeding to the Integrator pass (STEP 4).
