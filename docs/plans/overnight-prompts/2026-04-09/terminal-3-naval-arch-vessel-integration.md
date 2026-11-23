# Terminal 3 — Naval-Architecture Vessel/Hull Integration (Claude)

We are in /mnt/local-analysis/workspace-hub.
Use `uv run` for all Python.
Commit to `main` and push after each completed implementation/fix cycle.
Do not branch.
TDD first. Mock external/network dependencies. Do NOT ask the user any questions.
Run `git pull origin main` before every push.

IMPORTANT: first inspect current state before coding.
1. Read the current issue body for #1859.
2. Inspect the current naval_architecture modules.
3. Inspect available vessel-fleet/hull-model data sources in worldenergydata.
4. Narrow to the missing delta only.

Do NOT write to paths owned by other terminals:
- digitalmodel/src/digitalmodel/field_development/
- digitalmodel/tests/field_development/
- scripts/ai/, config/agents/, config/ai-tools/, scripts/cron/setup-cron.sh
- notes/agent-work-queue.md, scripts/refresh-agent-work-queue.*
- docs/governance/, docs/reports/session-governance/

Only write to:
- digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
- digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py
- digitalmodel/src/digitalmodel/naval_architecture/integration.py
- digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py
- digitalmodel/tests/naval_architecture/

## TASK: Issue #1859

Build a bounded first-pass vessel/hull integration layer that makes worldenergydata vessel records usable by digitalmodel naval_architecture modules.

Minimum deliverables:
1. Add or extend an adapter that converts vessel-fleet records into the principal-dimensions shape expected by naval_architecture modules.
2. Add tests under `digitalmodel/tests/naval_architecture/` for:
   - construction-vessel record normalization
   - missing/partial dimensions
   - integration path into at least one hydrostatics/stability-facing function
3. If needed, add a small helper in `integration.py` or `ship_data.py` to load/normalize records.
4. If `curves_of_form.py` needs a minimal hook for principal dimensions, keep it narrow and backward-compatible.
5. Do not attempt full 3D hull-geometry ingestion in this terminal. Keep this to principal dimensions + adapter wiring.

Suggested workflow:
1. Inspect naval architecture module APIs and existing tests.
2. Identify one stable integration point.
3. Write tests first.
4. Implement the adapter and the smallest integration hook necessary.
5. Run targeted tests.

Required verification:
- `uv run pytest digitalmodel/tests/naval_architecture -k 'ship or vessel or dimension or stability' -v`

Commit message:
`feat(naval-arch): wire vessel fleet dimensions into naval architecture adapters (#1859)`

## IMPLEMENTATION CROSS-REVIEW (mandatory)

This is architecture-heavy. Run both Codex and Gemini review if Gemini CLI is available.

After the implementation commit is pushed:
1. Capture the committed diff:
   - `git show --stat --patch HEAD > /tmp/terminal-3-impl.diff`
2. Write `/tmp/terminal-3-review.md` with:
   - issue #1859 context
   - changed files
   - backward-compatibility risks
   - verification command/result
   - the exact diff
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-3-review.md)" | tee /tmp/terminal-3-codex-review.txt`
4. If available, run Gemini review too:
   - `gemini exec "$(cat /tmp/terminal-3-review.md)" | tee /tmp/terminal-3-gemini-review.txt`
5. Fix MAJOR/HIGH findings once, commit, push, and rerun the reviewer(s) that found them.
6. Post a brief issue comment on #1859 with implementation summary, test result, and final review verdicts.

If Gemini CLI is unavailable, note that in the issue comment and proceed with Codex review only.
