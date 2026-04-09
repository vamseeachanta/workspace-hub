# Terminal 2 — Field-Development Economics Facade (Claude)

We are in /mnt/local-analysis/workspace-hub.
Use `uv run` for all Python.
Commit to `main` and push after each completed implementation/fix cycle.
Do not branch.
TDD first. Mock external/network dependencies. Do NOT ask the user any questions.
Run `git pull origin main` before every push.

IMPORTANT: first inspect current state before coding.
1. Read the current issue body for #1858.
2. Inspect existing `field_development/` economics-related modules.
3. Inspect `worldenergydata` packages that already expose FDAS/economics/cost functionality.
4. Narrow to the missing delta only.

Do NOT write to paths owned by other terminals:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/tests/field_development/test_benchmarks.py
- worldenergydata/subseaiq/analytics/
- digitalmodel/src/digitalmodel/naval_architecture/
- scripts/ai/, config/agents/, config/ai-tools/, scripts/cron/setup-cron.sh
- notes/agent-work-queue.md, scripts/refresh-agent-work-queue.*
- docs/governance/, docs/reports/session-governance/

Only write to:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/src/digitalmodel/field_development/__init__.py
- digitalmodel/tests/field_development/test_economics.py

## TASK: Issue #1858

Create a bounded first-pass economics facade for field development that wires existing worldenergydata capabilities into digitalmodel without trying to solve the entire epic.

Minimum deliverables:
1. `economics.py` exposes a narrow facade API for:
   - economic input normalization
   - CAPEX/OPEX/ABEX estimate retrieval through adapters
   - NPV/IRR/MIRR-style evaluation through a single entry point
2. `__init__.py` exports the new public surface cleanly.
3. `test_economics.py` covers:
   - facade construction from minimal input
   - adapter selection / delegation to mocked backend calls
   - handling of unsupported fiscal regime / missing fields
4. Keep workflow wiring local to this module unless an existing import surface absolutely requires a small export change.

Suggested workflow:
1. Inspect `capex_estimator.py`, `opex_estimator.py`, and any existing field-development patterns.
2. Inspect worldenergydata economics/FDAS interfaces.
3. Write tests first using mocks/fakes.
4. Implement only the facade + adapter layer, not a large workflow engine.
5. Run targeted tests.

Required verification:
- `uv run pytest digitalmodel/tests/field_development/test_economics.py -v`

Commit message:
`feat(field-dev): add economics facade over worldenergydata backends (#1858)`

## IMPLEMENTATION CROSS-REVIEW (mandatory)

After the implementation commit is pushed:
1. Capture the committed diff:
   - `git show --stat --patch HEAD > /tmp/terminal-2-impl.diff`
2. Write `/tmp/terminal-2-review.md` with:
   - issue #1858 context
   - changed files
   - adapter risks, schema risks, and verification command
   - the exact diff
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-2-review.md)" | tee /tmp/terminal-2-codex-review.txt`
4. If MAJOR/HIGH issues are identified, fix once, commit, push, and rerun Codex review.
5. Post a brief issue comment on #1858 with implementation summary, test result, and final Codex verdict.

Stop after one review-fix iteration unless the remaining fix is trivial.
