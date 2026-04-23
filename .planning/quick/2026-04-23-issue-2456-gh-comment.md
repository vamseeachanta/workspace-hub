### Plan posted for #2456 — `status:plan-review`

Plan file (committed on `nightly/2454-2457-planwave` at `f2d8eac` with sibling workers' plans included via shared-index race — see provenance note below):
- `docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md`

### Scope

- Bounded to **lazy-wave only**. Steep-wave and drilling-riser explicitly deferred (no fixture in `model_library/`).
- Forward path `spec.yml → SpecToSingleConverter → compare against committed monolithic A05 YAML`.
- Introduces `SEMANTIC_DIFF_TAXONOMY.md` (doesn't currently exist; roadmap already references it) + a `semantic_diff.py` classifier + a new test module.
- Promotes the lazy-wave riser row in `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` from "Partial but high-value" → "Ready now" (spec→native YAML level, not `.sim` level — `.sim` remains #1652/#1788 scope).

### Adversarial review summary

| Provider | Round | Verdict |
|---|---|---|
| Claude | r1 | **MINOR** (with 4 follow-on blockers listed below) |
| Codex | — | **UNAVAILABLE** — sandbox permission gate blocked CLI dispatch |
| Gemini | — | **UNAVAILABLE** — sandbox permission gate blocked CLI dispatch |

Review artifacts: `scripts/review/results/2026-04-23-plan-2456-{claude,codex,gemini}.md`

### r1 Claude blockers to resolve before `status:plan-approved`

1. **Finding #1** — Converter output-key contract (PascalCase vs snake_case for `LineTypes.Name`, `OuterDiameter`, `WaterDepth`, `EndAConnection`, etc.) is not yet verified against `spec_to_single.py`. Implementation must do a field-contract discovery pass before freezing any test assertion.
2. **Finding #3** — `semantic_diff` list alignment is underspecified. Plan needs a `NAME_KEYED_LIST_PATHS` map for `LineTypes`, `Lines`, `Vessels`, `VesselTypes`, `WaveTrains`, `Constraints` so that reordered name-keyed lists are Category A rather than spuriously Category D.
3. **Finding #4** — Category B "OrcaFlex defaults" is a hand-wave. Must be converted to an explicit `ORCAFLEX_DEFAULTS` registry with fail-closed policy (unknown field → Category D until registered).
4. **Finding #6** — spec→modular forward coverage should be explicitly scoped in or out. Current plan ignores it.

Minor findings #2, #5, #7, #8, #9, #10, #11 are documented in the r1 artifact and can be addressed during implementation.

### Cross-provider gap

Codex and Gemini reviews are **UNAVAILABLE** in this batch worker session (permission gate blocked CLI dispatch — see `feedback_permission_gate_blocks_cross_review`). A true cross-provider pass from an unsandboxed session is required before this plan advances to `status:plan-approved`. Suggested next step: rerun `scripts/review/plan-review-fanout.sh docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md` from an interactive shell.

### Commit provenance note

Commit `f2d8eac` on `nightly/2454-2457-planwave` contains the plan files for #2454, #2455, and #2456 because parallel workers had staged their plans in the shared worker index when worker-3 serialized the commit (`feedback_multi_agent_commit_serialization`). The commit message names worker-3 only; the sibling plans in that commit were authored by workers 1 and 2 on their respective issues. Subsequent worker-1 update landed as `13e7ecc`. Main session should reconcile attribution (amend or per-worker cherry-pick) if this matters downstream.

### `docs/plans/README.md` not updated

Worker-3's write boundary forbids edits to `docs/plans/README.md`. The plan-index row must be added by the main overnight session or by the user at approval time (`feedback_parallel_agent_write_only_pattern`).

### Labels

Applying `status:plan-review`. Plan is not yet safe to advance to `status:plan-approved` until the 4 r1 blockers are addressed and a real cross-provider review lands.
