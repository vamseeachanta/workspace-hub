# Plan for #2801: Machine-equality matrix across the multi-machine ecosystem

> **Status:** adversarial-reviewed (r1 Claude MAJOR→fixed; Codex r2 pending)
> **Complexity:** T2
> **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2801
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** scripts/review/results/2026-05-26-plan-2801-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/nightly-readiness.sh` — 25 harness checks (R1…R-XPROV) emitting `.claude/state/harness-readiness-<host>.yaml`. Covers the **harness** dimension only.
- Found: `scripts/readiness/compare-harness-state.sh` — diffs harness readiness across workstations via **SSH** (ace-linux-2) and **stale-report detection** (licensed-win-1). Confirms transport differs per machine: Linux peers are SSH-reachable, Windows peers are not and must push via git.
- Found: `scripts/readiness/harness-config.yaml` — single source of truth for the **workstation roster** (`dev-primary, dev-secondary, licensed-win-1, licensed-win-2, macbook-portable`) and `tier1_repos` (`assetutilities, digitalmodel, worldenergydata, assethold`). **Gap:** `home-win` is absent from this config though it is in the #2795 roster.
- Gap: no script measures the non-harness dimensions (compute, data access, skills inventory, kanban/dispatch, memory freshness, scheduler) or assembles a cross-machine matrix.

### Standards
Not applicable — operational/harness issue, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — operational infra work, not domain knowledge.

### Documents consulted
- `.claude/memory/context.md` — machine table + memory-sync model ("Git IS the sync mechanism"). **Contradicted by spike** (see Evidence): claims `digitalmodel`/`worldenergydata` are nested under workspace-hub; they are siblings at `/mnt/local-analysis/`.
- Issue #2795 — locked machine roster + `domain:`/`machine:`/`ai:` label scheme; dispatch queues at `.claude/dispatch/<machine>.yaml`.
- Issues #2229 (Windows-parity live validation), #2765 (scheduler parity report), #2258 (plugin-inventory parity), #2524 (machine-aware dispatch ledger) — each covers one parity slice; this plan is the umbrella assessment that consumes them, not a duplicate.
- `.gitignore` lines 164–197 — `.claude/state/*` is ignored with an explicit negation allow-list; only `harness-readiness-licensed-win-1.yaml` is un-ignored today.

### Gaps identified
1. No collector for the 6 non-harness dimensions → must be built.
2. No matrix builder joining per-machine reports → must be built.
3. `.gitignore` lacks a negation for `equality-*.yaml` → reports would be silently un-tracked and never sync (build gap).
4. `harness-config.yaml` roster lags #2795 (`home-win` missing) → reconcile.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-26 via `gh issue view`):
- `#2801` — OPEN — assess(workstations): machine-equality matrix … (created this session)

**File existence** (`ls`/`git ls-files` 2026-05-26):
- EXISTS: `scripts/readiness/{nightly-readiness.sh,compare-harness-state.sh,harness-config.yaml}`
- EXISTS (git-tracked negation): `.gitignore:178 !.claude/state/harness-readiness-licensed-win-1.yaml`
- CONFIRMED gitignored: `git check-ignore -v .claude/state/equality-dev-primary.yaml` → `.gitignore:168 .claude/state/*`
- CONFIRMED not-tracked: `git ls-files .claude/state/harness-readiness-ace-linux-1.yaml` → empty (Linux readiness files are local-only by design; SSH covers them)
- MISSING (this plan creates): `scripts/readiness/collect-equality.sh`, `scripts/readiness/build-equality-matrix.py`, `tests/readiness/test_collect_equality.py`, `tests/readiness/test_build_equality_matrix.py`

**Spike proofs** (de-risking prototype run this session, preserved at `/tmp/eq-prototype/`, NOT committed):
```
$ bash collect-equality.sh --stdout   # dev-primary / ace-linux-1
dimensions.compute: 32c / 31Gi / 881G free / GPU GTX 750 Ti
dimensions.data_access.tier1_repos: all 4 = "sibling:/mnt/local-analysis/<repo>"   # NOT nested → context.md stale
dimensions.harness.providers: claude/codex/gemini/hermes all present; gh_auth=ok; python_cmd=uv-run
dimensions.skills.repo_skill_count: 407       # maxdepth-3 SKILL.md count
dimensions.scheduler: 38 jobs, has_repo_sync=true, has_parity_review=true
```
- Spike validated the collector parses (`yaml.safe_load` OK) and the matrix builder renders (1/4 active reporting; PENDING when <2 machines — correct conservative default).

**Reproduction proofs** (Step 1.5): N/A — #2801 alleges no runtime failure (assessment/infra feature). Spike evidence above substitutes and is stronger than reproduction.

<!-- distinct sources: issue #2801, harness-config.yaml, nightly/compare scripts, context.md, .gitignore, adjacent issues, spike = 7 ≥ 3 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-26-issue-2801-machine-equality.md |
| Collector | scripts/readiness/collect-equality.sh |
| Matrix builder | scripts/readiness/build-equality-matrix.py |
| Collector tests | tests/readiness/test_collect_equality.py |
| Matrix tests | tests/readiness/test_build_equality_matrix.py |
| Per-machine reports | .claude/state/equality-<machine>.yaml (git-tracked via new negation) |
| Matrix report | docs/reports/YYYY-MM-DD-machine-equality-matrix.html |
| Plan review — Claude | scripts/review/results/2026-05-26-plan-2801-claude.md |
| Plan review — Codex | scripts/review/results/2026-05-26-plan-2801-codex.md |

---

## Deliverable

A regenerable machine-equality matrix: each machine self-reports 8 dimensions via `collect-equality.sh` into a git-tracked `equality-<machine>.yaml`, and `build-equality-matrix.py` joins them into an HTML report with per-cell `EQUAL`/`DIVERGES`/`EXPECTED-DIFF`/`MISSING-EVIDENCE`/`UNREACHABLE` verdicts.

---

## Pseudocode

```
# collect-equality.sh (runs per machine; Linux/macOS/Git-Bash)
detect OS (uname) and machine-label (hostname → roster, --machine override)
compute:      cores/ram/disk/gpu per-OS branch (nproc|sysctl|wmic)
data_access:  for each tier1 repo → nested | sibling:<path> | absent
harness:      provider presence (claude/codex/gemini/hermes), gh auth,
              python_cmd; REFERENCE harness-readiness-<machine>.yaml (don't re-run)
skills:       count SKILL.md (maxdepth 3)
kanban:       list .claude/dispatch/*.yaml
memory:       context.md mtime + ~/.hermes presence
behavior:     status=deferred (future cross-machine identical-prompt probe)
scheduler:    cron job count + has_repo_sync + has_parity_review (Linux/mac);
              "task-scheduler" sentinel on Windows
emit YAML → .claude/state/equality-<machine>.yaml (or --stdout)

# build-equality-matrix.py
load roster FROM scripts/readiness/harness-config.yaml `workstations:` (M1: single
  source of truth — do NOT hardcode the machine list). Classify each as ACTIVE vs
  UNREACHABLE via a `status`/`linux_reachable` overlay; home-win + macbook-portable
  are UNREACHABLE for now.
for each equality-<m>.yaml present: parse
for each dimension × machine:
    if unreachable & no report → UNREACHABLE
    elif active & no report    → MISSING-EVIDENCE
    elif dimension's reported status == "deferred" (behavior v1) → MISSING-EVIDENCE  # M2
    elif dimension in EXPECTED_DIFF (compute, python_cmd ONLY) → EXPECTED-DIFF
    elif <2 active reporting    → PENDING
    else verdict = EQUAL if value==majority else DIVERGES
render HTML table → docs/reports/<date>-machine-equality-matrix.html

# M2: EXPECTED_DIFF = {compute, python_cmd} only. Behavior is NOT expected-diff —
#     it stays MISSING-EVIDENCE until the cross-machine probe lands, so real
#     behavioral divergence is never masked green.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/readiness/collect-equality.sh | per-machine self-report collector |
| Create | scripts/readiness/build-equality-matrix.py | join reports → HTML matrix |
| Create | tests/readiness/test_collect_equality.py | TDD: collector schema/OS-branch/label |
| Create | tests/readiness/test_build_equality_matrix.py | TDD: verdict logic + roster |
| Modify | .gitignore | add `!.claude/state/equality-*.yaml` **after line 168** (`.claude/state/*`), adjacent to the existing `!harness-readiness-licensed-win-1.yaml` negation (m2) |
| Modify | scripts/readiness/harness-config.yaml | add `home-win` to roster with `ssh_target: null` + `linux_reachable: false` (m3); reconcile with #2795 |
| Update | docs/plans/README.md | index row for this plan |

---

## TDD Test List

| Test name | What it verifies | Input | Expected |
|---|---|---|---|
| test_collect_emits_valid_yaml | output parses + has 8 dimension keys | run `--stdout` on a tmp fixture root | `yaml.safe_load` OK, keys present |
| test_collect_machine_label_from_hostname | hostname→label map | `HOST=ace-linux-1` | machine=`dev-primary` |
| test_collect_machine_override | `--machine` wins over hostname | `--machine licensed-win-2` | machine=`licensed-win-2` |
| test_collect_data_access_sibling | sibling repo detected when not nested | tmp sibling `digitalmodel/.git` | `sibling:<path>` not `absent` |
| test_collect_sources_readiness_value | harness dim's `readiness_overall` is SOURCED from fixture file; collector does not modify that file (m1 — positive assertion, not "no re-run") | fixture `harness-readiness-X.yaml` overall=fail | `readiness_overall==fail`, file mtime unchanged |
| test_matrix_roster_from_config | roster read from harness-config.yaml, not hardcoded (M1) | config with N machines | matrix has exactly those N columns |
| test_matrix_pending_under_two | <2 active machines → PENDING not EQUAL | 1 equality yaml | cell verdict `PENDING` |
| test_matrix_diverges_on_minority | value ≠ majority of ≥2 reporters → DIVERGES | 3 yamls, 1 differs | minority cell `DIVERGES` |
| test_matrix_expected_diff_dims | compute + python_cmd ONLY are EXPECTED-DIFF (M2) | any | `EXPECTED-DIFF` |
| test_matrix_behavior_deferred_is_missing | deferred behavior → MISSING-EVIDENCE, never EXPECTED-DIFF (M2) | report w/ behavior.status=deferred | `MISSING-EVIDENCE` |
| test_matrix_unreachable_fixed | home-win/macbook always UNREACHABLE w/o report | no report | `UNREACHABLE` |
| test_matrix_missing_evidence | active machine w/o report | no report for dev-secondary | `MISSING-EVIDENCE` |
| test_gitignore_negation_tracks_equality | `equality-*.yaml` is git-trackable after negation | `git check-ignore` | not ignored |
| test_harness_config_home_win_shape | home-win added with ssh_target null + linux_reachable false (m3) | parse config | fields present, consumers tolerate |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/readiness/ -v`
- [ ] No regression in scope: `uv run pytest tests/readiness/` green (whole-suite green is NOT this plan's contract — known unrelated flakiness per memory)
- [ ] `collect-equality.sh` runs live on dev-primary and writes a parseable `equality-dev-primary.yaml`
- [ ] `git check-ignore .claude/state/equality-dev-primary.yaml` returns non-match (negation works)
- [ ] `build-equality-matrix.py` renders HTML with correct verdict counts for a 1-machine and a synthetic 3-machine fixture
- [ ] `home-win`/`macbook-portable` render `UNREACHABLE`; the 4 active machines render live or `MISSING-EVIDENCE`
- [ ] Review artifacts posted to scripts/review/results/
- [ ] Issue comment posted on #2801 with matrix link + the 3 architecture findings as follow-ups

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | MAJOR → fixes applied | M1 roster-hardcoding (now reads harness-config.yaml), M2 behavior masked by EXPECTED-DIFF (now MISSING-EVIDENCE), m1 untestable negative reframed, m2 gitignore ordering pinned, m3 home-win config shape + consumer check, nit regression scope |
| Codex (r2) | PENDING | requires plan pushed to GitHub first (codex needs pushed artifact) |

**Overall result:** r1 PASS-with-revisions; awaiting Codex r2 (T2 second provider). Not approval-ready until r2 clears.

Revisions made based on review:
- M1: build-equality-matrix.py reads roster from harness-config.yaml (single source of truth); added test_matrix_roster_from_config.
- M2: removed Behavior from EXPECTED_DIFF; deferred behavior → MISSING-EVIDENCE; added test_matrix_behavior_deferred_is_missing.
- m1: reframed test_collect_references_readiness → test_collect_sources_readiness_value (positive assertion + file-unmodified check).
- m2: pinned .gitignore negation insertion point (after line 168, adjacent to line 178).
- m3: home-win added with ssh_target null + linux_reachable false; added test_harness_config_home_win_shape; verify nightly-readiness.sh + compare-harness-state.sh tolerate the entry.
- nit: regression AC scoped to tests/readiness/.

---

## Risks and Open Questions

- **Risk:** Windows compute fields are hard to capture in Git Bash; `.ps1` companion may be needed for accurate `licensed-win-*` compute. Mitigation: collector emits `task-scheduler`/best-effort sentinels on Windows; a `.ps1` is a follow-up if Git-Bash values prove unreliable.
- **Risk:** other-machine reports only land via the 4-hourly `repo-sync` cron; matrix stays `MISSING-EVIDENCE` until each machine runs the collector once. Mitigation: optionally hook `collect-equality.sh` into `nightly-readiness.sh` (flagged as open question below).
- **Risk:** `.gitignore` negation must use the exact `!.claude/state/equality-*.yaml` form; wildcard negation under an excluded dir works only because `.claude/state/` itself is re-included at line 164. Test `test_gitignore_negation_tracks_equality` guards this.
- **Open:** Should `collect-equality.sh` auto-run from `nightly-readiness.sh` (auto-populate) or stay manual/cron-only? (flag for user at approval)
- **Open:** Behavior dimension is `deferred` in v1 — is a cross-machine identical-prompt probe in scope now or a follow-up issue?

---

## Complexity: T2

**T2** — two new scripts + two test files, two existing files modified (`.gitignore`, `harness-config.yaml`); multi-file harness work, TDD required, no cross-provider engineering review needed. Per the cross-review depth rule, T2 = 2 providers (Claude inline + Codex).
