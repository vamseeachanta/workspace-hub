# Session Exit Report — Doc-Intel Planning (2026-04-20)

> Consolidated record of a single long-form session that reviewed the llm-wiki / resource/document-intelligence ecosystem, filed 12 GitHub issues, iterated 3 of them through 3 rounds of adversarial cross-provider review, identified 2 structural infrastructure gaps, and landed a complete handoff for the next session.

## Session arc (chronological)

1. **Ecosystem review** — mapped llm-wikis (L3) / `/mnt/ace/` (L1) / repo docs / online research onto the operating-model (#2205) 6-layer pyramid. Identified 4 gap bundles: completeness, info-flow strengthening, online codes/CFR, AI-capability uplift.
2. **Portfolio audit** — inventoried 70+ existing issues; grouped to features (governance, conformance, navigation, promotion, ingestion, umbrella). Reviewed the 2026-04-19 Claude adversarial review prompt; found 12 defects (P1–P12).
3. **Filed 5 initial issues** (#2392–#2396) across the gap bundles; drafted 5 plans + Claude self-reviews (all MINOR).
4. **Iter-1 cross-review** — 10/10 MAJOR. Convergent defects: sha256 unenforced, unverified claims, AC-test gaps, threat-model absent, dep statuses unverified.
5. **Path B (splits)** — closed #2393 → #2402+#2403; closed #2396 → #2400+#2401+#2404. 5 successor issues filed with tighter scope.
6. **Path A (v2 rewrites)** — #2392/#2394/#2395 rewritten with §Identity, §Tier, §Threat, §AC↔Test sections.
7. **Iter-2 cross-review** — 6/6 MAJOR. Real bugs caught: pseudocode correctness bug (#2395 undefined `part`), identity self-contradiction (#2394), storage authority ambiguity (#2393→#2402 lesson), eCFR rate limit 4× over-spec.
8. **Path α (template + evidence)** — updated `_template-issue-plan.md` with §Evidence subsection. v3 plans for #2392/#2394/#2395 embedded `gh`/`ls`/`sed` output inline.
9. **Iter-3 cross-review (final)** — 6/6 MAJOR. New defects: #2395 desync-repair still broken for older parts, `natural_key()` TypeError edge case, hard-dep mocking strategy gap. Class B "unverified claims" became convergent.
10. **Iteration cap hit on #2392/#2394/#2395** — closed with carry-forward defect catalogs; filed meta-issue #2405 to address root-cause infrastructure gap.
11. **#2405 filing** — cross-review sandbox lacks repo access; reviewers cannot verify live-state claims the prompt mandates.
12. **User approvals** — #2401/#2402/#2403/#2405 approved on GitHub.
13. **#2405 iter-1** — Codex+Gemini MAJOR. v2 fixes Class A real defects inline.
14. **#2405 iter-2** — **Codex timeout ×2** at 300s + 600s (infrastructure bug discovered). Gemini returns MAJOR with 4 real P1 bugs (budget-exhaustion logic, claim/impl mismatch, regex inconsistency, readlink flag-injection). #2405 v3 fixes all four.
15. **#2403 iter-1** — Codex timeout, Gemini MAJOR (sha256 compliance gap + 2 test-promotion findings). #2403 v2 fixes.
16. **#2406 filed** — Codex dispatch-stdin-hang bug (distinct from #2405 scope; reliability not verification).
17. **#2402 planned** — build+query plan carrying forward all v1 #2393 lessons (single authority, cost-cap impl, p95-as-test, secret-safety, model-pin).
18. **Handoff** — `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` written with 5 prioritized first-actions for next session.

## Issues touched (12 total)

### Filed this session (8 new + 4 inherited statuses)

| # | Title | Final state |
|---|---|---|
| 2392 | wiki coverage-gap detector | CLOSED — blocked by #2405; carry-forward defects documented |
| 2393 | embeddings index (umbrella) | CLOSED — rescoped to #2402 + #2403 |
| 2394 | retrieval-augmented planner | CLOSED — blocked by #2405; carry-forward defects documented |
| 2395 | eCFR ingestion | CLOSED — blocked by #2405; carry-forward defects documented |
| 2396 | MCP server (umbrella) | CLOSED — rescoped to #2400 + #2401 + #2404 |
| 2400 | MCP server core (3 tools) | OPEN, awaits user scope approval |
| 2401 | MCP multi-agent registration | OPEN `status:plan-approved`, blocked on #2400 |
| 2402 | embeddings build+query | OPEN `status:plan-approved`, v1 plan drafted |
| 2403 | embeddings model-selection spike | OPEN `status:plan-approved`, v2 plan drafted |
| 2404 | MCP audit log + allowlist | OPEN, awaits user scope approval |
| 2405 | cross-review sandbox repo access (META) | OPEN `status:plan-approved`, v3 plan drafted |
| 2406 | fix Codex dispatch-stdin hang | OPEN, priority:high, blocks reliable reviews |

## Artifacts landed on `origin/main`

### Plan files (11 total — 8 new, 3 carried-across-versions)
- `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` (v3, historical)
- `docs/plans/2026-04-20-issue-2393-embeddings-index-l2-l3.md` (v1, historical)
- `docs/plans/2026-04-20-issue-2394-retrieval-augmented-planner.md` (v2, historical)
- `docs/plans/2026-04-20-issue-2395-ecfr-ingestion.md` (v2, historical)
- `docs/plans/2026-04-20-issue-2396-doc-intel-mcp-server.md` (v1, historical)
- `docs/plans/2026-04-20-issue-2402-embeddings-build-index.md` **(active v1)**
- `docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md` **(active v2)**
- `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md` **(active v3)**

### Review artifacts (21 total)
Under `scripts/review/results/`:
- 5 × Claude self-review v1 (MINOR each)
- 5 × Codex v1 (MAJOR each)
- 5 × Gemini v1 (MAJOR each)
- 3 × Codex v2 (MAJOR each — on #2392/#2394/#2395)
- 3 × Gemini v2 (MAJOR each)
- 3 × Codex v3 (MAJOR each)
- 3 × Gemini v3 (MAJOR each)
- 1 × Codex on #2405 v1 (MAJOR)
- 1 × Gemini on #2405 v1 (MAJOR)
- 1 × Codex on #2405 v2 (timeout→191-byte stub; infrastructure finding)
- 1 × Gemini on #2405 v2 (MAJOR — 4 P1 bugs)
- 1 × Codex on #2403 v1 (timeout→stub)
- 1 × Gemini on #2403 v1 (MAJOR)

### Other artifacts
- `docs/plans/_template-issue-plan.md` — updated with §Evidence subsection (2026-04-20)
- `docs/plans/README.md` — all 12 issues indexed with current status
- `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` — next-session prompt

## Commits (this session) — chronologically on `main`

```
5b4c347cd docs(plans): 5 initial doc-intel plans + Claude self-reviews
43f608f10 docs(plans): 10 iter-1 cross-review artifacts (MAJOR×10)
27821dafa docs(plans): v2 rewrites #2392/#2394/#2395 + split #2393/#2396
07c7d3250 docs(plans): iter-2 artifacts (MAJOR×6)
4226f8695 docs(plans): v3 rewrites + template §Evidence section
d66a81e87 docs(plans): iter-3 artifacts (MAJOR×6 — cap reached)
4de4294a4 docs(plans): close #2392/#2394/#2395 blocked by #2405
d067a4d51 docs(plans): #2405 plan — pre-verification attestation (v1)
11ac126b1 docs(plans): #2403 plan — embeddings model-selection spike
5c9923acf docs(plans): #2405 v2 + iter-1 artifacts
a20575ace docs(plans): #2405 v3 + #2403 v2 — Gemini iter-2/iter-1 fixes
a78b5631f docs(plans): #2402 plan — embeddings build+query
2adf4ae89 docs(handoffs): doc-intel planning session handoff 2026-04-20
```

Plus 5 auto-sync commits interspersed (provider-audit artifacts unrelated to this session).

## Structural findings (durable value beyond specific plans)

### 1. Review sandbox has no verification access (#2405)
Root cause of every iteration's convergent "unverified claims" finding. Cross-review is structurally broken until this lands. Proposed fix: pre-verification attestation script runs locally, prepends `## Attested Evidence` block to prompts.

### 2. Codex dispatcher hangs on substantial prompts (#2406)
`submit-to-codex.sh` passes prompt via argv; for ≥15K-char prompts, `codex exec` waits for stdin input and hangs. Exit 124 at both 300s and 600s timeouts. Gemini reliable throughout. Fix: pass prompt via stdin. Separate from #2405.

### 3. Template §Evidence subsection is necessary but insufficient
Catches factual errors at authoring time (e.g., eCFR rate-limit 4× over-spec was caught by evidence-gathering, not by review). But doesn't satisfy reviewers who lack repo access — that's what #2405 fixes.

### 4. Iteration cap (3/WRK) works as designed
Three of #2392/#2394/#2395 hit the cap. Each iteration caught genuinely new defects (v1 structural → v2 logic → v3 edge-case). Further iteration would have hit diminishing returns. The cap correctly escalated the structural finding (#2405) to a meta-issue instead of burning unlimited cycles.

### 5. Split-pattern beats monolithic plans
#2393 (embeddings) split into #2402+#2403 and #2396 (MCP) split into #2400+#2401+#2404 both became more tractable. Smaller scope = fewer defect surfaces = faster review convergence.

## Known gotchas for future sessions

1. **Auto-sync races:** `git push` frequently fails with "cannot lock ref". Workflow: `stash -u && pull --rebase && stash pop && push`.
2. **`data/document-index/code-registry.yaml` does NOT exist.** Real path: `data/design-codes/code-registry.yaml`. v1 #2393 had wrong path.
3. **`scripts/data/doc_intelligence/` already exists** with 30+ files. Do not claim to create.
4. **eCFR rate limit is 1,000 req/hour (≈16/min)**, not 60/min. v1/v2 #2395 had it 4× over-spec.
5. **Codex sandbox has no repo access.** Gemini-only reviews are the reliable path until #2405 + #2406 land.
6. **Plan template §Evidence subsection is mandatory** for all new plans (added at commit `4226f8695`).

## Session metrics

| Metric | Count |
|---|---|
| GitHub issues filed (new) | 12 |
| GitHub issues closed | 5 |
| Plan files drafted | 8 |
| Plan iterations (v1/v2/v3) | 20 total |
| Cross-provider review passes | 27 |
| Reviews returning MAJOR | 25 of 27 |
| Real bugs caught (defects that would have shipped) | 15+ |
| Infrastructure findings | 2 (#2405 + #2406) |
| Commits on `main` | 13 |
| GH comments posted | 20+ |

## Exit verification

- [x] All work committed on `origin/main`
- [x] HEAD matches `origin/main` (no ahead/behind)
- [x] Handoff document written and pushed
- [x] No plan-gate blockers (all commits were safe-path docs)
- [x] Cross-review iteration budget correctly accounted per issue
- [x] Carry-forward defect catalogs posted on closed-issue comments
- [x] Meta-issue #2405 filed + #2406 follow-on filed
- [x] Session exit report (this document) written

## Next session entrypoint

**Read first:** `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md`

**Default first action:** Implement #2406 (Codex dispatch stdin-hang fix). Smallest scope, unblocks reliable cross-review for everything downstream.

**If user says otherwise, alternative actions priority-ordered in handoff.**

---

*Session terminated cleanly. All state durable. Ready for exit.*
