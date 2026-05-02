# Adversarial review — Plan #2590 (LLM-Wiki W2-A: DNV bounded summary promotion)

- **Plan path:** `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md`
- **Commit / state:** working-tree (untracked plan), reviewed 2026-05-02
- **GitHub issue:** #2590
- **Reviewer:** Claude (single-author per memory `feedback_permission_gate_blocks_cross_review.md`)
- **Codex provider status:** UNAVAILABLE — codex-cli 0.124.0 stdin-hang regression (#2479)
- **Gemini provider status:** UNAVAILABLE — sandbox cwd=/tmp blocks workspace reads
- **Stance:** adversarial; defects until proven otherwise

---

## Verdict: MAJOR

Three P1 (blocking) defects. Multiple P2/P3 issues. The plan as written misrepresents the gap landscape, overreaches a sanction citation, and lets its acceptance criteria miss the central risk it itself names.

---

## P1 — Blocking defects

### P1-1 — False gap claim: 5 of the 10 "to be created" pages already exist in `engineering/wiki/standards/`

**Plan claim (Resource Intelligence Summary, line 25):**
> "Gap: no summary-promotion artifact exists for the `/mnt/ace/O&G-Standards/DNV/` corpus in the `engineering-standards` wiki. The single existing DNV wiki page (`knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`) sits in the **engineering** wiki..."

**Plan claim (line 67):**
> "No engineering-standards wiki pages exist for any DNV code: DNV-ST-F101, DNV-RP-C203, DNV-RP-C205, DNV-RP-B401, DNV-OS-E301 (in this wiki domain), DNV-OS-F201, DNV-RP-F101, DNV-RP-F105, DNV-RP-F109, DNV-RP-H103."

**Verified ground truth** (`ls knowledge/wikis/engineering/wiki/standards/`):
```
api-579-ffs.md
dnv-os-e301.md
dnv-rp-c203.md   ← exists, plan silent
dnv-rp-c205.md   ← exists, plan silent
dnv-rp-f101.md   ← exists, plan silent
dnv-rp-f105.md   ← exists, plan silent
ocimf-meg4.md
ocimf-tandem-mooring.md
TEMPLATE.md
```

The plan accurately flags `dnv-os-e301.md` cross-domain duplication (line 35, line 218, Risks). It is **silent on the four other pre-existing DNV pages** — `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`. These contain *substantive technical content* (not stubs); `dnv-rp-c203.md` is 116 lines with S-N curve methodology, DFF tables, Miner's-rule formulas. `dnv-rp-c205.md` carries Morison-equation regimes. These pre-existing pages are full prose — the very category #2482 vendor-derivative governance sweeps over.

The plan therefore creates a 5x cross-wiki collision (not 1x as Risks claims), and ships ten pages while four of them have a non-bounded prose-y twin in the engineering wiki. A future `Citation(code_id="DNV-RP-C203", ...)` resolver hitting the engineering-domain page (which already has `code_id`-equivalent matching at filename level and `sources: [dnv-rp-c203]` frontmatter) versus the engineering-standards-domain page (with `extraction_policy: metadata-only`) will get non-deterministic resolution.

**Required fix before APPROVE:**
1. Resource Intelligence must list all 4 pre-existing DNV pages, with content classification (stub vs prose).
2. Risks section must escalate "cross-wiki duplication" from a DNV-OS-E301-only risk to a 5-page-pattern risk.
3. The plan must commit to one of: (a) retro-bound the existing engineering-domain pages with `extraction_policy: metadata-only` frontmatter so they can be the citation target (and W2-A becomes a frontmatter-retrofit + 5 new pages, not 10 new pages), or (b) explicit "the engineering-domain pages are NOT citation targets and will be migrated/deprecated in a follow-up" with a tracked follow-up issue number.
4. Acceptance criterion needed: `code_id` uniqueness across all wiki domains under `knowledge/wikis/*/wiki/standards/*.md` is asserted by the test suite (otherwise resolver semantics are silently ambiguous).

### P1-2 — #2471 sanction-scope overreach

**Plan claim (line 10):**
> **Path sanction:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) — `wiki/standards/<code-id>.md` routing

