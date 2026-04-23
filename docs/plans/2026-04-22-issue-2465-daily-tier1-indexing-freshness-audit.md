# Plan for #2465: daily tier-1 indexing freshness audit and scorecard refresh

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2465
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2465-claude.md | scripts/review/results/2026-04-22-plan-2465-codex.md | scripts/review/results/2026-04-22-plan-2465-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/knowledge/registry-freshness-check.py` — existing freshness-check pattern that ingests YAML registries and emits a structured freshness report. This is the closest architectural analog and a sound template for tone/structure, though it is not a drop-in dependency for tier-1 indexing.
- Found: `scripts/cron/` — hosts ~20 tracked cron scripts (e.g., `architecture-scan-weekly.sh`, `control-plane-drift.sh`, `coverage-drift-report.sh`, `broken-windows-sweep.sh`, `comprehensive-learning-nightly.sh`). This is the established home for scheduled maintenance, but **this plan does NOT introduce a new script there**; scope boundaries below explain why.
- Found: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — baseline portfolio scorecard.
- Found: `docs/reports/tier-1-indexing-freshness-latest.md` — active freshness report, already claiming `Scheduled job: tier1-indexing-daily (aefef5167f2f) at 30 3 * * *`.
- Found: `tests/docs/test_banned_stale_references.py`, `tests/docs/test_staleness_scanner.py`, `tests/quality/test_check_doc_drift.py` — existing doc-hygiene / staleness regression tests; the freshness audit's concept of "stale reference detection" should reuse this language and not reinvent a new one.
- Gap: no dedicated script that implements the tier-1 indexing freshness audit logic as a single callable target (not `registry-freshness-check.py`, which targets different inputs).
- Gap: no pytest that asserts the daily freshness artifact has been refreshed within the expected cadence.
- Gap: no canonical source document that defines what the daily audit checks, what counts as pass/fail, and what escalation means.

### Standards

| Standard | Status | Source |
|---|---|---|
| Tier-1 indexing and code-placement contract | proposed under #2460 (this audit's rule source) | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Control-plane entry point rule | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Data placement boundary | existing baseline | `docs/standards/DATA_PLACEMENT.md` |
| Cron-health evidence-line contract | existing baseline (#2291) — this audit must emit a conforming evidence line | `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` |
| Freshness-cadences registry | existing baseline (#2105) — this audit must register or cite a daily cadence entry | `data/document-index/freshness-cadences.yaml` |
| Scheduled-tasks canonical source-of-truth | existing baseline — new cron entries MUST be declared in this YAML (per `scripts/cron/crontab-template.sh` HARD RULE) | `config/scheduled-tasks/schedule-tasks.yaml` |

### LLM Wiki pages consulted

- Not applicable — this is harness/documentation automation, not a domain-knowledge issue.

### Documents consulted

- GitHub issue #2465 — scope: daily audit, self-contained + local-safe, checks canonical entry points + operator maps + registry references + source-hygiene drift, writes/refreshes a daily freshness artifact, avoids legacy product-doc reference patterns.
- `docs/reports/tier-1-indexing-freshness-latest.md` — already names a scheduled job id and cadence. This plan treats that as a pre-existing remote scheduler routine state, not as authoritative evidence that the audit *implementation* exists. Checked: no `scripts/cron/tier1-indexing-daily*` file exists in the repo tree; the routine id (`aefef5167f2f`) matches the remote-scheduler naming pattern used elsewhere in the ecosystem.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — "Daily Maintenance Requirement" section explicitly calls for a daily curation job. This is the authority the plan implements.
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — defines *what* the canonical routing surfaces are. #2465 is the freshness loop over those surfaces; it has no content of its own beyond monitoring them.
- Sibling plans #2461 (assetutilities), #2462 (digitalmodel), #2463 (aceengineer-website), #2464 (workspace-hub index split) — define the per-repo implementations the freshness audit must cover once executed.
- Memory `project_daily_readiness_cron.md` — confirms the ecosystem uses remote scheduler routines (e.g., `trig_019GWtRosbZ9rw1HxrGpsvy9`) rather than only on-disk cron files, so the freshness report's claim of a scheduled `aefef5167f2f` routine is credible pre-existing state, not a fabrication.
- **`.claude/rules/` (coding-style.md, patterns.md, README.md)** — harness-class source required by the retrieval-contract union (this issue is labeled `cat:harness` AND `cat:automation`). `patterns.md` "Enforcement Gradient" (Level 0 prose → Level 1 micro-skill → Level 2 script → Level 3 hook) positions this audit at Level 2: it is a script with binary exit signaling, NOT a hook. `coding-style.md` "Path Handling" rule mandates the audit script use `$(git rev-parse --show-toplevel)` or `${REPO_ROOT}` from `cadence-common.sh`, never hardcoded absolute paths.
- **`config/agents/` (ai-agents-registry.json, routing-config.yaml, behavior-contract.yaml, drift-policy.yaml)** — harness-class source required by the retrieval-contract union. Evidence: `grep -rni "tier.1.indexing\|TIER1_INDEXING\|tier-1.indexing" config/agents/ .claude/rules/` returned zero matches on 2026-04-22, confirming no agent-routing dependency on a per-repo tier-1 indexing surface. The audit therefore does not need to cross-wire into `config/agents/`.
- **`scripts/cron/lib/cadence-common.sh`** — cadence library sourced by every daily/weekly/quarterly cron script in `scripts/cron/`. Provides `cadence_init_repo_root` (resolves `REPO_ROOT`) and `cadence_period daily` (resolves current `YYYY-MM-DD` date string). The new script MUST source this library to match existing cron conventions.
- **`scripts/cron/crontab-template.sh`** — authoritative reference confirming `config/scheduled-tasks/schedule-tasks.yaml` is the single source of truth for cron entries: *"HARD RULE: all cron/task-scheduler entries must be declared here. Do NOT edit cron entries here — edit schedule-tasks.yaml instead."* Any plan claiming "daily scheduled job exists" as a deliverable must include a `schedule-tasks.yaml` entry.
- **#2291 cron-health evidence-line contract** (`docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md`) — establishes the format `task=<id> status=<color> artifact=<path> log=<path> ts=<iso8601>` consumed by the cron-health dashboard. The audit MUST emit one conforming line at end-of-run or it will be invisible to the dashboard.
- **#2105 freshness-cadences and staleness signals** (`docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md` + `data/document-index/freshness-cadences.yaml`) — governs how freshness checks register their cadence and expected-age thresholds. The audit must register a daily cadence entry or cite an existing entry that applies.

### Gaps identified

- No on-disk implementation of the audit logic matching the freshness report's claim of a daily routine.
- No canonical definition of what the audit checks, what the pass/fail thresholds are, or what counts as escalation.
- No regression test confirming the daily freshness artifact has been refreshed on cadence.
- No explicit guarantee that the audit uses canonical routing surfaces only (not noisy inventories like `docs/CONTENT_INDEX.md`).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):
- `#2465` — OPEN — `feat(automation): daily tier-1 indexing freshness audit and scorecard refresh`
- `#2460` — OPEN — contract dependency
- `#2461`, `#2462`, `#2463`, `#2464` — OPEN — per-repo remediation targets this audit will monitor after they land

