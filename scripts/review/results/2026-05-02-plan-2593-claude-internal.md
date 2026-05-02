# Adversarial review — plan #2593 W2-D online-resource-registry refresh

> **Reviewer:** Claude (single-author, internal)
> **Provider matrix:** Codex UNAVAILABLE per #2479 (codex-cli 0.124.0 stdin-hang regression). Gemini UNAVAILABLE — sandbox overlay blindness + permission gate per memory `feedback_permission_gate_blocks_cross_review.md`. Single-author review.
> **Plan:** `docs/plans/2026-05-02-issue-2593-llm-wiki-W2D-online-resource-registry-refresh.md` (277 lines, draft)
> **Issue:** [#2593](https://github.com/vamseeachanta/workspace-hub/issues/2593) (OPEN)
> **Date:** 2026-05-02
> **Stance:** defects until proven otherwise

---

## VERDICT: MAJOR

3 MAJOR · 5 MINOR

---

## MAJOR

### M1 — Schema additions (`last_verified`, `superseded_by`) introduce split-brain without a schema-evolution path

**Where:** plan §"TDD Test List" row 7 + §"Risks and Open Questions" 5th risk + `Acceptance Criteria` row 5.

**Quoted claim:**
> "every patch entry has `id`, `url`, `name`, `type`, `domain`, `revision`, `last_verified`, `code_id` (when applicable)"
> "`last_verified` is added only to patch-introduced entries; existing entries continue to use `last_checked`. A follow-up issue will harmonize the two field names."

**Why this is a defect:** the plan introduces a new field name (`last_verified`) for the same semantic as the existing field (`last_checked`) and explicitly defers harmonization. After this plan lands, the registry will have two fields meaning roughly the same thing on different subsets of entries. Every consumer (`scripts/data/generate-domain-resource-views.py`, `scripts/document-intelligence/cross-reference-registries.py`, `tests/data/test_build_online_resource_registry.py`) must now know about both. The plan offers no rationale for why a *new* name is needed instead of reusing `last_checked`, and offers no follow-up issue number — just a forward promise. This is the exact split-brain pattern that creates audit-debt the next quarterly refresh has to clean up. Either (a) reuse `last_checked` and the plan reduces to a value-update, or (b) the schema-evolution belongs in its own plan that updates all consumers atomically. Same critique applies to `superseded_by` (no consumer reads it, no existing entry sets it, no follow-up wired).

**Severity rationale:** the *deliverable* is a YAML patch sidecar; consumers don't read it yet. But Acceptance Criterion row 5 says "every patch entry has … `last_verified`", which freezes the divergent field name into the artifact this plan ships. Once shipped, future refreshes inherit the split.

**Fix:** either (a) drop `last_verified` from the patch schema and reuse `last_checked` everywhere, or (b) split out a schema-evolution sub-issue that lands BEFORE W2-D and harmonizes the two consumers. State explicitly which path.

---

### M2 — `test_url_resolves_sample` reaches the live network from pytest with no opt-out marker

**Where:** plan §"TDD Test List" row 6.

**Quoted claim:**
> `test_url_resolves_sample` — sample of 10 entries (deterministic, seeded by hash) returns 200 OR 3xx via WebFetch at audit-time | 10 sampled entries | unverifiable URLs flagged as `flaky`, NOT `missing` (per Risks below)

**Why this is a defect:**
1. The test runs in `tests/data/` — same harness as the existing `test_build_online_resource_registry.py` that runs on every `uv run pytest tests/data/`. There is no `@pytest.mark.network` / `@pytest.mark.audit` gate proposed, no `--audit` opt-in flag. Acceptance Criterion row 2 explicitly says `uv run pytest tests/data/` must pass with no regression. That command will, on the next CI run, hit `WebFetch` 10 times against publisher portals. CI without internet access (or behind rate limits) will flake.
2. "Flaky NOT missing" is a *result classification* (verification_status field in the audit report, per the Risks section) — but the **test itself** is binary pass/fail. The plan never states what assertion the test makes when WebFetch returns 503. Does it pass-with-warning? Does it skip? The TDD list is silent.
3. The plan calls out the W2-D *audit-time* test ("the W2-D test will be a separate audit-time test, not a duplicate" — line 19). But the audit-time vs build-time distinction is not enforced by any pytest marker or directory split. Co-locating audit-time URL-resolution with schema validation in the same file violates that distinction.

**Severity rationale:** this directly creates the kind of brittle test the prompt's check 9 explicitly flags. URL-resolution at build-time is the named anti-pattern.

**Fix:** (a) put audit-time tests in `tests/audits/` or under `@pytest.mark.audit` so default pytest skips them; (b) define explicit pass/skip semantics for 503 / timeout / DNS-fail; (c) tighten Acceptance Criterion row 1 to say `uv run pytest tests/data/test_online_resource_registry.py -v -m "not audit"` (or equivalent).

---

### M3 — Cross-link verification to W1 wave conflates "publisher URL" with "registry entry" and misses the actual gap

**Where:** plan §"Pseudocode" step 3 + §"Resource Intelligence Summary" / "LLM Wiki pages consulted":

**Quoted claim:**
> ```
> for plan in [#2586, #2587, #2589]:
>     for standards_page in plan.proposed_pages:
>         if standards_page.publisher_url not in registry:
>             missing_entries.append((standards_page, "referenced by W1 plan"))
> ```

**Why this is a defect:** I read W1-A (#2586) — line 114 of that plan lists API RP 2A-WSD's canonical URL as `https://store.accuristech.com/standards/api-rp-2a-wsd-r2025`. Grep of the registry for `accuristech` returns **zero matches**. So W1-A's anchor URL is genuinely missing. But the W2-D pseudocode treats `standards_page.publisher_url` as a known attribute on `plan.proposed_pages` — it is not. W1-A proposes wiki pages, not URL pointers. The plan needs to either (a) explicitly enumerate the W1 publisher URLs it will check (5-10 of them, listed inline), or (b) define what "proposed_pages" extraction means: from frontmatter? From the plan's standards-table rows? From issue body?

Worse, the plan misses a real cross-link:

- W1-A line 32 cites `API RP 2SK 3rd Ed (2005, R2008)` with 66 occurrences in `digitalmodel`. The registry's only API RP 2SK entry is `https://www.api.org/products-and-services/standards/important-standards-announcements/standard-2sk` — the *announcements* portal, not the document. So even where the registry has an entry, it's pointing at the wrong thing for W1-A's purpose. The W2-D pseudocode `if standards_page.publisher_url not in registry` will FALSE-NEGATIVE this case (URL is present, but not the right URL), missing exactly the gap a cross-link audit should catch.

**Severity rationale:** the cross-link check is one of the plan's three named deliverables; getting it wrong defeats the audit's purpose.

**Fix:** (a) list the specific URLs from W1-A/B/D that W2-D will verify (explicit ≤15-URL list in §Resource Intel before plan-approval); (b) checking should be by *code_id* (e.g., API-RP-2SK, DNV-ST-F101) not by URL string-match — that requires `code_id` linkage, which is the plan's third schema gap. So M3 is mutually-supporting with M1.

---

## MINOR

### m1 — Path-naming convention drift inside the workspace's review-artifact dir

**Where:** plan §Artifact Map rows 6-8 + §Acceptance Criteria final row.

**Claim:** Review artifacts go to `scripts/review/results/2026-05-02-plan-W2D-{claude,codex,gemini}.md`.

**Defect:** existing convention in `scripts/review/results/` is **plan-NNNN** (issue number), not **plan-WAVE**. Examples in dir: `2026-05-02-plan-2532-claude.md`, `2026-05-02-plan-2541-claude.md`, `2026-05-02-plan-2550-claude.md`. The "W2D" naming is an outlier that breaks `gh issue view 2593 --json title | …` ↔ review-file lookup. The prompt for THIS review explicitly requested `2026-05-02-plan-2593-claude-internal.md`, illustrating the friction.

**Fix:** rename to `2026-05-02-plan-2593-{claude,codex,gemini}.md` to match dir convention.

### m2 — "Codex/Gemini pending" rows in Adversarial Review Summary are dead text given environment

**Where:** plan §Adversarial Review Summary table rows 2-3.

**Claim:** "| Codex | (pending) | … | | Gemini | (pending) | …"

**Defect:** per memory `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_permission_gate_blocks_cross_review.md`, neither cross-review channel is operational this batch. Listing them as "pending" in a draft is past-tense drift in the *opposite* direction — pretending capacity that does not exist. Plan should either (a) remove the rows, (b) mark them `n/a — #2479` and `n/a — sandbox`, or (c) explicitly authorize single-author Claude review.

### m3 — `total_entries: 247` vs body-count 248 escalation path is unspecified

**Where:** plan §"Line excerpts" + §"Risks and Open Questions" 4th risk + §TDD test row 2.

**Claim:** "audit report records it as a finding; W2-D does not attempt to fix it (out of scope)."

**Defect:** `test_frontmatter_total_entries_matches_body` is in the test list as a FAIL-allowed test — ACK row 1 explicitly carves out "excluding `test_frontmatter_total_entries_matches_body` which is allowed to fail and is documented as the rationale for fixing frontmatter in a follow-up PR." A test that's expected to fail is a `pytest.xfail`, not an unmarked test. As written, it'll either (a) flag every CI run permanently or (b) be silently skipped because of how the contributor wrote it. No follow-up issue number is provided. The "follow-up PR" claim is a forward promise without an artifact.

**Fix:** decorate with `@pytest.mark.xfail(reason="247-vs-248 drift, follow-up #NNNN")` once the follow-up issue exists; do NOT write the xfail before the issue is filed.

### m4 — Acceptance criterion "≥10 stale OR ≥5 missing" is satisfiable by reading the plan itself

**Where:** plan §Acceptance Criteria row 3.

**Claim:** "Audit report identifies **≥10 stale entries OR ≥5 missing high-value entries** (whichever bound is reached first; need not satisfy both)."

**Defect:** the plan's Resource Intel section already names 4 missing high-value entries (API RP 2A-WSD R2025, DNV-ST-F101, ISO 19901-7 FDIS, MARPOL Annex VI). Adding any 1 more during implementation trivially satisfies the ≥5 bound without doing the WebFetch sweep at all. The bound should require *new* findings beyond what the plan already names — e.g., "≥5 missing entries beyond the 4 in §Resource Intel" or "≥10 stale entries with revision-string evidence". As written the criterion is gameable.

### m5 — `docs/plans/README.md` update is mentioned but not specified

**Where:** plan §Files to Change row 4 + §Acceptance Criteria row 6.

**Claim:** "Update | docs/plans/README.md | add this plan to the plan index"

**Defect:** there is no §"Plan Index Entry" snippet showing what gets added. Other plans in this batch (2586/2587/2588/2589) presumably also update the same file — race-condition risk per memory `feedback_multi_agent_commit_serialization.md`. This is a minor, but worth surfacing in a wave with parallel plan-landing.

**Fix:** include a one-liner of the exact text to insert and the exact line number / section heading to insert under, so multiple W-N agents don't conflict on the same file.

---

## Affirmative findings (verified, no defect)

- **Plan claim "registry has zero `revision` fields today"** — VERIFIED. `grep -E "^[[:space:]]*revision:" data/document-index/online-resource-registry.yaml | wc -l` = **0**.
- **Plan claim "248 entries"** — VERIFIED. `grep -c "^- id:" …` = **248**.
- **Plan claim "frontmatter says total_entries: 247"** — VERIFIED. Header line 2 of registry yaml.
- **Plan claim "238/9/1 last_checked distribution"** — VERIFIED exactly.
- **Cited issue states (#2540/#2586/#2587/#2588/#2589/#2593 OPEN, #2302/#2471 CLOSED)** — VERIFIED via `gh issue view`.
- **Cited file existence (4 scripts + existing test)** — VERIFIED via `ls`.
- **Cited commit `24eccfc49`** — VERIFIED in git log; bounded-patch precedent (8 dead URLs + 1 archive) is real.
- **Cited recent file commits** — VERIFIED, last targeted edit was indeed #2302.
- **Audit-only nature** — VERIFIED. Plan §"Files to Change" includes only Create/Update on `docs/audits/…`, `…proposed-patch.yaml`, `tests/data/test_online_resource_registry.py`, `docs/plans/README.md`. The registry yaml itself is on the explicit "NOT modified" list (line 217). No registry edits slipped in elsewhere.
- **Past-tense drift** — minimal. Plan uses future tense throughout for the deliverable. Workflow-status checkbox `[x] Plan drafted` is appropriate (the plan IS drafted as of this review).
- **`docs/audits/` dir creation claim** — VERIFIED. `ls docs/audits` returns "No such file or directory" today; plan correctly states "creates docs/audits/ dir".

---

## Decision

**MAJOR** — three substantive defects (M1 schema split-brain, M2 brittle network test, M3 cross-link semantics). MINORs are cleanup. Do not approve until M1/M2/M3 are addressed in a v2 draft.