**Plan claim (line 62):**
> "`project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` is the sanctioned path; #2471 codified it for CSA Z276 and the principle now generalizes to API (W1-A) and DNV (this W2-A plan)."

**Verified ground truth — `gh issue view 2471`:**
- Title: "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- Acceptance criteria: "sanctioned CSA durable destination is documented", "Blocks CSA portion of: #2227"
- The body is **explicitly CSA-Z276 scoped**. No DNV. No general-standards generalization.

**Memory `project_wiki_standards_path_decision.md` confirms (literal quote):**
> "**#2471 is CSA-Z276-only** (verified 2026-04-25), referenced codification plan does not exist; general offshore/marine substrate now scoped to aceengineer-strategy aces-#4"

**Verified `.claude/rules/calc-citation-contract.md`:**
- Item 2 says: "Citation target: a wiki page with #2471 frontmatter (`code_id`, `publisher`, `revision`)."
- This rule **does** treat the #2471 frontmatter triple as the contract baseline — but it does so by referencing the *frontmatter shape* #2471 codified for CSA, not by claiming #2471 sanctioned the path globally. The plan conflates "frontmatter triple from #2471" with "#2471 sanctioned the path." Those are different claims.

**Defect:** The plan's "Path sanction: #2471" header overreaches. The `wiki/standards/` path generalization to DNV is not actually sanctioned by #2471's body — it's an inferred extension. Memory explicitly cautions that "the referenced codification plan does not exist." Calling #2471 the path sanction for DNV is the kind of citation overreach the calc-citation contract was written to prevent. Plan-level meta-irony.

**Required fix:** Either (a) drop "Path sanction: #2471" and replace with "Frontmatter contract per #2471 (originally CSA-scoped); path generalization per project memory `project_wiki_standards_path_decision.md` (and #2586 W1-A precedent)", or (b) cite the actual sanction surface for DNV — which, on the evidence, doesn't exist as a code-pinned issue. The honest framing is (a).

### P1-3 — Acceptance criteria miss the headline rebrand risk

**Risks section (line 293):** the plan flags rebranding as a real risk and proposes `legacy_code_id: DNV-OS-F101` on the dnv-st-f101.md page.

**Verified ground truth — internal callers:**
```
75 DNV-ST-F101
24 DNVSTF101    ← variant
13 DNV-OS-F101  ← legacy
12 DNV_ST_F101  ← variant
```

Internal callers use 4 distinct spellings. The plan's mitigation — `legacy_code_id: DNV-OS-F101` on a single page — bridges only the spelling pair `(DNV-ST-F101, DNV-OS-F101)`. It does not bridge `DNVSTF101` or `DNV_ST_F101` (37 hits combined).

**Acceptance criterion gap:** The plan has a test `test_legacy_code_id_only_on_renamed_codes` which asserts the field is *present and equals "DNV-OS-F101"* — but it does NOT exercise the resolver path for either of the variant spellings. The "rebrand bridge" is not testable end-to-end as written. A `Citation(code_id="DNV_OS_F101", ...)` from a digitalmodel call site would still raise `CitationResolutionError` after this plan lands.

The Risks section's mitigation does not match what the Acceptance Criteria can detect. The risk is real (#2481 D2 fail-closed contract makes this a calc-time failure mode); the test does not catch it.

**Required fix:** Either (a) add a test/AC that constructs a `Citation` with each historical spelling variant and asserts the resolver normalizes to the canonical page, or (b) acknowledge in Risks that the bridge covers only the `OS-F101 ↔ ST-F101` exact-form pair and that variant-spelling normalization is out of scope (and file a follow-up).

---

## P2 — Significant defects

### P2-1 — Future-tense drift: review-artifact paths committed before review runs

**Lines 14, 151–153, 269:** the plan pre-commits paths for `2026-05-02-plan-DNV-W2-{claude,codex,gemini}.md`. The Review artifacts table at line 14 names these as "to be produced post-plan-review by main session"; the Acceptance Criteria at line 269 names them as a hard pass condition.

