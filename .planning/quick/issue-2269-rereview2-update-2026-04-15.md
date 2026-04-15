Wave 2 rereview update for #2269:

New rereview artifacts
- `scripts/review/results/2026-04-15-plan-2269-codex-rereview2.md`
- `scripts/review/results/2026-04-15-plan-2269-claude-rereview2.md`
- `scripts/review/results/2026-04-15-plan-2269-gemini-rereview2.md`

Current rereview result
- Claude improved to MINOR
- Codex remains MAJOR
- Gemini remains MAJOR
- plan is still not approval-ready

What tightened in this patch wave
1. explicit both-paths-exist bootstrap policy plus version-mismatch guard
2. exact fork/version verification mechanism: `foamVersion` + `$WM_PROJECT_DIR`
3. explicit YAML handoff mechanism: wrapper uses embedded Python normalization, not bash-native YAML editing
4. typed `tutorials` schema and enum constraints
5. explicit pytest strategy, including `OPENFOAM_BASHRC_PATHS` override and `@pytest.mark.openfoam`
6. explicit benchmark trigger and `damBreak` clarification
7. Risks/Decisions split cleaned up

Net
- #2269 is improving, but still in needs-revision state.
- Main remaining blockers are around final runtime-truth pinning and fully deterministic schema/test mechanics from the Codex/Gemini lanes.
