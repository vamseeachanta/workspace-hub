# Plan for #2475: licensed OrcaWave/OrcaFlex native load-run proof protocol

> **Status:** draft (v3 — review MAJORs partially addressed; approval blocked pending provider-runner fix and re-review)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2475
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2475-claude.md | scripts/review/results/2026-04-23-plan-2475-codex.md | scripts/review/results/2026-04-23-plan-2475-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/solver/process-queue.py` — licensed-win-1 queue processor for OrcaWave and OrcaFlex jobs; writes `result.yaml`, moves jobs to `queue/completed/` or `queue/failed/`, and can export OrcaWave `.xlsx` sidecars.
- Found: `scripts/solver/submit-job.sh` — dev-primary job submitter; creates `queue/pending/<timestamp>-<name>.yaml`, commits, and pushes.
- Found: `scripts/solver/queue-health.sh` — reports pending/completed/failed queue health and git pull failures.
- Found: `queue/job-schema.yaml` — documented queue schema with required `solver` and `input_file`, optional `export_excel`, `description`, `submitted_by`, `submitted_at`.
- Found: `docs/architecture/solver-queue.md` — architecture: dev-primary pushes pending YAML, licensed-win-1 polls every 30 minutes, OrcFxAPI executes, results return via git.
- Found: `docs/plans/licensed-win-1-execution-guide.md` — machine-specific guide: licensed-win-1 has Python/Git Bash/OrcFxAPI/Claude/Codex/Gemini, no Hermes/uv, use `python` not `uv run`.
- Found: `docs/plans/licensed-win-1-session-3-prompts.md` — prior detailed prompt patterns for OrcaWave `.owr` fixtures and OrcaFlex validation.
- Gap: no current protocol artifact defines the semantic-proof load/run evidence bundle for PR #528 fixtures and next-wave proof issues.

### Standards
| Standard / contract | Status | Source |
|---|---|---|
| Solver queue architecture | active | `docs/architecture/solver-queue.md` |
| Licensed-win-1 execution constraints | active | `docs/plans/licensed-win-1-execution-guide.md` |
| OrcaWave/OrcaFlex machine boundary | active | `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` |
| Queue job schema | active but minimal | `queue/job-schema.yaml` |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/entities/solver-queue.md` is referenced from the index as the durable queue entity page.
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` documents the handoff flow but not native load/run proof protocol.
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` and `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` are supporting links for the protocol, but the protocol artifact itself should live in `docs/plans/` or `docs/solver/` rather than only wiki pages because it is an execution prompt/proof contract.

### Documents consulted
- Issue #2475 — asks for a licensed-machine protocol proving generated native inputs can load/run and return durable evidence.
- `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` — states deterministic semantic tests do not prove licensed applications load/run generated native inputs.
- `docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md` — identifies #2475 as one of the first next-wave planning targets.
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — explicitly separates dev-primary work from licensed-machine validation.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md`, `docs/plans/2026-04-23-issue-2455-rigid-jumper-plet-to-plem-semantic-proof.md`, and `docs/plans/2026-04-23-issue-2456-lazy-wave-riser-semantic-proof.md` — first-wave proof plan context.
- Related issues #1586/#1595/#1650/#1763/#1764/#1788/#1789 — existing queue/fixture/proof context.

### Gaps identified
- No single protocol lists which PR #528 proof fixtures are eligible for licensed load/run, how to generate native files, which command shape to run on licensed-win-1, and what evidence files to return.
- Existing `queue/job-schema.yaml` does not encode semantic-proof metadata such as source issue, expected solver, fixture family, or evidence checklist. This issue should not necessarily change schema yet; it must first define the protocol and evidence contract.
- Existing licensed prompts are fixture-generation oriented, not semantic-proof evidence-bundle oriented.
- The protocol needs to distinguish semantic failure from solver-version/default differences and unrelated environment failures.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2475` — OPEN — licensed load-run proof protocol
- `#2476` — OPEN — semantic-equivalence contract/cookbook
- `#2455/#2456/#2457` — CLOSED — first-wave deterministic proofs merged via digitalmodel PR #528
- `#1586` — OPEN — solver queue hardening remains active
- `#1595` — CLOSED — submit-batch/watch-results queue tooling landed
- `#1650` — OPEN — queue schema enforcement remains future work
- `#1763/#1764` — CLOSED — prior licensed fixture generation work
- `#1788/#1789` — OPEN — remaining licensed fixture/snapshot tasks

