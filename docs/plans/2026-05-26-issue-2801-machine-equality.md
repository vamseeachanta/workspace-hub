# Plan for #2801: Machine-equality matrix across the multi-machine ecosystem

> **Status:** revising (T2 done on original scope; user decisions D1/D2/D3 grew it to T3 — delta re-review required before approval)
> **Complexity:** T3 (grew from T2 after D1/D2/D3)
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
| Plan review — Claude r1 | scripts/review/results/2026-05-26-plan-2801-claude.md |
| Plan review — Codex r2 | scripts/review/results/2026-05-26-plan-2801-codex.md |
| Plan review — Claude r3 (delta) | scripts/review/results/2026-05-26-plan-2801-claude-r3-delta.md |
| Plan review — Codex (delta) | scripts/review/results/2026-05-26-plan-2801-codex-delta.md |
| Plan review — Gemini (delta) | scripts/review/results/2026-05-26-plan-2801-gemini-delta.md |

---

## Deliverable

A regenerable machine-equality matrix: each machine self-reports 8 dimensions via `collect-equality.sh` into a git-tracked `equality-<machine>.yaml` (counts/booleans/enums only — no secrets/paths/commands), collected **weekly + on-demand with commit-on-change** (D1). `build-equality-matrix.py` joins them into an HTML report using **two grading families** (D2): cold dims (compute, data access) graded as **conformance to a declared per-machine baseline** (`CONFORMS`/`BELOW-BASELINE`/`MISSING-BASELINE`); uniform dims (harness, skills, kanban, memory, **behavior probes**, scheduler) graded by equality (`EQUAL`/`DIVERGES`/`NO-MAJORITY`/`EXPECTED-DIFF`/`PENDING`); plus `MISSING-EVIDENCE`/`UNREACHABLE`. The **behavior dimension ships in v1** (D3) as a deterministic, side-effect-free harness-behavior probe corpus.

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
behavior:     run the DETERMINISTIC harness-behavior probe corpus (D3, v1) — see below.
scheduler:    cron job COUNT + has_repo_sync(bool) + has_parity_review(bool) (Linux/mac);
              "task-scheduler" sentinel on Windows
              # C4: emit COUNTS/BOOLEANS ONLY — NEVER serialize raw cron lines,
              #     job commands, or env values.
emit YAML → .claude/state/equality-<machine>.yaml (or --stdout)

# D1 — Cadence + idempotent commit (cold dims rarely change). PER-MACHINE WEEKLY (D1-1):
#   * Each machine runs the collector on ITS OWN weekly schedule so all 4 active machines
#     populate (a single dev-primary cron would only cover dev-primary):
#       - Linux (ace-linux-1, ace-linux-2): weekly crontab entry installed by the Linux
#         cron installer (one entry: `collect-equality.sh && build-equality-matrix.py`).
#       - Windows (licensed-win-1/2): weekly task in scripts/windows/setup-scheduler-tasks.ps1
#         (sibling to the #2229 NightlyReadiness/MemoryBridgeSync tasks).
#   * On-demand: `collect-equality.sh --now` on any machine.
#   * COMMIT-ON-CHANGE: content hash EXCLUDING generated_at; if unchanged vs committed file,
#     do NOT rewrite/commit (no weekly git churn even though the job runs weekly).
#   * Hot dims (harness/skills) stay fresh via the nightly harness-readiness REFERENCE.

# D3 — Behavior probe corpus (deterministic harness behavior — NOT LLM output, which is
#       non-deterministic and not diffable). Each probe is READ-ONLY / side-effect-free and
#       yields a stable enum/hash comparable across machines:
#   b1 gate_blocks_unsafe_write : run .claude/hooks/plan-approval-gate.sh in DRY-RUN against a
#        synthetic "Write to src/ without approval marker" payload → expect "deny" (no real write)
#   b2 skill_resolves           : issue-planning-mode SKILL.md present + frontmatter parses → ok/fail
#   b3 artifact_format_default  : read .claude/rules → "html" | other
#   b4 harness_file_size_gate   : check-harness-file-size.sh exit (pass/fail) on the 4 adapter md files
#   b5 settings_permissions_hash: sha256 of the CANONICALIZED .claude/settings.json permissions
#       block — parse JSON, sort keys, strip insignificant whitespace, force LF — THEN hash.
#       (D3-1: canonicalize or Windows CRLF vs Linux LF + key order → false DIVERGES on identical policy.)
#       Hash only — never the contents; uniform hash across machines = same gate behavior.
#   Probes that cannot run side-effect-free on a machine emit "n/a" → MISSING-EVIDENCE (not a fake pass).
#   (D3-1: b1 must invoke plan-approval-gate.sh via a verified no-write path — synthetic stdin,
#    decision echoed, no log append; if that contract can't be confirmed, b1 emits "n/a".)

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
load baselines FROM harness-config.yaml workstations.<m> (D2: compute_floor,
  required_data_access, role). These are the DECLARED expectations for cold dims.
