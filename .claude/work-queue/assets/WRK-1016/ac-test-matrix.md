# WRK-1016 Acceptance Criteria Test Matrix

| AC | Description | Test / Verification | Result |
|----|-------------|---------------------|--------|
| AC-1 | Inventory of all settings files (table: file, repo, last-modified, size) | Manual audit during Phase 1 — inventory captured in execute.yaml | PASS |
| AC-2 | Permissions audit: allow/deny lists reviewed; gaps and risks documented | Added `Bash(sudo:*)` and `Bash(chmod 777:*)` to deny list | PASS |
| AC-3 | Hooks audit: latency measured; slow hooks flagged (>2s threshold) | All hooks <2s; check-encoding.sh improved 7.272s→0.276s | PASS |
| AC-4 | Agent harness file compliance: CLAUDE.md/AGENTS.md/CODEX.md/GEMINI.md ≤20 lines | `wc -l` all 6 harness files — max 18 lines | PASS |
| AC-5 | Plugin gap analysis | All 9 official plugins already enabled; no gaps | PASS |
| AC-6 | `pyproject.toml` tool config reviewed; missing best-practice defaults proposed | OGManufacturing: added [tool.ruff] with line-length=100, target-version=py311 | PASS |
| AC-7 | ≥5 concrete improvements applied | 9 improvements applied | PASS |
| AC-8 | Changes committed and INDEX regenerated | Pending commit stage | PENDING |
| AC-9 | Comprehensive-learning Phase 10 captures canonical settings baseline | Future Work captured for comprehensive-learning | PENDING |
