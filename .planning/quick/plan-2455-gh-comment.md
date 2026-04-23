## Plan drafted for #2455 — adversarial review complete (MINOR)

**Plan:** `docs/plans/2026-04-23-issue-2455-rigid-jumper-plet-to-plem-semantic-proof.md` (intended canonical path on `nightly/2454-2457-planwave`)
**Plan draft location (this worker):** `.planning/quick/plan-2455-draft.md` on `integration/runbook-main-compatible` (see "Landing-path note" below)
**Review artifact:** `scripts/review/results/2026-04-23-plan-2455-claude.md`
**Complexity:** T3

### What the plan delivers

A committed PLET-to-PLEM rigid jumper semantic-equivalence harness in `digitalmodel/`:
- trimmed non-proprietary fixture `spec.yml` + expected-native snapshot under `tests/fixtures/orcaflex/jumper/plet_to_plem_proof/`
- `solvers/orcaflex/modular_generator/semantic_diff.py` classifier with five taxonomy categories (IGNORABLE / ALLOWED / NORMALIZED / REFERENCE_SAFE / BLOCKING)
- pytest suite `tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py` covering three LineTypes, coating + buoyancy + strake layers, OCS 200-V connector, PLET/PLEM constraints, 17-segment PreBendCurvature M-profile, stage durations, and positive/negative classifier controls
- CLI driver `scripts/validation/jumper_plet_to_plem_semantic_diff.py` with `0`/`2` exit codes
- new `docs/standards/SEMANTIC_DIFF_TAXONOMY.md` (closes the roadmap's dangling reference at line 40 of `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`)
- roadmap readiness promotion: PLET-to-PLEM rigid jumper from "Partial but high-value" → "Ready now"

### Resource intelligence (verified 2026-04-23T09:04:40Z)

- **Roadmap anchor:** `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` line 118 lists PLET-to-PLEM in Partial readiness; lines 8-10 define the forward-contract scope; line 40 cites `SEMANTIC_DIFF_TAXONOMY.md` which does not yet exist in the tree.
- **Existing template input:** `digitalmodel/docs/domains/orcaflex/library/templates/jumper_rigid_subsea/spec.yml` (492 lines) — three LineTypes `10.75"Jumper_wCoat`, `..._wBuoy`, `..._wStrake` with 17 PreBend segments.
- **Existing monolithic reference:** `digitalmodel/docs/domains/orcaflex/jumper/plet_to_plem/monolithic/SZ.yml` (21 409 lines) + `DZ_AHCoff.yml` (21 557 lines) per #1905.
- **Existing generic roundtrip test:** `digitalmodel/tests/solvers/orcaflex/modular_generator/test_semantic_roundtrip.py` (6DBuoy / current / cross-ref / booleans) — no jumper family case.
- **Existing reporting-only fixture:** `digitalmodel/tests/fixtures/reporting/jumper_plet_plem.metadata.json` — bounded 9-object / 1200 m; does NOT prove generator fidelity at 1996 m.
- **Existing forward pipeline:** `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/{extractor.py,schema.py,cli.py,post_validator.py,sections.py,__main__.py}` + full `format_converter/` bidirectional pivot.

### Adversarial review summary

| Provider | Verdict | Notes |
|---|---|---|
| Claude (single-author) | **MINOR** | 10 findings, all tightenings — none block implementation |
| Codex | *deferred* | Planning-session sandbox prevents `codex exec` dispatch and Codex requires the artifact pushed to GitHub first (per prior incident memory). |
| Gemini | *deferred* | Same planning-session provenance constraint. |

Single-author Claude review with transparent provenance — see `scripts/review/results/2026-04-23-plan-2455-claude.md` for full findings.

**Top MINOR findings worth folding into the implementation PR:**
1. Fixture-size ceiling in Acceptance Criteria (≤ 2 000 lines) is 4× the demonstrated template size (492); tighten to ≤ 700 lines.
2. Test name `test_OCS_200V_collet_linetype_ea_te_per_m` mismatches its expected-output unit (mass-per-length, not EA); rename.
3. Floating-point tolerance for `PreBendCurvaturex/y` assertions is unstated — specify `math.isclose` bounds or prove bytewise preservation.
4. `expected_native.snapshot.yml` needs an explicit regeneration procedure so legitimate generator refactors have a documented audit trail.
5. `docs/standards/SEMANTIC_DIFF_TAXONOMY.md` acceptance is partially circular — plan should pre-commit at least one worked example per category so the taxonomy is not self-scored.
6. CLI invocation syntax (`uv run python -m ...` vs direct) needs one canonical form — `scripts/` are not installed as a package by default.
7. Proprietary-content scrub is token-denylist-only — extend to an explicit allowlist or author the fixture by hand from the template.
8. Cross-reference resolution in `classify_diff` should be section-scoped (mirrors `post_validator.py` semantics) to avoid flat-namespace collisions.
9. `spec_upgrader.py` exclusion is correct but the plan should add a defensive test asserting the pinned entry path does NOT invoke the upgrader.
10. `taxonomy_rules[structure_type]` indirection has only `jumper` defined — specify behavior on unknown `structure_type` (strict equality default or ValueError).

### Landing-path note (governance transparency)

This worker (worker-2) operates in session sandbox `/mnt/local-analysis/workspace-hub` and could not physically write the plan file to the assigned worktree at `/mnt/local-analysis/worktrees/ws-2454-2457-planwave/docs/plans/...`. Concurrent sibling worker-1 (issue #2454) advanced the worktree branch from `0e9d61159` → `f2d8eac12` during this session; a git-plumbing stage attempt collided with that commit.

Outcomes:
- **Plan draft:** fully authored at `/mnt/local-analysis/workspace-hub/.planning/quick/plan-2455-draft.md` (311 lines) — re-attach / `cp` into the worktree before merging to main.
- **Review artifact:** at `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-23-plan-2455-claude.md` — on `integration/runbook-main-compatible`, not yet on the target branch.
- **Codex / Gemini review:** deferred to a non-sandboxed session because the canonical plan file is not yet visible on the target branch (Codex sandbox requires a GitHub-visible artifact per prior incident).

### Label decision

Applying `status:plan-review` because the plan content itself is approval-ready by the MINOR verdict. The landing-path gap is an infrastructure handoff for the main session, not a plan-content defect — it does not change whether the user should review the plan now.

**However:** the user should decide whether a single-author Claude review is sufficient to advance to `status:plan-approved`, or whether Codex+Gemini cross-review should run first from a non-sandboxed session. The memory-noted policy (`project_cross_review_policy.md`) implies cross-provider coverage is the default gate.

### Related work

- Parent roadmap: #1572
- Jumper data/catalog: #1905
- Forward-fidelity Priority 1 cluster: #1652, #1788
- Solver queue hardening (Priority 2): #1586
