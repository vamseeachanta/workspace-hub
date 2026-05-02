### Verdict: APPROVE

### Summary
v3 successfully resolves Gemini r2 P1 (regex YAML patching) via the overlay-file pivot, eliminates the hyphen-path import smell with underscore filenames + conftest, and addresses all six Claude r2 P3s with concrete, testable mechanisms (atomic write, UTC ISO seconds, allow-list guard, byte-identity assertion, three-bucket counting). The design is sound, attested evidence is consistent with plan claims, and the AC + 28-test list provides strong verification. Remaining concerns are P2/P3 clarifications, not structural defects.

### Issues Found
- [P2] #2471 forward-compat fields (`code_id`, `publisher`, `revision`) are described as extracted from notes 'when extractable', but no extraction algorithm or test is specified. Risk: ambiguous behavior at runtime, fragile heuristic, or quietly-empty fields that downstream consumers (#2227, #2207) will silently miss.
- [P3] Apparent test-assertion conflict: `test_partition_dry_run_matches_23_15_2` asserts exact 23/15/2 counts, but the surrounding prose says 'if the live count differs, the runner reports the actual numbers and the AC requires the three-bucket invariant to hold.' These two statements cannot both be true under failure conditions.
- [P3] AC item 'Review artifacts for all three providers posted to scripts/review/results/' conflicts with the explicit UNAVAILABLE status for Codex due to upstream regression #2479. AC will fail-by-construction unless reworded.
- [P3] Atomic-write pseudocode (`tmp.write_bytes(...); os.replace(tmp, final)`) has no `try/finally` cleanup. If `os.replace` raises, the `.tmp` sibling lingers — the test `test_overlay_atomic_write_no_partial` asserts 'tmp file removed' but the implementation contract doesn't guarantee it.
- [P3] `partition_three_bucket` pseudocode signature doesn't show how the catalog_only bucket is identified — by hardcoded id list (`imo_gisis`, `gisis_imo_org_5db4e8`) or by running the classifier first? Ordering matters because the classifier and partitioner appear in separate steps; if hardcoded, the coupling to specific ids should be explicit.
- [P3] `source_checksum` is computed by re-serializing the entry dict through `yaml.safe_dump(sort_keys=True, default_flow_style=False)`. PyYAML emission can vary across versions (Unicode escaping, scalar style). For a stable canonical hash consider JSON-canonical (`json.dumps(sort_keys=True, ensure_ascii=False, separators=(',',':'))`) or pin PyYAML.
- [P3] `test_no_writes_outside_allow_list` description doesn't specify whether the test invokes `git diff` itself (and how) or relies on a CI-side gate. As a pytest test it must shell out; the runner-side ban on subprocess does not bind tests, but the implementation contract should be explicit.
- [P3] 30-second wall-clock budget for scanning 19,191 marine-engineering pages assumes ~1.5 ms/file end-to-end (open + read first 30 lines + line-prefix check). On cold cache or networked filesystems this is tight; the budget rationale isn't shown.

### Suggestions
- For #2471 forward-compat fields, either specify the extraction approach (e.g., 'absent unless a leading `DNV-OS-XXXX` token appears in notes — single regex `\b([A-Z]{2,4}-[A-Z]{1,3}-[A-Z0-9]+)\b`') with a dedicated test, or explicitly defer all three fields to a follow-up issue and remove the optional schema rows.
- Rename `test_partition_dry_run_matches_23_15_2` to `test_partition_dry_run_documents_v3_split` and either decorate it `@pytest.mark.dry_run_baseline` (informational) or assert only the invariant + a `WARN`-level mismatch log when actuals differ.
- Soften the review-artifacts AC to 'review artifacts for all available providers (Claude + Gemini at minimum; Codex contingent on #2479 resolution)'.
- Wrap the overlay write in `try: tmp.write_bytes(payload); os.replace(tmp, final); finally: tmp.unlink(missing_ok=True)` and add this to the Generator contract pseudocode.
- Make the catalog_only mechanism explicit in pseudocode: either pass `CATALOG_ONLY_IDS = {'imo_gisis', 'gisis_imo_org_5db4e8'}` into `partition_three_bucket`, or partition AFTER classification (which would also let the partitioner derive maritime-law from `classify_domain` rather than a hardcoded id set).
- Replace per-entry-block `yaml.safe_dump`-then-sha256 with JSON-canonical encoding for `source_checksum` to remove PyYAML version sensitivity. Keep YAML for the overlay file itself.
- Add a one-line implementation note for `test_no_writes_outside_allow_list`: 'invokes `subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], check=True, text=True)` from the test (subprocess ban applies only to runner module).'
- Consider adding `time.perf_counter` instrumentation to the duplicate-check loop and emit a wall-clock summary in the report header — gives ground truth on the 30-s budget without requiring `RUN_PERF_TESTS=1`.

### Questions for Author
- How are `code_id`, `publisher`, and `revision` extracted from free-text notes? Regex? Manual id→fields map? Or fully deferred to a follow-up?
- Is `test_partition_dry_run_matches_23_15_2` intended as a hard assertion (failing CI when actuals drift from 23/15/2) or as informational baseline documentation?
- When `os.replace` fails mid-overlay-write, where does cleanup of the `.tmp` sibling happen? The test asserts removal but the contract pseudocode doesn't show it.
- Has the 30-s duplicate-check budget been validated empirically against the live 19,191-page marine-engineering wiki (cold cache), or is it an estimate?
- Does the catalog_only bucket (`imo_gisis`, `gisis_imo_org_5db4e8`) come from a hardcoded id allow-list or from running `classify_domain` and routing `maritime-law` results? The pseudocode is ambiguous on which runs first.
- Given Codex is UNAVAILABLE for v3 per #2479, is the v3 review fanout proceeding with Claude + Gemini only, and does that satisfy the project cross-review policy, or does cross-review need an explicit waiver?
