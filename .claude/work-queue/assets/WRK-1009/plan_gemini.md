YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-1009 Plan — Skill upkeep and curation: evals, A/B tests, daily cron integration (Refined)

**Route B — Medium complexity | dev-primary | Orchestrator: Claude | Reviewer: Gemini (Reliability Focus)**

*Plan decisions (Stage 5 user review 2026-03-10):*
*① Eval defs: central `specs/skills/evals/` (not per-skill)*
*② A/B mode: static schema validation only — no live model runs (mitigates L3 parsing and quota risks)*
*③ Retirement threshold: 0.05 baseline_usage_rate + ≥10 invocations minimum (conservative)*
*④ Pilot skills: work-queue, workflow-gatepass, comprehensive-learning*
*⑤ Added: skill→script conversion scan phase*

## Phase 0: Skill→Script Conversion Scan (Robustness Added)

- 0a. Implement `scripts/skills/identify-script-candidates.sh` — scans all 508 `SKILL.md` files for deterministic patterns.
  - **Reliability measure:** Ensure the scanner handles missing directories, symlinks, and malformed markdown without crashing. Use strict regex boundaries.
- 0b. Emit `specs/skills/script-conversion-candidates.md` — list of skill name, path, rationale, and suggested script path.
  - **Reliability measure:** Write to a temporary file first and move atomically (`mv temp target`) to prevent partial writes if interrupted.
- 0c. No actual conversion in this WRK — output is a candidate list only.

## Phase 1: Eval Framework Design (TDD-first & Fault Tolerant)

- 1a. Write `specs/skills/skill-eval-framework.md` — capability eval schema, procedural eval schema, A/B eval modes.
- 1b. Write failing tests in `scripts/skills/tests/test_skill_evals.sh` (bash, bats-style) covering schema validation, JSONL format, cron hooks, and corrupt/missing file handling.
- 1c. Implement `scripts/skills/run-skill-evals.sh` — reads eval defs from `specs/skills/evals/*.yaml`.
  - **Reliability measure:** Implement robust carry-forward logic. If a YAML definition is missing, empty, or corrupt, the script must log a `WARN`, skip the file, and continue processing rather than exiting with a fatal error.
  - Emit JSONL report to `.claude/state/skill-eval-results/YYYY-MM-DD.jsonl`.
- 1d. Write central eval definitions for 3 pilot skills in `specs/skills/evals/` (work-queue, workflow-gatepass, comprehensive-learning).

## Phase 2: Curation Tooling (Concurrency & Safety)

- 2a. Write `scripts/cron/skill-curation-nightly.sh` — wraps `run-skill-evals.sh`, duplicate detection, retirement flagging.
  - **Reliability measure:** Use `flock` on state files (e.g., candidate lists and JSONL reports) to prevent file lock races if multiple cron jobs or manual runs overlap.
- 2b. Wire into `scripts/cron/comprehensive-learning-nightly.sh` as new Step 4b.
  - **Reliability measure:** Ensure step 4b is wrapped in a `set +e` block or equivalent trap so that a failure in skill curation does not halt the rest of the comprehensive learning cron.
- 2c. Duplicate detection: scan all `SKILL.md` frontmatter fields safely, accounting for missing `name:` fields or malformed YAML frontmatter.
- 2d. Failing evals → write candidate WRK file to `.claude/state/skill-eval-candidates/` atomically.

## Phase 3: Daily Report Integration

- 3a. Eval summary emitted via `scripts/productivity/sections/skill-evals.sh` for `/today`.
  - **Reliability measure:** The script must handle the absence of `YYYY-MM-DD.jsonl` gracefully (e.g., reporting "No data for today" instead of throwing `file not found` errors).
- 3b. `/reflect` ecosystem block shows: eval health, # retirement candidates, # duplicates.

## Test Strategy (Expanded for Surface Area Coverage)

