# Terminal 1 — SubseaIQ → Field-Development Benchmark Bridge (Claude)

We are in /mnt/local-analysis/workspace-hub.
Use `uv run` for all Python.
Commit to `main` and push after each completed implementation/fix cycle.
Do not branch.
TDD first. Mock external/network dependencies. Do NOT ask the user any questions.
Run `git pull origin main` before every push.

IMPORTANT: first inspect current state before coding.
1. Read the current issue body for #1861.
2. Inspect existing field-development benchmark code and any SubseaIQ analytics files.
3. Narrow to the missing delta only. Do not rewrite already-good code.

Do NOT write to paths owned by other terminals:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_economics.py
- digitalmodel/src/digitalmodel/naval_architecture/
- scripts/ai/, config/agents/, config/ai-tools/, scripts/cron/setup-cron.sh
- notes/agent-work-queue.md, scripts/refresh-agent-work-queue.*
- docs/governance/, docs/reports/session-governance/

Only write to:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/tests/field_development/test_benchmarks.py
- worldenergydata/subseaiq/analytics/ (new files only)

## TASK: Issue #1861

Build the first usable bridge from scraped SubseaIQ project data into field-development benchmark logic.

Minimum deliverables:
1. `benchmarks.py` exposes a small, testable API for:
   - loading normalized project records
   - deriving concept-selection benchmark bands
   - deriving simple subsea architecture benchmark stats
2. `test_benchmarks.py` covers:
   - concept-type aggregation by water-depth band
   - tieback/equipment summary calculations from a small fixture dataset
   - graceful handling of missing fields
3. If helpful, add one small analytics helper under `worldenergydata/subseaiq/analytics/` to normalize or summarize raw records.
4. Keep this first pass bounded: do not attempt full production cost modeling in this terminal.

Suggested workflow:
1. Inspect `digitalmodel/src/digitalmodel/field_development/` and identify existing patterns.
2. Inspect any existing SubseaIQ dataset/layout under `worldenergydata/`.
3. Write tests first.
4. Implement the narrow benchmark bridge.
5. Run only targeted tests first, then any nearby relevant tests if cheap.

Required verification:
- `uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v`

Commit message:
`feat(field-dev): add SubseaIQ benchmark bridge scaffold (#1861)`

## IMPLEMENTATION CROSS-REVIEW (mandatory)

After the implementation commit is pushed:
1. Capture the committed diff for review:
   - `git show --stat --patch HEAD > /tmp/terminal-1-impl.diff`
2. Write a self-contained review prompt to `/tmp/terminal-1-review.md` that includes:
   - issue #1861 context
   - changed files
   - the exact diff from `/tmp/terminal-1-impl.diff`
   - explicit request for adversarial review with verdict APPROVE|MINOR|MAJOR
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-1-review.md)" | tee /tmp/terminal-1-codex-review.txt`
4. If Codex returns MAJOR, or identifies clear HIGH-severity defects, fix them once, commit, push, and rerun the Codex review.
5. Post a brief issue comment on #1861 summarizing:
   - what was implemented
   - test command/result
   - final Codex verdict

Stop after one review-fix iteration unless the remaining fix is trivial.
