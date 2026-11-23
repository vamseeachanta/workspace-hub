# Terminal 2 — field-development economics facade

Repo: /mnt/local-analysis/workspace-hub
Rules: use `uv run` for Python, TDD first, commit to `main`, `git pull origin main` before every push, do not branch, do not ask the user questions.

Status note:
- A prior launch of this stream produced no reliable execution artifact.
- Current evidence suggests `economics.py`, `__init__.py`, and `test_economics.py` already exist in `digitalmodel`.
- On this run, do not remain silent. Start by printing:
  - issue read: yes/no
  - files inspected: list
  - first implementation step: one sentence

Launch requirement:
- For unattended runs, pass this prompt as a command argument and close stdin with `</dev/null>`.
- If you cannot read the issue, target files, or adapters, stop and report the exact blocker immediately.
- Do not end without either implementation artifacts or an explicit blocker artifact.

First inspect current state:
1. Read GH issue #1858.
2. Inspect economics-related modules under `digitalmodel/src/digitalmodel/field_development/`.
3. Inspect relevant `worldenergydata` economics / FDAS interfaces.
4. Inspect whether broader workflow integration is still missing.
5. Implement only the missing delta.

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
- `digitalmodel/src/digitalmodel/field_development/workflow.py` only if it does not exist and is required for the still-missing delta

Task:
Create or finish the bounded economics facade work that wires existing `worldenergydata` capabilities into digitalmodel, focusing only on the still-missing delta.

Minimum deliverables:
1. Confirm the current state of `economics.py`, `__init__.py`, and `test_economics.py` before editing anything.
2. Implement only the remaining bounded facade/API or workflow-integration work.
3. Add or update targeted tests for adapter delegation, validation, and unsupported/missing inputs.
4. If the facade is already substantially present, switch to second-pass defect finding and regression-test completion instead of re-implementing it.

Verification:
- `uv run pytest digitalmodel/tests/field_development/test_economics.py -v`
- plus any one additional targeted test or command needed to prove the missing delta is now addressed

Mandatory closeout:
1. If implementation succeeds, capture `/tmp/terminal-2-impl.diff`, `/tmp/terminal-2-review.md`, and reviewer output.
2. If blocked or if the run degrades into a no-op, write `/tmp/terminal-2-blocker.md` with:
   - what was attempted
   - whether the prompt was passed as an argument with stdin closed
   - last successful observable action
   - exact blocker or failure mode
3. Post a brief GH issue comment only if new implementation or a concrete blocker was found.
