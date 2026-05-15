# Disagreement report — plan #2710 (2026-05-14)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | UNKNOWN |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan omits required missing-file validation for the interactive wrapper. Issue `#2710` acceptance says “Both wrappers reject missing input files with a clear error before any git operations,” and scope says the bash wrapper “Validates each input before proceeding (solver in supported list; input file exists).” Plan `Pseudocode > Step 2` only checks `INPUT_FILE is empty`; it never checks `[[ -f "${REPO_ROOT}/${INPUT_FILE}" ]]` before confirmation or dry-run. Plan `Acceptance Criteria` even uses `path/to/test.owd` in `--dry-run` and expects success, which directly conflicts with the issue’s missing-file rejection criterion.
- The test strategy cannot mock `submit-job.sh` as written. Plan `TDD Test List` says tests “use a mock `submit-job.sh` injected via `PATH` manipulation,” but plan `Pseudocode > Step 5` resolves `SUBMIT_SCRIPT = "${SCRIPT_DIR}/submit-job.sh"` and then runs `exec bash "${SUBMIT_SCRIPT}" ...`. Existing `scripts/solver/submit-batch.sh` lines 9-10 and 124 also use a script-dir path, not `PATH`. A `PATH` mock will not intercept this, so `test_live_delegation_orcawave` and `test_live_delegation_orcaflex` risk invoking the real `scripts/solver/submit-job.sh`, which commits and pushes per `scripts/solver/submit-job.sh` lines 38-40.
- Plan explicitly duplicates solver validation despite the issue forbidding duplicate validation logic. Issue `#2710` acceptance says “No duplicate validation logic — both layers funnel into `submit-job.sh`.” Plan `Architecture Decision` chooses “hardcoded list in both layers,” and plan `Pseudocode > Step 1` implements menu choice validation for `orcawave`, `orcaflex`, and blocked `aqwa`. That is not just presentation; it is a second solver gate that must drift-track `scripts/solver/submit-job.sh` lines 13-16.
- Harness retrieval is incomplete under the repo’s own planning workflow. Issue `#2710` has label `cat:harness`, and `docs/plans/README.md` says Harness/Infra issues require `CONTROL_PLANE_CONTRACT.md`, `config/agents/` settings, and `.claude/rules/` in addition to universal sources. Plan `Resource Intelligence Summary > Standards` says “Not applicable — harness/tooling UX change,” so it skips the class-specific retrieval bundle the planning guide requires.
- The plan drops an explicit issue documentation requirement. Issue `#2710` scope says “Skill appears in available-skills listings (verify by running with --list option to whatever skill-discovery mechanism is canonical).” Plan `Files to Change` only creates `.claude/skills/coordination/solver-submit/SKILL.md`, creates the wrapper/test, and modifies `scripts/solver/README.md`; plan `Acceptance Criteria` only checks YAML frontmatter and README. It does not identify or verify the canonical skill-discovery listing, despite `docs/SKILLS_INDEX.md` being a repo-level skill catalog.

### gemini

(no findings unique to this provider)

