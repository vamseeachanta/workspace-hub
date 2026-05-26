# Plan for #2801: Machine-equality matrix across the multi-machine ecosystem

> **Status:** plan-review (T2 complete: Claude r1 + Codex r2, all findings applied via r3-inline; approval-ready, awaiting USER)
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

A regenerable machine-equality matrix: each machine self-reports 8 dimensions via `collect-equality.sh` into a git-tracked `equality-<machine>.yaml` (counts/booleans/enums only — no secrets/paths/commands), and `build-equality-matrix.py` joins them into an HTML report with per-cell `EQUAL`/`DIVERGES`/`NO-MAJORITY`/`EXPECTED-DIFF`/`PENDING`/`MISSING-EVIDENCE`/`UNREACHABLE` verdicts.

---

## Pseudocode

```
# collect-equality.sh (runs per machine; Linux/macOS/Git-Bash)
detect OS (uname) and machine-label (hostname → roster, --machine override)
compute:      cores/ram/disk/gpu per-OS branch (Linux nproc/free; macOS sysctl).
              # C2: Windows v1 — try NUMBER_OF_PROCESSORS + best-effort; if a field
              #     can't be read reliably (wmic absent on modern Win), emit "unknown"
              #     sentinel → matrix renders MISSING-EVIDENCE (NOT a fake value).
              #     Accurate Windows compute deferred to a .ps1 companion (follow-up issue).
data_access:  for each tier1 repo → nested | sibling:<path> | absent
harness:      provider presence (claude/codex/gemini/hermes), gh auth,
              python_cmd; REFERENCE harness-readiness-<machine>.yaml (don't re-run)
skills:       count SKILL.md (maxdepth 3)
kanban:       list .claude/dispatch/*.yaml
memory:       context.md mtime + ~/.hermes presence
behavior:     status=deferred (future cross-machine identical-prompt probe)
scheduler:    cron job COUNT + has_repo_sync(bool) + has_parity_review(bool) (Linux/mac);
              "task-scheduler" sentinel on Windows
              # C4: emit COUNTS/BOOLEANS ONLY — NEVER serialize raw cron lines,
              #     job commands, or env values.
emit YAML → .claude/state/equality-<machine>.yaml (or --stdout)

# C4 — Serialization allowlist (security/legal baseline; file is git-tracked, repo may publish):
#   ALLOWED values: integers, booleans, status enums, provider-presence enums,
#     OS/hostname, repo-RELATIVE labels, "sibling:<path-under-/mnt/local-analysis>"
#     (a checkout location, not a secret).
#   FORBIDDEN: raw cron lines, shell commands, env var values, tokens/keys,
#     gh token (emit gh_auth as enum ok|logged-out|absent — NEVER the token),
#     absolute $HOME paths beyond the approved repo-relative labels.
#   Enforced by test_collect_no_forbidden_fields scanning emitted YAML against a denylist.

# build-equality-matrix.py
load roster FROM scripts/readiness/harness-config.yaml `workstations:` (M1: single
  source of truth — do NOT hardcode the machine list). Classify each as ACTIVE vs
  UNREACHABLE via a `status`/`linux_reachable` overlay; home-win + macbook-portable
  are UNREACHABLE for now.
for each equality-<m>.yaml present: parse
# Verdict precedence (C3 — evaluate top-to-bottom, first match wins):
for each dimension × machine:
    if unreachable & no report           → UNREACHABLE
    elif active & no report              → MISSING-EVIDENCE
    elif value is None / parse-error / sentinel("unknown") → MISSING-EVIDENCE   # C6
    elif dimension status == "deferred" (behavior v1)      → MISSING-EVIDENCE   # M2
    elif dimension in EXPECTED_DIFF (compute, python_cmd ONLY) → EXPECTED-DIFF
    elif active reporters with a real value < 2            → PENDING
    else:                                                                       # C1 tie handling
        counts = Counter(real values across active reporters)
        top, n = counts.most_common(1)[0]
        if number of values tied at n > 1 → NO-MAJORITY    # explicit, never silently EQUAL
        else verdict = EQUAL if value == top else DIVERGES
render HTML table → docs/reports/<date>-machine-equality-matrix.html

# M2: EXPECTED_DIFF = {compute, python_cmd} only. Behavior is NOT expected-diff —
#     it stays MISSING-EVIDENCE until the cross-machine probe lands.
# C1: ties (2 disagree, 4-split-2/2) render NO-MAJORITY — never an order-dependent
#     false EQUAL. New verdict added to legend.
# C6: compute is EXPECTED-DIFF only for successfully-collected values; a failed/
#     missing compute field is MISSING-EVIDENCE (collection failure ≠ hardware variance).
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
| test_matrix_pending_under_two | <2 real-value reporters → PENDING not EQUAL | 1 equality yaml | cell verdict `PENDING` |
| test_matrix_two_equal | exactly 2 reporters, same value → EQUAL (C3) | 2 yamls same | `EQUAL` |
| test_matrix_two_disagree_no_majority | exactly 2 reporters, different → NO-MAJORITY not EQUAL (C1) | 2 yamls differ | `NO-MAJORITY` |
| test_matrix_four_split_tie | 4 reporters 2/2 → NO-MAJORITY (C1) | 4 yamls 2/2 | `NO-MAJORITY` |
| test_matrix_diverges_on_minority | value ≠ strict majority of ≥3 → DIVERGES | 3 yamls, 1 differs | minority cell `DIVERGES` |
| test_matrix_expected_diff_dims | compute + python_cmd ONLY are EXPECTED-DIFF (M2) | successfully-collected values | `EXPECTED-DIFF` |
| test_matrix_compute_failure_is_missing | compute "unknown" sentinel → MISSING-EVIDENCE not EXPECTED-DIFF (C6) | report w/ compute.cores=unknown | `MISSING-EVIDENCE` |
| test_matrix_behavior_deferred_is_missing | deferred behavior → MISSING-EVIDENCE (M2) | behavior.status=deferred | `MISSING-EVIDENCE` |
| test_matrix_precedence_unreachable_over_missing | unreachable w/ stale report still UNREACHABLE (C3) | home-win w/ stale yaml | `UNREACHABLE` |
| test_matrix_unreachable_fixed | home-win/macbook UNREACHABLE w/o report | no report | `UNREACHABLE` |
| test_matrix_missing_evidence | active machine w/o report | no report for dev-secondary | `MISSING-EVIDENCE` |
| test_collect_no_forbidden_fields | emitted YAML carries no cron lines/commands/env/tokens/abs-home paths (C4) | run collector, scan output vs denylist | no denylist hit; gh_auth is enum not token |
| test_gitignore_negation_tracks_equality | `equality-*.yaml` trackable after negation (C5) | `git check-ignore -q` + `git add -n` | check-ignore exit≠0 AND `git add -n` succeeds |
| test_harness_config_home_win_shape | home-win added with ssh_target null + linux_reachable false (m3) | parse config | fields present, consumers tolerate |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/readiness/ -v`
- [ ] No regression in scope: `uv run pytest tests/readiness/` green (whole-suite green is NOT this plan's contract — known unrelated flakiness per memory)
- [ ] `collect-equality.sh` runs live on dev-primary and writes a parseable `equality-dev-primary.yaml`
- [ ] `git check-ignore -q .claude/state/equality-dev-primary.yaml` exits non-zero AND `git add -n` succeeds (C5 — proves trackable, not just unmatched)
- [ ] Emitted YAML passes `test_collect_no_forbidden_fields` — no cron lines, commands, env values, tokens, or absolute $HOME paths; `gh_auth` is an enum (C4)
- [ ] `build-equality-matrix.py` renders correct verdicts for 1-machine, synthetic 3-machine, 2-disagree (NO-MAJORITY), and 4-split (NO-MAJORITY) fixtures
- [ ] `home-win`/`macbook-portable` render `UNREACHABLE`; the 4 active machines render live or `MISSING-EVIDENCE`
- [ ] Review artifacts posted to scripts/review/results/
- [ ] Issue comment posted on #2801 with matrix link + the 3 architecture findings as follow-ups

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | MAJOR → fixes applied | M1 roster-hardcoding (now reads harness-config.yaml), M2 behavior masked by EXPECTED-DIFF (now MISSING-EVIDENCE), m1 untestable negative reframed, m2 gitignore ordering pinned, m3 home-win config shape + consumer check, nit regression scope |
| Codex (r2) | MAJOR → fixes applied (r3 inline) | C1 tie-handling undefined (→ NO-MAJORITY verdict), C2 Windows wmic unreliable (→ unknown sentinel/MISSING-EVIDENCE, .ps1 follow-up), C3 verdict state-machine under-tested (→ +5 tests), C4 no redaction contract for git-tracked state (→ serialization allowlist + test_collect_no_forbidden_fields), C5 gitignore test weak (→ check-ignore -q + add -n), C6 compute-failure masked as expected-diff (→ MISSING-EVIDENCE) |

**Overall result:** T2 complete (Claude r1 + Codex r2). r1/r2 surfaced DIFFERENT defects → per the r3-inline loop-break rule, all r2 findings applied as main-session inline patches (NOT a re-dispatched round). Plan is now approval-ready. Implementation remains blocked pending USER approval.

Codex r2 revisions applied:
- C1: explicit NO-MAJORITY verdict for ties (2-disagree, 4-split-2/2); +test_matrix_two_disagree_no_majority, test_matrix_four_split_tie, test_matrix_two_equal.
- C2: Windows compute emits `unknown` sentinel → MISSING-EVIDENCE; accurate Windows compute deferred to .ps1 follow-up issue.
- C3: verdict precedence order pinned; +test_matrix_compute_failure_is_missing, test_matrix_precedence_unreachable_over_missing.
- C4: serialization allowlist (counts/booleans/enums only; no cron lines/commands/env/tokens/abs-paths; gh_auth as enum); +test_collect_no_forbidden_fields.
- C5: gitignore acceptance → `git check-ignore -q` (exit≠0) + `git add -n` success.
- C6: compute parse-error/missing → MISSING-EVIDENCE, distinct from EXPECTED-DIFF hardware variance.

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
- **Resolved (Codex r2 Q1):** ties render as explicit `NO-MAJORITY` verdict (reuses no existing color; added to legend) — never an order-dependent false EQUAL.
- **Resolved (Codex r2 Q2):** Windows compute is NOT required accurate in v1 — emits `unknown` sentinel → MISSING-EVIDENCE; accurate Windows compute is a follow-up `.ps1` companion issue.
- **Follow-up issue (C2):** PowerShell collector companion for accurate `licensed-win-*` compute.
- **Open:** Should `collect-equality.sh` auto-run from `nightly-readiness.sh` (auto-populate) or stay manual/cron-only? (flag for user at approval)
- **Open:** Behavior dimension is `deferred` in v1 — is a cross-machine identical-prompt probe in scope now or a follow-up issue?

---

## Complexity: T2

**T2** — two new scripts + two test files, two existing files modified (`.gitignore`, `harness-config.yaml`); multi-file harness work, TDD required, no cross-provider engineering review needed. Per the cross-review depth rule, T2 = 2 providers (Claude inline + Codex).
