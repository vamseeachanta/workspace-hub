# WRK-1047 Plan Final — Harness Readiness: All Workstations

**Route B | Complexity: Medium | Orchestrator: Claude**
**Revised: 2026-03-08 — cross-review findings resolved (Claude MINOR, Codex MINOR, Gemini MINOR)**

---

## Objective

Every session on every workstation starts on a clean, verified harness so the team
spends 100% of session time on engineering — not debugging hooks, missing plugins, or
provider workflow failures.

---

## Cross-Review Finding Resolutions

| Finding | Provider | Severity | Resolution |
|---------|----------|---------|------------|
| `claude plugin list` unverified | Claude | P1 | **Confirmed valid** — command exists, parses name + status per plugin. Use required-set match, not count. |
| R-HOOK-LATENCY runs live hooks with side effects | Claude | P1 | **Replaced** with static analysis: check hook file size <200 lines + grep for blocking patterns (`git commit`, `curl`, `wget`, network calls). |
| R-PLUGINS count-based too brittle | Codex | P1 | **Fixed**: R-PLUGINS checks required plugin names from `harness-config.yaml`, ignores optional/extra plugins. |
| Cross-workstation report schema underspecified | Codex | P1 | **Fixed**: host-qualified file naming + explicit schema defined below. |
| licensed-win-1 manual-only defeats nightly mission | Gemini | P1 | **Fixed**: Windows Task Scheduler job writes YAML report to shared mount; compare-harness-state.sh reads it. |
| R-SKILLS baseline undefined | Claude | P2 | **Fixed**: baseline stored in `harness-config.yaml`; auto-set on first pass; updated via `--update-baseline` flag only. |
| No tests for Phase C/E | Claude | P2 | **Fixed**: T13–T16 added. |
| WRK-SIM non-numeric ID may fail validators | Claude/Codex | P2 | **Fixed**: Use `WRK-9999` (reserved fixture number). Verify-gate-evidence.py confirmed to accept numeric WRK IDs. |
| SSH failure || true masks real failures | Codex | P2 | **Fixed**: SSH failure → DEGRADED state emitted in report (not silent skip); surfaced in morning readiness output. |
| Hostnames hardcoded | Gemini | P2 | **Fixed**: all hostnames, paths, and baselines in `harness-config.yaml`. |
| harness-readiness-report.yaml schema unspecified | Claude/Codex | P3 | **Fixed**: schema defined explicitly below. |
| jq availability on licensed-win-1 unverified | Claude | P3 | **Fixed**: add R-JQ prerequisite check; graceful skip with install hint if absent. |
| R-PRECOMMIT doesn't verify hook executability | Codex | P3 | **Fixed**: check file is executable in addition to presence. |
| Phase D architecturally distinct | Claude | P3 | **Retained in WRK-1047** — simulation validates the harness tools end-to-end; bounded as distinct deliverable with clear ACs. |

---

## Resource Intelligence Summary

**Extend + wire, not rebuild:**

| Component | Status | Action |
|-----------|--------|--------|
| `nightly-readiness.sh` (11 checks) | ✅ exists | Extend with 6 new checks + update 2 existing |
| `ai-agent-readiness.sh` | ✅ exists | Reuse as-is (R-AI-CLI already wired) |
| `orchestrator-variation-check.sh` | ✅ exists | New WRK-9999 fixture; wire to cron |
| `parse-session-logs.sh` | ✅ exists | Reuse as-is |
| `sync-knowledge-work-plugins.sh` | ✅ exists | Wire into R-SKILLS |
| `claude plugin list` | ✅ confirmed | Parse by name; required-set from harness-config.yaml |

---

## harness-config.yaml Schema (committed before Phase A tests)

`scripts/readiness/harness-config.yaml`:

```yaml
schema_version: 1
required_plugins:
  - frontend-design
  - skill-creator
  - code-review
  - pr-review-toolkit
  - feature-dev
  - playground
  - pyright-lsp
  - claude-md-management
  - hookify
  - superpowers
skill_count_baseline: 0        # set on first --update-baseline run
command_count_baseline: 0      # set on first --update-baseline run
tier1_repos:
  - assetutilities
  - digitalmodel
  - worldenergydata
  - assethold
workstations:
  dev-primary:
    ws_hub_path: /mnt/local-analysis/workspace-hub
    ssh_target: null   # local
    report_path: .claude/state/harness-readiness-dev-primary.yaml
  dev-secondary:
    ws_hub_path: /mnt/workspace-hub
    ssh_target: ace2
    report_path: .claude/state/harness-readiness-dev-secondary.yaml
  licensed-win-1:
    ws_hub_path: null   # Windows; scheduled task pushes report to dev-primary
    ssh_target: null
    report_path: .claude/state/harness-readiness-licensed-win-1.yaml
prerequisites:
  - jq
  - git
  - uv
  - claude
```

