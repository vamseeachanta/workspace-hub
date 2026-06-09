# Plan for #2986: Harden skill validation uv resolution and diagnostics

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-06-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2986
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-06-08-plan-2986-r1-claude.md | scripts/review/results/2026-06-08-plan-2986-r1-codex.md | scripts/review/results/2026-06-08-plan-2986-r2-claude.md | scripts/review/results/2026-06-08-plan-2986-r2-codex.md | scripts/review/results/2026-06-08-plan-2986-r1-gemini.md | scripts/review/results/2026-06-08-plan-2986-r3-claude.md | scripts/review/results/2026-06-08-plan-2986-r3-codex.md | scripts/review/results/2026-06-08-plan-2986-r3-gemini.md | scripts/review/results/2026-06-08-plan-2986-r4-claude.md | scripts/review/results/2026-06-08-plan-2986-r4-codex.md | scripts/review/results/2026-06-08-plan-2986-r5-claude.md | scripts/review/results/2026-06-08-plan-2986-r5-codex.md | scripts/review/results/2026-06-08-plan-2986-r5-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/cron/comprehensive-learning-nightly.sh` — line 8 already prepends `${HOME}/.local/bin`, `${HOME}/.cargo/bin`, and `/usr/local/bin`; lines 88-91 run `bash scripts/skills/validate-skills.sh .claude/skills` as best-effort and collapse failures to `WARNING: skill validation issues found`.
- Found: `scripts/skills/validate-skills.sh` — lines 13-16 require `command -v uv`; if unresolved, it exits 2 with only `uv is required to validate skill frontmatter`; line 18 defaults `UV_CACHE_DIR` itself rather than using the existing shared helper.
- Found: `scripts/lib/uv-env.sh` — existing `uv_env_setup` helper sets and creates repo-local `UV_CACHE_DIR`; this should be reused instead of duplicating cache setup.
- Found: `scripts/lib/python-resolver.sh` — existing resolver pattern exports a validated runtime path (`PYTHON`) for shell callers, but exits at source time on failure; the proposed `uv` resolver should reuse the validated-runtime idea while explicitly remaining source-safe and function-based.
- Found: `.claude/skills/development/skill-eval/SKILL.md:130-138` and `.agents/skills/development/skill-eval/SKILL.md:130-138` — direct documentation callers invoke `bash scripts/skills/validate-skills.sh` without the nightly wrapper's PATH setup.
- Found: `.github/workflows/skills-validation.yml` — CI installs `uv` with `astral-sh/setup-uv@v4`, then hard-fails on `scripts/skills/validate-skills.sh` and the validator regression tests; its path filters currently omit `scripts/lib/*.sh` and `tests/cron/test_skill_validation_uv_resolution.py`.
- Found: `tests/enforcement/test_validate_skills_frontmatter.py` — malformed YAML cases are generated dynamically, not stored as reusable fixture files.
- Found: `tests/cron/` — pytest-style cron tests exist, so the new cron/path probes should use pytest rather than a new shell harness.

### Standards

| Standard | Status | Source |
|---|---|---|
| Workspace issue planning gate | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Cron best-effort behavior | applicable | `scripts/cron/comprehensive-learning-nightly.sh:88-91` |
| Shared uv environment setup | applicable | `scripts/lib/uv-env.sh` |
| Resolver idiom | applicable | `scripts/lib/python-resolver.sh` |
| Python execution through `uv` | applicable | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md:148` |

### LLM Wiki pages consulted

- No wiki pages apply. This issue changes workspace-hub cron/tooling behavior only.

### Documents consulted

- Issue #2986 — defines the follow-up risk: #2981 made `validate-skills.sh` require `uv`, and cron/logging should not silently lose the local nightly validation value.
- Issue #2981 / PR #2987 — introduced strict YAML-backed skill validation and CI hard-fail behavior that this plan must preserve.
- `docs/plans/README.md` — confirms T2 issue plans require resource intel, adversarial review, user approval, and TDD before implementation.
- `scripts/review/results/2026-06-08-plan-2986-r1-claude.md` — r1 MAJOR: direct minimal-PATH reproduction bypassed the real cron wrapper; the plan must be reframed.
- `scripts/review/results/2026-06-08-plan-2986-r1-codex.md` — r1 MAJOR: CI path filters would miss new resolver/test paths; plan must include workflow updates.
- `scripts/review/results/2026-06-08-plan-2986-r2-claude.md` — r2 MAJOR: review-artifact citations pointed at empty stubs, deliverable still overstated production cron reliability, direct callers were under-evidenced, and resolver control-flow needed clarification.
- `scripts/review/results/2026-06-08-plan-2986-r2-codex.md` — r2 MAJOR: review-artifact citations pointed at empty stubs, Gemini review evidence was missing, and empty-HOME diagnostics were ambiguous.
- `scripts/review/results/2026-06-08-plan-2986-r1-gemini.md` — Gemini r1 MAJOR: local file-existence retrieval failed in Gemini's workspace, but its pseudocode findings were valid (`REPO_ROOT`, stderr diagnostics, `$SCRIPT_DIR` path, and `uv-env.sh` workflow filters).
- `scripts/review/results/2026-06-08-plan-2986-r3-claude.md` — r3 MAJOR: source ordering was still CWD-fragile; workflow path filters needed both trigger blocks; cache test naming/env scrubbing needed precision.
- `scripts/review/results/2026-06-08-plan-2986-r3-codex.md` — r3 MAJOR: source ordering remained CWD-fragile and unset `HOME` under `set -u` needed `${HOME:-}` handling.
- `scripts/review/results/2026-06-08-plan-2986-r3-gemini.md` — Gemini r3 MAJOR: file-existence retrieval remained unavailable in Gemini workspace; valid findings required `$ROOT` assignment and literal diagnostic handling.
- `scripts/review/results/2026-06-08-plan-2986-r4-claude.md` — r4 MINOR: plan was implementable; remaining findings were scoping/test-hermeticity advisories.
- `scripts/review/results/2026-06-08-plan-2986-r4-codex.md` — r4 MAJOR: resolver candidates must be validated by execution, source-safety needs a direct test, and default root must not remain caller-CWD-relative.
- `scripts/review/results/2026-06-08-plan-2986-r5-claude.md` — r5 MINOR: prior r4 Codex MAJOR blockers were resolved; remaining item is user confirmation of the scope reframe from observed cron break to direct-caller hardening/diagnostics.
- `scripts/review/results/2026-06-08-plan-2986-r5-codex.md` — r5 MINOR: no blockers; minor wording mismatch for non-executable `UV_BIN` diagnostics and reminder to commit/push review artifacts before `status:plan-review`.
- `scripts/review/results/2026-06-08-plan-2986-r5-gemini.md` — r5 UNAVAILABLE: Gemini CLI loaded the workspace but failed its shell-retrieval tool interface (`run_shell_command` missing), so it produced no usable plan verdict.

### Gaps identified

- No shared `uv` binary resolver exists for shell scripts; `uv-env.sh` handles cache setup only.
- `validate-skills.sh` is less robust than its callers: it assumes callers made `uv` reachable on `PATH`, has no `UV_BIN` override, and emits terse diagnostics when run directly from skill-eval docs, agent sessions, or other automation.
- The nightly wrapper already resolves `/home/vamsee/.local/bin/uv` when `HOME` is set, so this issue is defensive hardening plus diagnostics, not proof that the current cron wrapper is broken on this machine.
- CI path filters do not include future `scripts/lib/uv-resolver.sh` or `tests/cron/test_skill_validation_uv_resolution.py` changes.
- No test proves the direct validator entrypoint can resolve common user-installed `uv` locations under a minimal `PATH`.
- No test proves missing `uv` produces actionable install/path/override guidance.

### Evidence

**Issue statuses** (verified 2026-06-09T02:16:29Z via `gh issue view`):
- `#2986` — OPEN — `fix(cron): make nightly skill validation resolve uv reliably`
- `#2981` — CLOSED — `fix: make SKILL.md frontmatter YAML-valid for review dispatch`

**File existence** (`ls` / `nl` 2026-06-09T02:16:29Z):
- EXISTS: `scripts/cron/comprehensive-learning-nightly.sh`
- EXISTS: `scripts/skills/validate-skills.sh`
- EXISTS: `scripts/lib/uv-env.sh`
- EXISTS: `scripts/lib/python-resolver.sh`
- EXISTS: `.github/workflows/skills-validation.yml`
- EXISTS: `tests/enforcement/test_validate_skills_frontmatter.py`
- EXISTS: `tests/cron/`
- MISSING (new — this plan may create): `scripts/lib/uv-resolver.sh`
- MISSING (new — this plan may create): `tests/cron/test_skill_validation_uv_resolution.py`

**Line excerpts** (`nl -ba scripts/cron/comprehensive-learning-nightly.sh | sed -n '7,91p'`):
```
     7	# Ensure uv and other user-installed tools are on PATH (cron has minimal PATH)
     8	export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"
...
    88	# Step 4: validate skill frontmatter (best-effort — WRK-308)
    89	echo "--- Skill validation $(date +%Y-%m-%dT%H:%M:%S) ---"
    90	bash scripts/skills/validate-skills.sh .claude/skills || \
    91	  echo "WARNING: skill validation issues found — see above"
```

**Line excerpts** (`nl -ba scripts/skills/validate-skills.sh | sed -n '1,20p'`):
```
     1	#!/usr/bin/env bash
     2	set -euo pipefail
...
    13	if ! command -v uv >/dev/null 2>&1; then
    14	  echo "uv is required to validate skill frontmatter" >&2
    15	  exit 2
    16	fi
...
    19	exec uv run --no-project --with pyyaml python "$SCRIPT_DIR/validate_skills_frontmatter.py" "$ROOT"
```

**Existing cron wrapper path proof**:
```
$ env -i HOME="$HOME" PATH=/usr/bin:/bin bash -c 'export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"; command -v uv; uv --version'
/home/vamsee/.local/bin/uv
uv 0.10.0
```

- Observed at: 2026-06-09T02:16:29Z
- Interpretation: with `HOME` set, the current cron wrapper already resolves local `uv`; the issue should not claim this machine's wrapper path is currently broken.

**Direct validator entrypoint reproduction**:
```
$ PATH=/usr/bin:/bin UV_CACHE_DIR=.claude/state/uv-cache bash scripts/skills/validate-skills.sh .claude/skills
uv is required to validate skill frontmatter
```

- Observed at: 2026-06-09T02:16:29Z
- Exit code: 2
- Interpretation: the reusable validator entrypoint is brittle when called directly under minimal PATH and emits terse guidance. That is the concrete behavior this plan will harden.

**Direct caller excerpts** (`nl -ba .claude/skills/development/skill-eval/SKILL.md | sed -n '130,138p'`):
```
   130	```bash
   131	# Check for structural violations (README presence, word count, description length, XML tags)
   132	bash scripts/skills/audit-skill-violations.sh
   133	
   134	# Validate skill structure (name conventions, required fields)
   135	bash scripts/skills/validate-skills.sh
   136	
   137	# Check which skills lack any script call reference
   138	bash scripts/skills/skill-coverage-audit.sh
```

- `.agents/skills/development/skill-eval/SKILL.md:130-138` contains the same direct validation command.

**Current count of distinct sources:** 10

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-09-issue-2986-cron-uv-resolution.md` |
| Plan index | `docs/plans/README.md` |
| Resolver | `scripts/lib/uv-resolver.sh` |
| Existing uv env helper | `scripts/lib/uv-env.sh` |
| Validator wrapper | `scripts/skills/validate-skills.sh` |
| Skills validation workflow | `.github/workflows/skills-validation.yml` |
| Cron-path tests | `tests/cron/test_skill_validation_uv_resolution.py` |
| Existing validator tests | `tests/enforcement/test_validate_skills_frontmatter.py` |
| Plan review — Claude r1 | `scripts/review/results/2026-06-08-plan-2986-r1-claude.md` |
| Plan review — Codex r1 | `scripts/review/results/2026-06-08-plan-2986-r1-codex.md` |
| Plan review — Claude r2 | `scripts/review/results/2026-06-08-plan-2986-r2-claude.md` |
| Plan review — Codex r2 | `scripts/review/results/2026-06-08-plan-2986-r2-codex.md` |
| Plan review — Gemini r1 | `scripts/review/results/2026-06-08-plan-2986-r1-gemini.md` |
| Plan review — Claude r3 | `scripts/review/results/2026-06-08-plan-2986-r3-claude.md` |
| Plan review — Codex r3 | `scripts/review/results/2026-06-08-plan-2986-r3-codex.md` |
| Plan review — Gemini r3 | `scripts/review/results/2026-06-08-plan-2986-r3-gemini.md` |
| Plan review — Claude r4 | `scripts/review/results/2026-06-08-plan-2986-r4-claude.md` |
| Plan review — Codex r4 | `scripts/review/results/2026-06-08-plan-2986-r4-codex.md` |
| Plan review — Claude r5 | `scripts/review/results/2026-06-08-plan-2986-r5-claude.md` |
| Plan review — Codex r5 | `scripts/review/results/2026-06-08-plan-2986-r5-codex.md` |
| Plan review — Gemini r5 unavailable | `scripts/review/results/2026-06-08-plan-2986-r5-gemini.md` |

---

## Deliverable

`validate-skills.sh` direct callers will gain a `UV_BIN` override, common-path fallback, source-safe resolver diagnostics, and existing `uv_env_setup` cache behavior, while the nightly cron wrapper keeps its current best-effort semantics and CI keeps hard-fail coverage for the new resolver/test paths.

---

## Pseudocode

```
function resolve_uv:
    source-safe: define functions only; do not exit at source time
    define validate_uv_candidate(candidate, source_label):
        if candidate is empty:
            return failure without printing the candidate
        if candidate is not executable/resolvable:
            print "uv candidate is not executable: <source_label> (<candidate>)" to stderr
            return failure
        if "$candidate" --version succeeds:
            print candidate and return success
        print "uv candidate failed validation: <source_label> (<candidate>)" to stderr
        return failure
    if UV_BIN is set:
        if validate_uv_candidate "$UV_BIN" "UV_BIN": return success
        print "UV_BIN is set but is not a usable uv executable" to stderr and return failure
    if command -v uv succeeds:
        if validate_uv_candidate "$resolved_path" "PATH uv": return success
        continue to common-path candidates after stderr diagnostic
    home_dir="${HOME:-}"
    build candidate list from "$home_dir/.local/bin/uv", "$home_dir/.cargo/bin/uv", "/usr/local/bin/uv"
    skip HOME-derived candidates when home_dir is empty, but mention those literal candidate labels in diagnostics
    for candidate in candidates:
        if validate_uv_candidate "$candidate" "common path": return success
    print actionable guidance to stderr:
        "uv is required..."
        "looked in PATH, UV_BIN, $HOME/.local/bin/uv, $HOME/.cargo/bin/uv, /usr/local/bin/uv; HOME-derived paths skipped when HOME is empty"
        "install with the documented uv installer or set UV_BIN=/path/to/uv"
    return failure
```

```
validate-skills.sh:
    set SCRIPT_DIR from BASH_SOURCE
    set REPO_ROOT from git -C "$SCRIPT_DIR" rev-parse --show-toplevel fallback
    ROOT="${1:-$REPO_ROOT/.claude/skills}"
    source "$REPO_ROOT/scripts/lib/uv-env.sh"
    source "$REPO_ROOT/scripts/lib/uv-resolver.sh"
    verify skills root exists
    uv_env_setup "$REPO_ROOT"
    UV=""
    UV="$(resolve_uv)" or exit 2
    exec "$UV" run --no-project --with pyyaml python "$SCRIPT_DIR/validate_skills_frontmatter.py" "$ROOT"
```

```
comprehensive-learning-nightly.sh:
    preserve existing best-effort behavior
    make no broad nightly side-effect change
    if modified, only make log text point at validate-skills resolver diagnostics
```

```
skills-validation.yml:
    add path filters under BOTH pull_request.paths and push.paths for:
        scripts/lib/uv-resolver.sh
        scripts/lib/uv-env.sh
        tests/cron/test_skill_validation_uv_resolution.py
    add a pytest step for the cron/path resolver tests
    keep setup-uv and hard-fail validator steps
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/lib/uv-resolver.sh` | Centralize shell `uv` binary discovery and missing-`uv` diagnostics. |
| Modify | `scripts/skills/validate-skills.sh` | Use `uv-env.sh` plus the resolver instead of raw `command -v uv`; preserve `UV_CACHE_DIR` and CI hard-fail behavior. |
| Modify | `.github/workflows/skills-validation.yml` | Include new resolver/test paths in filters and run the new cron/path tests. |
| Modify | `scripts/cron/comprehensive-learning-nightly.sh` | Optional narrow log wording only; no semantic change unless review/implementation finds it necessary. |
| Create | `tests/cron/test_skill_validation_uv_resolution.py` | TDD coverage for direct validator resolution under cron-like PATH and missing-`uv` diagnostics. |
| Modify | `tests/enforcement/test_validate_skills_frontmatter.py` | Add or adjust coverage only if needed to prove #2981 validator hard-fail behavior remains intact. |
| Update | `docs/plans/README.md` | Add this revised plan to the index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_validate_skills_resolves_uv_from_home_local_under_minimal_path` | Direct validator entrypoint finds `$HOME/.local/bin/uv` when `PATH=/usr/bin:/bin`. | Scrubbed subprocess env containing only required vars; temp HOME with executable `.local/bin/uv`; minimal PATH; temp skill root. | `validate-skills.sh` invokes the temp `uv` path. |
| `test_validate_skills_honors_uv_bin_override` | Explicit `UV_BIN` wins over PATH and common locations. | Scrubbed subprocess env; temp executable pointed to by `UV_BIN`. | `validate-skills.sh` invokes `UV_BIN`. |
| `test_validate_skills_rejects_non_executable_uv_bin` | Bad override is fail-closed and actionable. | Scrubbed subprocess env; `UV_BIN` pointing at a non-executable file. | Exit 2; stderr names `UV_BIN` and says it is not executable. |
| `test_validate_skills_rejects_executable_but_failing_uv_bin` | Executable override is not trusted until `uv --version` succeeds. | Scrubbed subprocess env; `UV_BIN` points at executable script that exits nonzero for `--version`. | Exit 2; stderr names `UV_BIN` and says the candidate failed validation. |
| `test_validate_skills_rejects_failing_path_uv_and_uses_common_path` | Broken `PATH` shim does not mask a valid common-path/user install candidate. | Scrubbed subprocess env; fake `PATH` `uv` fails `--version`; temp HOME `.local/bin/uv` passes. | Stderr names the failed PATH candidate; validator invokes the HOME candidate. |
| `test_validate_skills_rejects_failing_common_path_uv` | Broken common-path executable still produces actionable missing-uv diagnostics. | Scrubbed subprocess env; only available common-path candidate fails `--version`. | Exit 2; stderr names the failed candidate and install/`UV_BIN` remediation. |
| `test_uv_resolver_is_source_safe_when_uv_missing` | `scripts/lib/uv-resolver.sh` defines functions only and does not exit at source time. | Scrubbed subprocess env with no usable `uv`; shell command sources resolver then echoes `after`. | Shell exits 0 and prints `after`; no resolver failure happens until `resolve_uv` is called. |
| `test_validate_skills_default_root_is_repo_relative_from_foreign_cwd` | Direct absolute invocation with no root arg does not look for `.claude/skills` in caller CWD. | Scrubbed subprocess env; run `bash <repo>/scripts/skills/validate-skills.sh` from a temp directory with fake valid `uv`. | Wrapper reaches repo-root `.claude/skills` and invokes fake `uv`, rather than failing on temp-cwd `.claude/skills`. |
| `test_validate_skills_missing_uv_diagnostic_is_actionable` | Missing `uv` failure names searched/skipped paths and remediation without tripping `set -u`. | Scrubbed subprocess env with `HOME` unset, minimal PATH, no `UV_BIN`. | Exit 2; stderr, not stdout captured into `UV`, includes literal `UV_BIN`, `$HOME/.local/bin/uv`, `$HOME/.cargo/bin/uv`, `/usr/local/bin/uv`, notes HOME-derived paths were skipped, and includes install guidance. |
| `test_validate_skills_honors_explicit_uv_cache_dir` | Wrapper reuses `uv_env_setup` passthrough behavior without dirtying the real repo. | Scrubbed subprocess env with explicit `UV_CACHE_DIR=<tmp-cache>`; fake `uv` records environment. | Fake `uv` receives the temp `UV_CACHE_DIR`; no repo-state dependency is required for the assertion. |
| `test_validate_skills_derives_uv_cache_default` | Wrapper derives the repo-local default when `UV_CACHE_DIR` is unset. | Scrubbed subprocess env with `UV_CACHE_DIR` unset; fake `uv` records environment. | Fake `uv` receives `<repo>/.claude/state/uv-cache`; test treats the directory as expected generated state or cleans it if created. |
| `test_validate_skills_existing_yaml_validation_still_runs` | #2981 behavior remains: when `uv` exists, real validator catches bad YAML. | Dynamically created malformed SKILL.md fixture. | Nonzero validation result with YAML/frontmatter error. |
| `test_skills_validation_workflow_includes_new_paths` | CI hard-fail coverage includes the resolver, env helper, and new test file. | Read `.github/workflows/skills-validation.yml`. | Path filters include `scripts/lib/uv-resolver.sh`, `scripts/lib/uv-env.sh`, and `tests/cron/test_skill_validation_uv_resolution.py`; test step runs the new pytest file. |

---

## Acceptance Criteria

- [ ] New tests pass: `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest tests/cron/test_skill_validation_uv_resolution.py -v`
- [ ] Existing validator tests pass: `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest tests/enforcement/test_validate_skills_frontmatter.py -v`
- [ ] Full skill validation still passes with real `uv`: `UV_CACHE_DIR=.claude/state/uv-cache bash scripts/skills/validate-skills.sh .claude/skills`
- [ ] Direct minimal-PATH success probe with known HOME resolves exact binary: `HOME=<tmp-home-with-.local-bin-uv> PATH=/usr/bin:/bin bash scripts/skills/validate-skills.sh <tmp-skills-root>` invokes `<tmp-home>/.local/bin/uv`.
- [ ] Direct minimal-PATH failure probe with `HOME` unset exits 2 without `set -u` crash and names literal `UV_BIN`, `$HOME/.local/bin/uv`, `$HOME/.cargo/bin/uv`, `/usr/local/bin/uv`, notes HOME-derived paths were skipped, and includes install guidance.
- [ ] `.github/workflows/skills-validation.yml` path filters and steps cover `scripts/lib/uv-resolver.sh`, `scripts/lib/uv-env.sh`, and the new resolver/test artifacts; CI hard-fail behavior from #2981 is not softened.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes.
- [ ] Code/artifact review completes with no MAJOR blockers before closeout.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Direct reproduction bypassed real cron wrapper; deliverable overstated reliability; AC/test ambiguity; prior art missing. |
| Codex r1 | MAJOR | CI path filters omitted new resolver/test paths; dynamic fixture claim was false; `uv-env.sh` prior art missing. |
| Claude r2 | MAJOR | Review artifact citations pointed at empty files; deliverable still overstated production reliability; direct callers and source-safe resolver contract needed evidence. |
| Codex r2 | MAJOR | Review artifact citations pointed at empty files; Gemini evidence missing; empty-HOME diagnostic wording ambiguous. |
| Gemini r1 | MAJOR | File-existence retrieval failed in Gemini workspace; valid pseudocode findings required `REPO_ROOT`, stderr diagnostics, `$SCRIPT_DIR`, and `uv-env.sh` workflow-filter coverage. |
| Claude r3 | MAJOR | Source ordering remained CWD-fragile; workflow filters needed both trigger blocks; tests needed scrubbed env/default-cache precision. |
| Codex r3 | MAJOR | Source ordering remained CWD-fragile; unset HOME under `set -u` needed `${HOME:-}` and a test. |
| Gemini r3 | MAJOR | File-existence retrieval still failed in Gemini workspace; valid findings required `$ROOT` assignment and literal diagnostic handling. |
| Claude r4 | MINOR | Plan was implementable; remaining findings were scoping/test-hermeticity advisories. |
| Codex r4 | MAJOR | Executable `uv` candidates needed `--version` validation; source-safe resolver needed a direct test; no-arg direct invocation needed repo-root-relative default root or explicit scoping. |
| Claude r5 | MINOR | Prior r4 Codex blockers resolved; remaining issue is explicit user confirmation that direct-caller hardening plus diagnostics is the accepted resolution of the cron-titled issue. |
| Codex r5 | MINOR | No blockers; minor wording mismatch for non-executable `UV_BIN` diagnostics and reminder to commit/push artifacts before moving to `status:plan-review`. |
| Gemini r5 | UNAVAILABLE | CLI tool-interface failure: Gemini could not execute its shell-retrieval tool (`run_shell_command` missing), so no usable verdict was produced. |

**Overall result:** PASS WITH MINOR FINDINGS — no MAJOR blockers remain from the usable r5 reviews; Gemini r5 is documented as unavailable. Implementation remains blocked until user approval adds `status:plan-approved`.

Revisions made based on review:
- Reframed deliverable from "cron is broken" to defensive hardening of the direct validator entrypoint plus clearer diagnostics.
- Added faithful cron wrapper proof showing current line-8 PATH prepend resolves `/home/vamsee/.local/bin/uv` when `HOME` is set.
- Added `uv-env.sh` and `python-resolver.sh` to resource intelligence and implementation constraints.
- Made minimal-PATH acceptance criteria branch-specific and falsifiable.
- Added workflow path-filter and pytest-step updates for new resolver/test artifacts.
- Replaced nonexistent "existing malformed fixture" claim with dynamic malformed fixture wording.
- Repointed review-artifact citations to non-empty `-r1-*` / `-r2-*` artifacts.
- Added concrete direct callers from `.claude/skills/development/skill-eval/SKILL.md` and `.agents/skills/development/skill-eval/SKILL.md`.
- Narrowed the deliverable to `UV_BIN` override, direct-caller hardening, diagnostics, and CI coverage instead of claiming new production cron reliability.
- Made resolver contract source-safe and clarified empty-HOME diagnostics.
- Added `REPO_ROOT`/`SCRIPT_DIR` setup to pseudocode, required resolver diagnostics on stderr, preserved `$SCRIPT_DIR/validate_skills_frontmatter.py`, and included `scripts/lib/uv-env.sh` in workflow path-filter coverage.
- Moved `SCRIPT_DIR`/`REPO_ROOT` setup before sourcing libs, made source paths repo-root-relative, bound `ROOT`, required `${HOME:-}` handling under `set -u`, required scrubbed subprocess envs, and made workflow filter updates explicit for both `pull_request` and `push`.
- Added candidate execution validation with `uv --version` before accepting `UV_BIN`, `PATH`, or common-path candidates.
- Added direct source-safety and foreign-CWD default-root tests so direct-entrypoint hardening is not implied only through wrapper behavior.
- Made the no-argument default skills root repo-root-relative and pinned resolver assignment to avoid the `local VAR="$(cmd)"` exit-code trap.
- Aligned non-executable `UV_BIN` diagnostics with the planned test assertion.

---

## Risks and Open Questions

- **Risk:** Testing the full nightly script would run destructive or expensive side effects. The implementation should use focused subprocess/static probes around the skill-validation path, not execute the whole nightly pipeline.
- **Risk:** A fake `uv` test double can prove resolution but not real YAML validation. The plan keeps separate real-validator tests to cover #2981 behavior.
- **Risk:** Other cron scripts use `uv` directly. This issue is scoped to `validate-skills.sh` and its nightly/CI consumers; broader resolver adoption should be filed separately if review finds repeated risk.
- **Open:** Whether nightly skill validation should remain best-effort or become hard-fail is out of scope. Current plan preserves best-effort nightly behavior and hard-fail CI behavior.

---

## Complexity: T2

**T2** — small shared shell resolver, one validator entrypoint, one workflow update, focused pytest coverage, and preservation of an existing CI hard-fail workflow.