**File existence** (verified 2026-04-24):
- EXISTS: `scripts/solver/process-queue.py`
- EXISTS: `scripts/solver/submit-job.sh`
- EXISTS: `scripts/solver/queue-health.sh`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `docs/architecture/solver-queue.md`
- EXISTS: `docs/plans/licensed-win-1-execution-guide.md`
- EXISTS: `docs/plans/licensed-win-1-session-3-prompts.md`
- MISSING (new): `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md`
- MISSING (new): `docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md`

**Line excerpts**:
- `docs/architecture/solver-queue.md` lines 11-12: licensed-win-1 polls via git, runs OrcFxAPI, and pushes completed/failed results.
- `scripts/solver/process-queue.py` lines 151-158: requires `solver` and `input_file`; lines 181-183 route to `run_orcawave` or `run_orcaflex`; lines 189-198 write result metadata.
- `queue/job-schema.yaml` lines 12-20: minimal required/optional job schema.
- `docs/plans/licensed-win-1-execution-guide.md` lines 3-7: licensed-win-1 has OrcFxAPI and agent CLIs, but not Hermes; lines 103-112 require `python` not `uv run`.

Source count: 10+ distinct sources consulted.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2475-licensed-load-run-proof-protocol.md` |
| Protocol doc | `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md` |
| Licensed-machine prompt | `docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md` |
| Evidence manifest template | `docs/solver/templates/semantic-proof-evidence-manifest.yaml` |
| Existing execution guide update | `docs/plans/licensed-win-1-execution-guide.md` |
| Plan index | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2475-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2475-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2475-gemini.md` |

---

## Deliverable

A self-contained licensed-win-1 proof protocol and execution prompt that define how to load/run OrcaWave/OrcaFlex native inputs generated from semantic-proof fixtures, what evidence artifacts to return, and how to classify failures without expanding structure-family implementation scope.

---

## Pseudocode

```text
create protocol doc:
    define proof levels: deterministic semantic proof, licensed load proof, licensed run proof, evidence bundle accepted
    list eligible first-wave fixtures with explicit sources: L03 OrcaWave (#2457), PLET-to-PLEM (#2455), lazy-wave and steep-wave riser variants (#2456)
    define proof levels and dispatch criteria:
        load-only proof = required for every fixture; bounded native file open/import without time-domain solve
        run proof = allowed only when fixture has a documented short analysis duration or OrcaWave frequency/heading grid small enough for an expected <15 minute wall-clock run
        skip-run classification = required when runtime bounds are unknown, fixture is binary-only, or missing inputs block safe execution
    define evidence bundle fields: machine, solver version, OrcFxAPI version, git SHAs, input paths, output paths, result.yaml when queue is used, logs, screenshots/exports where available
    define evidence authoring ownership: the licensed-win-1 prompt writes the evidence manifest directly after each command; process-queue.py result.yaml remains an input/source, not the only evidence emitter
    define classification matrix: semantic mismatch, solver-version/default drift, missing license/API, missing input artifact, unrelated environment failure, runtime/disk guard exceeded
    define GitHub linkage: PR #528, issues #2455-#2457, issue #2475, follow-up issues #2472-#2474

create licensed-win-1 prompt:
    prerequisites: git pull workspace-hub and digitalmodel; python imports OrcFxAPI/yaml/openpyxl/numpy; if yaml/openpyxl/numpy are missing, install them with python -m pip install pyyaml openpyxl numpy
    run read-only discovery first: verify generated native input files exist or document missing generation step
    for each eligible fixture:
        attempt native load
        attempt minimal calculate/run only when safe and bounded
        export logs/result metadata/evidence manifest
    commit only docs/evidence artifacts or comment-only if protocol chooses not to commit binary outputs
    post concise GitHub comment with pass/fail table and returned artifact paths

create evidence manifest template:
    schema fields for solver, fixture, issue, command, expected input, outputs, versions, verdict, failure_class
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md` | Durable protocol and failure-classification matrix |
| Create | `docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md` | Self-contained prompt for licensed-win-1 execution |
| Create | `docs/solver/templates/semantic-proof-evidence-manifest.yaml` | Reusable evidence bundle template; creates missing parent directory `docs/solver/templates/` |
| Modify | `docs/plans/licensed-win-1-execution-guide.md` | Add a discoverable entry pointing licensed-win-1 operators to the new semantic-proof prompt |
| Modify | `docs/plans/README.md` | Add plan index row |
| No change | `scripts/solver/process-queue.py` | Protocol first; the licensed-machine prompt will write the richer evidence manifest manually from command output and git metadata. Queue `result.yaml` remains supporting evidence only. Queue code/schema upgrades belong to #1650 unless later approved. |
| No change | `queue/job-schema.yaml` | Schema enforcement is tracked separately by #1650 unless this plan is explicitly expanded after review |
| No change | `digitalmodel/src/**` | No solver code changes in this protocol issue |