But: per memory `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_gemini_sandbox_overlay_blindness.md`, both Codex and Gemini are unavailable for headless dispatch in current state. The Acceptance Criterion as written would block the implementation issue indefinitely. The plan needs an explicit "single-author Claude review acceptable per `feedback_permission_gate_blocks_cross_review.md`" carve-out OR drop the codex/gemini lines from AC.

The Adversarial Review Summary at lines 281–283 hedges this ("may be UNAVAILABLE pending downgrade") in commentary but doesn't relax the AC. Acceptance criteria should match operational reality, not aspiration.

### P2-2 — `digitalmodel` grep-frequency as a relevance proxy is unstated as an assumption

**Lines 105–122 evidence block:** ranks codes by `grep ... | sort -rn`. **Verified:** the counts are accurate.

But the plan uses these counts as the priority-selection criterion (line 298: "biased by (a) digitalmodel internal-reference frequency"). Hidden assumption: `digitalmodel` is the dominant downstream consumer. This is not asserted or sourced in the Resource Intelligence Summary. If `assethold`, `worldenergydata`, `acma-projects` (all sibling repos) cite a different DNV distribution, the priority ranking is wrong. The plan does not show that `digitalmodel` is the citation hotspot relative to its siblings.

Drift from W1-A precedent: #2586's W1-A plan should have answered the same question for API. Cross-repo consumer audit is a one-time cost that should be paid once, not per-publisher.

### P2-3 — `test_no_raw_pdf_text_bleed_through` denylist is vendor-front-matter-only and brittle

**Line 251:** the `RAW_TELLTALE_PHRASES` list targets DNV cover-page strings ("Det Norske Veritas AS", "Veritasveien 1", etc.). Per the plan's own acknowledgement (line 292): "If a future contributor pastes scope text from the PDF, the denylist may miss novel phrases."

The mitigation appeals to (a) word-count ceiling 500, (b) positive-shape structural test, (c) `extraction_policy: metadata-only` frontmatter. But (a) and (b) do not stop a 200-word verbatim copy of a single normative clause that fits inside the structural shape; (c) is a YAML hint, not enforcement.

Per memory `feedback_naive_secret_scan_false_positive_cascade.md`, simple regex denylists generate false positives. Per #2482, the deny-list goal is no clause-text in git. The proposed test architecture cannot detect a verbatim 100-word clause copy that omits cover-page strings.

**This is a known limitation** the plan admits. But the AC at line 260 ("zero matches for the `RAW_TELLTALE_PHRASES` denylist") treats the denylist as the gate, when the actual goal is "no verbatim clause text." The test contract under-asserts the policy. Recommend an additional cosine-similarity / shingle-match test against the source PDF text (extract once, never commit, compare during CI).

### P2-4 — Code-style mismatch with W1-A is "deferred" via plan-review handoff

**Lines 295, 313:** the plan uses uppercase-with-hyphens `DNV-OS-E301` style; W1-A uses lowercase-kebab `api-rp-2a-wsd`. The plan flags this as an Open question and defers harmonization.