## harness-readiness-report.yaml Schema

Host-qualified output at `.claude/state/harness-readiness-<hostname>.yaml`:

```yaml
schema_version: 1
host: dev-primary
generated_at: "2026-03-08T02:00:00Z"
overall: pass|fail|degraded
pass_count: N
fail_count: N
checks:
  R-JQ:           {status: pass|fail|skip, detail: ""}
  R-PLUGINS:      {status: pass|fail|skip, detail: "missing: [pyright-lsp]"}
  R-HOOKS:        {status: pass|fail|skip, detail: ""}
  R-HOOK-STATIC:  {status: pass|fail|skip, detail: "hooks/stop.sh: 312 lines (>200)"}
  R-SETTINGS:     {status: pass|fail|skip, detail: ""}
  R-UV:           {status: pass|fail|skip, detail: ""}
  R-PRECOMMIT:    {status: pass|fail|skip, detail: ""}
  R-HARNESS:      {status: pass|fail|skip, detail: "digitalmodel/CLAUDE.md: 24L"}
  R-SKILLS:       {status: pass|fail|skip, detail: "skill_count=142 < baseline=150"}
```

---

## Implementation Phases

### Phase A — Extend `nightly-readiness.sh` + commit `harness-config.yaml`

**New checks** (following existing `check_rN()` pattern):

| Check ID | Pass criterion |
|----------|---------------|
| R-JQ | `jq --version` exits 0; if absent → skip remaining JSON checks with install hint |
| R-PLUGINS | `claude plugin list` output contains all names from `required_plugins` in harness-config.yaml |
| R-HOOKS | Every path in `.claude/settings.json` `hooks:` block exists on disk |
| R-HOOK-STATIC | Each hook file: ≤200 lines AND no blocking patterns (`git commit`, `curl`, `wget`, `http://`, `https://`) |
| R-SETTINGS | `jq empty .claude/settings.json` exits 0 |
| R-UV | `uv --version` parses to ≥0.5.0 |
| R-PRECOMMIT | `.pre-commit-config.yaml` present in each tier-1 repo from harness-config.yaml; contains `legal-sanity-scan.sh`; file is executable |

**Extended checks:**
- **R-HARNESS**: scan tier-1 repos (from `harness-config.yaml tier1_repos`) for CLAUDE.md/AGENTS.md/CODEX.md/GEMINI.md >20 lines
- **R-SKILLS**: `sync-knowledge-work-plugins.sh --dry-run` exits 0; SKILL.md count ≥ baseline; command count ≥ baseline; no `_diverged/` or `incoming/` leftovers

### Phase B — Host-qualified YAML output + comprehensive-learning signal

`nightly-readiness.sh` emits `.claude/state/harness-readiness-<hostname>.yaml` per schema above.

`comprehensive-learning-nightly.sh` Phase 1 reads local host report and emits:
`{event: "harness_readiness", host, overall, pass_count, fail_count, ts}`.

`--update-baseline` flag: when passed, sets `skill_count_baseline` and `command_count_baseline`
in `harness-config.yaml` to current counts. Must be run manually after legitimate skill additions.

### Phase C — `compare-harness-state.sh` (cross-workstation diff)

`scripts/readiness/compare-harness-state.sh`:
1. Run `nightly-readiness.sh` locally → local YAML report
2. SSH to dev-secondary (target from harness-config.yaml): run readiness check, `scp` report back
   - SSH failure → emit `overall: degraded` for that host; surface in diff output (NOT silent skip)
3. licensed-win-1: Windows Task Scheduler job runs Git Bash `nightly-readiness.sh` nightly and
   writes YAML to a path visible from dev-primary (shared mount or scp). compare-harness-state.sh
   reads that file if present; emits `degraded` if stale (>25h old).
4. Print unified diff table: per check ID, per host, pass/fail/degraded

### Phase D — WRK-9999 fixture + 3-provider simulation

`tests/work-queue/fixtures/WRK-9999/` — reserved fixture number; pre-populated evidence for
all 20 stages using valid YAML per each stage's schema contract.