for each equality-<m>.yaml present: parse

# Two grading families (D2):
#   COLD dims (compute, data_access) → CONFORMANCE to declared per-machine baseline.
#     Machines legitimately differ, so majority-vote is meaningless here.
#   UNIFORM dims (harness providers, skills, kanban, memory model, behavior probes,
#     scheduler presence) → equality/uniformity across active machines.

# Verdict precedence (C3 — evaluate top-to-bottom, first match wins):
for each dimension × machine:
    if unreachable & no report           → UNREACHABLE
    elif active & no report              → MISSING-EVIDENCE
    elif value is None / parse-error / sentinel("unknown"/"n/a") → MISSING-EVIDENCE   # C6
    elif dimension is COLD (compute|data_access):                                     # D2
        if no baseline declared for <m> → MISSING-BASELINE      # fail-closed, prompt to declare
        elif required_data_access ⊄ collector-probed-repo-set → MISSING-BASELINE  # D2-1 config error
        elif compute value fails numeric coercion (e.g. "31Gi"→31 raises) → MISSING-EVIDENCE  # D2-2
        elif meets compute_floor (coerced int compare) / required_data_access ⊆ actual-accessible → CONFORMS
        else → BELOW-BASELINE                                   # actionable drift
        # (compute_floor is a MINIMUM; a stronger machine still CONFORMS — hardware
        #  variance above floor is never flagged. data_access: required set ⊆ {repos not "absent"}.
        #  D2-1: a baseline naming a repo the collector never probes is a CONFIG error
        #        (MISSING-BASELINE), never a silent un-satisfiable BELOW-BASELINE.
        #  D2-2: compute fields are coerced ("31Gi"→31, "881G"→881); parse failure → MISSING-EVIDENCE.)
    else:   # UNIFORM dims — equality across active reporters
        if python_cmd dimension → EXPECTED-DIFF                 # OS-driven (uv vs python)
        elif active reporters with a real value < 2 → PENDING
        else:                                                   # C1 tie handling
            counts = Counter(real values across active reporters)
            top, n = counts.most_common(1)[0]
            if number of values tied at n > 1 → NO-MAJORITY     # never order-dependent false EQUAL
            else verdict = EQUAL if value == top else DIVERGES
render HTML table → docs/reports/<date>-machine-equality-matrix.html

