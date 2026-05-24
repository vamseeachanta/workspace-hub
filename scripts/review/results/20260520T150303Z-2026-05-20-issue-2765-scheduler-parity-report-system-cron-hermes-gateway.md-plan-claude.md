### Verdict: MAJOR

### Summary
The revision substantially improves on round 1 by defining logical-job mapping precedence, adding a read-only command contract, and adding unavailable/duplicate/freshness tests. However, it still has gaps in failure-mode handling, exit-code semantics, parser robustness, and explicit dependency on #2762 terms. The plan is close to approval-ready but needs targeted tightening before re-review can converge.

### Issues Found
- [P1] Read-only enforcement contract is asserted in prose and tested via monkeypatch, but there is no defined enforcement mechanism in the CLI itself (e.g., a hard-coded allowlist constant, a `subprocess` wrapper module, or refusal of any argv not in the allowlist). A monkeypatched test only proves the wrapper exists; it does not prove production code routes all subprocess calls through it. Specify the single chokepoint module/function and require all subprocess use to go through it.
- [P1] #2762 dependency is load-bearing for classification terms (`scheduler_plane`, `runtime_class`) but the plan does not pin a specific revision/SHA of #2762 nor define a fallback if #2762 lands incompatible terminology after this implementation. Either inline the term contract here, or block on #2762 reaching a frozen state.
- [P1] Logical-job mapping precedence step 2 (`known command/script basename mapping`) requires a registry of basename→logical-id mappings, but no such registry is specified as a deliverable. Without it, the precedence rule is unimplementable as written. Add the registry path (e.g., `config/cron/logical-job-aliases.yaml`) to the Files to Change table and add a test for unknown-basename fallback to step 3.
- [P2] No exit-code semantics defined. Operators running this in CI/cron need to know: does the report exit 0 when surfaces are unavailable? When duplicates are detected? When AI-bypass warnings fire? When 'blocker' state triggers? Without exit-code contract the report can't be wired to alerting.
- [P2] Parser tests use 'representative' fixtures but the plan does not capture the actual current outputs of `setup-cron.sh --dry-run`, `crontab -l`, and `hermes cron list` as committed fixture files. Round-1 finding about 'live surface proof captured before revision' should produce committed fixtures, not just a reproduction note. Add: fixtures committed under `tests/cron/fixtures/` derived from a named capture date.
- [P2] 'Unavailable is a first-class report state' is asserted but the schema for the unavailable record is not defined. What fields are populated vs null when a surface returns non-zero? Define the unavailable-row schema explicitly so downstream consumers can rely on it.
- [P2] Duplicate-warning rule conflates 'warning' and 'blocker' states without defining how the report communicates the difference (exit code? section? severity field?). The AI-bypass case escalates to blocker — surface the state machine.
- [P3] Acceptance criterion 'CLI subprocess collection is read-only by construction and test-verified' is binary-asserted; add a concrete check: e.g., grep for forbidden command tokens in the implementation file, run as a unit test.
- [P3] Test list lacks a malformed-input case: what does the parser do with truncated `hermes cron list` output, mixed line endings, or an entry whose schedule field is missing? Brittleness of human-CLI parsing is named as a risk but not tested.
- [P3] Operator docs file is listed as a deliverable but its required sections are not enumerated (interpretation matrix, unavailable-state troubleshooting, no-mutation guarantee, exit codes). Spell out the doc skeleton so the review can verify completeness post-implementation.
- [P3] Plan claims 'never call mutating scheduler commands' in pseudocode but the pseudocode itself doesn't show the allowlist gate — pseudocode and contract should be consistent.

### Suggestions
- Add a dedicated `scripts/cron/_safe_subprocess.py` (or equivalent chokepoint) with a frozen allowlist constant; require all subprocess invocations in the report CLI to import from it; add a lint test that greps the implementation for direct `subprocess.run`/`os.system` calls outside this module.
- Commit the actual captured outputs as fixtures (`tests/cron/fixtures/setup-cron-dry-run.txt`, `crontab-l.txt`, `hermes-cron-list.txt`) with a header comment naming the capture date and host. This grounds parser tests in real CLI shape, not synthesized representations.
- Define exit-code contract in plan and test it: e.g., `0` = all surfaces parity-clean, `1` = warnings (duplicates, stale, unavailable), `2` = blockers (AI bypass, parser failure), `3` = read-only contract violation attempted.
- Add a `logical_job_aliases.yaml` registry as a first-class artifact and a test that the registry is loaded and applied in step 2 of precedence; include a test for unknown basename falling through to step 3.
- Either pin #2762 to a specific issue revision/SHA, or copy the necessary scheduler-plane/runtime-class enum values inline in this plan and note 'will be reconciled with #2762 final terminology before merge.'
- Spell out the unavailable-row schema (e.g., `{surface, status: 'unavailable', reason, captured_at, command_attempted}`) and reference it in the unavailable-surface test.
- Add malformed-input parser tests for each of the three text surfaces (truncated, blank, schedule-missing).
- Enumerate the Operator docs sections in the plan (Overview, Surfaces compared, Exit codes, Unavailable troubleshooting, Read-only guarantee, Limitations) so review can confirm completeness.

### Questions for Author
- What is the single subprocess chokepoint module that production code must route through, and how is that enforced (lint test, import constraint)?
- Will logical-job basename aliases live in a committed registry file, or be hardcoded in the CLI? If the latter, how are new jobs added without code changes?
- What exit codes should the report return for each state (clean / warning / blocker / contract violation)? Is the report intended to be run by alerting/CI, or only interactively?
- Is #2762's scheduler-plane/runtime-class terminology frozen, or could it change after this plan ships? If unfrozen, what is the reconciliation plan?
- Are committed parser fixtures (real captures from current ace-linux-1 state) part of this scope, or are tests intended to use synthesized examples?
- What does the report do when `hermes cron list` returns a non-zero exit code mid-run — abort, mark Hermes surface unavailable and continue, or retry?
- Should the 'blocker' state (AI-provider duplicate across planes without documented exception) cause the CLI to exit non-zero, even though the tool is otherwise read-only/advisory?
