# Overnight Claude Review — Plan #2271

> **Date:** 2026-04-16
> **Context:** Overnight planning review pass
> **Plan reviewed:** `docs/plans/2026-04-16-issue-2271-harden-shared-skill-propagation-for-engineering-portability.md`
> **Prior reviews:** None (initial draft)

## Verdict: MINOR

## Assessment

The plan provides a thorough analysis of the two existing propagation scripts and correctly identifies the key hardening gaps (dry-run reporting, skip-reason logging, placeholder detection, provider adapter validation, regression tests). The Resource Intelligence Summary is well-grounded with 8 distinct sources. The pseudocode covers both scripts comprehensively. Several minor issues need attention.

### Strengths

1. **Both propagation scripts identified and analyzed.** The plan correctly separates `sync-knowledge-work-plugins.sh` (external HTTP fetch from anthropics/knowledge-work-plugins) and `merge-submodule-skills.sh` (internal filesystem copy from submodule repos) and proposes consistent hardening for both.
2. **Dry-run YAML report schema is well-defined.** The pseudocode specifies the exact fields for the machine-readable report, making implementation straightforward.
3. **Skip-reason reporting addresses a real gap.** The existing `SKIP_DIRS` mechanism in `merge-submodule-skills.sh` is indeed silent — the plan correctly identifies this as a hardening target.
4. **Provider adapter state validation is a novel addition.** Neither script currently validates downstream state; this catch-all check prevents silent corruption.

### Issues requiring revision

1. **YAML generation in bash scripts needs a concrete mechanism decision.** The plan mentions "prefer `python3` inline" but does not commit to a specific approach. The #2269 plan explicitly pinned embedded `python3` for YAML normalization. Resolution: make the same explicit decision here — will each script shell out to `python3 -c "..."` for YAML generation, or will a shared helper script be created?

2. **The `propagation-report-template.yaml` artifact may be unnecessary overhead.** If the schema is defined in the pseudocode and validated by tests, a separate template YAML file adds maintenance burden without clear value. Resolution: consider whether the schema should live in the test fixtures or as a separate artifact, and justify the choice.

3. **Test harness architecture for bash scripts is underspecified.** The plan lists 10 tests in `test_propagation_scripts.py` but does not describe how pytest will invoke bash scripts, manage fixtures, or handle the difference between "fixture-only" and "live propagation" tests. Resolution: add a test architecture note specifying subprocess invocation, fixture directory layout, and test markers (e.g., `@pytest.mark.live_propagation`).

4. **Provider adapter state validation scope is vague.** "Check `.claude/settings.json` is valid JSON" is clear, but what constitutes valid adapter state beyond JSON parsing? Resolution: define the minimum validation contract (valid JSON + required top-level keys + no empty files).

5. **No explicit mention of rollback mechanism.** The pseudocode mentions "suggest rollback command" if validation fails, but does not specify what that command is. Resolution: define the rollback strategy (e.g., `git checkout -- .claude/skills/` to restore to pre-propagation state).

### Retrieval adequacy

- **adequate** — 8 distinct sources with specific file paths and findings. The plan inspected both propagation scripts, the portability contract, the enforcement gradient rules, and the sibling #2269 plan.

### Recommendation

**approval-ready after minor revisions** — Address the 5 items above (YAML generation mechanism, template file justification, test architecture, validation scope, rollback strategy) and the plan can advance to adversarial review.

**Execute tomorrow?** No — plan is draft status. Requires minor revisions, then adversarial review from Codex and Gemini before implementation.
