# Terminal 3 — naval-architecture vessel/hull integration

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

Status note:
- This first-pass stream is already implemented and verified.
- If reused, this prompt is for second-pass audit/hardening only, not for first-pass implementation.

First inspect current state:
1. Read GH issue #1859.
2. Inspect `digitalmodel/src/digitalmodel/naval_architecture/` and existing tests.
3. Inspect prior review output or issue comments if available.
4. Implement only a concrete missing delta if one is found.

Do NOT write to:
- `digitalmodel/src/digitalmodel/field_development/`
- `digitalmodel/tests/field_development/`
- `notes/agent-work-queue.md`
- `scripts/refresh-agent-work-queue.*`
- `scripts/workflow/`
- `tests/work-queue/`
- `docs/governance/`
- `docs/reports/session-governance/`

Only write to:
- `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`
- `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py`
- `digitalmodel/src/digitalmodel/naval_architecture/integration.py`
- `digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py`
- `digitalmodel/tests/naval_architecture/`

Task:
Run a bounded second-pass audit on the existing vessel/hull integration layer and only fix concrete residual issues.

Minimum deliverables:
1. Inspect existing implementation, tests, and prior review outputs first.
2. Only make changes for a specific defect, schema mismatch, or missing regression test.
3. Keep any follow-up backward-compatible and narrow.
4. Do not expand into broader hull-geometry or workflow work.

Verification:
- `uv run pytest digitalmodel/tests/naval_architecture -k 'ship or vessel or dimension or stability' -v`
- if a stateful/order-dependent test issue is suspected, verify with an additional targeted combined run

Mandatory closeout:
1. If code changed, capture `/tmp/terminal-3-impl.diff`, `/tmp/terminal-3-review.md`, and reviewer outputs.
2. If no changes were needed, write `/tmp/terminal-3-audit.md` with audit scope, verification result, and `no further delta required`.
3. External review is useful, but do not block closeout solely on Gemini availability or capacity issues.
