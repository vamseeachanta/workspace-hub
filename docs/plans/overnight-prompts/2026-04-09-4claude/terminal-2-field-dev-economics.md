# Terminal 2 — field-development economics facade

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

First inspect current state:
1. Read GH issue #1858.
2. Inspect economics-related modules under `digitalmodel/src/digitalmodel/field_development/`.
3. Inspect relevant `worldenergydata` economics / FDAS interfaces.
4. Implement only the missing delta.

Do NOT write to:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`
- `worldenergydata/subseaiq/analytics/`
- `digitalmodel/src/digitalmodel/naval_architecture/`
- `digitalmodel/tests/naval_architecture/`
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.*`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Only write to:
- `digitalmodel/src/digitalmodel/field_development/economics.py`
- `digitalmodel/src/digitalmodel/field_development/__init__.py`
- `digitalmodel/tests/field_development/test_economics.py`

Task:
Create a bounded economics facade that wires existing `worldenergydata` capabilities into digitalmodel.

Minimum deliverables:
1. `economics.py` facade API for input normalization, CAPEX/OPEX/ABEX estimate retrieval via adapters, and one NPV/IRR/MIRR-style evaluation entry point.
2. `__init__.py` exports the new public surface cleanly.
3. `test_economics.py` covering facade construction, adapter delegation via mocks/fakes, and unsupported fiscal regime / missing-field handling.
4. Keep scope local to this module; do not build a broader workflow engine.

Verification:
- `uv run pytest digitalmodel/tests/field_development/test_economics.py -v`

Commit message:
- `feat(field-dev): add economics facade over worldenergydata backends (#1858)`

Mandatory review after push:
1. `git show --stat --patch HEAD > /tmp/terminal-2-impl.diff`
2. Write `/tmp/terminal-2-review.md` with issue context, changed files, verification result, and exact diff.
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-2-review.md)" | tee /tmp/terminal-2-codex-review.txt`
4. If Codex finds MAJOR/HIGH issues, fix once, commit, push, rerun review.
5. Post a brief GH issue comment on #1858 with implementation summary, test result, and final verdict.