**File existence** (from direct `ls` on 2026-04-22):
- EXISTS: `scripts/knowledge/registry-freshness-check.py` (analog only, not a dependency)
- EXISTS: `scripts/cron/` (20+ existing scripts, none named `tier1-indexing-daily`)
- EXISTS: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- EXISTS: `docs/reports/tier-1-indexing-freshness-latest.md`
- MISSING (new — this plan proposes): `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md` — audit definition / contract doc
- MISSING (new — this plan proposes): `scripts/cron/tier1-indexing-daily.sh` OR `scripts/automation/tier1-indexing-freshness-audit.py` (placement decided at implementation time)
- MISSING (new — this plan proposes): `tests/docs/test_tier1_indexing_freshness_audit.py` — regression test for artifact cadence + audit definition coverage
- MISSING on disk (pre-existing remote state): matching cron file for the scheduler routine `aefef5167f2f` — this plan explicitly does not rely on that remote state being preserved; implementation must guarantee the audit can run locally without it.

**Gap proofs**:
- `ls scripts/cron/tier1-indexing-daily* 2>&1` → "No such file or directory" → confirms no on-disk cron target yet.
- `ls scripts/automation/ 2>&1 | head` → not inspected in this draft (no forbidden-path assumption made); implementation may create the script in either `scripts/cron/` or `scripts/automation/`.
- `grep -r "tier-1-indexing-freshness" scripts/ 2>&1 | head` → no matches outside report reference, confirming the audit logic does not yet live in repo code.