| Test | Type | Pass condition |
|------|------|---------------|
| Eval script exits 0 on valid eval dir | unit | exit code = 0 |
| Eval script logs WARN and continues on missing/corrupt YAML | unit | exit code = 0, stdout contains WARN |
| Eval script exits 1 on fatal system errors (e.g., permissions) | unit | exit code = 1, stderr output |
| JSONL report has required fields | unit | skill, result, timestamp, eval_type |
| JSONL append is atomic/safe under concurrent load | integration | no interleaved JSON lines |
| Duplicate detection flags same-name skill | unit | stdout contains "DUPLICATE" |
| Duplicate detection handles missing frontmatter | unit | stdout contains "MISSING_NAME" |
| Retirement flag: rate < 0.05 AND calls < 10 | unit | flagged as candidate |
| Retirement safe: rate ≥ 0.05 → not flagged | unit | not in candidate list |
| script-candidate scan produces output file atomically | unit | specs/.../candidates.md exists, no partial |
| script-candidate scan handles non-markdown files safely | unit | ignores binaries/scripts silently |
| Cron integration: step 4b runs and isolates failures | integration | comprehensive-learning completes even if 4b fails |
| Pilot eval work-queue PASS | integration | JSONL result=pass for work-queue |
| Daily report handles missing JSONL safely | unit | outputs fallback text |
| Daily report parses JSONL correctly | unit | calculates correct PASS/FAIL counts |
| Schema validation rejects unknown A/B eval modes | unit | eval fails schema check |

## Scope Boundary (deferred)

External upstream scan (openai/skills, anthropics/skills), live A/B model runs, auto-remediation — all follow-on WRKs.

## Deliverables

- `specs/skills/skill-eval-framework.md`
- `specs/skills/evals/work-queue.yaml`, `workflow-gatepass.yaml`, `comprehensive-learning.yaml`
- `specs/skills/script-conversion-candidates.md`
- `scripts/skills/run-skill-evals.sh`
- `scripts/skills/identify-script-candidates.sh`
- `scripts/skills/tests/test_skill_evals.sh`
- `scripts/cron/skill-curation-nightly.sh`
- Updated `scripts/cron/comprehensive-learning-nightly.sh` (Step 4b)

---

## Gemini Notes: Systems Reliability Review

1. **L3 Gemini Output Parsing Failure Modes:** 
   By restricting the A/B eval modes to *static schema validation only* (Plan Decision ②), we successfully bypass the immediate risks of L3 Gemini output parsing (partial YAML, fenced code, prose hallucinations). If future WRKs introduce live model runs, we must enforce `gemini --json` (or strictly prompt for parseable JSON) and wrap the execution in a validation loop `jq -e` to handle parsing fallbacks safely.
2. **Carry-Forward Logic & Missing Files:** 
   *(Note: Interpreting the `portfolio-signals.yaml` prompt parameter as the eval definitions)*. If `specs/skills/evals/*.yaml` files are missing, empty, or corrupt, the script must not crash the nightly cron. I have updated Phase 1c to ensure that corrupt files are logged as `WARN` and skipped. The carry-forward logic must assume a default state (e.g., "UNTESTED") rather than failing the entire batch.
3. **Dual-Mode Tie-Break:** 
   *(Note: Interpreting the `engineering >= harness` prompt parameter as capability vs. procedural schemas)*. If an eval definition triggers both capability and procedural schemas, and they conflict (e.g., capability passes, procedural fails), the framework should default to the safest state: `FAIL`. The static mode evaluation must strictly require both sides of the dual-mode check to pass in order to clear the evaluation.
4. **Test Coverage:** 
   The original 9 tests were insufficient for a script heavily reliant on file I/O and cron execution. I expanded the test suite to 16 tests. The new tests explicitly cover concurrency (concurrent JSONL appending), malformed files (missing YAML frontmatter, corrupt eval defs), and cron failure isolation.
5. **Nightly Cron Risks:** 
   - **File Lock Races:** Multiple nightly processes or manual interventions could write to the `.claude/state/skill-eval-results/YYYY-MM-DD.jsonl` simultaneously. Phase 2a now mandates using `flock` or atomic appends.
   - **3 AM Quota / API Limits:** Eliminated by Plan Decision ② (static validation only).
   - **CLI Version Drift:** The nightly scripts should use explicit paths to dependencies (e.g., `yq` or `jq`) and verify their presence at the start of the script to prevent silent failures if environment paths drift during cron execution.
