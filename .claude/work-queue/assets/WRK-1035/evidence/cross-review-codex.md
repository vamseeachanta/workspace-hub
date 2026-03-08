# Cross-Review: Codex
> WRK-1035 | 2026-03-08

## Verdict: MINOR

The plan is technically sound and the implementation sequence is coherent. All 14 gaps map
directly to real deficiencies confirmed in the current codebase. The scope is large but
correctly bounded — the phasing and parallelisation notes prevent the most dangerous
merge-conflict scenarios. Several minor issues need resolution before implementation begins.

---

## Findings

### P2-MINOR — Phase 3, Gap 3: Elapsed-time rule conflicts between plan and resource-intelligence

**Plan section:** Phase 3, gap 3 (line 163) states the minimum is **300s** for Stages 5, 7,
and 17.

**Resource-intelligence.yaml** (gap 3, line 167–168) states the minimum is **60s for plan
stages** and **300s for close**. These are different numbers for the same check.

The user-review-plan-draft.yaml artifact for WRK-1035 itself records
`elapsed_time_minimum: 300s for all hard-gate stages (5, 7, 17)` — this matches the plan,
not the resource-intelligence.

**Impact:** If the implementation follows the plan (300s for all gates), any fast-moving
session where the user approves within 5 minutes but over 60s will pass the resource-intel
spec but fail the verifier. Conversely if 60s is used for plan stages, the plan narrative
is inconsistent with the implementation.

**Resolution required:** Pin the canonical value to **300s for all three gates (5, 7, 17)**
in both the plan and in the tests (T15, T16, T17). Update the resource-intelligence.yaml
gap 3 description to match. Document the rationale: 300s = minimum realistic human review
time for any gate, not just close.

---

### P2-MINOR — Phase 3, Gap 3: False-positive risk on legitimate fast sessions not addressed

**Plan section:** Phase 3, gap 3; Risks section (absent for this specific check).

The 300s elapsed-time rule between `opened_at` (browser-open YAML) and `reviewed_at`
(approval YAML) will produce false positives in at least two legitimate scenarios:

1. **Re-review sessions**: User opened HTML in an earlier session (large `opened_at` gap),
   then in a new session approves after reading the already-open browser tab. The delta will
   be calculated as very large — no false positive in this direction — but if `opened_at` is
   re-written at each session start, the delta would reset and a quick approval after context
   reload would falsely fail.

2. **Multi-tab / pre-read sessions**: User reads the plan directly in their editor before the
   browser-open event fires. They respond "approve" within 60s of the agent writing
   `browser-open.yaml`, but they read the plan for 10 minutes before the `xdg-open` call
   executed. The gate sees < 300s and fails despite genuine review.

**Impact:** No resolution currently in plan. This is flagged as MINOR because the user can
always add a WAIT-bypass, but the verifier will still FAIL on close for those WRKs unless
the bypass is also recorded in a way the verifier respects.

**Resolution required:** Add a `review_bypass_reason` field to approval artifacts that, when
non-empty AND reviewer is in the human allowlist, causes the elapsed-time check to emit WARN
instead of FAIL. Tests T15/T17 should add a bypass-path variant. Document in plan Risks.

---

### P2-MINOR — Phase 4, start_stage.py: "Stale future-stage artifact" detection is
session-scoped but no session boundary is available to the script

**Plan section:** Phase 4, start_stage.py bullet 5 (line 261–263):
"Scan for stale future-stage artifacts (any artifact in stages N+1..N+5 directories
written in **the current session**)."

**Current state of start_stage.py:** The script has no access to a session identifier or
session start timestamp. The stage contract YAMLs do not include `session_id` fields. The
only session boundary information lives in `activation.yaml` (`session_id`) and the
checkpoint (`checkpoint.yaml`), neither of which is currently read by start_stage.py.

**Impact:** Without session boundary knowledge, the script cannot distinguish "artifact
written in this session" from "artifact written in a prior session." If it checks file mtime
instead, a legitimate artifact written 2 hours ago in a long session would be flagged; an
artifact written 30s ago in a previous session would be missed.

**Resolution required:** Change the detection logic to: scan for artifact files in stages
N+1..N+5 that exist at ALL (not session-scoped). Emit WARNING for any found, regardless of
session. This is a stronger check (no false negatives) and does not require session tracking.
Update T35 to match: "stale future artifact exists → WARNING logged (regardless of session)."
Log the artifact path and mtime in the warning so the human can triage.