---

## TDD / Validation List

| Check | What it verifies | Command / input | Expected output |
|---|---|---|---|
| protocol_exists | protocol doc exists | `test -f docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md` | exists |
| prompt_exists | licensed-machine prompt exists | `test -f docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md` | exists |
| manifest_template_valid_yaml | manifest template parses | `uv run --no-project python -c "import yaml; yaml.safe_load(open('docs/solver/templates/semantic-proof-evidence-manifest.yaml'))"`` | no exception |
| prompt_self_contained | prompt includes all required anchors, not just any one anchor | `for pat in OrcFxAPI "python -m pip install" "#2475" "#2455" "#2456" "#2457" "Evidence manifest" "Return format"; do grep -q "$pat" docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md || exit 1; done` | all anchors found |
| protocol_classification_matrix | protocol includes all failure classes and proof-level distinctions | `for pat in "semantic mismatch" "solver-version/default drift" "unrelated environment failure" "load-only proof" "run proof" "skip-run"; do grep -q "$pat" docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md || exit 1; done` | required terms found |
| no_implementation_scope_creep | no solver code or digitalmodel source changed | `git diff --name-only origin/main...HEAD -- docs/plans docs/solver scripts/solver queue digitalmodel/src digitalmodel/tests` | only docs/plans and docs/solver files for this issue |
| markdown_links | referenced local files and issue anchors are present or explicitly external | `for pat in "docs/solver/orcawave-orcaflex-native-load-run-proof-protocol" "licensed-win-1-semantic-proof-load-run-prompt" "semantic-proof-evidence-manifest" "#2475" "#2455" "#2456" "#2457"; do grep -R -q "$pat" docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md || exit 1; done` | required anchors found |

---

## Acceptance Criteria

- [ ] Protocol doc defines proof levels, eligible first-wave fixtures, evidence bundle shape, and failure-classification matrix.
- [ ] Licensed-win-1 prompt is self-contained, discoverable from `licensed-win-1-execution-guide.md`, and uses machine-appropriate commands (`python`, not `uv run`; no Hermes assumption).
- [ ] Evidence manifest template exists and is valid YAML.
- [ ] Protocol explicitly distinguishes deterministic semantic proof from licensed load/run proof.
- [ ] Protocol does not modify queue code or digitalmodel implementation under this issue unless plan review explicitly requires it before approval.
- [ ] Validation checks above pass.
- [ ] Plan review artifacts exist, are non-empty, contain an explicit `## Verdict` line with APPROVE/MINOR/MAJOR/UNAVAILABLE, and contain no MAJOR blocker before approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (r2) | Review-runner evidence state inconsistent, artifact-map date drift, vacuous review-artifact acceptance, and validation-command issues. Plan-local issues addressed in v3 where applicable. |
| Codex | UNAVAILABLE (r1/r2) | `codex exec --no-interactive` wrapper incompatibility; substantive Codex review blocked by review-runner issue outside this plan. |
| Gemini | MAJOR (r2) | Regex checks used `grep -E` alternatives instead of asserting all anchors; manifest YAML command quoting was invalid. Addressed in v3. |

**Overall result:** not approval-ready — fresh re-review required after provider-runner/package issues are fixed or explicitly waived by policy. Provider-runner hardening is tracked by #2477.

---

## Risks and Open Questions

- **Risk:** The protocol may need generated native input files that are not currently committed. Mitigation: prompt starts with discovery and returns a missing-input classification rather than fabricating proof.
- **Risk:** Queue job schema may be too weak for evidence metadata. Mitigation: keep schema edits out of scope unless review says they are mandatory; otherwise file follow-up under #1650.
- **Risk:** Licensed solver execution can be slow, consume disk, or block the queue if full runs are not bounded. Mitigation: protocol separates load-only smoke from run smoke and requires explicit bounded commands.
- **Risk:** Binary solver artifacts may be too large for git. Mitigation: evidence manifest/logs are primary; binary outputs are committed only if size policy allows and are otherwise summarized with paths/hashes.
- **Open:** Whether #2475 should include the first actual licensed run, or only define the protocol and prompt. Default: define protocol + prompt; first execution can happen after approval, with returned evidence under the same issue if bounded.

---

## Complexity: T2

Docs/protocol/prompt issue with high engineering impact and licensed-machine constraints; no source-code implementation planned.