# D2: cold dims use CONFORMS/BELOW-BASELINE/MISSING-BASELINE — dissolves the C1 tie
#     problem for compute (no cross-machine vote; each compared to its own declared floor).
# D3: behavior is now a UNIFORM dim — its probe results (b1..b5) should match across
#     machines; a divergent probe (e.g. one machine's gate doesn't block) → DIVERGES.
# C6: a failed/missing cold value → MISSING-EVIDENCE (collection failure ≠ baseline miss).
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
| Modify | scripts/readiness/harness-config.yaml | (a) add `home-win` with `ssh_target: null` + `linux_reachable: false` (m3); (b) **D2: add per-machine `role` + `compute_floor` + `required_data_access` baseline blocks** for the declared-conformance grading |
| Modify | Linux cron installer (e.g. `scripts/cron/` setup) | **D1-1: per-machine weekly crontab entry** on ace-linux-1 + ace-linux-2 → `collect-equality.sh && build-equality-matrix.py` (commit-on-change) |
| Modify | scripts/windows/setup-scheduler-tasks.ps1 | **D1-1: weekly EqualityReport task** on licensed-win-1/2 (sibling to #2229 NightlyReadiness) |
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
| test_matrix_expected_diff_python_only | python_cmd is the ONLY EXPECTED-DIFF dim (compute moved to conformance, D2) | uv vs python | `EXPECTED-DIFF` |
| test_matrix_precedence_unreachable_over_missing | unreachable w/ stale report still UNREACHABLE (C3) | home-win w/ stale yaml | `UNREACHABLE` |
| test_matrix_unreachable_fixed | home-win/macbook UNREACHABLE w/o report | no report | `UNREACHABLE` |
| test_matrix_missing_evidence | active machine w/o report | no report for dev-secondary | `MISSING-EVIDENCE` |
| test_collect_no_forbidden_fields | emitted YAML carries no cron lines/commands/env/tokens/abs-home paths (C4) | run collector, scan output vs denylist | no denylist hit; gh_auth is enum not token |
| test_gitignore_negation_tracks_equality | `equality-*.yaml` trackable after negation (C5) | `git check-ignore -q` + `git add -n` | check-ignore exit≠0 AND `git add -n` succeeds |
| test_harness_config_home_win_shape | home-win added with ssh_target null + linux_reachable false (m3) | parse config | fields present, consumers tolerate |
| **D2 — conformance** | | | |
| test_matrix_compute_conforms_above_floor | compute ≥ declared floor → CONFORMS (stronger HW not flagged) | 32c vs floor 16c | `CONFORMS` |
| test_matrix_compute_below_floor | compute < declared floor → BELOW-BASELINE | 8c vs floor 16c | `BELOW-BASELINE` |
| test_matrix_data_access_required_subset | required_data_access ⊆ actual → CONFORMS | actual ⊇ required | `CONFORMS` |
| test_matrix_data_access_missing_required | a required repo absent → BELOW-BASELINE | missing `digitalmodel` | `BELOW-BASELINE` |
| test_matrix_missing_baseline_fail_closed | cold dim, no baseline declared → MISSING-BASELINE (fail-closed) | machine w/o baseline block | `MISSING-BASELINE` |
| test_matrix_baseline_unprobed_repo_is_config_error | required_data_access names a repo collector never probes → MISSING-BASELINE not BELOW-BASELINE (D2-1) | baseline requires `foo-repo` | `MISSING-BASELINE` |
| test_matrix_compute_coercion_parse_fail | compute field that won't coerce → MISSING-EVIDENCE not silent CONFORMS (D2-2) | ram_total="garbage" | `MISSING-EVIDENCE` |
| test_collect_settings_hash_canonical | b5 hash stable across CRLF/LF + key reorder of identical policy (D3-1) | same policy, CRLF vs LF | identical sha256 |
| **D3 — behavior probe** | | | |
| test_collect_behavior_probes_readonly | probe corpus writes nothing (side-effect-free) | run collector, snapshot fs before/after | no fs mutation |
| test_collect_behavior_gate_blocks | b1 gate-dry-run on synthetic unsafe write → `deny` | synthetic Write-to-src payload | probe result `deny`/ok |
| test_matrix_behavior_uniform_equal | identical probe results across machines → EQUAL | 2 machines same probes | `EQUAL` |
| test_matrix_behavior_divergence | one machine's gate probe differs → DIVERGES | b1 differs on 1 of 3 | `DIVERGES` |
| **D1 — cadence/idempotency** | | | |
| test_collect_commit_on_change_skips_timestamp | content hash excludes generated_at; timestamp-only change → no rewrite | run twice, no real change | 2nd run skips write/commit |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/readiness/ -v`
- [ ] No regression in scope: `uv run pytest tests/readiness/` green (whole-suite green is NOT this plan's contract — known unrelated flakiness per memory)
- [ ] `collect-equality.sh` runs live on dev-primary and writes a parseable `equality-dev-primary.yaml`
- [ ] `git check-ignore -q .claude/state/equality-dev-primary.yaml` exits non-zero AND `git add -n` succeeds (C5 — proves trackable, not just unmatched)
- [ ] Emitted YAML passes `test_collect_no_forbidden_fields` — no cron lines, commands, env values, tokens, or absolute $HOME paths; `gh_auth` is an enum (C4)
- [ ] `build-equality-matrix.py` renders correct verdicts for 1-machine, synthetic 3-machine, 2-disagree (NO-MAJORITY), and 4-split (NO-MAJORITY) fixtures
- [ ] `home-win`/`macbook-portable` render `UNREACHABLE`; the 4 active machines render live or `MISSING-EVIDENCE`
- [ ] **D2:** cold dims grade against declared baseline — `dev-primary` 32c ≥ floor → CONFORMS; a synthetic below-floor machine → BELOW-BASELINE; a machine with no baseline block → MISSING-BASELINE
- [ ] **D3:** behavior probe corpus (b1–b5) runs side-effect-free on dev-primary and emits comparable enums; `test_collect_behavior_probes_readonly` confirms no fs mutation
- [ ] **D1:** running the collector twice with no real change does NOT rewrite/commit the YAML (commit-on-change; timestamp excluded from the hash)
- [ ] Review artifacts posted to scripts/review/results/
- [ ] Issue comment posted on #2801 with matrix link + the 3 architecture findings as follow-ups

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | MAJOR → fixes applied | M1 roster-hardcoding (now reads harness-config.yaml), M2 behavior masked by EXPECTED-DIFF (now MISSING-EVIDENCE), m1 untestable negative reframed, m2 gitignore ordering pinned, m3 home-win config shape + consumer check, nit regression scope |
| Codex (r2) | MAJOR → fixes applied (r3 inline) | C1 tie-handling undefined (→ NO-MAJORITY verdict), C2 Windows wmic unreliable (→ unknown sentinel/MISSING-EVIDENCE, .ps1 follow-up), C3 verdict state-machine under-tested (→ +5 tests), C4 no redaction contract for git-tracked state (→ serialization allowlist + test_collect_no_forbidden_fields), C5 gitignore test weak (→ check-ignore -q + add -n), C6 compute-failure masked as expected-diff (→ MISSING-EVIDENCE) |
| Claude (r3 delta on D1/D2/D3) | MAJOR (1+3) | D1-1 weekly cron covers only dev-primary (OPEN — needs cadence-coverage decision); D2-1 baseline may name unprobed repo (→ MISSING-BASELINE config-error, fixed); D2-2 compute needs numeric coercion (→ fixed); D3-1 settings hash CRLF/LF false-divergence (→ canonicalize, fixed) |

**Overall result:** T2 review (Claude r1 + Codex r2) complete on the ORIGINAL scope. **Post-r2 the user made 3 decisions (D1/D2/D3) that materially changed scope** — see below. The plan is therefore NOT approval-ready until the delta is re-reviewed; the behavior-probe (D3) and conformance model (D2) were never seen by Codex r2.

### Post-r2 user decisions (2026-05-26) — re-review REQUIRED on the delta
- **D1 (cadence):** cold dims collected weekly + on-demand, commit-on-change (no daily git churn); hot dims referenced from nightly readiness.
- **D2 (verdict model):** cold dims (compute, data access) graded as conformance to a DECLARED per-machine baseline in harness-config.yaml (`CONFORMS`/`BELOW-BASELINE`/`MISSING-BASELINE`), not majority-vote. Dissolves the C1 tie problem for cold dims.
- **D3 (behavior in v1):** behavior probe ships in v1 as a deterministic, side-effect-free harness-behavior corpus (b1–b5: gate-blocks, skill-resolves, artifact-format, file-size-gate, settings-perms-hash) — NOT LLM-output diffing. This adds scope that touches hook invocation; needs scrutiny.
- **Scope/complexity:** grows from T2 → **T3** (now touches harness-config baselines, weekly cron wiring, and read-only hook invocation). Per the depth rule, T3 ⇒ 3-provider review on the delta.

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
- **Resolved (Codex r2 Q1):** ties render as explicit `NO-MAJORITY` (uniform dims only; cold dims use conformance per D2, so cold-dim ties cannot occur).
- **Resolved (Codex r2 Q2 / D3):** Windows compute emits `unknown` → MISSING-EVIDENCE; accurate Windows compute is a follow-up `.ps1` companion.
- **Resolved (D1):** cadence = weekly + on-demand, commit-on-change.
- **Resolved (D2):** cold dims use declared-baseline conformance.
- **Resolved (D3):** behavior probe ships in v1.
- **Risk (NEW, D3):** behavior probes invoke harness scripts (e.g. plan-approval-gate.sh). They MUST be read-only/dry-run — a probe that triggers a real write, log append, or push would corrupt state. Mitigation: each probe runs against synthetic input with no repo mutation; `test_collect_behavior_probes_readonly` snapshots the fs before/after and fails on any change; probes that can't run side-effect-free emit `n/a` → MISSING-EVIDENCE.
- **Risk (NEW, D2):** declared baselines in harness-config.yaml become stale if a machine's role/hardware changes and the baseline isn't updated → false BELOW-BASELINE. Mitigation: baseline is small and co-located with the roster (one edit site); MISSING-BASELINE fails closed and prompts a declaration.
- **Risk (NEW, D1):** commit-on-change hash must exclude `generated_at` (and any other volatile-but-meaningless field) or idempotency breaks. Guarded by `test_collect_commit_on_change_skips_timestamp`.
- **Follow-up issue (C2):** PowerShell collector companion for accurate `licensed-win-*` compute.

---

## Complexity: T3

**T3** (grew from T2 after D1/D2/D3) — two new scripts + two test files, plus modifications to `.gitignore`, `harness-config.yaml` (roster + declared baselines), and `scripts/cron/weekly-hermes-parity-review.sh`; the behavior probe invokes harness hook scripts read-only. Systemic harness surface (config + cron + hooks). Per the cross-review depth rule, T3 ⇒ 3-provider review (Claude + Codex + Gemini) on the changed scope.