But the W2-A plan and W1-A (#2586) are both in `status:plan-review` simultaneously. Deferring harmonization via "if user prefers a single case-style across all wikis, this plan can be respun in lowercase before approval" creates a tight coupling: approving either plan as-is locks in the inconsistency. This is exactly the inter-plan inconsistency that should be resolved *during* plan-review, not deferred from it.

Verified by reading `knowledge/wikis/engineering-standards/CLAUDE.md` (the engineering-standards CLAUDE.md schema): the example codes given are `csa-z276`, `api-17j`, `ocimf-meg4` — all lowercase-kebab. The existing engineering-standards page `api-17e.md` uses `code_id: api-17e` (lowercase). The DNV pilot in the *engineering* wiki uses uppercase. The engineering-standards CLAUDE.md schema **explicitly samples lowercase-kebab**.

So: the W2-A plan's choice to adopt uppercase contradicts the engineering-standards CLAUDE.md schema example. The plan acknowledges the W1-A inconsistency but misses the wiki-CLAUDE.md schema inconsistency (which is more authoritative than a sibling plan).

**Required fix:** adopt lowercase-kebab to match (a) the engineering-standards CLAUDE.md schema, (b) the existing `api-17e.md` engineering-standards page, (c) the W1-A precedent. The "match the existing DNV pilot in *engineering*" argument is weakened by the fact that the existing pilot lives in the wrong wiki for citation contract purposes anyway.

### P2-5 — `test_citation_schema_resolvable` does not actually exercise resolver

**Line 247:** the test constructs `Citation(...)` with `section="placeholder"`. Per `digitalmodel/src/digitalmodel/citations/schema.py`, `Citation.__post_init__` enforces non-empty strings and `wiki_path` shape — that's it. **It does not read the wiki page.** The test as described would pass even if every wiki page were missing on disk.

**The actual fail-closed resolver is `CitationResolutionError`** raised by a separate code path that reads the file (referenced in `registry.py`). The plan's test exercises `CitationValidationError` (constructor-time) only.

**Required fix:** the test must invoke the resolver function (whatever calls `_read_frontmatter` from `schema.py`) and assert the page actually resolves with frontmatter matching. Otherwise this AC is hollow.

---

## P3 — Minor defects

### P3-1 — DNV-RP-H103 path inaccuracy

**Line 40:** `online-resource-registry.yaml` `local_backup_path` cited as `/mnt/ace/docs/_standards/SNAME/hydrostatics-stability/DNV-RP-H103-Marine-Operations-2010.pdf`. **Verified copy on disk** is at `/mnt/ace/O&G-Standards/DNV/Recommended-Practices/DNV-RP-H103_(2011)_Modelling_and_Analysis_of_Marine_Operations.pdf` (note: 2011, not 2010). Plan should use the DNV-corpus path, which it does correctly in line 86 — but the Resource Intelligence cites the SNAME-folder backup path. Pick one source of truth.

### P3-2 — `page_count: 5` on existing index.md is misread

**Verified `engineering-standards/wiki/index.md`:** `page_count: 5, source_count: 5` in frontmatter, but the body table shows only 5 source rows and one heading-only `[[Elements ingest catalog — doris-codes-specs]]` link — and `wiki/standards/` directory contains only `api-17e.md` (1 file). Plan claims (line 224) bump to 15 (5 + 10). But the existing 5 are all *sources*, not standards. Total file count after this plan = 5 sources + 10 standards + 1 existing standards = 16, not 15. Off-by-one.

### P3-3 — Standards-transfer-ledger 4-row addition list omits two

**Line 54:** plan claims ledger lacks "DNV-RP-C203, DNV-RP-C205, DNV-RP-H103, or DNV-OS-E301" rows, and adds 4. **Verified by grep** of the ledger: confirmed those 4 IDs are absent. But the plan also depends on `DNV-RP-F103` (16 hits in digitalmodel — top-15) which is *not* in the W2-A top-10 yet has ledger rows `DNV-RP-F103` and `DNV-RP-F103-2010` already (line 54 mentions). Why are these excluded from W2-A while included in evidence claims? The exclusion is line 119 "noted but excluded" — but the rationale ("cathodic-protection sibling of B401, lower freq") is shaky given F103's hit count exceeds DNV-OS-F201 (22) and DNV-RP-F109 (19), both of which made the cut.

Recommend: apply the priority ranking consistently or document the disqualifying criterion (e.g., "siblings of higher-ranked codes are deferred to W2-B").

### P3-4 — Word-count budget inconsistency

**Plan TDD line 244:** "100 < N < 500" (open-set lower bound).
**Plan AC line 244 says** "matches W1-A's tightened 500-word ceiling."

W1-A's ceiling could not be cross-checked here without reading the W1-A plan; flagging as P3 for plan-author to confirm parity. If W1-A is `<500` strict and W2-A is `<500` strict, fine. If one is `<= 500`, mismatch.

### P3-5 — "DNV is the publisher" doesn't capture DNV GL legacy

The 2013 merger of Det Norske Veritas + Germanischer Lloyd produced "DNV GL" (2013–2021), reverted to "DNV" in 2021. Plan uses `publisher: DNV` for codes whose 2013–2021 editions were published as "DNV GL". Frontmatter uses a single canonical publisher; per `Citation` schema literal-equality on revision/publisher (line 263), this is fine for the *current* edition but loses provenance for archived 2013–2021 editions. Minor — flag as a comment in the plan.

---

## Verified evidence

### Issue states (gh issue view, 2026-05-02)
- `#2471` CLOSED — title literally "decide sanctioned CSA Z276 wiki routing" — confirmed CSA-only scope. ✅
- `#2540` OPEN — confirmed. ✅
- `#2586` OPEN — confirmed. ✅
- `#2227` CLOSED — confirmed. ✅
- `#2482` CLOSED — confirmed. ✅
- `#2481` CLOSED — confirmed. ✅

### Files on disk
- `/mnt/ace/O&G-Standards/DNV/` — `find -maxdepth 4 -name '*.pdf' -o -name '*.PDF'`: **99 files** ✅ (matches plan claim)
- DNV-OS-F101 on disk (multiple revisions 2000–2013) ✅
- DNV-RP-C203 on disk (2000, 2005, 2008, 2011) ✅
- DNV-OS-E301 on disk (2008, 2010) ✅
- DNV-RP-H103 on disk at `Recommended-Practices/DNV-RP-H103_(2011)_*` ✅

### Pre-existing engineering-domain pages (NOT engineering-standards) — counterevidence to plan
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md` (4762 bytes, prose-rich) ❌ plan silent
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-c205.md` (5642 bytes, prose-rich) ❌ plan silent
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-f101.md` (3840 bytes) ❌ plan silent
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-f105.md` (1974 bytes) ❌ plan silent
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` ✅ plan acknowledges

### Internal-reference grep (2026-05-02 reproduction)
Plan's table (lines 105–122) verified exact-match reproducible. ✅

### `engineering-standards/CLAUDE.md` schema example codes
`csa-z276`, `api-17j`, `ocimf-meg4` — **lowercase-kebab**. Plan adopts uppercase, contradicting the wiki's own schema example. (P2-4)

### `digitalmodel/src/digitalmodel/citations/schema.py`
Confirmed: `Citation.__post_init__` runs string-non-empty + wiki-path-shape checks only; does NOT read the wiki page. The test described in plan line 247 is hollow as written. (P2-5)

### `.claude/rules/calc-citation-contract.md`
Re-read end-to-end. The contract names #2471 only as the source of the **frontmatter triple** (`code_id`/`publisher`/`revision`), not as the path-sanction surface. Plan's "Path sanction: #2471" header is a misattribution. (P1-2)

---

## Required revisions before APPROVE

1. **P1-1**: Add the 4 pre-existing DNV pages to Resource Intelligence; commit to one of {retrofit-existing, deprecate-existing, accept-collision-with-tracked-follow-up} — not silent.
2. **P1-2**: Replace "Path sanction: #2471" with the honest provenance citation (frontmatter from #2471, path generalization from project memory + W1-A precedent only).
3. **P1-3**: Either add resolver-level rebrand-variant tests OR scope-down the rebrand mitigation in Risks to "exact-pair only, variant-spelling normalization deferred to W2-B".
4. **P2-1**: Relax AC for review artifacts to single-author-acceptable per memory carve-out, OR remove codex/gemini paths from the gate.
5. **P2-4**: Pick lowercase-kebab to match wiki CLAUDE.md schema + W1-A; document the existing-pilot-style decision as "supersede the engineering-domain pilot's casing in the engineering-standards-domain page."
6. **P2-5**: Replace `test_citation_schema_resolvable` with a test that actually exercises the resolver (file-read + frontmatter parse + assertion of `code_id`/`publisher`/`revision` match). Constructor-only validation is hollow.

After 1–6, P2-2/P2-3/all P3 are addressable as inline edits.

---

## Reviewer disclosure

- Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`.
- Codex unavailable: `codex-cli 0.124.0` upstream stdin-hang regression (#2479).
- Gemini unavailable: sandbox cwd=/tmp blocks workspace-hub overlay reads (per memory `feedback_gemini_sandbox_overlay_blindness.md`).
- Recommendation: when Codex 0.123.0 downgrade lands, dispatch a v2 review against the revised plan — at least P1-1 and P1-2 are the kind of evidence-based defects Codex's GitHub-connector reads find well.
