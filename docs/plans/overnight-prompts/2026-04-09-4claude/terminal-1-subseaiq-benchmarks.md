# Terminal 1 — SubseaIQ -> field-development benchmark bridge

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

Status note:
- The first-pass benchmark bridge slice already exists and its targeted tests pass.
- If this prompt is used again, do not rebuild the feature from scratch.
- Treat this as a second-pass audit/hardening pass only.

First inspect current state:
1. Read GH issue #1861.
2. Inspect `digitalmodel/src/digitalmodel/field_development/benchmarks.py` and its tests.
3. Inspect any SubseaIQ normalization/helper files that already exist.
4. Implement only a concrete missing delta if one is found.

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
Run a bounded second-pass audit on the existing SubseaIQ benchmark bridge implementation.

Minimum deliverables:
1. Inspect the existing implementation and tests before making any changes.
2. Only make code changes if you find a concrete defect, missing edge-case test, or review follow-up.
3. Prefer one narrowly scoped regression test or robustness fix over any feature expansion.
4. Do not duplicate already-landed first-pass work.

Verification:
- `uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v`
- if no code change is needed, still report the verification result and audit conclusion

Mandatory closeout:
1. If code changed, capture `/tmp/terminal-1-impl.diff`, `/tmp/terminal-1-review.md`, and reviewer output.
2. If no code changes were needed, write `/tmp/terminal-1-audit.md` summarizing what was checked, verification run, and why no further delta was required.
3. Post or prepare a brief issue update only if a new delta was found.
