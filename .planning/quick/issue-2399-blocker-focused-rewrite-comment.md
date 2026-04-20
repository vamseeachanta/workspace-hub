Integrated the latest Codex/Gemini blocker themes into the local #2399 draft.

New tightening changes applied in the draft:
- added explicit `.codex/CODEX.md` discoverability anchoring alongside AGENTS/CLAUDE/GEMINI/control-plane anchors
- upgraded retrieval grounding to include live harness surfaces: `config/agents/*`, `.claude/rules/*`, and `scripts/_core/sync-agent-configs.sh`
- removed reliance on the transient dependency-map report from the retrieval section
- shifted packaging toward one cohesive main review package instead of multiple parallel report artifacts
- added a fixture-backed golden-task corpus requirement under `tests/fixtures/model_release_battery/`
- tightened semantics from follow-up issue drafts toward actual created follow-up GitHub issues
- made scope stop-line explicit: this issue defines contract + fixtures + issue-creation logic, but does not build/operate the future runner

Status remains: NOT approval-ready yet.
A fresh adversarial re-review is still needed on this newest revision.
