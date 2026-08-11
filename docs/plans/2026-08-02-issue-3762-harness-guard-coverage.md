# Plan for #3762: Both context guards are name-based and miss the 20KB file that actually auto-loads

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-08-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3762
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-02-plan-3762-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

Issue class: **Harness/Infrastructure** — bundle requires `.claude/rules/`, `config/agents/` settings, CONTROL_PLANE_CONTRACT.md.

### Existing repo code

- Found: `scripts/cron/nightly-readiness.sh` `check_r5()` — sums a hardcoded three-element `candidates` array (`AGENTS.md`, `.claude/rules/coding-style.md`, `.claude/rules/patterns.md`) against a 16 KB cap.
- Found: `scripts/enforcement/check-harness-file-size.sh:63` — `git ls-files` glob over the literal names `CLAUDE.md`, `MEMORY.md`, `AGENTS.md`, `GEMINI.md` (plus `**/` variants), `MAX_LINES=20`.
- Found: `scripts/agents/build-soul-runtime.sh` — concatenates `config/agents/SHARED_SOUL.md` + a per-provider delta into six committed `*.runtime.md` artifacts.
- Found: `scripts/agents/install-soul-runtime.sh` — installs the machine-level symlinks; sole enforcement point for auto-load wiring (no CI runner has `~/.claude`).
- Found: `scripts/enforcement/check-soul-runtime-drift.sh` — rebuilds each artifact from sources and diffs against the committed copy. Currently reports `DRIFT` for `codex/AGENTS.runtime.md`.
- Found: `tests/enforcement/test_soul_auto_load.py` — 6 tests; 2 currently failing.
- Gap: no guard resolves harness surfaces by role. Every guard enumerates filenames.
- Gap: no workflow executes `tests/enforcement/test_soul_auto_load.py` or `check-soul-runtime-drift.sh`.

### Standards

Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — this plan touches no wiki content (`Client: N/A`).

### Documents consulted

- `.claude/rules/coding-style.md` — declares AGENTS.md/MEMORY.md/GEMINI.md capped at 20 lines and documents the symlink as the intended Claude auto-load path. Names `check-harness-file-size.sh` as the enforcer.
- `.claude/rules/patterns.md` — enforcement gradient (0 prose → 1 micro-skill → 2 script → 3 hook). This plan will move harness-surface coverage from Level 0/2-partial to Level 2-complete plus CI.
- Issue #3744 — prior instance of the identical root cause: four rules files were deleted and every reference survived; R5 summed 3 of 7 files and passed by counting nothing. The fix added a missing-candidate FAIL but did not address never-was-a-candidate.
- Issue #3743 / PR #3742 / PR #3749 — the CLAUDE.md retirement and the symlink restoration that created the coverage gap.
- PR #3761 §3 — six catalogued instances of "a check whose name describes a property it does not discriminate," the defect class this plan addresses in the enforcement layer.

### Gaps identified

- No role-based registry of harness surfaces exists; one will be created.
- No CI job observes harness runtime drift; one will be added.
- No test asserts that a newly added harness surface is covered by a guard; one will be added.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-02 via `gh issue view`):
- `#3762` — OPEN — fix(harness): both context guards are name-based and miss the 20KB file that actually auto-loads
- `#3744` — referenced as prior art for the same root cause
- `#3743` — referenced; CLAUDE.md retirement tracking issue

**File existence** (`ls -la` / `wc` 2026-08-02, at `7701d4e78`):
- EXISTS: `AGENTS.md` — 20 lines, 2,658 bytes
- EXISTS: `config/agents/SHARED_SOUL.md` — 115 lines, 15,019 bytes
- EXISTS: `config/agents/claude/SOUL.runtime.md` — 182 lines, 20,011 bytes
- EXISTS: `config/agents/codex/AGENTS.runtime.md` — 277 lines, 28,198 bytes
- EXISTS: `config/agents/{agy,gemini,hermes}/SOUL.runtime.md` — 150 / 166 / 187 lines
- EXISTS: `~/.claude/CLAUDE.md` → `config/agents/claude/SOUL.runtime.md` (symlink, verified via `ls -la`)
- MISSING (retired 2026-08-01): `CLAUDE.md` at repo root

**Line excerpts** (`grep -n scripts/enforcement/check-harness-file-size.sh`):
```
28:MAX_LINES=20
63:    git ls-files 'CLAUDE.md' 'MEMORY.md' 'AGENTS.md' 'GEMINI.md' \
64:                 '**/CLAUDE.md' '**/MEMORY.md' '**/AGENTS.md' '**/GEMINI.md' \
```