<!-- Verification: 7 distinct sources consulted (issue body + scorecard + freshness report + contract plan + three sibling plans + control-plane standard + existing analog script). Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md` |
| Audit contract doc | `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md` |
| Audit implementation | `scripts/cron/tier1-indexing-freshness.sh` (bash, sources `scripts/cron/lib/cadence-common.sh`; locked placement matching daily-cron convention of `control-plane-drift.sh`, `broken-windows-sweep.sh`, `coverage-drift-report.sh`) |
| Scheduled-tasks YAML entry | `config/scheduled-tasks/schedule-tasks.yaml` (append one `tier1-indexing-freshness` task block; existing tasks unchanged) |
| Daily freshness output | `docs/reports/tier-1-indexing-freshness-latest.md` (overwritten atomically) + dated snapshot `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md` |
| Log output | `logs/freshness/tier-1-indexing-freshness-YYYY-MM-DD.log` |
| Cadence registration | `data/document-index/freshness-cadences.yaml` (register the new daily cadence or cite an applicable existing entry per #2105) |
| Regression test | `tests/docs/test_tier1_indexing_freshness_audit.py` AND `tests/scripts/cron/test_tier1_indexing_freshness.py` (test the audit-definition contract doc and the script behavior respectively) |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2465-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2465-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2465-gemini.md` |

---

## Deliverable

One sentence: a daily, fully local, idempotent audit (implementation + contract doc + regression test) that checks each tier-1 repo's canonical routing triad (`AGENTS.md`, `README.md`, `docs/README.md`), its operator map, and its source-hygiene state, and overwrites `docs/reports/tier-1-indexing-freshness-latest.md` with the result — never relying on noisy inventories and never introducing references to product-doc files that do not exist.

---

## Pseudocode

