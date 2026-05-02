# Adversarial review — Plan #2588 (engineering wiki gap audit, W1-C)

- **Plan:** `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md`
- **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2588
- **Reviewer:** Claude (single-author internal — Codex/Gemini provider gates inaccessible from this planning-only session per memory `feedback_permission_gate_blocks_cross_review.md`)
- **Date:** 2026-05-02
- **Stance:** adversarial (defects-until-proven-otherwise)
- **Working tree:** `/mnt/local-analysis/workspace-hub` @ branch `main`
- **Provenance note:** Verified file/issue claims via local `find`/`grep`/`gh issue view` against the live tree on 2026-05-02. Counts and grep evidence below are reproducible from the plan's stated commands.

---

## Affirmatively-verified claims

| Plan claim | Verification | Result |
|---|---|---|
| `raw/` total = 521 files (520 in `papers/` + 1 root) | `find knowledge/wikis/engineering/raw -type f \| wc -l` | **521** — matches |
| `wiki/` total .md = 105 (or 106 with `.gitkeep`) | `find ... -name "*.md" \| wc -l` (105) and `find -type f` (106) | **matches** — internally consistent |
| `concepts=42, entities=23, sources=23, standards=9, workflows=5` | per-subdir `find -type f` | **matches** all five |
| `wiki/` root = 4 files (3 .md + .gitkeep) | `find -maxdepth 1 -type f` | **matches** (index.md, log.md, overview.md, .gitkeep) |
| Raw structure flat (no nested subdirs) | `find raw -maxdepth 4 -type d` returns only `raw` and `raw/papers` | **matches** |
| Standards inventory list (api-579, dnv-os-e301, dnv-rp-c203/c205/f101/f105, ocimf-meg4, ocimf-tandem-mooring, TEMPLATE) | `ls wiki/standards/` | **matches exactly** (9 files) |
| Issue states (#2540 OPEN, #2368 OPEN, #2373 OPEN, #2392 OPEN, #2378 OPEN) | `gh issue view <n>` | **all 5 match** |
| Filename-prefix bucketing — feedback_:56, ALLCAPS:88, plan-/review-/etc.:25, 2026-:9, *.json:9, *.yaml/yml:16 | `ls papers/ \| grep -c …` | **all 6 match** |
| agent prefix bucket = 34 | `ls \| grep -ciE` (case-insensitive) yields **34** | matches under case-insensitive interpretation (plan does not state `-i`; minor) |
| Total accounted-for-as-out-of-scope = ~237/520 (~46%) | sum of buckets above = 237; 237/520 = 45.6% | **matches** |
| `docs/audits/` does not exist | `ls docs/audits` | **confirmed missing** — plan correctly establishes |
| `_template-issue-plan.md`, `docs/plans/README.md`, sibling plans #2378/#2363/#2392 exist | `ls` | **all confirmed** |
| `dnv-os-e301.md` with #2471 frontmatter exists | head of file shows `code_id`, `publisher`, `revision` | **confirmed** |
| Citation-contract rule file present | `.claude/rules/calc-citation-contract.md` | **confirmed** |

---

## MAJOR findings

### MAJOR-1 — "no current Python module cites engineering wiki paths" is FALSE

Plan §Resource Intelligence Summary, line 17, states: *"Gap: no internal `digitalmodel/` Python module will be found citing `knowledge/wikis/engineering/...` paths — engineering wiki is not yet wired into calc citations."* And §Evidence (lines 85–89) prints an "(empty)" grep result with the comment *"no current Python module cites engineering wiki paths"*.

Live verification:
```
$ grep -rl "knowledge/wikis/engineering" /mnt/local-analysis/workspace-hub/digitalmodel/src/
digitalmodel/src/digitalmodel/citations/registry.py
$ grep -rl "knowledge/wikis/engineering" /mnt/local-analysis/workspace-hub/digitalmodel/
digitalmodel/src/digitalmodel/citations/registry.py
digitalmodel/tests/citations/test_schema.py
```

`registry.py:30` contains `"wiki_path": "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"` as part of the DNV-OS-E301 citation template — exactly the citation-contract pilot the plan's own resource summary cross-references. The plan's own `.claude/rules/calc-citation-contract.md` reading even mentions the pilot at `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (which calls into this registry).

This isn't a trivial inaccuracy. The plan's prioritization rationale is anchored on the claim that current cross-ref density is zero — *"prioritization cannot rely on existing `digitalmodel`-side reference density (count is zero everywhere). Must use the citation-contract intent (which standards calcs would cite) instead."* In reality, ONE wiki page (`dnv-os-e301.md`) is already wired into a calc, which is informative ground truth: the citation contract is operational, the engineering wiki is a live citation target. The audit should treat the existing wired path as the reference point for what fully-wired looks like and prioritize entries that fall within the same calc-adjacent surface (mooring/riser/fatigue standards consumed by `orcaflex/mooring_design.py` and siblings).

The plan should either (a) re-run the grep with the corrected scope and update the gap statement, or (b) acknowledge that ONE wiki path is wired and describe its role as the prioritization anchor. Leaving the false claim in place misleads downstream child-issue authors about the state of the citation contract.

**Fix:** Re-run grep against `/mnt/local-analysis/workspace-hub/digitalmodel/` (full tree, including `tests/`); update §Resource Intelligence Summary "Gap" bullet and §Evidence "Internal cross-reference scan" block; update the prioritization-rationale paragraph that currently asserts zero references.

### MAJOR-2 — Test contract is a structural shell that does not enforce the load-bearing acceptance criterion

Plan §Acceptance Criteria states: *"Each priority entry's rationale references one of: (a) SUT taxonomy discipline, (b) citation-contract intent (which calc would cite this), (c) raw-vs-wiki ratio."*

But the corresponding TDD test, `test_audit_priority_entry_schema`, only checks for *presence* of fields `{title, target_path, priority ∈ {P1,P2,P3}, rationale, candidate_sources}`. There is NO test that parses the `rationale` string and verifies it references one of (a)/(b)/(c). The audit can pass all 8 listed tests with rationales like *"feels important"* on every entry.

This matters because the acceptance criterion is the only thing that prevents the audit from devolving into 8-10 hand-waved priorities. The plan's own §Risks section flags exactly this hazard ("priority bias toward visible work") and offers the SUT-or-contract rationale rule as the mitigation — but the mitigation is unenforced.

**Fix:** Add a test like `test_audit_rationales_cite_required_anchors` that parses each rationale and asserts at least one of: a SUT discipline name, the literal string `citation-contract`/`citation contract`/`would cite`, or a ratio expression like `raw/wiki` or `\d+:\d+`. Without it, `test_audit_priority_entry_schema` is theater.

### MAJOR-3 — SUT taxonomy is asserted without source citation; one of three rationale anchors is uncheckable

Plan §"LLM Wiki pages consulted" line 40 introduces *"SUT (Society for Underwater Technology) public taxonomy: structural design / dynamic loading / construction & QA / materials technology / control engineering / fluid dynamics / reliability / hydro-mechanics / heat transfer / corrosion / soil mechanics / production flow management"* with no URL, document title, or version date. This list is then promoted in §Acceptance Criteria as one of three valid rationale anchors: *"Each priority entry's rationale references one of: (a) SUT taxonomy discipline…"*.

If a child-issue author writes a rationale like *"reliability"* or *"corrosion"* — which are common engineering words — there is no way to falsify whether they meant the SUT taxonomy entry or the generic English word. The taxonomy list resembles the SUT branch structure but the plan provides no anchor to verify it.

This degrades anchor (a) to "any sufficiently engineering-ish noun." Combined with MAJOR-2, the priority-list quality bar collapses.

**Fix:** Cite a specific SUT URL or document. Examples: <https://www.sut.org/about/branches-and-special-interest-groups/> or the SUT branch listings page. If no public canonical taxonomy exists, drop SUT and replace with a verifiable taxonomy (ISO 19900-series TOC, or the SPE OnePetro discipline tree).

---

## MINOR findings

### MINOR-1 — Case-insensitivity of agent-prefix bucket is implicit

Plan line 77 lists *"`claude/codex/gemini/agent/ai-/llm-/skill-/hermes/gsd-` prefix: 34 (agent/process — out of scope)"*. Reproducing without `-i` yields **20**, with `-i` yields **34**. The plan should explicitly state the regex and case sensitivity so re-verification at execution time is deterministic. Noted because the audit deliverable's `test_audit_file_counts_verifiable` asserts cited counts match `find` output within ±5% — without explicit regex, the test author can't reproduce the bucket-34 figure.

**Fix:** In §Evidence, write the literal command, e.g., `ls papers/ | grep -ciE '^(claude|codex|gemini|agent|ai-|llm-|skill-|hermes|gsd-)'`.

### MINOR-2 — Domain-engineering candidate count drifted

Plan says *"~14 files"* match the engineering regex; live count returns **12**. Within "~" margin but worth tightening, since this is the count of *target* content the audit ostensibly exists to surface — small but important.

**Fix:** Update to "12 files" or expand the regex to recover the missing 2.

### MINOR-3 — Root-file count discrepancy (105 vs 106)

§Resource Intelligence Summary line 14 says *"105 wiki output files across 5 subdirs … plus 4 root files"*. 42+23+23+9+5=102; +4 root = 106 (matches `find -type f`); but plan line 14 says "105 wiki output files … plus 4 root files" which double-counts. §Evidence line 59 says "106 files total" which is correct. Reconcile so both halves of the plan agree.

**Fix:** Restate line 14 as "102 files across 5 subdirs … plus 4 root files (total 106)" or "105 .md files (excluding `.gitkeep`)".

### MINOR-4 — Drift tolerance ±5% may swallow real changes

`test_audit_file_counts_verifiable` accepts ±5% drift. For `wiki/standards/` (9 files), 5% = 0.45 — i.e., the test catches every change. But for `raw/papers/` (520 files), 5% = 26 — the test won't catch a deletion of 25 files. If the audit is meant to be rerun after #2392 ships as a regression baseline (per §Risks "Open" #3), tolerance must shrink for raw counts.

**Fix:** Use absolute tolerance (±2 files) instead of percentage, OR per-subdir percentage with floor.

### MINOR-5 — `test_audit_no_wiki_writes` uses `HEAD~1`, will misfire if the audit lands as multiple commits

Test asserts *`git diff --name-only HEAD~1 -- knowledge/wikis/engineering/wiki/`* is empty. If the execution commit chain is more than one commit (test commit + audit commit), HEAD~1 misses the earlier commit. Should diff against the merge-base of the feature branch with `main`.

**Fix:** Use `git diff --name-only $(git merge-base HEAD origin/main) -- knowledge/wikis/engineering/wiki/`.

### MINOR-6 — Pseudocode column "top_5_files_by_name" risks long-run staleness

`table_B_wiki_inventory` includes *"top_5_files_by_name"* per subdir. Useful for the v1 audit but rapidly stale; if the audit becomes the regression baseline for #2392's detector output, name lists in markdown make diffing painful.

**Fix:** Replace with "first_5_files_alphabetical_at_audit_time" or drop and rely on file_count + verifier.

### MINOR-7 — "out-of-scope" prefix buckets may overlap

Plan does not assert mutual exclusivity of buckets. A file like `CLAUDE.md` is in both ALLCAPS (88) and agent_prefix (34, case-insensitive). Sum 237 may double-count. Should compute union via a single regex.

**Fix:** Compute `ls | grep -cE 'union-regex'` and report a single deduplicated count.

---

## Notes

- **Audit-only scope is genuinely held.** Files-to-Change table contains zero wiki paths; `test_audit_no_wiki_writes` enforces it; §Acceptance bullets reaffirm it. No stealth wiki edits detected.
- **Past-tense drift hunt:** clean. Plan correctly uses *"this plan creates"* / *"will be"* for not-yet-existent artifacts. The verified-evidence blocks are appropriately past-tense for completed verification activity. No mis-attributed artifact claims.
- **Deprecation pass open question** is answered ("Proposed default: YES") and scoped to *naming* prefixes only (no relocation execution) — appropriate for an audit-only plan.
- **Cross-domain concept question** is punted to user approval; appropriate.
- **Regression-check question** is punted as a follow-up; appropriate.
- **Resource Intelligence sources count = 6** (≥3 required); satisfied.
- **Adversarial scope-utility check:** Conditional. If MAJOR-2 + MAJOR-3 are addressed (rationale enforcement + verifiable taxonomy anchor), the audit will surface an actionable 8-10 priority list. As-drafted, the audit could legitimately ship with low-quality rationales because nothing tests them.
- **Single-author provenance:** Codex and Gemini provider channels were not invoked from this planning-only session (per memory `feedback_permission_gate_blocks_cross_review.md`). User should treat this review as 1-of-1, not 1-of-3.

---

## Verification checklist

- [x] Plan read in full
- [x] Counts re-verified (raw=521, wiki=105/106 reconciled)
- [x] Subdir tree re-verified (flat raw, 5 wiki subdirs)
- [x] Issue states re-verified (5/5 OPEN)
- [x] Filename-prefix bucketing re-verified (with case-sensitivity caveat)
- [x] digitalmodel cross-ref scan re-verified — DIVERGES from plan (MAJOR-1)
- [x] Audit-only scope re-verified (clean)
- [x] Test contract assessed (MAJOR-2)
- [x] SUT taxonomy provenance assessed (MAJOR-3)
- [x] Past-tense drift hunt completed (no findings)

---

**VERDICT:** MAJOR (3 P1 findings). The plan is structurally sound and the inventory work is solid, but a load-bearing factual claim (digitalmodel cross-refs) is wrong, the test contract does not enforce its load-bearing acceptance criterion, and one of three rationale anchors (SUT) is unverifiable as cited. Address MAJOR-1/2/3 and re-review.