**Line excerpts** (`grep -n scripts/cron/nightly-readiness.sh`):
```
73:  local candidates=(
74:    "${WORKSPACE_HUB}/AGENTS.md"
75:    "${WORKSPACE_HUB}/.claude/rules/coding-style.md"
76:    "${WORKSPACE_HUB}/.claude/rules/patterns.md"
77:  )
```

**Gap proofs:**
```
$ grep -rn 'test_soul_auto_load\|check-soul-runtime-drift' .github/workflows/
(no output) → confirms neither is wired into CI
```

**Reproduction proofs** (verify-against-repo-state):

```
$ uv run --with pytest pytest tests/enforcement/test_soul_auto_load.py -q
FAILED tests/enforcement/test_soul_auto_load.py::test_claude_md_has_autoload_directive
FAILED tests/enforcement/test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state
2 failed, 4 passed in 1.14s
```

```
$ bash scripts/enforcement/check-soul-runtime-drift.sh
OK     hermes/SOUL.runtime.md
OK     claude/SOUL.runtime.md
OK     codex/SOUL.runtime.md
DRIFT  codex/AGENTS.runtime.md — committed artifact differs from rebuilt sources
-CLAUDE.md is retired in this repo (2026-08-01) — do not reintroduce one. ...
+CLAUDE.md is retired **as a repo file** (2026-08-01) — do not reintroduce one. ...
+Claude's auto-load is a machine-level **symlink** ... Never replace that link with a regular file ...
```

- Reproduced at: 2026-08-02, working tree clean at `7701d4e78`
- Failure mode observed matches issue claim: **YES**, and exceeds it — the issue alleged missing coverage; reproduction additionally found a live red and a drifted artifact.

Distinct sources consulted: 9 (issue body, 5 scripts, 1 test file, 2 rules files, 3 prior issues).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-02-issue-3762-harness-guard-coverage.md` |
| Surface registry (new) | `config/agents/harness-surfaces.yaml` |
| Tests — registry coverage (new) | `tests/enforcement/test_harness_surface_coverage.py` |
| Tests — auto-load (modify) | `tests/enforcement/test_soul_auto_load.py` |
| Guard — size cap (modify) | `scripts/enforcement/check-harness-file-size.sh` |
| Guard — R5 budget (modify) | `scripts/cron/nightly-readiness.sh` |
| CI job (modify) | `.github/workflows/enforcement-gate.yml` |
| Plan review — Claude | `scripts/review/results/2026-08-02-plan-3762-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-02-plan-3762-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-08-02-plan-3762-agy.md` |

---

## Deliverable

Harness-surface coverage derived from the generator and the installer rather than from hardcoded
filename lists, wired into CI, with the pre-existing red test and the drifted Codex artifact
repaired first — so that a future harness file cannot lose guard coverage by being renamed, and
the reported context budget describes a session that actually runs.

---

## Pseudocode

Revised after r1 review — the first draft anchored completeness to a filename glob, summed a
cross-provider total no session loads, and let a hand-edited boolean remove a surface from the
budget. All three are corrected below.

`config/agents/harness-surfaces.yaml` — the registry both guards will consume. It carries
**roles and caps**, never membership: membership is derived.

```
providers:
  claude:
    installs: ~/.claude/CLAUDE.md          # parsed from install-soul-runtime.sh, not retyped
  codex:
    installs: ~/.codex/AGENTS.md
  ...
shared:
  - path: AGENTS.md              role: canonical-contract   line_cap: 20
  - path: .claude/rules/coding-style.md   role: rule        line_cap: null
  - path: .claude/rules/patterns.md       role: rule        line_cap: null
```

Guard logic. Two derivations replace the two hand-authored lists the first draft would have
introduced:

```
function generated_artifacts():
    # Anchored to the GENERATOR, not to a filename pattern. build-soul-runtime.sh
    # knows every artifact it emits because it writes them; a rename changes the
    # generator too, so coverage cannot be lost by renaming a file.
    return output paths declared by scripts/agents/build-soul-runtime.sh

function loaded_surface(provider):
    # Anchored to the INSTALLER. A surface counts toward a provider's budget iff
    # that provider's install path resolves to it. No declared exemption flag
    # exists to be flipped.
    return resolve(install-soul-runtime.sh install path for provider)

function check_registry_complete():
    FAIL if any generated_artifacts() path is absent from the registry
    FAIL if any registry path does not exist on disk    # per #3744: missing fails, never skips