---

### P2-MINOR — Phase 3, Gap 12: Claim-path retirement changes break existing passing WRKs
that use `evidence/claim.yaml`

**Plan section:** Phase 3, gap 12 (line 185–186):
"retire legacy WARN exemption — all WRKs after WRK-285 produce PASS or FAIL on claim gate"

**Current state:** `check_claim_gate()` in verify-gate-evidence.py calls
`evidence_file(assets_dir, "claim.yaml", ["claim-evidence.yaml"])` — it accepts EITHER
`claim.yaml` OR `claim-evidence.yaml` as the canonical file, with fallback WARN only when
neither exists.

The plan says: legacy path (`evidence/claim.yaml`) → FAIL; canonical path
(`<assets_root>/claim-evidence.yaml`) → PASS. But the current code treats `claim.yaml` as
the primary search target, not the legacy one.

**Impact:** WRKs that were correctly closed with `evidence/claim.yaml` (the majority of
recent WRKs) will suddenly start FAILING if the plan's "retire legacy WARN" is implemented
as written. This would break the integration eval for WRK-1035 itself.

**Resolution required:** Clarify which path is "canonical" vs "legacy." Examining the
resource-intelligence.yaml (gap 12): the canonical path is `<assets_root>/claim-evidence.yaml`
(written by claim-item.sh). The `evidence/claim.yaml` naming was an earlier convention.
Before retiring, audit how many active and archived WRKs use each path. Keep WARN for
`evidence/claim.yaml` (not FAIL), and add PASS for `<assets_root>/claim-evidence.yaml`.
Only FAIL when NEITHER exists. Update T29 to reflect this three-state model.

---

### P3-SUGGESTION — Phase 3, verify-gate-evidence.py modularisation: sub-module import
strategy needs to account for `uv run --no-project` environment

**Plan section:** Phase 3, Risks (line 505–507):
"Mitigation: refactor verify-gate-evidence.py into sub-modules
(`checks/timestamp.py`, `checks/identity.py`, `checks/structure.py`)"

**Current state:** verify-gate-evidence.py uses `uv run --no-project python` invocation
(as confirmed by close-item.sh line 108). Sub-modules imported with relative imports
(`from checks.timestamp import ...`) work only when the parent directory is on `sys.path`.
The `uv run --no-project` invocation without a `pyproject.toml` does not add the script's
parent directory to `sys.path` automatically unless `sys.path` is manipulated explicitly.

**Impact:** If sub-modules are placed at `scripts/work-queue/checks/timestamp.py` and
imported via relative or absolute package import, the import will fail at runtime without
explicit `sys.path` insertion.

**Resolution required:** Either (a) use absolute `sys.path.insert(0, ...)` manipulation in
the main file's module-level bootstrap (as `verify-gate-evidence.py` already does for the
optional `yaml` import), or (b) keep all new check functions in the same file but split
into clearly named sections with `# ── SECTION ──` headers. Given the file is already
1208 lines, option (a) is preferable. Add a test that imports each sub-module via `uv run`
to catch this before deployment.

---

### P3-SUGGESTION — Phase 2, close-item.sh: `executed_at` future-check uses wall-clock
comparison but `executed_at` may be intentionally set to schedule completion time

**Plan section:** Phase 2, close-item.sh bullet (line 118):
"Assert `execute.yaml` exists and `executed_at` is in the past before invoking verifier"

**Edge case:** For long-running executions, `executed_at` may be set to a planned completion
time slightly in the future when the agent writes it optimistically. A strict "< current
time" check will block close for up to 60s after the agent writes the artifact.

**Resolution required:** Allow a ±120s tolerance window (not zero tolerance) for the
`executed_at` past-check, or define `executed_at` explicitly as "time tests were run" and
enforce that test log artifact mtime >= `executed_at - 60s`. Document the tolerance in the
template YAML comment.

---

### P3-SUGGESTION — Phase 1 + Phase 5: `/wrk-resume` "deprecation to diagnostic-only" is
under-specified and may confuse agents already calling it

**Plan section:** Phase 5, wrk-resume.md bullets (line 351–355)
"Add distinction: `/wrk-resume` = session-level context restore; `/work run` = execute
next stage; both complement each other; resume is always a pre-step before `/work run`
when resuming a broken session"

