# Issue #2269 plan rewrite report — v1 → v2

**Plan:** `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
**Self-review:** `scripts/review/results/2026-04-21-plan-2269-claude-rev-2.md`
**Status transition:** `status:plan-approved` (2026-04-15) → rolled back to `status:plan-review` (2026-04-21) → awaiting cross-provider v2 review

## What changed (v1 → v2)

### 1. `python3` → `uv run python` (Codex MAJOR #1)
- **Pseudocode**: replaced "embedded Python via `python3`" with "`uv run python` (never `python3`)".
- **§Files to Change**: wrapper update explicitly "replace `python3` fallback with `uv run python` (fail fast if `uv` missing)".
- **§Acceptance Criteria**: new criterion — "uses `uv run python` for all Python embedding; **no `python3` fallback**; fails fast with `uv-missing` error if `uv` is absent".
- **§TDD Test List**: added `test_verify_script_fails_fast_when_uv_missing`.
- **§Decisions**: first decision entry = "Python invocation on Linux = `uv run python` only; no `python3` fallback. Per `AGENTS.md:14` + `.claude/memory/context.md:13-16`."
- **§Standards table**: new row citing `AGENTS.md:14` and `.claude/memory/context.md:13-16` as the normative Python-invocation sources.

Plan now matches the repo hard gate verified in `AGENTS.md:14`: "Python: `uv run` always — never bare `python3`".

### 2. Unverified bootstrap path (Codex MAJOR #2)
- **§Resource Intelligence**: new subsection "Bootstrap-path evidence (verified 2026-04-21)" that cites exact file/line evidence for each path (`run-openfoam-tutorials.sh:10`, `docs/research/openfoam-tutorials.md:27,43,95,132,175`) and records host probe status ("NOT verified on dev-secondary for v2; OpenFOAM not installed on ace-linux-1").
- **§Decisions**: reframed from "permanent supported bootstrap baseline" to "two-path **supported fallback list** … with the **attested primary** recorded at implementation time via live probe on dev-secondary".
- **§Acceptance Criteria #1** (new first AC): implementation commit must include an attested `ls` probe on dev-secondary showing which path actually exists; workflow doc §Prerequisites records the attested primary.
- Plan explicitly distinguishes "attested host reality" from "supported fallback policy", matching Codex's suggestion verbatim.

### 3. Wrapper/runner ambiguity (Codex MAJOR #3)
- **New §Wrapper/Runner Contract section** (six responsibilities for wrapper, five for runner, plus a handoff envelope table).
- **Single-owner rule**: wrapper exclusively owns bootstrap resolution, env sourcing, fork/version verification. Runner honors `--skip-bootstrap` and never self-sources when invoked by the wrapper.
- **Explicit `--skip-bootstrap` flag** added to runner CLI; wrapper ALWAYS invokes the runner with this flag.
- **New test**: `test_runner_skip_bootstrap_does_not_source_bashrc`.
- **§Files to Change**: runner update now says "add `--skip-bootstrap` flag; make self-sourcing conditional and deprecated-warned".
- **Handoff envelope table** pins every environment variable crossing the wrapper/runner boundary.

### 4. Other v2 improvements
- **§Adversarial Review History** reformatted as a wave table (six rows: v1-wave1 Claude/Codex/Gemini, v1-final, v1-rollback Codex/Gemini) + explicit v2 revision rationale section mapping each MAJOR to the concrete fix applied.
- **§Resource Intelligence** acknowledges the v1-landed wrapper scaffold already on disk and flags its current `python3` fallback as non-compliant (implementation must edit in place).
- **§Risks** adds two new entries: `uv` must be present on dev-secondary; live host probe may require operator access.
- **Gemini MINOR** (PyYAML availability) acknowledged in review history with a concrete mitigation (workflow doc troubleshooting + PyYAML treated as a `uv` dep).

## Claude v2 self-review verdict

**MINOR** — approve with minor inline tightening. All three Codex v1-rollback MAJORs resolved at the plan level via concrete mechanisms (not prose). Gemini's PyYAML minor acknowledged with a mitigation path.

Residual MINORs flagged in self-review:
1. `uv`-absence test fixture mechanism not pinned (monkeypatch `PATH`? env override? backdoor risk?).
2. Attested-path prerequisite has no defined exit if operator access to dev-secondary is blocked.
3. On-disk wrapper still contains the non-compliant `python3` fallback until implementation PR lands — creates a plan-vs-state contradiction window.
4. `uv run python` + heredoc stderr interactions (first-run chatter) not pinned; could leak into failure verdict `error_message`.

None are blocking for the next review cycle. Self-review caveat: same-author review carries lower weight than cross-provider review.

## New risks introduced by v2

- **`uv`-hard-dependency risk**: wrapper now fails fast if `uv` absent, with no fallback. If dev-secondary ever loses `uv` (e.g., system reinstall before `uv` is reprovisioned), the validator is inoperable. `config/workstations/registry.yaml:41` lists `uv` in dev-secondary tools, but this is now a runtime hard dependency rather than a soft preference. Workflow doc troubleshooting must document the recovery path.
- **`--skip-bootstrap` runner contract drift risk**: if someone later invokes `run-openfoam-tutorials.sh` standalone without `--skip-bootstrap`, the runner falls back to legacy self-sourcing behavior. This is intentional (backward-compat) but creates two execution paths the test harness must cover. `test_runner_skip_bootstrap_does_not_source_bashrc` covers the wrapper path; a companion test for the legacy standalone path is out of scope for this issue but worth a follow-up.
- **Attested-path prerequisite blocking risk**: if the implementation agent lacks shell access to dev-secondary at the moment of PR preparation, the hard requirement for an attested `ls` probe can block merge. Mitigation: pre-coordinate probe with operator, or allow a TBD-marked primary with a follow-up attestation issue (self-review recommended this).
- **Plan-vs-state contradiction window**: between now and implementation PR landing, the on-disk wrapper (`scripts/openfoam/verify-openfoam-baseline.sh:12-16`) contains the `python3` fallback that v2 forbids. Any automated plan-vs-state attestation check (per feedback_attestation_enables_contradiction_detection) would flag this. Expected resolution: implementation PR lands soon after v2 plan approval.

## Process notes

- Main session serializes commit/push; this agent wrote only plan + review + rewrite-report files. No commit, no push, no label change.
- Cross-provider review (Codex + Gemini fresh passes on v2) is the authoritative gate before `status:plan-approved` re-application. Self-review is not a substitute.
- Plan status reset from `plan-approved` to `plan-review` in the plan header; the GitHub label transition is user-owned.

## Word count
Approximately 890 words (well under 1500 cap).