function check_size_cap():
    for surface where line_cap is not null:
        FAIL if wc -l > line_cap

function check_budget(provider):
    # PER PROVIDER. Summing all six artifacts describes no session that has ever run.
    total = bytes(AGENTS.md) + bytes(shared rules) + bytes(loaded_surface(provider))
    report total against the cap, labelled with the provider
```

**RETRACTED after r2.** The first revision ended here with: *"A future surface that escapes both is
a surface that is neither generated nor installed — and therefore is not loaded."* That is false.
A surface can be loaded by runtime convention, plugin/skill bootstrap, repo instructions, or a
future agent boot path without passing through either script — and this plan's own Artifact Map
lists rules files and a workflow that are not generated artifacts. Deriving from two scripts is
rename-proof for files that still flow through those two scripts. It is not role-proof for harness
surfaces as a category, which is what the issue is about.

The corrected model: an explicit **auto-load taxonomy**, where every category must name an
enumerator, and a category with no enumerator is a hard failure rather than an empty set.

```
categories:                     enumerator
  generated runtime artifacts   build-soul-runtime.sh output list
  installer targets             install-soul-runtime.sh install paths
  repo-level auto-load          AGENTS.md + the rules it cites, resolved by parsing it
  provider memory runtimes      config/agents/*/MEMORY.runtime.md   (r2 F4 — was missing)
  inlined shared rules          the set AGENTS.md/runtime actually inlines
  provider bootstrap/skills     TO BE DETERMINED — see Open Questions

function check_taxonomy_complete():
    FAIL if any declared category has no enumerator          # empty set != satisfied
    FAIL if any enumerated path is absent from disk          # per #3744
    FAIL if any enumerated path is absent from the registry
```

The `shared:` block is likewise no longer hand-listed membership (r2 F2): it is enumerated by
parsing what `AGENTS.md` and the runtime artifacts actually cite, so deleting a rule from the
registry cannot remove it from the budget.

`check_budget(provider)` sums **every category** for that provider, not `AGENTS.md + shared rules +
one runtime artifact`. The budget scope is stated explicitly below because r2 showed the plan had
never defined it.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/enforcement/test_soul_auto_load.py` | Phase A — retarget the retired-CLAUDE.md assertion at the symlink mechanism |
| Modify | `config/agents/codex/AGENTS.runtime.md` | Phase A — rebuild via `build-soul-runtime.sh`; never hand-edit |
| Modify | `.github/workflows/enforcement-gate.yml` | Phase A — add a Harness Runtime Drift Guard job |
| Create | `config/agents/harness-surfaces.yaml` | Phase B — role-based registry |
| Create | `tests/enforcement/test_harness_surface_coverage.py` | Phase B — TDD suite for registry + both guards |
| Modify | `scripts/enforcement/check-harness-file-size.sh` | Phase B — read the registry instead of the filename glob |
| Modify | `scripts/cron/nightly-readiness.sh` | Phase B — `check_r5` reads the registry; report the true total |
| Update | `.claude/rules/coding-style.md` | Phase B — point the harness-file-size sentence at the registry |
| Create | `.claude/rules/` addition | Phase B — promote the two generalizable r1 findings (see Review Summary) |
| Update | `docs/plans/README.md` | index this plan |

**Out of scope, deliberately:** `config/agents/SHARED_SOUL.md` is not trimmed by this plan. Per r1
Finding 5 the trim has no falsifiable acceptance criterion until a per-provider budget target
exists, and it is a content decision for the owner rather than a coverage fix. It will be filed
separately once Phase B reports the true per-provider figures.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_declared_autoload_target_is_the_runtime_artifact` | wiring asserted by parsing `install-soul-runtime.sh` — hermetic, runs on a CI runner with no `~/.claude` | installer source | declared target is `config/agents/claude/SOUL.runtime.md` |
| `test_repo_root_claude_md_absent` | the retirement is asserted positively, not by a dangling reference | repo state | no `CLAUDE.md` at repo root |
| `test_live_symlink_reports_unavailable_off_host` | an absent `~/.claude` reports UNAVAILABLE, never PASS and never a silent skip | runner with no `~/.claude` | explicit UNAVAILABLE status |
| `test_registry_covers_every_generator_output` | coverage anchored to the generator, not a filename pattern | output list from `build-soul-runtime.sh` | every emitted path present in the registry |
| `test_renamed_artifact_still_covered` | a rename cannot drop coverage (the Finding-1 defect) | generator emitting a renamed path | coverage test fails until the registry is updated |
| `test_registry_entry_with_missing_file_fails` | absence fails, never skips (the #3744 lesson) | registry naming a nonexistent path | non-zero exit |
| `test_size_cap_flags_an_over_cap_surface` | the cap discriminates | surface with `line_cap: 20` at 21 lines | non-zero exit |
| `test_budget_is_per_provider_not_summed` | the reported figure describes a real session | registry with 6 artifacts | claude total excludes codex's artifact |
| `test_budget_includes_the_installed_surface` | the budget counts what the installer actually links | installer resolving to a runtime artifact | total ≥ that artifact's size |
| `test_budget_membership_has_no_declared_override` | no hand-editable flag can exempt a surface (Finding 3) | registry with a spurious exemption key | key is ignored or rejected |
| `test_budget_fails_when_an_installed_surface_is_missing` | preserves the #3744 fix | budgeted path deleted | FAIL, not a smaller total |
| `test_drift_check_returns_zero_on_clean_tree` | Phase A repair holds | rebuilt artifacts committed | exit 0 |

Each guard test will be **mutation-verified**: break the guard, confirm the test goes red. A test that still passes with the behaviour removed will be rewritten (`feedback_tests_that_pin_a_name_not_a_property`).

---

## Acceptance Criteria

- [ ] `uv run --with pytest pytest tests/enforcement/test_soul_auto_load.py -q` — 0 failures
- [ ] `bash scripts/enforcement/check-soul-runtime-drift.sh` — exit 0, no `DRIFT` lines
- [ ] `uv run --with pytest --with pyyaml pytest tests/enforcement/test_harness_surface_coverage.py -v` — all pass
- [ ] Every guard test mutation-verified; the mutation and the resulting failure recorded in the PR body
- [ ] Adding a stub artifact to the generator without registering it makes the coverage test fail
- [ ] **Renaming** a generated artifact makes the coverage test fail (the r1 Finding-1 regression test)
- [ ] R5 reports a **per-provider** figure including that provider's installed surface; every figure stated in the PR body
- [ ] No registry key exists that can exempt a surface from its provider's budget
- [ ] A CI job executes the drift check and the enforcement tests, and is visible on the PR
- [ ] No regression: `uv run --with pyyaml --with pytest pytest tests/dispatch/ tests/enforcement/ -q`
- [ ] `scripts/legal/legal-sanity-scan.sh --repo=workspace-hub` passes
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, inline) | **MAJOR** | (1) completeness check anchored to a filename glob — reproduces the fixed defect; (2) budget summed across providers describes no real session; (3) `counts_toward_session_budget` is a hand-editable backdoor; (4) symlink test has undefined CI behaviour; (5) Phase C has no acceptance criterion |
| Codex (r2) | **MAJOR** | (1) "escapes both → not loaded" is **false**; derivation is rename-proof, not role-proof; (2) `shared:` is still hand-listed membership — the closed backdoor, relocated; (3) the hermetic symlink test is **tautological** — parsing the installer validates the parser, not the wiring; (4) per-provider budget undercounts: omits `MEMORY.runtime.md`, inlined rules, skill surfaces; budget scope never defined; (5) the cap can be **reported around** — the plan can claim success with 24KB-vs-16KB intact; (+2 MINOR on tautological acceptance criteria and the ambiguous rename criterion) |
| Agy (r3) | not dispatched — see below |  |

**Overall result:** r1 FAIL → re-drafted → r2 FAIL → re-drafted again. Both rounds found the plan
reproducing, in a new place, the defect class it exists to fix. **Not eligible for `status:plan-review`.**

Agy was deliberately not dispatched: two independent providers already returned MAJOR on
substantive design grounds, and a third review of a draft that must change anyway spends quota to
confirm a known answer. Agy runs against the revised draft, per `feedback_r3_inline_loop_break_pattern`
(when r1 and r2 surface different defects, apply r3 as inline patches rather than dispatching).

Artifact: [`scripts/review/results/2026-08-02-plan-3762-claude.md`](../../scripts/review/results/2026-08-02-plan-3762-claude.md)

Revisions made based on review:
- Completeness is now derived from `build-soul-runtime.sh`'s own output list, not a `*.runtime.md` glob (F1).
- `check_budget` is per-provider; the cross-provider sum is removed (F2).
- `counts_toward_session_budget` is deleted. Membership derives from `install-soul-runtime.sh` (F3).
- The symlink assertion splits: a hermetic test parses the installer; a host-local lane reports UNAVAILABLE off-host rather than skipping (F4).
- **Phase C (trim `SHARED_SOUL.md`) is removed from this plan** and will be filed as its own issue (F5). It cannot be planned until the owner sets a per-provider target, and it is a content decision rather than a coverage one.
- Two findings generalize and will be promoted to `.claude/rules/` independently of how #3762 lands: a completeness check anchored to a filename pattern is not a completeness check; a declared exemption flag is a backdoor.

**After r2 (Codex):**
- The "neither generated nor installed → not loaded" claim is **retracted**, and the derivation-from-two-scripts model is replaced by an explicit **auto-load taxonomy** in which every category must name an enumerator and a category without one is a hard failure (F1).
- `shared:` is no longer hand-listed. It is enumerated by parsing what `AGENTS.md` and the runtime artifacts actually cite, so deleting an entry cannot silently drop it from the budget (F2).
- The installer-parsing test is demoted from "the hermetic wiring test" to what it is — a **parser unit test**. Live wiring now requires a host-local verification artifact attached before closeout; `UNAVAILABLE` blocks closeout rather than being an acceptable terminal state (F3).
- `MEMORY.runtime.md` and inlined shared rules are added to the budget, and **budget scope is now defined explicitly** (below) rather than left implicit (F4).
- **The cap is no longer deferrable.** See the decision recorded in Risks (F5).
- Acceptance criteria that could pass with the fix doing nothing are replaced with behavioural ones — including a criterion that adds a harness surface *outside* both scripts but inside the taxonomy and proves the guard catches it (F6, F1).
- A third generalizable finding is added for promotion: **a test that parses the thing it is validating tests the parser, not the behaviour.**

---

## Risks and Open Questions

- **Risk — editing `enforcement-gate.yml` stales the scheduler audit digest.** Per `feedback_scheduler_audit_digest_covers_ci_workflows`, the Scheduler Mutation Surface Guard's `source_digest` covers the CI workflows. Adding a job will require regenerating the identity inventory, re-affirming `source_digest`, and regenerating the HTML audit with `--render-html`. `resolved_on` and `pull_request` are hardcoded in `scheduler_mutation_contract.py:310` and must **not** change.
- **Risk — `check-scheduler-mutation-surfaces.py:88` reads the git index, not the working tree.** Changes must be staged before running it or it reports stale state.
- **Budget scope — DEFINED (r2 F4).** "Session budget" means **everything automatically loaded before the user's first prompt**, for one provider: `AGENTS.md`, the rules it cites, that provider's `SOUL.runtime.md`/`AGENTS.runtime.md`, that provider's `MEMORY.runtime.md`, and any inlined shared-rule text. It is *not* "repo harness files" and *not* "provider bootstrap files only". Skill/plugin bootstrap text is an open question below, not a silent exclusion.
- **The cap — DECIDED, not deferred (r2 F5).** r2 is right that leaving this open lets the issue close green while 24 KB against a 16 KB cap survives. So: **the guard fails on an over-cap provider.** If that turns CI red on landing, red is the correct report — the check finally works. What remains genuinely the owner's is only the *number* (whether 16 KB is still the right target once the true figure is visible) and whether trimming or raising closes the gap. The issue may **not** close with a reported-only guard; if the owner chooses to raise the cap, that is an explicit decision recorded on the issue, not a default.
- **Risk — Phase B makes a currently-green check go red.** Counting what actually loads will take R5 from `PASS 4KB/16KB` to a failing per-provider figure. That is the check finally working, not a regression, but it will surface as a new red and must be communicated as such.
- **Risk — `config/agents/agy/` and `gemini/` did not appear in the drift script output.** Whether they are intentionally unchecked after the agy swap (#3573) or an omission must be determined before the registry claims to cover them.
- **Risk — the PII gate scans whole files in a diff.** Touching the runtime artifacts drags their full contents through every diff-scanning check.
- **Open:** should `gemini/SOUL.runtime.md` still be built at all, given agy replaced gemini as the third provider (#3573)? Six artifacts may be five.
- **Open:** does the owner want the cap enforced as a hard CI failure, or reported-only until the trim lands?

---

## Complexity: T3

Cross-provider and systemic: `SHARED_SOUL.md` is the common ancestor of six runtime artifacts consumed by four providers, and the change alters two enforcement scripts plus a CI workflow. Per the AGENTS.md scale, T3 requires three-provider adversarial review at both the plan and code stages.