`tests/work-queue/test-workflow-simulation.sh`:
```bash
for provider in claude codex gemini; do
  bash scripts/review/orchestrator-variation-check.sh \
    --wrk WRK-9999 --orchestrator "$provider" \
    --scripts \
      "uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-9999" \
      "bash tests/work-queue/test-lifecycle-gates.sh" \
      "bash scripts/readiness/nightly-readiness.sh"
done
bash scripts/work-queue/parse-session-logs.sh WRK-9999
```

Provider differences documented:
- Codex: `--scripts` flag only (no interactive mode via SSH pipe)
- Gemini: JSON output format; `parse-session-logs.sh` handles via native store path

Added to nightly cron after first successful run.

### Phase E — `remediate-harness.sh`

`scripts/readiness/remediate-harness.sh --workstation <name>`:
- Reads `harness-readiness-<name>.yaml`
- Per FAIL check, prints exact fix command (does not execute)
- Covers: plugin install, hook restore from git, settings.json repair, uv install, pre-commit add, baseline update
- licensed-win-1: Windows fix commands in Git Bash syntax; Task Scheduler setup documented in `scripts/work-queue/templates/licensed-win-1-task-scheduler.xml`

---

## TDD Strategy (16 tests)

| Test | Scenario | Expected |
|------|----------|---------|
| T1 | All checks pass | exit 0; report overall=pass |
| T2 | Required plugin missing from `claude plugin list` output | R-PLUGINS FAIL |
| T3 | Extra unlisted plugin present | R-PLUGINS PASS (required-set only) |
| T4 | Oversized CLAUDE.md in tier-1 repo | R-HARNESS FAIL |
| T5 | Hook file absent from disk | R-HOOKS FAIL |
| T6 | Hook file contains `git commit` pattern | R-HOOK-STATIC FAIL |
| T7 | Hook file >200 lines | R-HOOK-STATIC FAIL |
| T8 | settings.json invalid JSON | R-SETTINGS FAIL |
| T9 | uv absent from PATH | R-UV FAIL |
| T10 | pre-commit missing legal entry | R-PRECOMMIT FAIL |
| T11 | SKILL.md count below baseline | R-SKILLS FAIL |
| T12 | command count below baseline | R-SKILLS FAIL |
| T13 | SSH to dev-secondary unreachable | compare-harness-state.sh: dev-secondary = degraded; no crash |
| T14 | Stale licensed-win-1 report (>25h old) | compare-harness-state.sh: licensed-win-1 = degraded |
| T15 | remediate-harness.sh reads report with R-PLUGINS FAIL | prints `claude plugin install pyright-lsp` |
| T16 | harness-readiness-report.yaml schema validation | all required fields present, correct types |

---

## Execution Order

```
commit harness-config.yaml (before any Phase A tests)
  → Phase A (T1–T12 TDD → extend nightly-readiness.sh)
  → Phase B (YAML output + comprehensive-learning signal)
  → Phase C (T13–T14 TDD → compare-harness-state.sh)
  → Phase D (WRK-9999 fixture → simulation → nightly cron)
  → Phase E (T15–T16 TDD → remediate-harness.sh)
```

## Phase-Level Acceptance Criteria

| Phase | Done when |
|-------|-----------|
| A | `nightly-readiness.sh` gains 7 new check functions; all T1–T12 pass on dev-primary |
| B | `harness-readiness-dev-primary.yaml` written after nightly run; comprehensive-learning emits signal row |
| C | `compare-harness-state.sh` produces diff table; T13/T14 pass; licensed-win-1 Task Scheduler template committed |
| D | `variation-test-results-{claude,codex,gemini}.md` all PASS; simulation in nightly cron |
| E | `remediate-harness.sh` prints correct fix for ≥3 failure types; T15/T16 pass |

---

## Risks / Dependencies

| Risk | Mitigation |
|------|-----------|
| Codex interactive mode unavailable via SSH | Use --scripts flag; documented in Phase D |
| dev-secondary SSH unavailable at cron time | DEGRADED state (not skip); surfaced in diff output |
| licensed-win-1 no automated SSH | Task Scheduler + shared mount; stale-report detection |
| jq absent on licensed-win-1 | R-JQ check first; graceful skip with install hint |
| Plugin output format may change | Parse by name substring match, not exact line format |
| WRK-9999 fixture frontmatter must be valid | Build via exit_stage.py scaffolding for each stage |

---
*Plan final: 2026-03-08 | Route B | Stage 6 cross-review findings resolved*
