# Terminal 3 — naval-architecture vessel/hull integration

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

First inspect current state:
1. Read GH issue #1859.
2. Inspect `digitalmodel/src/digitalmodel/naval_architecture/` and existing tests.
3. Inspect vessel-fleet / hull-model data sources in `worldenergydata`.
4. Implement only the missing delta.

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
Build a bounded first-pass vessel/hull integration layer that makes `worldenergydata` vessel records usable by digitalmodel naval_architecture modules.

Minimum deliverables:
1. Add/extend an adapter that converts vessel records into principal dimensions expected by naval_architecture modules.
2. Add tests for record normalization, missing/partial dimensions, and one integration path into a hydrostatics/stability-facing function.
3. Add a small helper in `integration.py` or `ship_data.py` only if needed.
4. If `curves_of_form.py` needs a hook, keep it narrow and backward-compatible.
5. No full 3D hull-geometry ingestion.

Verification:
- `uv run pytest digitalmodel/tests/naval_architecture -k 'ship or vessel or dimension or stability' -v`

Commit message:
- `feat(naval-arch): wire vessel fleet dimensions into naval architecture adapters (#1859)`

Mandatory review after push:
1. `git show --stat --patch HEAD > /tmp/terminal-3-impl.diff`
2. Write `/tmp/terminal-3-review.md` with issue context, changed files, compatibility risks, verification result, and exact diff.
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-3-review.md)" | tee /tmp/terminal-3-codex-review.txt`
4. If Gemini CLI is available, run Gemini too:
   - `gemini exec "$(cat /tmp/terminal-3-review.md)" | tee /tmp/terminal-3-gemini-review.txt`
5. If reviewers find MAJOR/HIGH issues, fix once, commit, push, rerun only the reviewer(s) that found them.
6. Post a brief GH issue comment on #1859 with implementation summary, test result, and final verdicts.
