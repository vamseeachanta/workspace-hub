# Plan for #3255: Memory-staleness alerting (generalize session-curation freshness)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3255
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-26-plan-3255-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This issue (#3255, child of epic #3248) asks to generalize the just-shipped session-curation
freshness verdict family so the matrix also alerts when **memory surfaces** go stale: the canonical
`.claude/memory/` tree (bridge-managed `context.md` / `agents.md`) and the per-provider memory
runtimes (`config/agents/{codex,gemini}/MEMORY.runtime.md`, `~/.hermes/memories/`). It explicitly
leaves the design open: a new matrix line item `memory_freshness` (sibling to `session_curation`) OR
an alert in the bridge cron. **This plan recommends the line-item approach** and justifies the
rejection of alert-only below.

### Existing repo code
- Found: `scripts/readiness/build-equality-matrix.py:198-227` — `freshness_verdict(report, now)`:
  the time-since-last-run grading family for `session_curation` (CURATED-FRESH ≤12h / CURATED-STALE
  ≤24h / CURATED-EXPIRED >24h / MISSING-EVIDENCE fail-closed). Thresholds are module constants
  `CURATION_STALE_H=12`, `CURATION_EXPIRED_H=24` (lines 61-62). **This is the exact pattern to generalize.**
- Found: `scripts/readiness/build-equality-matrix.py:231-265` — `skill_currency_verdict()` (#3249):
  the most recent sibling line item; reads an audit FACTS block from a per-machine state JSON written
  by a dedicated audit script. Provides the present/absent + fail-closed (`MISSING-EVIDENCE`) idioms
  to copy for multi-surface grading.
- Found: `scripts/readiness/build-equality-matrix.py:353-384` — `verdict_for()` precedence
  orchestrator: routes `session_curation`→`freshness_verdict`, `skill_currency`→`skill_currency_verdict`.
  A new branch `memory_freshness`→`memory_freshness_verdict` slots here. Note `is_stale()`
  (STALE-CHECKOUT) still dominates all dims (line 367) — a dirty/behind checkout suppresses the
  memory cell too, which is correct.
- Found: structural wiring touchpoints in the same module: `BASE_DISPLAY_DIMS` (399-401), `GROUPS`
  (413-422), `ROLLUP_SEVERITY` (427-434), `OK_VERDICTS` (450-451), `remediate()` (454-506), HTML
  legend spans (664-666).
- Found: `scripts/curation/audit_skill_currency.py` (176 lines, #3249) — the audit-script template:
  PEP-723 inline deps, `machine_label()`, writes `.claude/state/skill-currency-<machine>.json` with
  `audited_at` + facts, `--stdout` dry-run, fail-closed `None` on unreadable surfaces. **`audit_memory_freshness.py` clones this shape, and REUSES its `machine_label()`** (not a re-implementation).
- Found (**freshness-signal precedent**): `audit_skill_currency.py:12-25` docstring locks the
  #3249 review decision to compare the **COMMITTED git tree** (`git ls-tree -r HEAD`), explicitly
  rejecting mtime because *"mtime is non-deterministic on fresh checkouts"* and *"immune to … WIP
  blinding the very alert you want."* This is the exact hazard the #3255 adversarial review flagged:
  `.claude/memory/{context.md,agents.md}` and `config/agents/{codex,gemini}/MEMORY.runtime.md` are
  **git-bridged** (written by the bridge, then committed + `git pull`'d onto every box), so their
  `st_mtime` equals git-checkout time, not refresh time → false reds on healthy boxes. **The memory
  audit therefore takes its freshness clock from `git log -1 --format=%cI -- <path>` (last-commit
  time of the bridged path), NOT from `st_mtime`** — the same git-over-mtime posture #3249 already set.
- Found: `scripts/memory/bridge-hermes-claude.sh` — the writer of every git-bridged memory surface:
  regenerates `.claude/memory/context.md` (§4) + `agents.md` (§3), emits the Codex/Gemini
  `MEMORY.runtime.md` read-back slices (§7b, lines 296-311), then commits `.claude/memory/` +
  `config/agents/{codex,gemini}/MEMORY.runtime.md` **only if the diff is non-empty** (§8, line 327).
  So a git-log commit time of these paths IS the bridge's last *content* refresh, and it is identical
  on every clone (commit metadata travels with the repo) — machine-invariant by construction.
- Found: `scripts/curation/curate_session_memory.py:158-170` — `memory_delta(since)` already `rglob`s
  `.claude/memory/*.md` (leak-safe: relative basenames only, bounded to 200). **The memory audit
  REUSES `memory_delta(None)` to enumerate the present canonical memory surface rather than rebuilding
  the scan** (adversarial must-fix #3); it imports `memory_delta` + `MEMORY` from the sibling module.
  Crucially, enumeration (which files are present) is decoupled from the freshness CLOCK (git-log) —
  `memory_delta`'s internal `st_mtime` read is used only for the changed-file list, never as the
  staleness signal for a git-bridged surface.
- Found: `scripts/curation/curate-session-memory.sh:30-37` — the every-6h cron wrapper that invokes
  `audit_skill_currency.py` **best-effort** (a failed audit does not block curation), then rebuilds
  the matrix. The new memory audit is added as a third best-effort call here — **no new cron job.**
- Found: `scripts/curation/curate-session-memory.ps1:88-97` — the **Windows** Task-Scheduler companion
  already invokes `audit_skill_currency.py` best-effort in its own §1b ("*Without this the
  skill_currency cell is permanently MISSING-EVIDENCE on Windows boxes*"). The memory audit MUST get
  an identical §1c here (adversarial must-fix #2) — otherwise `memory_freshness` is permanently
  MISSING-EVIDENCE on every Windows box, which run the `.ps1`, not the `.sh`.
- Found: `scripts/readiness/collect-equality.sh:149-182` (sections 6b/6c) + emit block 376-389 — how
  `session_curation` / `skill_currency` state JSON is referenced (never re-run) and emitted into
  `equality-<machine>.yaml`. A new section 6d + emit block follows this exactly.
- Found: `config/scheduled-tasks/schedule-tasks.yaml:92-114` — `equality-matrix-refresh` daily cron
  (`50 5 * * *`) is the **dead-man's-switch**: it rebuilds the matrix every day independent of the
  curation cron, so a frozen render still ages a dead cell to red. The new line item inherits this
  switch for free.

### Standards
Not applicable — this is harness/infrastructure tooling, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — harness-internal change, out of scope of `wiki-sibling-routing.md`
(`.claude/rules/wiki-sibling-routing.md` "Do not apply when … workspace-hub-internal artifact").

### Documents consulted
- Epic #3248 body — gap #7 ("No memory-staleness alerting (the session-curation freshness pattern
  generalizes here)"); this child closes it. Epic mandate: integrate, do not rebuild.
- `docs/plans/_template-issue-plan.md` — section headers followed here.
- `.claude/rules/patterns.md` — enforcement gradient (Level-2 script + tests; this stays Level-2).
- `.claude/rules/coding-style.md` — no hardcoded absolute paths (`scripts/enforcement/check-no-abs-paths.sh`).
- `tests/readiness/test_session_curation_freshness.py` (153 lines) + `tests/readiness/test_skill_currency.py`
  — the kebab-case importlib loading idiom + boundary/fail-closed test taxonomy to mirror.

### Gaps identified
- No existing implementation grades memory-surface freshness anywhere — `collect-equality.sh:145-147`
  emits `context_md_mtime` into the `memory` dim, but it is volatile-EXCLUDED from the canonical hash
  (line 396) and only feeds the equality `memory` dim, never a freshness verdict.
- No `audit_memory_freshness.py`, no `memory-freshness-<machine>.json` state, no `memory_freshness`
  dimension, verdict family, group, or remediation entry.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-26 via `gh issue view`):
- `#3255` — OPEN — "Self-improvement: memory-staleness alerting (generalize session-curation freshness) — epic #3248"
- `#3248` — OPEN — "Epic: robust cross-provider self-improvement & skill-currency ecosystem"

**File existence** (`ls` 2026-06-26):
- EXISTS: scripts/readiness/build-equality-matrix.py (691 lines)
- EXISTS: scripts/curation/audit_skill_currency.py (176 lines — template)
- EXISTS: scripts/curation/curate-session-memory.sh (54 lines — Linux/Git-Bash wrapper)
- EXISTS: scripts/curation/curate-session-memory.ps1 (117 lines — Windows Task-Scheduler wrapper;
  already wires skill-currency audit at §1b, lines 88-97 — the slot the memory audit mirrors)
- EXISTS: scripts/memory/bridge-hermes-claude.sh (367 lines — writer of all git-bridged memory surfaces)
- EXISTS: scripts/readiness/collect-equality.sh (413 lines)
- EXISTS: config/agents/codex/MEMORY.runtime.md, config/agents/gemini/MEMORY.runtime.md
- MISSING (claude has NO runtime memory file): config/agents/claude/MEMORY.runtime.md
  (`ls` → "No such file or directory") — so the codex+gemini runtimes are the only two provider
  runtime files; claude's memory lives in `.claude/memory/` itself.
- EXISTS: ~/.hermes/memories/ (cross-provider.md, MEMORY.md, USER.md)
- EXISTS: .claude/memory/context.md, .claude/memory/agents.md (bridge-managed)
- MISSING (new — this plan creates): scripts/curation/audit_memory_freshness.py,
  tests/readiness/test_memory_freshness.py

**Line excerpts** (`build-equality-matrix.py:223-227` — the pattern to generalize):
```
    if age_h <= CURATION_STALE_H:
        return "CURATED-FRESH"
    if age_h <= CURATION_EXPIRED_H:
        return "CURATED-STALE"
    return "CURATED-EXPIRED"
```

**Line excerpts** (`curate-session-memory.sh:30-37` — best-effort audit call to mirror):
```
SKILL_AUDIT="$REPO_ROOT/scripts/curation/audit_skill_currency.py"
if command -v uv >/dev/null 2>&1; then
  uv run --no-project --with pyyaml python "$SKILL_AUDIT" || echo "skill-currency audit failed (soft)" >&2
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SKILL_AUDIT" || echo "skill-currency audit failed (soft)" >&2
fi
```

**Gap proofs:**
- `grep -rn "memory_freshness" scripts/` → empty → confirms the dimension/verdict does not exist.
- `ls scripts/curation/audit_memory_freshness.py` → "No such file or directory" → audit tool absent.

**Freshness-signal proof** (`git log -1 --format=%cI -- .claude/memory/context.md` vs `stat -c %y`):
- The git-log commit time of a bridged path is the same on every clone (commit metadata), while
  `st_mtime` reflects the most recent `git checkout`/`git pull` that rewrote the file locally. On a
  box that pulled a no-change tree, `st_mtime` is stale even though the bridge is healthy elsewhere →
  confirms `st_mtime` is the wrong freshness signal and `git log` is the checkout-surviving one.

**Reproduction proofs:** N/A — this is a feature-add (new line item), not an alleged runtime
failure. No failing test/broken import to reproduce.

<!-- Source count: issue body + epic #3248 + 9 cited source files (build-equality-matrix.py,
     audit_skill_currency.py, curate_session_memory.py, curate-session-memory.sh,
     curate-session-memory.ps1, bridge-hermes-claude.sh, collect-equality.sh, schedule-tasks.yaml,
     test_session_curation_freshness.py) = ≥3 satisfied. -->

---

## Decision: line item, not alert-only

**Recommend: a new matrix line item `memory_freshness`, sibling to `session_curation`.** Rejected the
alert-only-in-bridge-cron alternative for three reasons:

1. **Dead-man's-switch.** The matrix grades freshness at BUILD time vs real `now`, and
   `equality-matrix-refresh` rebuilds DAILY independent of any curation/bridge cron
   (`schedule-tasks.yaml:92-114`). The graded signal is the **git-log commit time** of the bridged
   memory paths: when the bridge cron dies, no new memory commit lands, the commit time stops
   advancing, and the daily matrix rebuild ages the cell past 36h→72h to red — on every clone, since
   the commit time is machine-invariant. An alert living *inside* the bridge cron cannot fire when
   the bridge cron itself dies — which is precisely the staleness we must detect. The line item
   inverts that failure mode; the git-log clock (not a file mtime that a routine `git pull` would
   reset) is what makes the dead-man's-switch trustworthy.
2. **Consistency.** #3246 (`session_curation`) and #3249 (`skill_currency`) already established the
   audit-script → state-JSON → collect-emit → verdict-family → matrix-cell pipeline. A third sibling
   reuses ~90% of the substrate (epic #3248 mandate: integrate, don't rebuild).
3. **Visibility.** A green/red matrix cell + per-machine remediation card is reviewable at a glance
   across the fleet; a buried cron log line is not.

No new cron is added: the audit runs inside the existing every-6h `curate-session-memory.sh` wrapper
(Linux/Git-Bash, best-effort) **and its Windows twin `curate-session-memory.ps1` §1c** (so Windows
boxes are not permanently MISSING-EVIDENCE), and grading rides the existing daily
`equality-matrix-refresh`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-26-3255-memory-staleness-alert.md |
| Audit engine (new) | scripts/curation/audit_memory_freshness.py |
| Verdict family (modify) | scripts/readiness/build-equality-matrix.py |
| Collector emit (modify) | scripts/readiness/collect-equality.sh |
| Cron wrapper — Linux (modify) | scripts/curation/curate-session-memory.sh |
| Cron wrapper — Windows (modify) | scripts/curation/curate-session-memory.ps1 |
| Verdict tests (new) | tests/readiness/test_memory_freshness.py |
| Collector schema test (modify) | tests/readiness/test_collect_equality.py |
| Plan review — Claude | scripts/review/results/2026-06-26-plan-3255-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-26-plan-3255-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-26-plan-3255-gemini.md |

---

## Deliverable

A `memory_freshness` machine-equality line item: `scripts/curation/audit_memory_freshness.py` emits
per-machine `.claude/state/memory-freshness-<machine>.json` capturing the last-**refresh** timestamp
of each present memory surface — derived from the **git-log last-commit time** of the git-bridged
surfaces (repo `.claude/memory/{context.md,agents.md}`, codex/gemini `MEMORY.runtime.md`) so the
signal survives `git checkout`/`git pull`, and from real `st_mtime` only for the non-git-tracked
`~/.hermes/memories/` surface — reusing `curate_session_memory.memory_delta()` to enumerate the
canonical memory files (not a rebuilt scan) and `audit_skill_currency.machine_label()` for labelling.
`build-equality-matrix.py::memory_freshness_verdict()` grades the OLDEST present surface at build time
against real `now` (MEMORY-FRESH ≤36h / MEMORY-STALE ≤72h / MEMORY-EXPIRED >72h / MISSING-EVIDENCE
fail-closed) and renders it as a new matrix group cell with a remediation card. The audit is wired
into BOTH curation wrappers (`curate-session-memory.sh` Linux + `curate-session-memory.ps1` Windows)
so no box is permanently MISSING-EVIDENCE — all under full TDD, reusing the session-curation freshness
pattern and the existing every-6h wrapper + daily dead-man's-switch (no new cron).

---

## Pseudocode

`scripts/curation/audit_memory_freshness.py` (clone of `audit_skill_currency.py` shape; imports
`memory_delta` + `MEMORY` from `curate_session_memory`, and `machine_label` from `audit_skill_currency`):
```
# --- the freshness clock per surface ---------------------------------------------------------
# GIT-BRIDGED surfaces (written by bridge-hermes-claude.sh, then committed + git-pull'd onto every
# box): st_mtime == git-checkout time, NOT refresh time → would false-red healthy boxes. So the
# refresh clock is the LAST-COMMIT time of the path, which survives checkout and is machine-invariant.
def _git_commit_iso(rel_paths):                      # mirrors audit_skill_currency's git-over-mtime posture
    out = run(["git","-C",REPO,"log","-1","--format=%cI","--", *rel_paths], timeout=10, soft=True)
    return out.strip() or None                       # empty ⇒ untracked / never committed ⇒ surface absent

SURFACES (each → {present, refreshed_at, signal}):
  repo_memory   : signal="git-commit"; files = memory_delta(None)   # REUSE the leak-safe scan, don't rebuild
                  canonical = [".claude/memory/context.md", ".claude/memory/agents.md"]
                  present = both canonical files exist AND _git_commit_iso(canonical) is not None
                  refreshed_at = _git_commit_iso(canonical)
                  # canonical pair only — DELIBERATELY excludes .claude/memory/topics/ (auto-mirror
                  # churns constantly and would mask a dead bridge by always looking fresh).
  codex_runtime : signal="git-commit"; refreshed_at = _git_commit_iso(["config/agents/codex/MEMORY.runtime.md"])
  gemini_runtime: signal="git-commit"; refreshed_at = _git_commit_iso(["config/agents/gemini/MEMORY.runtime.md"])
  hermes_memories: signal="file-mtime"; present iff ~/.hermes/memories/*.md exists  # LOCAL, not git-tracked
                   refreshed_at = ISO(newest st_mtime among ~/.hermes/memories/*.md)  # mtime is correct here

function audit(machine):
    for each surface:
        if not present → {present: false}
        else → {present: true, refreshed_at: ISO, signal: "git-commit"|"file-mtime"}  # TIMESTAMP, not age
    return {machine, audited_at: now_iso, surfaces: {...}, schema_version: 1}
    # writes .claude/state/memory-freshness-<machine>.json; --stdout dry-run; --machine override.
    # NEVER emits abs paths / file contents / client ids — basenames + ISO stamps + bools only.
    # git unavailable / not-a-repo ⇒ _git_commit_iso returns None ⇒ those surfaces absent (fail-closed).
```

`build-equality-matrix.py::memory_freshness_verdict(report, now=None)`:
```
MEMORY_STALE_H = 36 ; MEMORY_EXPIRED_H = 72       # daily bridge cadence (not 6-hourly like curation)
mf = report.dimensions.memory_freshness
if not dict(mf) or not isinstance(mf.audited_at, str): return MISSING-EVIDENCE
ages = []
for each present surface with a parseable refreshed_at:
    age = (now - parse(refreshed_at)).hours
    if age < 0: return MISSING-EVIDENCE      # future stamp ⇒ clock skew ⇒ fail closed
    ages.append(age)
if not ages: return MISSING-EVIDENCE          # no present surface proved a timestamp
worst = max(ages)                             # OLDEST present surface dominates
if worst <= MEMORY_STALE_H:   return MEMORY-FRESH
if worst <= MEMORY_EXPIRED_H: return MEMORY-STALE
return MEMORY-EXPIRED
```

`verdict_for()` adds: `if dim == "memory_freshness": return memory_freshness_verdict(rep)` (after the
`skill_currency` branch, before COLD_DIMS — and after `is_stale()` so STALE-CHECKOUT still dominates).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/curation/audit_memory_freshness.py | per-surface last-**refresh** emitter: git-log commit time for git-bridged surfaces, `st_mtime` only for local `~/.hermes/`; REUSES `curate_session_memory.memory_delta` (enumeration) + `audit_skill_currency.machine_label` |
| Create | tests/readiness/test_memory_freshness.py | TDD: verdict boundaries + structural wiring + git-log-not-mtime regression (sandboxed tmp git repo) |
| Modify | scripts/readiness/build-equality-matrix.py | add `MEMORY_STALE_H/EXPIRED_H`, `memory_freshness_verdict()`, `verdict_for` branch, `BASE_DISPLAY_DIMS`, `DISPLAY_DIMS`, `GROUPS`, `ROLLUP_SEVERITY`, `OK_VERDICTS`, `remediate()`, HTML legend/CSS |
| Modify | scripts/readiness/collect-equality.sh | section 6d (reference state JSON) + `memory_freshness:` emit block; keep timestamps IN the canonical payload (not volatile-excluded) |
| Modify | scripts/curation/curate-session-memory.sh | third best-effort audit call (after skill audit, before collect-equality) |
| Modify | scripts/curation/curate-session-memory.ps1 | §1c best-effort audit call mirroring the §1b skill-currency block (Windows boxes run the `.ps1`, not the `.sh`) |
| Modify | tests/readiness/test_collect_equality.py | assert the new `memory_freshness:` emit keys appear |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_fresh_at_1h | nominal recent surface | all surfaces refreshed_at 1h ago | MEMORY-FRESH |
| test_fresh_at_exactly_36h_boundary_inclusive | stale threshold inclusive | worst surface 36h | MEMORY-FRESH |
| test_stale_at_36_5h | just past fresh | worst surface 36.5h | MEMORY-STALE |
| test_stale_at_exactly_72h_boundary_inclusive | expired threshold inclusive | worst surface 72h | MEMORY-STALE |
| test_expired_at_73h | just past stale | worst surface 73h | MEMORY-EXPIRED |
| test_worst_surface_dominates | oldest present surface drives verdict | repo 1h, gemini 80h | MEMORY-EXPIRED |
| test_absent_surface_ignored | an absent surface is not graded | repo 1h present, others absent | MEMORY-FRESH |
| test_missing_evidence_no_present_surface | nothing present | all surfaces present:false | MISSING-EVIDENCE |
| test_missing_evidence_no_dim | block absent | dimensions={} | MISSING-EVIDENCE |
| test_missing_evidence_non_dict_dim | scalar/list where dict expected | memory_freshness="x"/[]/42/None | MISSING-EVIDENCE |
| test_missing_evidence_no_audited_at | facts block lacks audited_at | dict without audited_at | MISSING-EVIDENCE |
| test_missing_evidence_garbled_stamp | unparseable refreshed_at | "yesterday"/""/"2026-13-99" | MISSING-EVIDENCE |
| test_missing_evidence_future_stamp_failclosed | negative age (clock skew) | worst surface -3h | MISSING-EVIDENCE |
| test_memory_freshness_in_display_dims | dim registered | — | in BASE_DISPLAY_DIMS & DISPLAY_DIMS |
| test_memory_fresh_is_ok_verdict | green set | — | MEMORY-FRESH in OK_VERDICTS |
| test_memory_group_exists | group wiring | — | GROUPS has ("memory-freshness", …, ["memory_freshness"]) |
| test_rollup_severity_ordering | severity order | — | EXPIRED>STALE>FRESH; FRESH==0 |
| test_verdict_for_routes_memory_freshness | orchestrator routes to verdict fn | expired stamp, clean provenance | MEMORY-EXPIRED |
| test_verdict_for_stale_checkout_dominates | dirty checkout suppresses cell | dirty provenance | STALE-CHECKOUT |
| test_remediate_memory_stale_returns_action | remediation card present | MEMORY-STALE | non-None (action, owner, by_design=False) |
| test_audit_emits_timestamps_not_ages | audit emits ISO refreshed_at, no abs paths | run audit() in sandboxed tmp git repo | refreshed_at is ISO; no "/" abs-path leakage |
| **test_audit_bridged_surface_uses_git_commit_not_mtime** | **CORE must-fix #1**: bridged surface freshness = git commit time, immune to a bumped mtime | tmp git repo: commit context.md+agents.md, then `os.utime(... now)` to make mtime fresh while the commit stays old | refreshed_at == the OLD git commit ISO (NOT the fresh mtime); surface `signal == "git-commit"` |
| test_audit_repo_memory_reuses_memory_delta | must-fix #3: enumeration goes through `curate_session_memory.memory_delta`, not a re-implemented rglob | monkeypatch/spy `memory_delta`; run audit() in tmp repo | `memory_delta` is invoked for repo_memory enumeration |
| test_audit_hermes_surface_uses_local_mtime | local (non-git) surface freshness = real mtime | tmp `~/.hermes/memories/x.md` with set mtime; HOME redirected | hermes_memories.refreshed_at == file mtime ISO; `signal == "file-mtime"` |
| test_audit_machine_label_reused | label comes from `audit_skill_currency.machine_label`, not a re-impl | set EQ_MACHINE=foo | emitted `machine == "foo"` |
| test_audit_git_unavailable_failcloses | git missing / not-a-repo ⇒ bridged surfaces absent | run audit() in a non-git tmp dir | repo_memory/codex/gemini present == False (fail-closed) |
| test_audit_absent_surface_marked | missing surface → present:false | tmp repo w/o ~/.hermes | hermes_memories.present == False |

---

## Acceptance Criteria

- [ ] New tests pass: `uv run --no-project --with pyyaml pytest tests/readiness/test_memory_freshness.py -v`
- [ ] No regression: `uv run --no-project --with pyyaml pytest tests/readiness/ -q` passes (existing
      session-curation + skill-currency + collect-equality suites stay green).
- [ ] `uv run --no-project --with pyyaml python scripts/curation/audit_memory_freshness.py --stdout`
      emits valid JSON with `audited_at` + a `surfaces` block carrying ISO `refreshed_at` timestamps,
      a per-surface `signal` field (`git-commit` for the three git-bridged surfaces, `file-mtime` for
      `hermes_memories`), and booleans only — no absolute paths, no file contents.
- [ ] Freshness signal is checkout-surviving: the audit derives git-bridged surfaces' `refreshed_at`
      from `git log -1 --format=%cI -- <path>`, NOT `st_mtime`; locked by
      `test_audit_bridged_surface_uses_git_commit_not_mtime`.
- [ ] No rebuilt scan: the repo_memory enumeration imports and calls
      `curate_session_memory.memory_delta`; `machine_label` is imported from `audit_skill_currency`
      (not re-implemented). Locked by `test_audit_repo_memory_reuses_memory_delta` +
      `test_audit_machine_label_reused`.
- [ ] BOTH curation wrappers invoke the audit best-effort: `curate-session-memory.sh` (Linux) AND
      `curate-session-memory.ps1` §1c (Windows) — verified by `grep audit_memory_freshness` in each.
- [ ] `bash scripts/readiness/collect-equality.sh --stdout` (or env equivalent) includes a
      `memory_freshness:` block; `build-equality-matrix.py` renders a "Memory freshness" group cell.
- [ ] Thresholds (36h/72h) are module constants with an inline rationale comment tying them to the
      daily bridge cadence (distinct from curation's 12h/24h).
- [ ] No abs-path leak: `bash scripts/enforcement/check-no-abs-paths.sh` passes on changed files.
- [ ] Legal scan: `bash scripts/legal/legal-sanity-scan.sh` clean (no client identifiers).
- [ ] Review artifacts posted to scripts/review/results/ (T2 → ≥2 providers).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |

**Overall result:** PENDING (plan not yet reviewed)

Revisions made based on review (pre-dispatch adversarial pass, folded 2026-06-26):
- **Core freshness signal corrected (must-fix #1):** git-bridged surfaces
  (`.claude/memory/{context.md,agents.md}`, codex/gemini `MEMORY.runtime.md`) are graded by
  `git log -1 --format=%cI` (checkout-surviving, machine-invariant) instead of `st_mtime`, which on a
  git-bridged file equals checkout time and false-reds healthy boxes. Only the local
  `~/.hermes/memories/` surface keeps `st_mtime`. Mirrors `audit_skill_currency.py`'s git-over-mtime
  precedent. New regression test `test_audit_bridged_surface_uses_git_commit_not_mtime`.
- **Windows wiring added (must-fix #2):** `curate-session-memory.ps1` §1c invokes the audit
  best-effort, mirroring its §1b skill-currency block — without it the cell is permanently
  MISSING-EVIDENCE on Windows.
- **Scan reuse (must-fix #3):** the audit imports + calls `curate_session_memory.memory_delta` for
  the canonical-memory enumeration and `audit_skill_currency.machine_label` for labelling, rather than
  rebuilding either. New tests `test_audit_repo_memory_reuses_memory_delta` + `test_audit_machine_label_reused`.

---

## Risks and Open Questions

- **Risk (WRONG freshness signal — the core adversarial must-fix):** `st_mtime` of a git-bridged
  file equals its last `git checkout`/`git pull` write, NOT its refresh time. The bridge writes
  `.claude/memory/{context.md,agents.md}` + codex/gemini `MEMORY.runtime.md` on the owner box, commits,
  and every other box gets them by `git pull` — which only rewrites a file (bumping mtime) when the
  CONTENT changed. So an mtime-based signal would (a) false-red a healthy box that pulled a no-change
  tree, and (b) be per-machine noisy. **Fix:** grade git-bridged surfaces by `git log -1 --format=%cI
  -- <path>` (last-commit time), which is checkout-surviving and machine-invariant — the same
  git-over-mtime posture `audit_skill_currency.py` already locked (#3249: *"mtime is non-deterministic
  on fresh checkouts"*). Only `~/.hermes/memories/` (local, not git-tracked) uses real `st_mtime`.
  Locked by `test_audit_bridged_surface_uses_git_commit_not_mtime` + `test_audit_hermes_surface_uses_local_mtime`.
- **Risk (dead-man's-switch integrity):** the audit must emit checkout-surviving TIMESTAMPS
  (`refreshed_at`), NOT pre-computed ages — only then can the daily matrix rebuild age a frozen cell
  to red. Tests `test_audit_emits_timestamps_not_ages` + `test_verdict_for_routes_memory_freshness`
  lock this.
- **Risk (canonical-hash volatility):** `collect-equality.sh:396` excludes volatile fields from the
  change-detection hash. The `memory_freshness` timestamps must stay IN the canonical payload (like
  `last_curated_at`) so a genuine memory refresh forces an `equality-<machine>.yaml` rewrite carrying
  the new stamp; do NOT add them to the exclude regex. Note the three git-bridged surfaces are now
  machine-invariant (same commit time on every clone), so they do not cause spurious per-machine hash
  divergence — only the local `hermes_memories` mtime legitimately varies per box. Verify in
  `test_collect_equality.py`.
- **Risk (topics/ masking):** including `.claude/memory/topics/` (auto-mirror, constant churn) in the
  `repo_memory` surface would always look fresh and defeat the alert. The audit reuses
  `memory_delta(None)` for the leak-safe enumeration but takes the freshness clock from
  `git log` of ONLY the bridge-managed canonical pair (`context.md`, `agents.md`) — topics never
  enter the clock. Documented inline + asserted by `test_audit_*` fixtures.
- **Risk (quiet-period false-stale on git-log):** because the bridge commits the bridged surfaces
  only when their content changed (`bridge-hermes-claude.sh:327`), a genuinely-static memory tree on
  a healthy box stops advancing its commit time and the cell could age to MEMORY-STALE/EXPIRED.
  Accepted: this is a uniform, machine-invariant signal (not per-box flakiness), `hermes_memories`
  (local mtime) still tracks live Hermes writes on the owner box, and a 72h+ gap with zero memory
  commits is itself worth surfacing. The alternative (bridge stamping a daily heartbeat field) was
  rejected — it would force a daily commit on every box, defeating the bridge's diff-gated
  churn-control. Thresholds are tunable constants if the cadence proves too aggressive.
- **Risk (threshold calibration):** 36h/72h assumes daily bridge cadence (`provider-dream-bridge` /
  `hermes-claude-bridge` @ ~04:0x). If a bridge legitimately runs less often on some box, a green box
  could false-flag. Mitigation: thresholds are named module constants, tunable in one place; start
  conservative (72h red = 3 missed daily runs).
- **Risk (Windows MISSING-EVIDENCE — adversarial must-fix #2):** Windows boxes run
  `curate-session-memory.ps1`, not the `.sh`. Without a §1c audit call there, `memory_freshness` is
  permanently MISSING-EVIDENCE on every Windows box. Fix: mirror the existing §1b skill-currency
  block. Verified by the acceptance `grep` on both wrappers.
- **Risk (per-machine surface variance):** Windows boxes have no `~/.hermes/memories/`; absent
  surfaces are ignored (present:false), never graded — mirrors `skill_currency` present/absent. A box
  where ALL surfaces are absent grades MISSING-EVIDENCE (fail-closed), not green.
- **Open:** should claude's own memory get a dedicated runtime file (`config/agents/claude/MEMORY.runtime.md`)
  to match codex/gemini? Today it does not exist; the `repo_memory` surface (`.claude/memory/`) covers
  claude. Flag for user — out of scope here; would be a separate bridge-config change.

---

## Complexity: T2

**T2** — one new engine module + one new test file, plus surgical edits to three existing files
(matrix verdict engine, collector, cron wrapper) and one existing test. Multi-file and harness-touching
but a direct clone of the #3246/#3249 substrate; not cross-provider-systemic. TDD mandatory; ≥2-provider
adversarial review.
