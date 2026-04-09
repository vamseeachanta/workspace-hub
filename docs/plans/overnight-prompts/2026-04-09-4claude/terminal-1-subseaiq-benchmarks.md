# Terminal 1 — SubseaIQ -> field-development benchmark bridge

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

First inspect current state:
1. Read GH issue #1861.
2. Inspect `digitalmodel/src/digitalmodel/field_development/`.
3. Inspect available SubseaIQ data/layout under `worldenergydata/`.
4. Implement only the missing delta.

Do NOT write to:
- `digitalmodel/src/digitalmodel/field_development/economics.py`
- `digitalmodel/src/digitalmodel/field_development/__init__.py`
- `digitalmodel/tests/field_development/test_economics.py`
- `digitalmodel/src/digitalmodel/naval_architecture/`
- `digitalmodel/tests/naval_architecture/`
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.*`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Only write to:
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py`
- `digitalmodel/tests/field_development/test_benchmarks.py`
- `worldenergydata/subseaiq/analytics/` (new files only)

Task:
Build a bounded first-pass bridge from SubseaIQ project records into field-development benchmark logic.

Minimum deliverables:
1. `benchmarks.py` with a small API for loading normalized project records and deriving concept-selection / subsea architecture benchmark stats.
2. `test_benchmarks.py` covering water-depth band aggregation, tieback/equipment summary calculations, and missing-field handling.
3. Optionally one small analytics helper under `worldenergydata/subseaiq/analytics/` if needed for normalization.
4. Keep scope bounded; no full cost-model workflow here.

Verification:
- `uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v`

Commit message:
- `feat(field-dev): add SubseaIQ benchmark bridge scaffold (#1861)`

Mandatory review after push:
1. `git show --stat --patch HEAD > /tmp/terminal-1-impl.diff`
2. Write `/tmp/terminal-1-review.md` with issue context, changed files, verification result, and exact diff.
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-1-review.md)" | tee /tmp/terminal-1-codex-review.txt`
4. If Codex finds MAJOR/HIGH issues, fix once, commit, push, rerun review.
5. Post a brief GH issue comment on #1861 with implementation summary, test result, and final verdict.
