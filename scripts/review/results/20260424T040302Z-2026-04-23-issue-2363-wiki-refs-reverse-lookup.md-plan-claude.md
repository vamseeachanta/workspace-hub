### Verdict: MAJOR

### Summary
Plan is well-scoped with clear in/out-of-scope carve-outs, solid resource intel, and a comprehensive 13-case TDD list. However, several correctness-critical mechanisms (side-cache for old_keys, concurrent-write locking, cross-registry atomicity) are named in pseudocode but not specified in detail. The acceptance criteria also weaken the stated scope ("at least one L2 surface" vs. the scope's two named surfaces), and the data-PR review strategy is qualitative rather than machine-verifiable.

### Issues Found
- [P1] Side-cache for old_keys is load-bearing but unspecified. Pseudocode calls read_cached_keys_for_page() and update_cached_keys_for_page() without defining the cache's location, format, invariants, or recovery behavior when corrupt/absent. If the cache drifts from registry state, add/update/delete correctness silently breaks — and on first run (no cache) a page-update looks like pure additions, leaving stale refs orphaned.
- [P1] Concurrent-write protection is asserted but not designed. The risk section says 'emitter uses atomic write (temp + rename) and a repo-local file-lock alongside the target YAML,' but no library, lock-file naming convention, crash-recovery behavior, or cross-platform story is specified. Given both emitter and backfill can touch the same registry, this needs to be a concrete design, not a promise.
- [P2] Cross-registry atomicity gap: the emitter loops over L2_REGISTRIES and writes each with atomic_yaml_write, but a crash between the first and second registry write leaves inconsistent state. No transaction/journal/recovery strategy is described.
- [P2] Acceptance-criteria/scope mismatch: scope lists two L2 surfaces as first-wave targets, but acceptance criterion says 'At least one L2 surface ... stores wiki_refs.' Either both are required (tighten AC) or only one is (loosen scope) — otherwise reviewers cannot tell when the plan is actually 'done.'
- [P2] Data-PR review strategy is qualitative ('eyeball report counts plus YAML line-diff spot-checks'). For potentially large mutations across standards-transfer-ledger.yaml and registry.yaml, a machine check (e.g., 'every wiki_refs entry resolves to a git-tracked file and that file's frontmatter cites this doc_key') would catch defects humans will miss at line-diff scale.
- [P2] Bulk-ingest cost not addressed. llm_wiki.py ingests are sometimes batch operations; calling emit_wiki_refs() once per page rewrites L2 YAMLs N times. No batching/deferred-flush mode is specified. For marine-engineering's 19K pages this becomes O(N) full YAML rewrites per backfill run.
- [P3] Exit code 3 for 'no hits' deviates from Unix convention (0 success / 1 generic failure / 2 usage error). Shell scripts consuming this CLI may misclassify 'no hits' as a tooling error. Either adopt convention (1 = no hits) or document the deviation prominently in the runbook.
- [P3] `repo_relative(wiki_page_path)` base is not specified. Is it repo root, or the wiki root under knowledge/wikis/<domain>/? Determinism of sorted output and portability of stored paths depends on this — belongs in the spec, not left to the implementer.
- [P3] `docs/reports/wiki-refs-backfill-<date>.md` — git-tracked status not verified in resource intel. If this path is gitignored, the 'report written' acceptance criterion will silently not persist.
- [P3] `extract_canonical_doc_keys(fm)` returns a set but the wiki frontmatter convention for multi-citation pages is not stated. Is `doc_key` singular or list? Does `sources:` hold canonical sha256 values alongside slugs? Without a fixed schema reference, the extractor is under-specified.
- [P3] Domain-count drift between issue body (engineering 83) and README (engineering 77) is noted but not reconciled. If counts matter for the backfill report, pick one source of truth.

### Suggestions
- Add a 'Side-cache design' subsection: pick a concrete path (e.g., `.cache/wiki-refs/page-keys.json` or a SQLite file), define schema, document the 'cache-absent' semantics (full rescan vs. treat-as-empty), and add a test `test_emit_handles_missing_cache_on_first_run`.
- Pick a concrete locking library (portalocker recommended for cross-platform) and specify lock-file naming (`<registry>.lock`). Add a test that simulates two concurrent emitters and verifies serialized outcome.
- Add a post-write verifier: after emit_wiki_refs finishes, a small function asserts the invariant 'for every wiki_refs entry W on row R, the file at W exists and its frontmatter cites R.doc_key.' Call it from a --verify flag on the backfill tool so the data PR can be machine-checked.
- Tighten or relax acceptance criterion #4 to match scope. Recommended: require both ledger.yaml and registry.yaml populated, since both are first-wave scope.
- Add a `--batch` or deferred-flush mode to emit_wiki_refs for bulk-ingest paths; update the TDD list with a test verifying N-page ingest produces ≤ constant number of YAML writes per registry.
- Align exit codes with Unix convention: 0 success, 1 no hits, 2 usage error. Update tests accordingly.
- Add an explicit 'Path conventions' subsection stating that wiki_refs values are repo-root-relative POSIX paths, and add a test enforcing this.
- Verify `docs/reports/` is git-tracked before shipping (run `git check-ignore docs/reports/`); if not, either un-ignore or relocate the backfill report.
- Document the canonical frontmatter key(s) that hold doc_key citations (single vs. list) by referencing `knowledge/wikis/<domain>/CLAUDE.md`; add a test for each shape the extractor must accept.
- Resolve the engineering-count drift in one place (README is authoritative) and have the backfill tool recompute counts at runtime rather than relying on issue-body figures.

### Questions for Author
- Where does the per-page side-cache live, what is its schema, and what is the correctness behavior when the cache is missing, partial, or corrupt? Is a full rescan on first run acceptable?
- Which locking primitive will protect concurrent registry writes (portalocker, fcntl, flock wrapper)? What is the crash-recovery policy if a writer dies holding the lock?
- Is the first-wave scope 'both L2 surfaces populated' or 'at least one'? The scope section and acceptance criterion disagree — which is binding?
- Is `doc_key` in wiki frontmatter a single scalar, a list, or merged into `sources:`? The extractor's contract depends on this and it should be cited from the domain CLAUDE.md schema.
- For the 'doc_key present in frontmatter but no matching L2 row' case you flag as an open question, what is the expected production frequency? That governs whether 'log and skip' is safe or whether it risks hiding data drift.
- Will the emitter be called from any Git-hook context (pre-commit/pre-push) in v1, or is CLI-only the locked answer? The answer changes the locking and performance requirements materially.
- Is `docs/reports/` git-tracked in this repo? If gitignored, the backfill report will not persist and the acceptance criterion must change.
- For exit codes, is there existing tooling in `scripts/knowledge/` that already uses exit 3 = no hits (i.e., is this a project convention) or is this a new deviation from Unix convention?
