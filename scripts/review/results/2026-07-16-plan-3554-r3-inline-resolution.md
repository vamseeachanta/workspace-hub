# Issue 3554 r3 inline resolution

Two Codex review rounds returned MAJOR with non-overlapping findings. The main session will apply r3 inline under the workspace loop-break rule and will not dispatch a third automatic review cycle.

## r1 findings resolved

1. **Same-checkout serialization coverage:** the plan will require `test_same_checkout_concurrent_publishers_converge`, including registered-worktree, temporary-directory, and persistent Git-lock residue checks.
2. **Retry interface unspecified:** the plan will define `--max-attempts N` (default 3) and `--retry-delay-seconds N` (default 2), with invalid configuration rejected before Git mutation.
3. **HTML artifact action stale:** the file table will classify the existing HTML artifact as `Modify`.

## r2 findings resolved

1. **False multi-file Bash syntax gate:** acceptance will use three separate `bash -n` commands for publisher, cron wrapper, and collector.
2. **Review artifact path/race:** r1 will remain preserved as `...-codex-r1.md`; the completed canonical `...-codex.md` will carry r2. The zero-byte observation itself will be promoted to existing tooling issue #3537.
3. **Unsupported Control-Plane Contract claim:** the plan will narrow the citation to repository entry-point/provider-adapter boundaries and will cite scheduled-task YAML as Windows execution authority.
4. **Collector/publisher partial-read race:** scope will add same-directory temporary output plus atomic rename in `collect-equality.sh`, prior-report preservation on failure, and concurrent reader completeness tests.
5. **Undefined security scan:** acceptance will retain the exact legal scan command and remove the undefined scan phrase.

## Main-session verification

- The plan will name every affected script and test path.
- The review table will disclose Claude and Gemini as UNAVAILABLE and both Codex rounds as MAJOR-before-patch.
- No implementation file will be changed during planning.
- Implementation will remain blocked pending explicit user approval.

## Residual review risk

Only Codex supplied substantive provider review. The two rounds improved different correctness surfaces, but there is no cross-provider consensus. The user approval checkpoint must treat that diversity gap as explicit residual risk rather than inferred approval.
