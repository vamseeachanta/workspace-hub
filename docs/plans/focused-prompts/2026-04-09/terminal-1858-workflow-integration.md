# Focused run — issue #1858 workflow integration completion

Repo to work in: /mnt/local-analysis/workspace-hub/digitalmodel
Prompt source file lives in workspace-hub, but implementation is in the nested `digitalmodel` repo.
Rules:
- use `PYTHONPATH=src uv run python -m pytest` for tests unless a narrower command is better
- commit to `main`
- `git pull origin main` before push
- do not branch
- do not ask the user questions
- print a startup checklist immediately:
  - issue read: yes/no
  - files inspected: list
  - first implementation step: one sentence

Scope:
This is NOT a fresh economics facade implementation. The facade already exists and has recent wiring for CostPredictor + DCF/carbon bridge functions. This run should only address the still-missing integration delta for #1858.

Inspect first:
1. GH issue #1858 and latest comments
2. `src/digitalmodel/field_development/economics.py`
3. `src/digitalmodel/field_development/__init__.py`
4. `tests/field_development/test_economics.py`
5. look for any existing `workflow.py` or field-development orchestration surface
6. inspect related issue references if mentioned in code/comments (#1848 / #2051 if visible)

Write boundaries:
Only write to:
- `src/digitalmodel/field_development/`
- `tests/field_development/`
- minimal related docs/reports if needed for evidence

Do NOT write to:
- `../.claude/`
- `../docs/plans/`
- unrelated digitalmodel modules
- naval architecture modules

Concrete target delta:
1. Determine the narrowest real workflow/orchestration integration missing after commit `71578748`.
2. If `workflow.py` does not exist, create the smallest useful orchestration surface needed to expose the economics facade cleanly.
3. Add targeted tests proving the workflow/integration path works.
4. Do not broaden into unrelated fiscal/ML follow-up work unless absolutely required for the integration path.

Suggested implementation shape:
- prefer a thin workflow entry point that calls the existing economics facade rather than duplicating logic
- keep API shape simple and testable
- use mocks/fakes for external adapters where needed

Verification:
- `PYTHONPATH=src uv run python -m pytest tests/field_development/test_economics.py -q`
- run any new targeted workflow tests

Mandatory closeout:
1. Capture `/tmp/issue-1858-impl.diff` and `/tmp/issue-1858-review.md`
2. Run Codex adversarial review on the committed diff
3. If blocked, write `/tmp/issue-1858-blocker.md` with exact blocker and partial progress
4. Post a brief GH issue comment on #1858 with what was implemented, verification, and what remains

Commit message:
`feat(field-dev): wire economics facade into workflow surface (#1858)`
