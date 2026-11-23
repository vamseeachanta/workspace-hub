# Plan for #3251: Re-sync skills to tier-1 + external repos (no freeze-at-link)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3251
> **Client:** N/A
> **Project:** (n/a)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-26-plan-3251-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This is a harness/infrastructure line item under self-improvement epic #3248 (gap #4: "updates
don't re-reach repos"). It mirrors two already-shipped sibling line items — `session_curation`
(#3246) and `skill_currency` (#3249) — and reuses their audit→state-file→matrix-verdict→cron
pattern. The new dimension audits the FILESYSTEM HEALTH of the shared-skill symlinks that
`propagate-ecosystem.sh` creates, which today are created once and never re-verified.

### Existing repo code
- Found: `scripts/propagate-ecosystem.sh` — already contains the full re-sync MECHANICS:
  `discover_submodules()` (scans both nested and flat-sibling layouts, returns repos with
  `.claude/skills/`), `SHARED_SKILL_DIRS=("guidelines" "meta" "workflows")`, `is_link()`
  (symlink on unix / junction+marker on windows), `detect_platform()`, `create_directory_link()`,
  and `directory_matches_template()`. `propagate_skills()` already DETECTS+REPAIRS a stale/wrong-target
  link (unix realpath check), replaces a flattened symlink-as-text file (`-e && ! -d` → the
  Windows `IntxLNK<path>` case), and honors `--dry-run`. **Gap:** it is only ever invoked manually
  (`config/scheduled-tasks/schedule-tasks.yaml` has NO propagate entry), so when a new repo appears
  or a link rots, nothing re-reaches it. **Sourceability defect (adversarial r0):** the file ends with
  TWO unconditional trailing statements — `main "$@"` (line 479) AND `exit 0` (line 480). Naively
  `source`-ing it to reuse `discover_submodules` would (a) execute the whole run and (b) then hit
  `exit 0`, which terminates the *sourcing* shell (the verify script) outright. BOTH lines must be
  guarded behind `[[ "${BASH_SOURCE[0]}" == "${0}" ]]` so direct execution is byte-for-byte unchanged
  while a `source` defines the functions, runs nothing, and returns control to the caller.
- Found: `scripts/curation/audit_skill_currency.py` (#3249) — the template for an audit that emits
  per-machine FACTS to `.claude/state/skill-currency-<machine>.json` and is graded by a matrix verdict.
  Note its basis is `git ls-tree HEAD` (committed tree) — **NOT reusable here**: the shared-skill
  symlinks are gitignored (`update_gitignore()` writes them into each repo's `.claude/skills/.gitignore`
  and `untrack_shared_dirs()` removes them from the index), so they never appear in the committed tree.
  Link health can ONLY be assessed against the WORKING TREE filesystem.
- Found: `scripts/readiness/build-equality-matrix.py` — a new matrix dimension is NOT a "three-place"
  change (adversarial r0 undercount). Adding `skill_link_health` touches **ALL of these** (verified
  against the live file, with current line anchors):
  1. **`skill_link_health_verdict(report)`** — new fn, placed after `skill_currency_verdict()` (ends L265).
  2. **`verdict_for()` dispatch** (L369-376) — add `if dim == "skill_link_health": return skill_link_health_verdict(rep)`
     BELOW the `skill_currency` branch and ABOVE the `COLD_DIMS` branch.
  3. **`BASE_DISPLAY_DIMS`** (L399-401) — append `"skill_link_health"`.
  4. **`DISPLAY_DIMS`** (L402) — derived as `BASE_DISPLAY_DIMS + provider_rows()`, so it inherits the new
     dim automatically, but `tests/readiness/*` assert membership/order, so it is a contract point.
  5. **`GROUPS`** (L413-422) — add the dim to exactly ONE group (we extend the existing
     `skills-currency` group to also carry link health, OR add a sibling `skills-link` group). The
     render comment is explicit: every `BASE_DISPLAY_DIM` must land in exactly one group or it never
     renders. **This is the touch-point the "three places" framing missed.**
  6. **`ROLLUP_SEVERITY`** (L427-434) — add `LINKS-BROKEN` (6), `LINKS-DRIFTED` (6). `LINKS-HEALTHY` (0).
     `EXPECTED-DIVERGENCE` (1) and `MISSING-EVIDENCE` (4) are already present and reused as-is.
  7. **`OK_VERDICTS`** (L450-451) — add `"LINKS-HEALTHY"` (so `remediate()`/`equivalence_section()` skip a
     healthy cell).
  8. **`remediate()`** (L454-506) — add `LINKS-BROKEN` and `LINKS-DRIFTED` branches returning the
     re-sync fix `(action, owner, by_design=False)`.
  9. **CSS `<style>`** (L624-628) — map `.links-healthy` (green `#c6f6d5`), `.links-broken`
     (red `#fed7d7`), `.links-drifted` (orange `#feebc8`); the cell class is `verdict.lower()`.
  10. **Legend `<span>`s** (L661-667) — add LINKS-HEALTHY / LINKS-DRIFTED / LINKS-BROKEN swatches.
  11. **Sync targets** named in the `remediate()` docstring (L448-449): the verdict→fix table in
      `.claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md` AND `reconcile-ecosystem.sh`
      must carry the two new verdicts too (see the reconcile bullet below).
  (`EXPECTED-DIVERGENCE` is deliberately reused for the TEMPLATE-ABSENT case rather than minting a new
  verdict — it is already styled, already OK-listed, already severity-1 — which keeps the count at ~11,
  not ~14.)
- Found: `scripts/readiness/collect-equality.sh` — section "6c SKILL CURRENCY" (lines 164-182) reads
  `skill-currency-<machine>.json` and emits the `skill_currency:` YAML block (in the heredoc, lines
  381-389). A parallel "6d SKILL-LINK HEALTH" section + `skill_link_health:` heredoc block is the
  wiring point. The machine label here (`MACHINE`, derived L43-56) is the READ side of the join: it
  reads `skill-link-health-${MACHINE}.json`, so the WRITE side (the new audit) MUST emit under the
  identical label — see the machine-label bullet below.
- Found: `scripts/readiness/collect-equality.ps1` — the Windows collector DELEGATES YAML emission to
  `collect-equality.sh` (it only overlays the Windows-hard CIM compute fields via `EQ_*` overrides),
  so the new "6d" block is picked up on Windows with NO PowerShell collector edit. (Confirmed by the
  `.ps1`/`curate-session-memory.ps1` design notes: "delegates the rest … to collect-equality.sh".)
- Found: machine-label mapping is currently DUPLICATED in bash (`collect-equality.sh` L43-56 and
  `reconcile-ecosystem.sh` L65-73) and again in Python (`audit_skill_currency.py::machine_label`,
  L53-63). Per the "REUSE the machine label, do not reimplement" constraint, the new bash audit must
  NOT add a fourth copy. We factor the canonical bash table into a sourceable
  `scripts/lib/machine-label.sh::machine_label()` and source it from the new audit (and from
  `collect-equality.sh`, the read-side join partner) so write-label ≡ read-label by construction.
- Found: `scripts/curation/curate-session-memory.sh` (L30-37) AND `scripts/curation/curate-session-memory.ps1`
  (L88-97) — BOTH the every-6h cron wrapper and its Windows Task Scheduler companion already run
  `audit_skill_currency.py` best-effort (soft). The new audit hooks into BOTH, right after the
  skill-currency audit, identically soft. (Windows boxes run ONLY the `.ps1`; omitting it leaves the
  Windows `skill_link_health` cell permanently MISSING-EVIDENCE — the exact failure the `.ps1`
  skill-currency block's own comment warns about.)
- Found: `scripts/readiness/reconcile-ecosystem.sh` — the report-first / `--apply` corrective-action
  driver. `equality_plan()` (L193-239) reads the matrix `--json` verdicts and maps each non-OK verdict
  to a plan row. TWO concrete edits: (a) add `LINKS-HEALTHY` to the OK-skip `case` (L203-205, beside
  `EXPECTED-DIVERGENCE` which is already skipped); (b) add `LINKS-BROKEN` / `LINKS-DRIFTED` `case`
  branches that `add AUTO-SAFE "$MACHINE" … "bash scripts/skills/resync-skill-links.sh --apply"` (link
  repair is reversible + idempotent → AUTO-SAFE). The dim/verdict regex (`'"[a-z_:]+": "[A-Z-]+"'`,
  L198) already matches `skill_link_health` / `LINKS-BROKEN`. The `--apply` loop runs the resync row
  inline (it does NOT contain `$CRON`, so it is not deferred to the canonical equality refresh).
- Gap: no periodic verify of link health; no matrix cell; no guard-gated re-sync entry point; no
  sourceable machine-label helper.

### Standards
Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — infrastructure tooling, not domain knowledge.

### Documents consulted
- `config/scheduled-tasks/schedule-tasks.yaml` — `session-curation` task (lines 70-92) is the cron
  carrier; confirmed NO existing propagate/resync schedule entry exists.
- `scripts/readiness/harness-config.yaml` — `expected_skill_divergence:` allowlist (added for #3249)
  is the precedent for an `expected_skill_link_divergence:` allowlist of repos that legitimately
  carry no shared-skill links.
- Parent epic #3248; sibling shipped issues #3246 (session_curation), #3249 (skill_currency).
- `MEMORY.md` cross-machine note: git push to state-refs HANGS in non-interactive context — this plan
  publishes NOTHING to a git ref (the audit writes a local `.claude/state/` JSON only, like #3249),
  so that blocker does not apply.

### Gaps identified
- No periodic verify that re-discovers repos and re-checks each shared-skill link's filesystem state.
- No matrix dimension grading link health, so a link rot / un-propagated new repo is invisible.
- `propagate-ecosystem.sh` cannot be sourced (functions are not reusable) — its trailing `main "$@"`
  runs on import AND the following `exit 0` then terminates the importing shell.
- No sourceable canonical `machine_label()` — the host→slug mapping is reimplemented 3× (two bash, one
  Python), so a new bash audit risks a 4th drifting copy unless a shared lib is introduced first.
- Latent config drift: `guidelines` is in `SHARED_SKILL_DIRS` but `.claude/skills/_internal/guidelines`
  does not exist, so it is silently skipped — the verify must SURFACE a configured-but-absent template,
  not silently treat it as healthy.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-26 via `gh issue view`):
- `#3251` — OPEN — "Self-improvement: re-sync skills to tier-1 + external repos (no freeze-at-link) — epic #3248"; labels cat:skills-improvement, domain:ai-orchestration; body: "propagate-ecosystem.sh links skills once; updates don't re-reach repos. Add a periodic re-sync/verify that detects stale links and re-propagates, with a dry-run audit. Closes gap #4. Parent: epic #3248"

**File existence** (`ls` 2026-06-26):
- EXISTS: scripts/propagate-ecosystem.sh  (trailing `main "$@"` L479 + `exit 0` L480 — both to be guarded)
- EXISTS: scripts/curation/audit_skill_currency.py  (`machine_label()` L53-63 — the Python copy)
- EXISTS: scripts/curation/curate-session-memory.sh  (skill-currency audit block L30-37)
- EXISTS: scripts/curation/curate-session-memory.ps1  (skill-currency audit block L88-97 — Windows companion)
- EXISTS: scripts/readiness/collect-equality.sh  (MACHINE map L43-56; §6c L164-182)
- EXISTS: scripts/readiness/collect-equality.ps1  (delegates YAML to collect-equality.sh — no §6d edit needed)
- EXISTS: scripts/readiness/reconcile-ecosystem.sh  (equality_plan() L193-239; OK-skip L203)
- EXISTS: scripts/readiness/build-equality-matrix.py
- EXISTS: scripts/readiness/harness-config.yaml
- EXISTS: scripts/lib/workstation-lib.sh  (registry helper; precedent for a sourceable lib)
- EXISTS: tests/readiness/test_skill_currency.py  (#3249 verdict test — the location pattern to mirror)
- EXISTS: tests/readiness/test_build_equality_matrix.py  (structural-wiring contract test for DISPLAY_DIMS/GROUPS)
- EXISTS: tests/readiness/test_reconcile_ecosystem.py  (reconcile plan test — extend for new verdicts)
- EXISTS: scripts/skills/tests/  (bash test dir — sibling tests already live here)
- EXISTS: .claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md  (verdict→fix table to extend)
- EXISTS: .claude/skills/_internal/{builders,documentation,meta,workflows}
- MISSING: .claude/skills/_internal/guidelines  (configured in SHARED_SKILL_DIRS, no template → silently skipped today)
- MISSING (new — this plan creates): scripts/skills/resync-skill-links.sh
- MISSING (new — this plan creates): scripts/lib/machine-label.sh  (sourceable canonical machine_label())
- MISSING (new — this plan creates): scripts/skills/tests/test_resync_skill_links.sh  (SANDBOXED — never scans real ecosystem)
- MISSING (new — this plan creates): tests/readiness/test_skill_link_health.py  (verdict + structural wiring; mirrors test_skill_currency.py)

**Reproduction proof — the freeze-at-link gap is live** (`bash scripts/propagate-ecosystem.sh --skills-only --dry-run`, 2026-06-26):
```
Propagating ecosystem to 56 submodules...
Platform: unix (using symlinks)
DRY-RUN MODE — no changes will be made
SKILLS:
  OK   assetutilities/meta (link exists)
  ...
  LINK CAD-DEVELOPMENTS/meta -> _internal/meta (new)
  LINK deckhand/meta -> _internal/meta (new)
  LINK deckhand-live/meta -> _internal/meta (new)
  LINK llm-wiki/meta -> _internal/meta (new)
  LINK sabithaandkrishnaestates/meta -> _internal/meta (new)
```
- Reproduced at: 2026-06-26. Failure mode matches issue claim: YES — repos that appeared after the
  last manual propagate run (CAD-DEVELOPMENTS, deckhand, deckhand-live, llm-wiki, sabithaandkrishnaestates)
  have NO shared-skill links; updates have frozen at link time and never re-reached them.

**Symlinks-are-gitignored proof** (confirms working-tree, not git-tree, basis):
- `scripts/propagate-ecosystem.sh` `update_gitignore()` + `untrack_shared_dirs()` write each shared dir
  into `.claude/skills/.gitignore` and `git rm --cached` it → links never committed → `git ls-tree`
  cannot see them → the #3249 committed-tree approach cannot grade link health.

**Source-count of sources consulted:** issue body + 13 files (propagate-ecosystem.sh,
audit_skill_currency.py, build-equality-matrix.py, collect-equality.sh, collect-equality.ps1,
reconcile-ecosystem.sh, curate-session-memory.sh, curate-session-memory.ps1, harness-config.yaml,
schedule-tasks.yaml, workstation-lib.sh, tests/readiness/test_skill_currency.py,
tests/readiness/test_build_equality_matrix.py) = 14 distinct sources (≥3 satisfied).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-26-3251-resync-skills-no-freeze-at-link.md |
| Re-sync/verify script | scripts/skills/resync-skill-links.sh |
| Sourceable propagate lib | scripts/propagate-ecosystem.sh (guard BOTH `main "$@"` + `exit 0`) |
| Sourceable machine label | scripts/lib/machine-label.sh (canonical `machine_label()`, reused) |
| Audit bash test (SANDBOXED) | scripts/skills/tests/test_resync_skill_links.sh |
| Verdict + wiring python test | tests/readiness/test_skill_link_health.py (mirrors test_skill_currency.py) |
| Matrix verdict + 11 touch-points | scripts/readiness/build-equality-matrix.py |
| State emit (§6d) | scripts/readiness/collect-equality.sh (read-side join; sources machine-label.sh) |
| State emit (Windows) | scripts/readiness/collect-equality.ps1 (delegates §6d to .sh — no edit) |
| Allowlist | scripts/readiness/harness-config.yaml |
| Cron wiring (Linux/macOS) | scripts/curation/curate-session-memory.sh |
| Cron wiring (Windows) | scripts/curation/curate-session-memory.ps1 |
| Guard-gated apply registration | scripts/readiness/reconcile-ecosystem.sh (equality_plan OK-skip + 2 verdict cases) |
| Verdict→fix table sync | .claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md |
| Schedule note | config/scheduled-tasks/schedule-tasks.yaml (no new task — runs inside session-curation) |

---

## Deliverable

A periodic, cross-platform `scripts/skills/resync-skill-links.sh` that (a) in default REPORT mode
re-discovers every ecosystem repo via `propagate-ecosystem.sh`'s `discover_submodules` + `SHARED_SKILL_DIRS`
(reached by SOURCING propagate after BOTH its trailing `main "$@"` and `exit 0` are guarded behind a
`BASH_SOURCE==$0` check), classifies each shared-skill link's working-tree state (HEALTHY / DANGLING /
FLATTENED / MISSING / MODIFIED-REAL-DIR / TEMPLATE-ABSENT), and writes per-machine facts to
`.claude/state/skill-link-health-<machine>.json` under the canonical label from the shared
`scripts/lib/machine-label.sh::machine_label()` (the same label `collect-equality.sh` reads); and (b)
under a guard-gated `--apply` re-propagates by delegating to `propagate-ecosystem.sh --skills-only`. A new
`skill_link_health` equality-matrix cell grades those facts (LINKS-HEALTHY / LINKS-DRIFTED / LINKS-BROKEN /
EXPECTED-DIVERGENCE / MISSING-EVIDENCE) across ALL ~11 matrix touch-points, with the audit wired into BOTH
the every-6h `curate-session-memory.sh` (Linux/macOS) AND `curate-session-memory.ps1` (Windows) cron
wrappers, and the guard-gated repair registered in `reconcile-ecosystem.sh`, so link rot can no longer
freeze silently on any platform.

---

## Pseudocode

**A. Make propagate-ecosystem.sh sourceable (reuse without re-running) — guard BOTH trailing lines:**
```
# The file currently ENDS with two unconditional statements:
#     main "$@"     # line 479
#     exit 0        # line 480  ← terminates the SOURCING shell, not just a direct run
# Replace BOTH with one guarded block so a `source` runs neither:
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"        # executed only when run directly
    exit 0           # preserve the forced-0 exit ONLY on direct run (set -uo pipefail, no -e)
fi                   # when sourced: functions + SHARED_SKILL_DIRS defined, main NOT run, no exit
# Regression: a direct `bash propagate-ecosystem.sh --skills-only --dry-run` must still discover
# the same repos and return the same exit code as today (the `exit 0` stays inside the guard).
```

**A2. scripts/lib/machine-label.sh — single source of the canonical label (REUSE, do not reimplement):**
```
# Extract the EXACT host→slug case currently inlined in collect-equality.sh L43-56 into a function:
machine_label() {                       # honors EQ_MACHINE / arg override, identical mapping
    [[ -n "${EQ_MACHINE:-}" ]] && { printf '%s' "$EQ_MACHINE"; return; }
    local host; host="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')"
    case "$host" in
      ace-linux-1*) echo dev-primary;;  ace-linux-2*) echo dev-secondary;;
      *macbook*)    echo macbook-portable;;
      ace-win-1*|licensed-win-1*) echo ace-win-1;;
      ace-win-2*|licensed-win-2*) echo ace-win-2;;
      *) echo "${host:-unknown}";;
    esac
}
# collect-equality.sh (read side) sources this and replaces its inline block with machine_label(),
# so the WRITE label (resync) and the READ label (collector §6d) are identical BY CONSTRUCTION.
```

**B. resync-skill-links.sh — verify + guard-gated apply:**
```
parse args: --apply (default report-only), --dry-run (force no-op even under --apply),
            --only <repo>, --json, --machine <label>, --verbose
source scripts/lib/machine-label.sh          # canonical machine_label() (no fourth reimplementation)
source scripts/propagate-ecosystem.sh        # now safe (guarded) — gets discover_submodules,
                                             # SHARED_SKILL_DIRS, is_link, detect_platform,
                                             # directory_matches_template, WS_HUB, PLATFORM
machine = --machine or machine_label()       # EXACT label collect-equality.sh §6d reads
internal = WS_HUB/.claude/skills/_internal

classify(repo, shared) -> state:
    target   = internal/shared
    link     = repo/.claude/skills/shared
    if not -d target:            return TEMPLATE-ABSENT      # e.g. guidelines has no _internal template
    if is_link(link):
        if windows: return HEALTHY                          # junctions resolve in place
        if -d link and realpath(link)==realpath(target): return HEALTHY
        return DANGLING                                     # link present but target unresolved/wrong
    if -e link and not -d link:  return FLATTENED           # symlink-as-text (Windows IntxLNK file)
    if -d link:
        return HEALTHY if directory_matches_template(link,target) else MODIFIED-REAL-DIR
    return MISSING                                          # nothing there → never propagated / new repo

REPAIRABLE = {DANGLING, FLATTENED, MISSING}                 # safe to auto-fix
report = {}
for repo in (discover_submodules filtered by --only):
    for shared in SHARED_SKILL_DIRS:
        report[repo][shared] = classify(repo, shared)
counts = tally states across all repo×shared cells
write .claude/state/skill-link-health-<machine>.json:
    { machine, audited_at(ISO-Z), platform, repos_total,
      healthy, missing, dangling, flattened, modified_real_dir, template_absent,
      repairable (= missing+dangling+flattened), unexpected_missing_repos[],   # MISSING minus allowlist
      schema_version: 1 }
print classified table grouped by state (report-first)

if --apply and repairable>0 and guard_ok():
    bash propagate-ecosystem.sh --skills-only        # idempotent; backs up MODIFIED dirs, never clobbers
    re-run classify to confirm repairable→0; re-write state file
else if --apply:
    print "nothing to repair" or "guard blocked apply (reason)"; exit 0

guard_ok():
    # never let --apply run blind in a bad state
    return  uv-or-python available (propagate needs it for relpath) \
        AND _internal/ exists \
        AND NOT (any cell == MODIFIED-REAL-DIR with no backup writable)   # propagate handles backups,
                                                                          # but refuse if backup target unwritable
```

**C. skill_link_health_verdict(report) — in build-equality-matrix.py:**
```
sc = report.dimensions.skill_link_health
if not dict or audited_at not str:                 return MISSING-EVIDENCE
if repos_total not int>0:                           return MISSING-EVIDENCE     # discover failed → fail-closed
if dangling>0 or flattened>0:                        return LINKS-BROKEN          # rotted links present
if len(unexpected_missing_repos)>0:                  return LINKS-DRIFTED         # un-propagated, not allowlisted
if template_absent>0:                                return EXPECTED-DIVERGENCE   # configured-but-no-template (surfaced)
return LINKS-HEALTHY
# precedence: BROKEN > DRIFTED > EXPECTED-DIVERGENCE > HEALTHY ; MISSING-EVIDENCE on any unreadable fact
```

`unexpected_missing_repos` = repos with a MISSING cell whose basename is NOT in
`harness-config.yaml::expected_skill_link_divergence` (repos that legitimately carry no shared skills).

**D. The ~11 build-equality-matrix.py edits (each line item is a concrete diff site):**
```
1.  def skill_link_health_verdict(report): …            # new fn after skill_currency_verdict (L265)
2.  verdict_for(): + if dim == "skill_link_health": return skill_link_health_verdict(rep)   # L373-374
3.  BASE_DISPLAY_DIMS += ["skill_link_health"]                                                # L399-401
4.  DISPLAY_DIMS = BASE_DISPLAY_DIMS + provider_rows()  # inherits new dim (contract-tested)  # L402
5.  GROUPS: append "skill_link_health" to the skills-currency group (or a new "skills-link")  # L413-422
6.  ROLLUP_SEVERITY += {"LINKS-BROKEN":6, "LINKS-DRIFTED":6, "LINKS-HEALTHY":0}                # L427-434
7.  OK_VERDICTS |= {"LINKS-HEALTHY"}                                                           # L450-451
8.  remediate(): + LINKS-BROKEN / LINKS-DRIFTED branches → re-sync action, by_design=False     # L454-506
9.  CSS: .links-healthy{#c6f6d5} .links-broken{#fed7d7} .links-drifted{#feebc8}                # L624-628
10. Legend: + <span> swatches for LINKS-HEALTHY / LINKS-DRIFTED / LINKS-BROKEN                 # L661-667
11. SYNC: SKILL.md verdict→fix table + reconcile-ecosystem.sh (see E) — named in remediate() docstring
# EXPECTED-DIVERGENCE + MISSING-EVIDENCE are pre-existing verdicts reused unchanged (no new CSS/severity).
```

**E. reconcile-ecosystem.sh::equality_plan() registration (2 edits):**
```
# (a) OK-skip — add LINKS-HEALTHY beside the verdicts already skipped (L203-205):
case "$verdict" in
  CONFORMS|EQUAL|PARITY|EXPECTED-DIFF|EXPECTED-DIVERGENCE|UNREACHABLE|ABSENT|LINKS-HEALTHY) continue ;;
esac
# (b) verdict→action — new branches in the per-verdict case (alongside STALE-CHECKOUT etc.):
LINKS-BROKEN|LINKS-DRIFTED)
  add AUTO-SAFE "$MACHINE" "[$dim] shared-skill links $verdict — re-sync (idempotent, reversible)" \
    "bash '$REPO_ROOT/scripts/skills/resync-skill-links.sh' --apply" ;;
# The command does NOT contain $CRON, so the --apply loop runs it inline (not deferred). MISSING-EVIDENCE
# falls through to the existing generic "no fresh report — collect equality on this box" handler.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/skills/resync-skill-links.sh | verify (report) + guard-gated `--apply` re-sync; sources machine-label.sh + propagate lib |
| Create | scripts/lib/machine-label.sh | sourceable canonical `machine_label()` (REUSE, not a 4th reimplementation) |
| Modify | scripts/propagate-ecosystem.sh | guard BOTH trailing `main "$@"` AND `exit 0` behind `BASH_SOURCE==$0` so the file is sourceable without running/exiting (byte-identical direct-run behavior) |
| Modify | scripts/readiness/collect-equality.sh | (1) source machine-label.sh + replace inline MACHINE case (read-side join parity); (2) "6d" section reads state JSON + emits `skill_link_health:` YAML heredoc block |
| Create | scripts/skills/tests/test_resync_skill_links.sh | SANDBOXED bash test (throwaway temp ecosystem; never scans real `$WS_HUB/*`/parent) of all 6 classify states + JSON shape + guard + apply + dry-run + sourceable-no-exit |
| Create | tests/readiness/test_skill_link_health.py | verdict precedence + fail-closed + structural wiring (BASE_DISPLAY_DIMS/GROUPS/ROLLUP_SEVERITY/OK_VERDICTS/CSS/legend/remediate) — mirrors test_skill_currency.py location |
| Modify | tests/readiness/test_reconcile_ecosystem.py | assert `LINKS-HEALTHY` is OK-skipped and `LINKS-BROKEN`/`LINKS-DRIFTED` map to an AUTO-SAFE resync row |
| Modify | scripts/readiness/build-equality-matrix.py | ALL ~11 touch-points (Pseudocode D): new verdict fn + dispatch + BASE_DISPLAY_DIMS + GROUPS + ROLLUP_SEVERITY + OK_VERDICTS + remediate + CSS + legend |
| Modify | scripts/readiness/harness-config.yaml | add `expected_skill_link_divergence:` allowlist (repos without shared-skill links) |
| Modify | scripts/curation/curate-session-memory.sh | run the audit best-effort (soft) right after `audit_skill_currency.py` |
| Modify | scripts/curation/curate-session-memory.ps1 | mirror the soft audit call on Windows (else the Windows `skill_link_health` cell is permanently MISSING-EVIDENCE) |
| Modify | scripts/readiness/reconcile-ecosystem.sh | `equality_plan()`: add `LINKS-HEALTHY` to OK-skip + `LINKS-BROKEN`/`LINKS-DRIFTED` → AUTO-SAFE `resync-skill-links.sh --apply` |
| Modify | .claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md | add the 2 new verdicts to the verdict→fix table (kept in sync per remediate() docstring) |
| No edit | scripts/readiness/collect-equality.ps1 | Windows collector delegates §6d YAML to collect-equality.sh — picked up automatically (documented, verified) |
| Update | config/scheduled-tasks/schedule-tasks.yaml | document that the audit runs inside the existing `session-curation` task (description only; no new schedule) |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

**SANDBOX contract (must-fix #5 — tests NEVER scan the real ecosystem):** the bash suite
(`test_resync_skill_links.sh`) builds a THROWAWAY temp ecosystem under `mktemp -d` and operates only
inside it. Setup per test: create `<sbx>/wshub/scripts/`, COPY the real `propagate-ecosystem.sh`,
`resync-skill-links.sh`, and `scripts/lib/machine-label.sh` into the matching sandbox paths, write
fake `_internal/{meta,workflows}` templates, and fabricate fixture sibling repos BOTH nested
(`<sbx>/wshub/<repo>/.claude/skills/`) and flat (`<sbx>/<repo>/.claude/skills/`) — exercising both
`discover_submodules` layouts. Because every script self-locates via `${BASH_SOURCE[0]}`/`SCRIPT_DIR`,
running the SANDBOX copy makes `WS_HUB` resolve to `<sbx>/wshub`, so discovery scans `<sbx>/wshub/*`
and `<sbx>/*` — never the live `$WORKSPACE_HUB` or its parent. Fixture repo names avoid `EXCLUDE_DIRS`
(e.g. `repo-healthy`, `repo-missing`). `EQ_MACHINE` is pinned to a fixed label so the state filename is
deterministic. The suite asserts the real ecosystem state dir is untouched (no
`.claude/state/skill-link-health-*` written outside the sandbox).

| Test name | File | What it verifies | Expected output |
|---|---|---|---|
| test_propagate_sourceable_no_exit | bash | sourcing the (guarded) sandbox propagate copy defines `discover_submodules`+`SHARED_SKILL_DIRS` and does NOT exit the caller | function defined, sourcing shell survives past the source line |
| test_propagate_direct_run_unchanged | bash | direct `--skills-only --dry-run` on the sandbox copy still discovers the fixture repos + exits 0 | same repo list + rc=0 as pre-guard |
| test_machine_label_parity | bash | `machine-label.sh::machine_label()` == collect-equality.sh's derivation for a battery of spoofed hosts (write-label ≡ read-label) | identical slug for each host; honors EQ_MACHINE |
| test_classify_healthy | bash | valid symlink to `_internal` target | state=HEALTHY |
| test_classify_missing | bash | no link present (new repo) | state=MISSING |
| test_classify_dangling | bash | symlink whose target was deleted | state=DANGLING |
| test_classify_flattened | bash | regular file holding `IntxLNK<path>` (Windows symlink-as-text) | state=FLATTENED |
| test_classify_modified_real_dir | bash | real dir with content differing from template | state=MODIFIED-REAL-DIR |
| test_classify_template_absent | bash | shared dir with no `_internal` template (`guidelines` slot) | state=TEMPLATE-ABSENT |
| test_state_json_shape | bash | JSON has all required keys + schema_version=1; counts sum to repos×dirs | keys present, sums correct |
| test_state_written_under_sandbox_only | bash | report writes state ONLY under `<sbx>` | no file under the real `.claude/state/` |
| test_report_mode_makes_no_changes | bash | report mode never touches filesystem | links unchanged (mtime/identity stable) |
| test_apply_repairs_missing_and_dangling | bash | `--apply` re-propagates repairable cells (1 missing + 1 dangling) | both → HEALTHY, repairable=0 after |
| test_apply_skips_modified_real_dir | bash | `--apply` never clobbers local modifications | dir preserved (or backed up), not deleted |
| test_apply_guard_blocks_without_internal | bash | guard refuses apply when `_internal/` absent | exit 0, "guard blocked", no changes |
| test_dry_run_under_apply_is_noop | bash | `--apply --dry-run` changes nothing | repairable unchanged |
| test_verdict_links_healthy | py | all cells healthy (dangling/flattened/unexpected/template_absent all 0) | LINKS-HEALTHY |
| test_verdict_links_broken_precedence | py | broken beats drifted (dangling=1 + unexpected_missing=[r]) | LINKS-BROKEN |
| test_verdict_links_drifted | py | un-propagated repo, not allowlisted (unexpected_missing_repos=[deckhand]) | LINKS-DRIFTED |
| test_verdict_expected_divergence | py | only template-absent (template_absent=1, else clean) | EXPECTED-DIVERGENCE |
| test_verdict_missing_evidence_repos_zero | py | discover failed (repos_total=0) | MISSING-EVIDENCE |
| test_verdict_missing_evidence_no_stamp | py | garbled state (audited_at absent) | MISSING-EVIDENCE |
| test_allowlist_suppresses_missing | py | allowlisted repo MISSING link is not "unexpected" | not in unexpected_missing_repos |
| test_wiring_dim_in_base_display_dims | py | `skill_link_health` ∈ BASE_DISPLAY_DIMS and DISPLAY_DIMS | membership true |
| test_wiring_dim_in_exactly_one_group | py | `skill_link_health` lands in exactly one GROUPS entry (else it never renders) | count == 1 |
| test_wiring_rollup_and_ok_verdicts | py | LINKS-BROKEN/DRIFTED in ROLLUP_SEVERITY; LINKS-HEALTHY in ROLLUP_SEVERITY + OK_VERDICTS | all present |
| test_wiring_remediate_branches | py | `remediate("skill_link_health", "LINKS-BROKEN")` returns an actionable, non-by_design fix; LINKS-HEALTHY → None | resync action / None |
| test_wiring_html_renders_cell_and_legend | py | end-to-end main() renders a `<th>skill_link_health</th>` row + `.links-broken` CSS + legend swatch | all substrings present |
| test_reconcile_links_healthy_skipped | py | reconcile `equality_plan` emits NO row for LINKS-HEALTHY | absent from plan |
| test_reconcile_links_broken_auto_safe | py | LINKS-BROKEN/DRIFTED → an AUTO-SAFE row invoking `resync-skill-links.sh --apply` | present, class AUTO-SAFE |

---

## Acceptance Criteria

- [ ] `bash scripts/skills/resync-skill-links.sh` (report mode) writes a valid
      `.claude/state/skill-link-health-<machine>.json` and exits 0 WITHOUT modifying any link.
- [ ] The written label equals `collect-equality.sh`'s `MACHINE` on the same host (join works);
      both derive it from the shared `scripts/lib/machine-label.sh::machine_label()`.
- [ ] On this box the report shows the currently-MISSING repos (CAD-DEVELOPMENTS, deckhand,
      deckhand-live, llm-wiki, sabithaandkrishnaestates) and flags `guidelines` as TEMPLATE-ABSENT.
- [ ] `bash scripts/skills/resync-skill-links.sh --apply` re-propagates repairable links and a
      subsequent report shows `repairable=0`; MODIFIED-REAL-DIR cells are never deleted.
- [ ] `bash scripts/skills/resync-skill-links.sh --apply --dry-run` makes no changes.
- [ ] `scripts/propagate-ecosystem.sh` run directly behaves identically to today (regression: a
      direct `--skills-only --dry-run` still discovers 56 repos, same exit code); SOURCING it executes
      NEITHER `main` NOR the trailing `exit 0` (the sourcing shell survives).
- [ ] Bash tests pass and are SANDBOXED: `bash scripts/skills/tests/test_resync_skill_links.sh` runs
      entirely inside a `mktemp -d` ecosystem and writes nothing under the real `.claude/state/`.
- [ ] Verdict + wiring tests pass: `uv run --no-project --with pyyaml python -m pytest tests/readiness/test_skill_link_health.py -v`.
- [ ] All ~11 matrix touch-points are exercised: `skill_link_health` ∈ BASE_DISPLAY_DIMS, in exactly
      one GROUPS entry, in ROLLUP_SEVERITY, with LINKS-HEALTHY in OK_VERDICTS, a `.links-broken` CSS
      class + legend swatch in the rendered HTML, and a `remediate()` branch for LINKS-BROKEN/DRIFTED.
- [ ] `build-equality-matrix.py` renders a `skill_link_health` cell; a forced DANGLING fixture
      grades LINKS-BROKEN, a clean tree grades LINKS-HEALTHY.
- [ ] `reconcile-ecosystem.sh`: LINKS-HEALTHY is OK-skipped; LINKS-BROKEN/DRIFTED emit an AUTO-SAFE
      `resync-skill-links.sh --apply` row. `test_reconcile_ecosystem.py` extended + green.
- [ ] BOTH `curate-session-memory.sh` AND `curate-session-memory.ps1` run the audit soft (a failed
      audit logs but does not fail the cron); the `.ps1` block mirrors its skill-currency block.
- [ ] SKILL.md verdict→fix table carries the two new verdicts (sync-with-remediate() docstring honored).
- [ ] No regression: existing `skill_currency` and `session_curation` cells still build;
      `tests/readiness/test_build_equality_matrix.py`, `test_skill_currency.py`, and
      `test_collect_equality.py` still pass (collect-equality.sh machine-label refactor preserves behavior).
- [ ] No absolute-path leak in committed code (paths derived from `WS_HUB`/`git rev-parse`, no
      `/mnt/local-analysis/...` literals); no client identifiers. `scripts/legal/legal-sanity-scan.sh` clean.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |
| Gemini | (pending) | |

**Overall result:** (pending)

Revisions made based on review (adversarial r0 must-fixes folded 2026-06-26):
1. propagate-ecosystem.sh ends with BOTH `main "$@"` (L479) AND `exit 0` (L480) — guard BOTH behind
   `BASH_SOURCE==$0` (the original "guard `main`" would still hit `exit 0` and kill the sourcing shell).
   Added `test_propagate_sourceable_no_exit` + `test_propagate_direct_run_unchanged`.
2. Matrix wiring was undercounted ("three places"). Enumerated ALL ~11 touch-points (Pseudocode D):
   verdict fn, verdict_for dispatch, BASE_DISPLAY_DIMS, DISPLAY_DIMS, GROUPS (the missed one — a dim
   not in a group never renders), ROLLUP_SEVERITY, OK_VERDICTS, remediate, CSS, legend, + SKILL.md/
   reconcile sync. Added structural-wiring tests.
3. Specified reconcile-ecosystem.sh registration (Pseudocode E): `LINKS-HEALTHY` added to the
   `equality_plan()` OK-skip + `LINKS-BROKEN`/`LINKS-DRIFTED` → AUTO-SAFE `resync --apply` rows; added
   `test_reconcile_ecosystem.py` assertions.
4. Wired the audit into curate-session-memory.PS1 (Windows), not just the `.sh` — else the Windows
   skill_link_health cell is permanently MISSING-EVIDENCE.
5. Defined a TDD SANDBOX (mktemp -d mini-ecosystem; scripts self-locate so WS_HUB pins to the sandbox)
   so the bash suite never runs propagate against the real `$WS_HUB/*` + parent/* ecosystem; added
   `test_state_written_under_sandbox_only`.
Additional consistency fixes: machine_label() REUSED via new `scripts/lib/machine-label.sh` (no 4th
reimplementation; collect-equality.sh read side sources it); corrected verdict-test path to
`tests/readiness/test_skill_link_health.py` (mirrors the #3249 sibling, not `scripts/readiness/tests/`).

---

## Risks and Open Questions

- **Risk (basis mismatch):** unlike #3249, this audit MUST stat the working tree (links are gitignored),
  so it is NOT WIP-immune — a developer mid-edit on a sibling repo could momentarily show MODIFIED-REAL-DIR.
  Mitigation: MODIFIED-REAL-DIR does not grade BROKEN/DRIFTED (it is benign), and `--apply` never touches it.
- **Risk (trailing `exit 0` kills the sourcing shell):** the file ends with `main "$@"` AND `exit 0`;
  guarding only `main` (as the original draft did) would still hit `exit 0` and terminate the verify
  script the instant it sources propagate. Mitigation: BOTH lines move inside the single
  `[[ BASH_SOURCE==$0 ]]` block; `test_propagate_sourceable_no_exit` proves the sourcing shell runs past
  the `source` line, and `test_propagate_direct_run_unchanged` proves direct-run rc/behaviour is identical.
- **Risk (sourcing side-effects):** `propagate-ecosystem.sh` sets `set -uo pipefail` and defines color vars
  + `WS_HUB`/`PLATFORM`/`SHARED_SKILL_DIRS`/`EXCLUDE_DIRS` at top level; sourcing it inherits those.
  Mitigation: the guard stops `main` AND `exit 0`; the verify script tolerates inherited `set -u` (all
  vars defined before use), intentionally REUSES the inherited `WS_HUB`/`PLATFORM`/`SHARED_SKILL_DIRS`,
  and never redefines a function name it sources.
- **Risk (machine-label refactor regression):** factoring `collect-equality.sh`'s inline MACHINE `case`
  into `scripts/lib/machine-label.sh` touches a tested collector. Mitigation: the extracted function is
  the same mapping byte-for-byte (incl. `EQ_MACHINE` override); `test_collect_equality.py` is run as a
  regression gate, and `test_machine_label_parity` pins write-label ≡ read-label across spoofed hosts.
  `reconcile-ecosystem.sh`'s copy is left as-is this pass (it derives the same slug independently and is
  not the join partner) — flagged as an optional follow-on consolidation to avoid scope creep.
- **Risk (test scans real ecosystem):** a naive bash test that just calls `resync-skill-links.sh` would
  run `discover_submodules` against the live `$WS_HUB/*` + parent/* (dozens of real repos), be slow,
  non-deterministic, and could even repair real links under `--apply`. Mitigation: the SANDBOX contract
  above — copy the scripts into a `mktemp -d` mini-ecosystem so self-location pins `WS_HUB` to the
  sandbox; `test_state_written_under_sandbox_only` asserts the real state dir is untouched.
- **Risk (guard over-eager apply):** auto-apply under cron could repair links the operator intentionally
  removed. Mitigation: the every-6h cron runs REPORT-ONLY (matrix cell turns orange/red); `--apply` is
  invoked only by `reconcile-ecosystem.sh --apply` (AUTO-SAFE) or manually — never inside the curate cron.
- **Risk (Windows junction detection):** `is_link()` on Windows relies on a sibling `.link-marker` file or
  `fsutil reparsepoint`; a junction without a marker could misclassify. Mitigation: reuse the EXISTING
  `is_link()` verbatim (already battle-tested by propagate); classify windows links HEALTHY when `is_link`
  is true (junctions resolve in place), matching propagate's own skip logic.
- **Risk (allowlist drift):** `expected_skill_link_divergence` must be seeded with repos that legitimately
  carry no shared skills, or every such repo grades LINKS-DRIFTED. Mitigation: seed the allowlist from a
  baseline report run and document the "update this list when intent changes" prompt, exactly as #3249 did.
- **Open:** should `guidelines` be FIXED (add `_internal/guidelines` template) rather than just surfaced as
  TEMPLATE-ABSENT? Flag for user — out of scope for this issue; this plan only SURFACES the gap.
- **Open:** state-ref cross-machine publish is intentionally OUT of scope (the audit writes a local state
  file only, like #3249) given the known non-interactive push hang; confirm that is acceptable.

---

## Complexity: T2

**T2** — one new bash audit + a new sourceable machine-label lib + a sourceability guard (both trailing
lines) on propagate; a new matrix dimension wired across ALL ~11 build-equality-matrix.py touch-points
(verdict fn + dispatch + BASE_DISPLAY_DIMS + GROUPS + ROLLUP_SEVERITY + OK_VERDICTS + remediate + CSS +
legend, plus the SKILL.md + reconcile sync targets); a collector §6d emit (with a machine-label refactor
of the read side); reconcile registration (OK-skip + 2 verdict cases); cron hooks in BOTH the `.sh` and
`.ps1` wrappers; and TDD across a SANDBOXED bash suite + a python verdict/wiring/reconcile unit. It
mirrors two already-shipped line items (#3246, #3249), so the pattern is proven; the touch-point count is
larger than the sibling because a new matrix DIMENSION (not just a verdict tweak) is being added. Not T3
because no new cross-machine transport or schema negotiation is introduced.
