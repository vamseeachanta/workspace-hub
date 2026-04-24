### Verdict: MAJOR

### Summary
Plan is well-researched, cites attested evidence, and the readiness-mismatch reconciliation (authoritative catalog = DOT/OMAE/OTC, not DOT/OMAE/ISOPE) is load-bearing and correct. However, two acceptance-critical specifications are missing or under-specified (cross-link JSONL schema and the deterministic clustering algorithm), and the runner has a brittle invariant that will break when ISOPE re-indexes. These should be resolved before execution.

### Issues Found
- [P1] Cross-link JSONL acceptance criterion references '#2068 candidate schema', but evidence block shows #2068 is OPEN. The schema may not exist yet, which creates a circular/forward dependency. Either inline the schema in this plan (as an appendix) or decouple the JSONL deliverable from this issue until #2068 lands its schema.
- [P1] `cluster_by_topic` pseudocode is elided (`...`) yet determinism is an explicit acceptance test (`test_cluster_top_n_is_deterministic`). Tokenization, stop-word set, min-df, cluster-count rule, and tie-break ordering must be pinned in the plan or the test will be ungrounded.
- [P2] Classifier precedence order `pipeline > VIV > hydrodynamics > marine > structural > subsea > misc` is asserted without rationale. A 'VIV fatigue on pipelines' paper would classify to `pipeline`, losing VIV signal. The precedence rule needs justification or the classifier should return a ranked list rather than a single winner.
- [P2] Pseudocode `assert {c.name for c in indexed} == {'DOT','OMAE','OTC'}` is brittle. When ISOPE (or any other collection) is re-indexed later, every runner invocation will abort until the code is patched. A warning-on-mismatch pattern would be more forward-compatible.
- [P2] `choose_target_wiki(domain, topic)` is called in pseudocode but the domain→target-wiki mapping table is never written down, despite the acceptance criterion constraining output to `{engineering, marine-engineering, naval-architecture}`. Without the table, the test `target_wiki_domain ∈ allowed_set` cannot be audited.
- [P2] Acceptance criterion 'Sum of classified papers == 14,180' does not specify behavior on malformed or un-classifiable records. If the runner drops a malformed row, this check silently fails; if it counts misc, no test catches silent mis-classification drift.
- [P3] The two upstream artifacts that still say `DOT/OMAE/ISOPE` (priority-queue §5.2 and staged-batch-packs §3.2) remain live in-repo and will mislead future agents. Flagging as 'optional follow-on' creates a silent-defect trap; a minimal footnote/cross-reference to the corrected set in those docs should be in-scope for this issue.
- [P3] TDD list has no error-path coverage: malformed catalog yaml, missing phase_a jsonl, empty cluster, or a collection whose `indexing_status` string is unexpected. Runner robustness is untested.
- [P3] No performance/timeout budget for the OMAE-scale slice (7,292 titles). The risk section notes the scale issue but the plan sets no measurable ceiling or CI-time budget.
- [P3] Evidence block is dated `2026-04-23` (today) but does not cite a commit SHA, so the attestation is not reproducibly re-verifiable if the repo moves.

### Suggestions
- Add a §Cross-Link JSONL Schema appendix inline (field names, types, example row) and mark it as the source of truth for this issue; note that #2068 adopts this schema rather than the reverse.
- Expand `cluster_by_topic` pseudocode with concrete determinism contract: stable sort keys, fixed stop-word list path (or embedded), min-df/max-df cutoffs, and the tie-break rule (e.g., lexical on paper_id).
- Replace the strict `assert` on `{DOT,OMAE,OTC}` with `log.warning + continue` when the set drifts, and add a test that ISOPE appearing as `phase_a_complete` in a synthetic fixture produces a WARN + deferred-list update rather than a crash.
- Add a domain→target-wiki mapping table to the plan (e.g., `pipeline → engineering`, `marine,hydrodynamics → marine-engineering`, `structural → naval-architecture`), and add a matching test that every domain maps to an allowed target.
- Spec malformed-record handling: 'malformed rows counted and emitted to a `batch-pack-2-skipped.jsonl` sibling file; acceptance sum becomes classified + skipped = 14,180' — makes drift observable.
- Add a minimal in-scope doc change that appends a one-line footnote to `llm-wiki-external-source-priority-queue.md` §5.2 and `llm-wiki-staged-batch-packs.md` §3.2 pointing readers to the corrected set in the new report. This is ~4 lines of docs and removes the silent-defect trap without re-opening closed issues.
- Add error-path tests: malformed catalog, missing jsonl, empty cluster, unknown indexing_status value, and unknown conference name.
- Add a CI-time performance budget (e.g., 'OMAE sub-slice completes in <5 min on reference machine; full run in <15 min') and a unit-level benchmark test with a generous ceiling.
- Capture the commit SHA in the evidence block (`git rev-parse HEAD` at evidence-gathering time) so the attestation block is independently re-verifiable later.
- Consider calling out which acceptance criterion each TDD test satisfies (traceability table) — helpful for the post-execution review.

### Questions for Author
- Is the `#2068` cross-link JSONL schema already drafted somewhere (a spec file, a closed sibling issue), or is this plan the first place it would be pinned down?
- When ISOPE is eventually re-indexed and becomes `phase_a_complete`, what is the expected behavior of this runner — crash (current assert), auto-include (loose set check), or require an explicit `--collections` flag? The answer determines whether the strict assert is correct.
- Are the six engineering domains (subsea, structural, marine, pipeline, VIV, hydrodynamics) a closed taxonomy you want enforced, or a seed list that can grow when the classifier finds new strong-term clusters?
- If a paper title matches both `pipeline` and `VIV`, should the output stub appear in one bucket only (current precedence), or in both with a flag? The current design silently drops the secondary signal.
- Should the in-scope doc reconciliation (footnote on the two contradicting upstream docs) be bundled into this issue, or strictly deferred? The plan flags it as 'for user decision at plan review' — this is that decision point.
- For the duplicate-check against the 19,191-page marine-engineering wiki: is there an existing `sources:`-frontmatter index the runner can read, or does the runner need to build one at startup? Runtime depends on the answer.
- Is there a precedent for how `#2364` emits its Classifier Trace that this runner should copy, or does this plan get to define the format?