```text
function audit_tier1_indexing_freshness():
    tier1_repos = read from docs/BUSINESS_BRAIN.md
                  # expected set today: workspace-hub, digitalmodel, assetutilities, aceengineer-website
    for each repo in tier1_repos:
        record presence:
            <repo>/AGENTS.md exists
            <repo>/README.md exists
            <repo>/docs/README.md exists
            <repo>/docs/maps/<repo>-operator-map.md exists  (best-effort; missing is a finding, not a crash)
        record source-hygiene drift:
            backup artifacts under <repo>/src/ or <repo>/<package>/ (e.g., *.bak, *.orig)
            runtime/cache noise under tracked source paths
        record legacy-reference drift (canonical routing surfaces only):
            scan AGENTS.md, README.md, docs/README.md, operator map
            flag any reference to a file that does not exist in the repo
            flag any block that advertises a deployment target or workflow file that does not exist
        derive per-repo status: green | yellow | red
            green  = all four triad surfaces present, no source-hygiene drift, no broken active references
            yellow = at least one surface missing or minor drift
            red    = multiple surfaces missing or tracked backup artifacts under source paths

    compose portfolio status:
        green   only if every repo is green
        yellow  if any repo is yellow and none are red
        red     if any repo is red

    write docs/reports/tier-1-indexing-freshness-latest.md with:
        generated-at timestamp
        per-repo status + concrete findings
        portfolio status
        explicit "uses canonical routing surfaces only" disclaimer
        scheduled-job metadata (routine id + cadence) pulled from input, not hardcoded

    exit code (three-level, matches sibling-cron convention in control-plane-drift.sh):
        0 if portfolio status is green
        1 if portfolio status is yellow (at least one repo has drift, nothing critical)
        2 if portfolio status is red (at least one required surface missing OR a legacy product-doc reference present OR the #2460 contract file missing)
        This lets the cron-health dashboard (#2291) distinguish "nothing wrong" from "drift detected" from "escalate now" without parsing the artifact body.

    emit cron-health evidence line (#2291 contract):
        task=tier1-indexing-freshness status=<green|yellow|red> artifact=<OUT_LATEST> log=<LOG> ts=<iso8601>

    on contract-missing (docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md not yet created by #2460):
        write report with status=red and clear error message
        emit evidence line with status=red reason=contract-missing
        exit 2  # do NOT substitute an internal copy of the rule set — that drift-source is worse than failing loudly
    
    on red portfolio:
        prepend report header with a single-line "Action required: <count> tier-1 repo(s) have missing required surfaces or legacy references. See per-repo findings below."

function scope_boundaries():
    # negative authority
    MUST NOT import or validate docs/CONTENT_INDEX.md or any raw inventory as canonical authority
    MUST NOT crawl /mnt/ace/data/, /mnt/local-analysis/, or remote storage
    MUST NOT make any network call
    MUST NOT modify source code in any tier-1 repo
    MUST NOT write outside of docs/reports/
    MUST fail closed if BUSINESS_BRAIN.md tier-1 set is missing or unreadable

function regression_guard():
    assert docs/reports/tier-1-indexing-freshness-latest.md was modified within the last 26 hours on trunk
      # 26h window accommodates schedule jitter and DST without letting stale reports slip by
    assert the report references all tier-1 repos named in BUSINESS_BRAIN.md
    assert the report contains no references to files that do not exist in the repo
    assert the report contains the negative-authority disclaimer verbatim
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md` | canonical definition of the audit: inputs, outputs, thresholds, escalation, per-repo scan-root table, routine-management appendix |
| Create | `scripts/cron/tier1-indexing-freshness.sh` | audit logic — bash, sources `scripts/cron/lib/cadence-common.sh`, idempotent, local-only, three-level exit codes |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | append one `tier1-indexing-freshness` task entry with `schedule: "30 6 * * *"`, `machines: [dev-primary, ace-linux-1]`, `requires: [bash, git]`, `is_claude_task: false`, and the log/command block matching sibling-cron shape; existing tasks unchanged |
| Modify (if not already covered) | `data/document-index/freshness-cadences.yaml` | register the new daily cadence OR cite an existing daily entry that applies (per #2105) |
| Create | `tests/docs/test_tier1_indexing_freshness_audit.py` | regression: audit-definition contract-doc coverage, negative-authority clause, scan-root table presence, report schema |
| Create | `tests/scripts/cron/test_tier1_indexing_freshness.py` | regression: script behavior — exit codes, report generation, evidence-line emission, contract-missing handling, read-only against tier-1 repos |
| Create (first run) / Overwrite (subsequent) | `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md` | dated per-run snapshot |
| Overwrite | `docs/reports/tier-1-indexing-freshness-latest.md` | latest-pointer overwritten atomically each run (not a manual edit artifact) |
| Update | `docs/plans/README.md` | add this plan's row |

Notes on scope boundaries:
- This plan **does** include the `config/scheduled-tasks/schedule-tasks.yaml` task-entry as a Files-to-Change row; installation via `bash scripts/cron/setup-cron.sh` on a `full`-variant host is the implementation-agent action, not the plan.
- This plan **does not** modify any tier-1 repo source code.
- This plan **does not** touch `aceengineer-website/**` (owned by sibling #2463), `tests/**` outside the two regression tests named above, or any other sibling plan's review artifacts.
- This plan **does not** depend on the pre-existing remote-scheduler routine `aefef5167f2f` being preserved; the implementation must be invokable manually and give the same output. Dual-writer cut-over (confirming the remote routine is disabled or re-pointed to the in-repo script) is a required implementation step documented in the contract doc's routine-management appendix.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_freshness_report_timestamp_within_window` | the daily freshness report's in-body `Generated: <iso8601>` timestamp is within 48 hours (accommodates scheduler jitter, DST transitions, and fresh-clone CI runs without letting stale reports slip by); checks timestamp inside report body, NOT filesystem mtime (which is unreliable after clone) | report body | in-body timestamp within 48h window |
| `test_freshness_report_covers_all_tier1_repos` | report names every repo in BUSINESS_BRAIN.md `### Tier-1` section (parsed by extracting leading pipe-delimited cells between `### Tier-1` and the next `### Tier-` header; NOT a whole-document grep) | report text + parsed tier-1 set | every parsed repo name present in report |
| `test_freshness_report_no_broken_refs` | report does not reference files that do not exist | report text + filesystem | every cited path resolves |
| `test_freshness_report_has_negative_authority_disclaimer` | report contains the exact sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` (matches #2460 contract negative-authority rule) | report text | exact sentence present |
| `test_freshness_report_red_has_action_required_prefix` | when portfolio is red, report header contains a single-line `Action required: <count> tier-1 repo(s) ...` prefix so a human reader sees urgency without live escalation | red-fixture run | `Action required:` prefix present |
| `test_freshness_report_shape_matches_enumerated_sections` | report contains all required sections by name: `## Overall Status`, `## Repo Status`, per-repo `### <repo> — <status>` with `Current concerns` and `Next actions` subsections, `## Assumption Check Against ... Scorecard` | report text | all enumerated section headings present in order |
| `test_audit_contract_has_required_sections` | `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md` contains: scope, inputs, per-repo checks, per-repo scan-root table, pass/fail thresholds, escalation rule, negative-authority clause, legacy-pattern avoidance statement, routine-management appendix (how to list/manage the `aefef5167f2f`-style remote routine) | contract doc text | all 9 sections present |
| `test_audit_contract_has_per_repo_scan_root_table` | contract doc contains a table with one row per tier-1 repo specifying the scan-root path(s) for source-hygiene checks (so `.bak`/`.orig` scans don't over-scan `node_modules/`/`dist/` or under-scan nested package trees) | contract doc text | table present, row per tier-1 repo |
| `test_audit_exits_three_level_on_portfolio_status` | script exits `0` on green, `1` on yellow, `2` on red — verified by four fixture scenarios (clean, hygiene-noise-only, missing-required-surface, legacy-reference-present) | mock portfolio fixtures | exit codes 0/1/2 match portfolio status |
| `test_audit_exits_red_when_contract_missing` | if `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` does not exist, script writes a report with clear error, emits evidence line with `status=red reason=contract-missing`, and exits `2` — does NOT substitute an internal copy of the rule set | temp repo without contract file | exit 2 + error report + evidence line |
| `test_audit_emits_cron_health_evidence_line` | at end of run, script writes one line in the #2291 contract format: `task=tier1-indexing-freshness status=<green\|yellow\|red> artifact=<path> log=<path> ts=<iso8601>` | run script | evidence line present once, parses to expected fields |
| `test_audit_is_read_only_on_tier1_source_trees` | running the script causes zero writes under any tier-1 repo's tracked source tree; only `docs/reports/` and `logs/freshness/` are written | run script; diff `git status --porcelain` in each tier-1 repo before/after | zero status-porcelain differences in tier-1 source trees |
| `test_audit_is_offline_ast_level` | for Python implementations, AST-level import-detection rejects `requests`, `urllib.*`, `http.client`, `httpx`, `aiohttp`; for bash, the script does not invoke `curl`/`wget`/`nc`/`ssh`/`rsync`/`ping`/`git fetch`/`git push` (checked via shellcheck source walk OR a no-network test fixture that fails the test if any outbound syscall is attempted) — replaces the brittle grep-based offline check | script AST/text + optional no-network fixture | no banned import/invocation detected |
| `test_schedule_task_entry_exists_in_yaml` | `config/scheduled-tasks/schedule-tasks.yaml` contains a `tier1-indexing-freshness` task with `schedule: "30 6 * * *"`, `machines` containing `dev-primary`, `requires: [bash, git]`, `is_claude_task: false`, and a `command` block invoking `scripts/cron/tier1-indexing-freshness.sh` | YAML file | entry present with all required fields |
| `test_schedule_task_passes_existing_validator` | `uv run python scripts/cron/validate-schedule.py` (or equivalent existing validator) exits 0 on the updated YAML | YAML + validator | validator exits 0 |
| `test_setup_cron_dry_run_installs_on_full_variant_only` | `bash scripts/cron/setup-cron.sh --dry-run` on a `full`-variant host lists the new task in the install preview; on `contribute` or `contribute-minimal` hosts, the new task is NOT listed | hostname-override invocation | full-variant lists; others don't |
| `test_cadence_registered_or_cited` | either a new daily cadence entry is registered in `data/document-index/freshness-cadences.yaml`, OR the contract doc cites an existing daily cadence entry that applies (per #2105) | YAML file + contract doc | cadence known to the #2105 staleness framework |
| `test_plans_readme_indexes_2465_plan` | planning index includes the #2465 row | `docs/plans/README.md` | row present |

Each test deterministic, offline, and runnable under 2 seconds on a cold cache.

---

## Acceptance Criteria

- [ ] `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md` exists and includes: scope, inputs, per-repo checks, **per-repo scan-root table** (one row per tier-1 repo specifying source-hygiene scan roots), pass/fail thresholds, three-level escalation rule (green/yellow/red → exit 0/1/2), **negative-authority clause** (exact sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority`), legacy-pattern avoidance statement, and a **routine-management appendix** (how to list/disable/re-point the pre-existing remote-scheduler routine `aefef5167f2f`, with `project_daily_readiness_cron.md` memory cited as the ecosystem pattern).
- [ ] `scripts/cron/tier1-indexing-freshness.sh` exists, is executable, starts with `#!/usr/bin/env bash` + `set -euo pipefail`, sources `scripts/cron/lib/cadence-common.sh`, contains zero hardcoded absolute paths outside comments, and is invokable manually (not dependent on scheduler state).
- [ ] script parses tier-1 repo set from the `### Tier-1` section of `docs/BUSINESS_BRAIN.md` (leading pipe-delimited cell extraction between `### Tier-1` and the next `### Tier-` header — NOT a whole-document grep), and parses the required-surface list from `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` rather than hard-coding either list.
- [ ] script exits `0` on green, `1` on yellow, `2` on red — verified by at least four fixture scenarios (clean / hygiene-noise-only / missing-required-surface / legacy-reference-present).
- [ ] script exits `2` with a clear error report when the #2460 contract file does not yet exist; does NOT substitute an internal copy of the rule set.
- [ ] script writes `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md` and atomically overwrites `docs/reports/tier-1-indexing-freshness-latest.md`; second-day runs replace the latest, not append.
- [ ] generated report contains the exact sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` (matches #2460 contract's negative-authority rule).
- [ ] generated report cites only current canonical routing surfaces; zero banned-pattern signatures (from the contract's banned list) appear in the report body.
- [ ] generated report shape matches enumerated sections by name: `## Overall Status`, `## Repo Status`, per-repo `### <repo> — <status>` with `Current concerns` and `Next actions` subsections, `## Assumption Check Against ... Scorecard`.
- [ ] on red portfolio, the report header contains a single-line `Action required: <count> tier-1 repo(s) have missing required surfaces or legacy references. See per-repo findings below.` prefix so a reader sees urgency without live escalation.
- [ ] script emits a #2291-conforming cron-health evidence line at end of run: `task=tier1-indexing-freshness status=<green|yellow|red> artifact=<path> log=<path> ts=<iso8601>`.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a `tier1-indexing-freshness` task entry with `schedule: "30 6 * * *"`, `machines: [dev-primary, ace-linux-1]`, `requires: [bash, git]`, `is_claude_task: false`; existing tasks unchanged.
- [ ] existing schedule validator (`scripts/cron/validate-schedule.py` or equivalent) passes on the updated YAML.
- [ ] `bash scripts/cron/setup-cron.sh --dry-run` on a `full`-variant host lists the new task in the install preview; on `contribute` or `contribute-minimal` hosts, the new task is NOT installed.
- [ ] daily cadence registered in `data/document-index/freshness-cadences.yaml`, OR contract doc cites an existing daily cadence entry that applies — per #2105; staleness framework must be able to see the new freshness artifact's expected age.
- [ ] script is read-only against tier-1 source trees: `git status --porcelain` shows zero changes in any tier-1 repo after a run.
- [ ] script makes zero outbound network calls (AST-level import check for Python, shellcheck-style scan for bash; no `curl`/`wget`/`nc`/`ssh`/`rsync`/`ping`/`git fetch`/`git push`).
- [ ] freshness-report staleness test checks the in-body `Generated:` timestamp (48h window), NOT filesystem mtime — the latter is unreliable after `git clone` or `git checkout`.
- [ ] dual-writer cut-over with the remote routine `aefef5167f2f` is documented in the routine-management appendix as a required implementation step (either disable the remote routine or re-point it to the in-repo script); the implementation PR must confirm the cut-over before the regression test is turned on in CI.
- [ ] dated snapshots policy: either commit them (contributing to archival debt) OR add `docs/reports/tier-1-indexing-freshness-*.md` to `.gitignore` except the `-latest` file — contract doc must state the chosen policy.
- [ ] targeted regression tests pass: `uv run pytest tests/docs/test_tier1_indexing_freshness_audit.py tests/scripts/cron/test_tier1_indexing_freshness.py -v`.
- [ ] `docs/plans/README.md` includes the #2465 index row.
- [ ] review artifacts exist under `scripts/review/results/` for Claude, Codex, and Gemini (or substitute NOT-RUN stubs with provenance for any provider not dispatched).

---

## Relationship to the broader repo-ecosystem knowledge layer

- This issue is the sustaining loop for the #2460 contract and the #2461/#2462/#2463/#2464 per-repo remediations. Its value depends on those surfaces being real, so the audit's per-repo findings are most meaningful once the sibling plans have executed.
- In the interim, the audit still produces value: it surfaces *missing* canonical surfaces as yellow/red findings, giving the operator a prioritized worklist rather than rediscovering gaps manually.
- It is intentionally simple at first pass: reporting only, no hard enforcement. Stricter enforcement (CI gate, pre-commit hook) is a follow-up once the sibling remediations have stabilized.
- The negative-authority clause — "uses canonical routing surfaces only, never raw inventories" — is what keeps the llm-wiki/tier-1 knowledge layer clean. Without it, the audit would drift back into the noisy-inventory pattern #2464 is actively cleaning up.

---

## Adversarial Review Summary

Two waves have run (r1, r2); the binding state is r2 plus post-r2 patches. r2 is a single-author Claude review under the documented permission-gate fallback (`feedback_permission_gate_blocks_cross_review.md` in memory) because `scripts/review/plan-review-fanout.sh` cannot dispatch in this session. Codex and Gemini have NOT been dispatched; a future dispatch-capable session must redispatch both before `status:plan-approved`.

### r1 wave (single-author Claude, historical)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Dual-writer hazard with remote routine `aefef5167f2f`; 26h mtime window too tight; source-hygiene scan-roots under-specified; grep-based offline check brittle; escalation stops at exit codes; report-shape not schema-pinned; routine-management appendix missing. |
| Codex | NOT RUN | Permission gate blocks subprocess dispatch. |
| Gemini | NOT RUN | Permission gate blocks subprocess dispatch. |

### r2 wave (single-author Claude, this session — supersedes r1)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | (1) schedule-tasks.yaml entry is not a Files-to-Change row despite the issue's `daily scheduled job exists` acceptance criterion and the HARD RULE in `scripts/cron/crontab-template.sh`. (2) Script-placement ambiguity (`scripts/cron/*.sh` OR `scripts/automation/*.py`) undermines planning. (3) Retrieval-contract union missing — `cat:harness` + `cat:automation` require `config/agents/` and `.claude/rules/` citations. (4) Binary exit scheme (0=green-or-yellow, non-zero=red) collapses yellow into green and starves the cron-health escalation framework (#2291). Plus all r1 minor findings still apply. |
| Codex | NOT RUN | Permission gate blocks subprocess dispatch. |
| Gemini | NOT RUN | Permission gate blocks subprocess dispatch. |

### Post-r2 patches applied in this draft

- **r2 MAJOR #1 (schedule-tasks.yaml):** added `Modify | config/scheduled-tasks/schedule-tasks.yaml` row to Files-to-Change; added `test_schedule_task_entry_exists_in_yaml`, `test_schedule_task_passes_existing_validator`, `test_setup_cron_dry_run_installs_on_full_variant_only`; added acceptance criteria for the entry, validator pass, and hostname-aware install.
- **r2 MAJOR #2 (placement):** locked `scripts/cron/tier1-indexing-freshness.sh` as the sole script path; required it to source `scripts/cron/lib/cadence-common.sh`; removed the "implementation agent decides" clause.
- **r2 MAJOR #3 (retrieval-contract union):** added `.claude/rules/` and `config/agents/` to Documents consulted with concrete findings (`patterns.md` enforcement-gradient positions this at Level 2; `coding-style.md` path-handling rule; grep-evidence showing no cross-wiring needed). Added `scripts/cron/lib/cadence-common.sh`, `scripts/cron/crontab-template.sh`, `#2291`, and `#2105` as required cited sources.
- **r2 MAJOR #4 (three-level exit):** updated pseudocode to `0=green, 1=yellow, 2=red` matching sibling-cron convention; added `test_audit_exits_three_level_on_portfolio_status`; added acceptance criterion requiring four-fixture verification.
- **r1+r2 MINOR (dual-writer cut-over):** added to routine-management appendix and acceptance criteria; implementation PR must confirm cut-over before CI regression test is turned on.
- **r1 MINOR (mtime window):** widened to 48 hours, moved the check to in-body `Generated:` timestamp (more robust against fresh-clone).
- **r1+r2 MINOR (scan-root table):** contract doc must include a per-repo scan-root table; test `test_audit_contract_has_per_repo_scan_root_table` enforces its presence.
- **r1 MINOR (offline check):** replaced grep-based check with AST-level (Python) / shellcheck-walk (bash) detection; expanded banned-invocation list.
- **r1 MINOR (red escalation prefix):** report header must include `Action required:` single-line prefix on red.
- **r1 MINOR (report schema):** acceptance criterion now enumerates the required section headings.
- **r1 MINOR (routine management):** added appendix requirement to contract doc; cited `project_daily_readiness_cron.md` ecosystem pattern.
- **r1 NIT (dated snapshots policy):** acceptance criterion now requires the contract doc to pick one policy (commit vs. gitignore).

**Current draft state:** PLAN-REVIEW READY — all r1 + r2 findings (MAJOR and MINOR) have been patched. A future cross-review session should redispatch Codex and Gemini before `status:plan-approved`. Progression to `status:plan-review` is supported by r2+patches.

---

## Risks and Open Questions

- **Risk:** the pre-existing remote-scheduler routine `aefef5167f2f` at `30 3 * * *` already rewrites `docs/reports/tier-1-indexing-freshness-latest.md` using some logic this plan does not own. Mitigation: the implementation must be able to regenerate the same-shape file deterministically; once it lands, the remote routine should be re-pointed at the in-repo implementation so that the report's logic is reviewable in git. If the remote routine is left as-is, the regression test still catches stale reports by checking mtime + content shape.
- **Risk:** shallow audits can miss drift that matters (broken internal deep-links, orphaned operator-map sections, source-hygiene artifacts under nested package paths). Mitigation: first pass is reporting-only; the contract doc must explicitly list what is *not* checked yet so later passes can close the gaps intentionally.
- **Risk:** the audit could be read as authorizing noisy crawls. Mitigation: scope boundaries explicitly forbid raw-inventory consumption and network calls; the regression test enforces the negative-authority disclaimer.
- **Open:** should per-run dated snapshots under `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md` be kept, or only the `-latest` file? This plan permits either, because neither changes the contract. Defer to implementation agent.
- **Open:** should the escalation rule wake a human (issue comment on a tracking issue) or only exit non-zero? This plan currently stops at exit codes; live escalation can be layered later, since it requires scheduler-side support.

---

## Complexity: T2

**T2** — single automation with contract doc, implementation script, and regression test. Limited surface, no new architecture. Not T1 because a new contract document plus a test harness plus a runtime script are required; not T3 because no cross-repo code changes, no new scheduler framework, and no deployment coordination are required.