**Issue:** The plan's user-review-plan-draft.yaml notes
`checkpoint_schema: /wrk-resume deprecated to diagnostic-only` — but the plan body (Phase 5)
does NOT say deprecated; it says the two commands complement each other. This contradiction
between the approval artifact and the plan text could lead an implementing agent to remove
`/wrk-resume` functionality that is still needed.

**Resolution required:** Remove the word "deprecated" from the checkpoint notes in
user-review-plan-draft.yaml or add an explicit note in Phase 5 clarifying: "deprecated
means `exec-next-stage` removed from `/wrk-resume`; context-restore functionality
preserved." The implementing agent will read both files.

---

### P3-SUGGESTION — Phase 6, spawn-team.sh test T46: exit code 0 on `scope_approved: true`
but script is a bash file — test approach unclear

**Plan section:** Phase 6, test T46 (line 596):
"`spawn-team.sh` exits 0 when `scope_approved: true`"

**Issue:** spawn-team.sh is a bash script (45 lines). The test file is
`test_spawn_team.py` (Python). Testing shell script exit codes from Python requires
`subprocess.run()`. This is a valid pattern, but the test must:
(a) Create a temp directory with a fake WRK structure and `user-review-capture.yaml`
(b) Set `WORKSPACE_ROOT` or equivalent env var so spawn-team.sh finds the right WRK
(c) Handle the case where the script sources other scripts that may not exist in test fixtures

None of this is addressed in the plan's test spec. If the existing test infrastructure
for shell scripts (e.g. test_stage1_gate.py, test_retroactive_approval.py) uses subprocess,
this is fine — but if those are pure Python unit tests, the approach needs to be documented.

**Resolution required:** Add a note to the test spec for T45–T47 stating that
`test_spawn_team.py` tests spawn-team.sh via `subprocess.run()` with a minimal WRK fixture
directory, and that a `WORKSPACE_ROOT` override env var is used to isolate from live data.

---

## What is solid

- **Phase ordering is correct.** Phase 1 → Phase 2 → Phase 3 is the right sequence; the
  plan's cross-dependency note (gap 14 needs Phase 1's template) is accurate. Phase 5+6
  single-pass SKILL.md edit rule prevents merge conflicts.

- **Backward compatibility mitigation for timestamp ordering (gap 1) is well-designed.**
  The `--since-wrk` flag approach is the correct pattern, mirroring the existing
  `stage5-migration-exemption.yaml` mechanism. Applying new checks only to WRKs closed
  post-deployment avoids retroactive failures on archived items.

- **The verify-gate-evidence.py modularisation plan is correct in principle.** 1208 lines +
  14 new checks = ~1600+ lines in a single file is unworkable. The sub-module split aligns
  with the coding-style.md 400-line limit.

- **Phase 4 pre-work requirement is the right engineering decision.** Mandating a scope
  review of start_stage.py / exit_stage.py before writing code prevents premature
  architectural commitment. The scripts are currently straightforward and the new
  requirements fit naturally within their patterns (confirmed by reading the actual files).

- **Phase 3, gap 5 (sentinel value rejection) + claim-item.sh fix is correctly coupled.**
  Adding the verifier check without fixing claim-item.sh would cause an unresolvable FAIL
  on every machine lacking session-state.yaml. The plan correctly identifies this and
  includes the fix in Phase 2 scope.

- **Stage contract YAML files exist for all 20 stages** (confirmed via glob). The
  start_stage.py extension has a clean foundation: `stage-{N:02d}-*.yaml` glob is already
  implemented and working. Stages 5 and 17 already have `human_gate: true` in their
  contracts, so the WAIT instruction for human-gate stages just needs a check against the
  `human_gate` field — no new contract fields needed.

- **Test coverage (47 tests, 5 files) is realistic and complete** for the stated scope.
  Each test maps to a specific gap or behavior, with both PASS and FAIL path coverage.
  The integration eval (run verifier against WRK-1035 itself) is a strong dogfooding signal.

- **Phase 5 pruning rules are precise.** The distinction between "redundant → delete" vs
  "script-converted → one-line reference note" vs "new reference material → references/"
  eliminates the ambiguity that causes content loss in pruning passes.

- **Codex identity check (R-05 extension)** correctly handles the case where "codex" appears
  in a cross-review artifact written BY Claude mimicking Codex output. The `reviewer` field
  check provides a second signal independent of keyword presence.
