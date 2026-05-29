# Plan for #2841 core (gaps 1–6): read-back legs + Codex skills/rules + weekly consistency check

> **Status:** draft
> **Complexity:** T3 (systemic; memory + harness + standing-check subsystems; touches Codex/Hermes runtimes)
> **Date:** 2026-05-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2841 (closes #2854, #2855, #2856, #2857 across phases)
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-28-plan-2841-core-claude.md

Implements the 7-gap walk decisions (#2841 gap-decisions comment 2026-05-28). Gaps 1–6; #2847 (gap 7) is a separate follow-on plan.

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/memory/bridge-hermes-claude.sh` — runs 04:00 (cron #2846), consolidates Hermes facts → repo `.claude/memory/`, `git add .claude/memory/` + commit + push (line ~254). **Extension host for the read-back slice emit.**
- `scripts/memory/distill-provider-sessions.py` — the dream (now on main, #2845); writes `crossprovider_*.md` + `MEMORY.md` index to Claude auto-memory. **Source for the slice.**
- `scripts/agents/build-soul-runtime.sh` — builds `AGENTS.runtime.md` (Codex) = `SHARED_SOUL.md` + `codex/SOUL.delta.md`. **Extension host for skill-index + inlined rules.**
- `config/agents/codex/SOUL.delta.md` — Codex delta; flows into `AGENTS.runtime.md` (Codex's only native instruction surface). **Add read + skills instructions.**
- `scripts/readiness/hermes-consistency-check.sh` — per-machine probe (#2860, on main). **Reused by the weekly check.**
- `config/scheduled-tasks/schedule-tasks.yaml` + `scripts/cron/setup-cron.sh` — cron single-source (#2846 pattern). **Add weekly-check entry.**
- `.claude/rules/coding-style.md`, `patterns.md` — the universal rules to inline for Codex.

### Gaps identified (to build)
- No curation selector that emits a budget-capped cross-provider slice.
- No Codex/Hermes read-back sink + no instruction for Codex to read it.
- `build-soul-runtime.sh` emits no skill-index and inlines no rules.
- No full-matrix weekly consistency check + no rolling-drift-issue mechanism.

### Evidence (verified 2026-05-28)
- `bridge-hermes-claude.sh` commits to repo: `grep -n 'git add .claude/memory/'` → line ~254 (confirmed during #2846).
- `~/.codex/memories/` is an empty git repo (Codex assessment, #2841 comment).
- Probe on main: `git cat-file -e origin/main:scripts/readiness/hermes-consistency-check.sh` → exists (PR #2861 merged).
- Codex entrypoint = `~/.codex/AGENTS.md` → `config/agents/codex/AGENTS.runtime.md` (assessment, verified).

### Reproduction (N/A — feature work, not a bug)
N/A — building new capability; the "gap" is absence, evidenced above. Read-back absence confirmed: nothing writes to `config/agents/codex/MEMORY.runtime.md` (`ls` → missing) or `~/.hermes/memories/cross-provider.md`.

<!-- Sources: 6 (issue + 5 files/assessments) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-28-issue-2841-readback-skills-rules-weeklycheck.md |
| **Phase A** curation selector | scripts/memory/curate_readback_slice.py (NEW) |
| Phase A tests | scripts/memory/tests/test_curate_readback_slice.py (NEW) |
| Phase A bridge edit | scripts/memory/bridge-hermes-claude.sh (MODIFY) |
| Phase A Codex read-instruction | config/agents/codex/SOUL.delta.md (MODIFY) |
| **Phase B** soul-runtime edits | scripts/agents/build-soul-runtime.sh (MODIFY) |
| Phase B tests | scripts/agents/tests/test_build_soul_runtime_codex.sh (NEW) |
| Phase B Codex skills-instruction | config/agents/codex/SOUL.delta.md (MODIFY) |
| **Phase C** weekly check | scripts/cron/consistency-weekly-check.sh (NEW) |
| Phase C tests | scripts/cron/tests/test_consistency_weekly_check.sh (NEW) |
| Phase C cron entry | config/scheduled-tasks/schedule-tasks.yaml (MODIFY) |

---

## Deliverable
Codex and Hermes boot from a budget-capped curated slice of consolidated memory; Codex's runtime artifact instructs skill enumeration + inlines universal rules; a weekly check emits the orchestrators×dimensions consistency matrix and upserts a rolling drift issue on divergence.

---

## Phases (each lands as its own gated PR; shared design, sequenced)

### Phase A — Memory read-back (closes #2855, #2856, #2854; #2841 memory)

> **REVISED per review F1 (CRITICAL):** the live `MEMORY.md` + `crossprovider_*` files are **outside the repo, per-machine, NOT git-tracked** — sourcing the slice from them would make the committed `MEMORY.runtime.md` differ per machine → infinite cross-machine churn commits. **Fix:** source ONLY from the **git-tracked `.claude/memory/` mirror** (machine-invariant), AND commit the Codex slice from a **single designated machine**.

**`curate_readback_slice.py`** (the ONE shared selector):
```
SOURCE = git-tracked .claude/memory/ ONLY (machine-invariant):
  - .claude/memory/KNOWLEDGE.md
  - .claude/memory/claude-auto-memory.md   (the bridge-maintained snapshot of the auto-memory index)
  - .claude/memory/topics/                  (mirrored feedback titles)
  NEVER read $HOME/.claude/projects/.../memory/ (per-machine, untracked — F1).
extract: index/title lines + KNOWLEDGE entries (description/title only, NOT full bodies)
SHARED vs provider taxonomy (F4): keep entries tagged shared; ALLOWLIST by the SHARED_SOUL/delta
  category model, not a substring denylist. Drop entries whose structured category is claude-only
  (mcp-scope, browser-automation, output-style). A title merely *mentioning* "browser" is NOT dropped.
per-sink char caps, truncating at ENTRY boundaries:
  --target codex  -> cap ~7000 ; --target hermes -> cap ~2000 (Hermes native limit)
  single entry > cap (F5): DROP-AND-WARN (emit a "[N entries omitted: oversize]" marker line, stderr warn) — never mid-entry cut.
deterministic: stable sort by name; NO timestamps in body (machine-invariant output for the same commit).
header: "MANAGED by curate_readback_slice.py — do not hand-edit".
```
**`bridge-hermes-claude.sh`** — after its existing consolidation+commit:
```
# Codex slice: committed, but ONLY on the designated single machine to avoid cross-machine churn (F1)
if [ "$HOSTNAME_SHORT" = "ace-linux-1" ]; then
  python curate_readback_slice.py --target codex > config/agents/codex/MEMORY.runtime.md
  # included in the existing `git add .claude/memory/ + config/agents/codex/` commit step
fi
# Hermes local sink: every machine (reads the same tracked mirror, writes local-only, NOT committed)
python curate_readback_slice.py --target hermes > ~/.hermes/memories/cross-provider.md
```
**`config/agents/codex/SOUL.delta.md`** — add: "At session start, read `config/agents/codex/MEMORY.runtime.md` for consolidated cross-provider memory."
**Decommission** `~/.codex/memories/` (operational: remove the empty local git repo / gitignore; documented in PR).
**Hermes load (F7) — concrete, not deferred:** verification = `grep` the memory/skills load list in `~/.hermes/config.yaml` for the `memories/` dir; if `cross-provider.md` isn't auto-loaded, add it explicitly. Extend `hermes-consistency-check.sh` §3 to assert `~/.hermes/memories/cross-provider.md` presence so Phase C actually checks it (turns the untestable AC into a tested one).

### Phase B — Codex skills + rules (closes #2857; #2841 skills+harness)

> **REVISED per review F3:** `build-soul-runtime.sh` currently emits codex `AGENTS.runtime.md` and codex `SOUL.runtime.md` **byte-identically** (both via `emit_runtime codex SOUL.delta.md <out>`, lines 59-60). Phase B must make ONLY `AGENTS.runtime.md` diverge — so it's a **post-emit append step targeting AGENTS.runtime.md alone**, after the existing `emit_runtime` calls; `SOUL.runtime.md` (codex + claude + others) stays untouched.

```
# ... existing emit_runtime calls (unchanged) ...
# NEW post-emit step — appends to config/agents/codex/AGENTS.runtime.md ONLY:
append "## Skill index" : for each .claude/skills/*/SKILL.md -> name + first frontmatter description line, sorted
append "## Universal rules (inlined for Codex)" : contents of .claude/rules/coding-style.md + patterns.md
# (goal-invocation/calc-citation/wiki-routing NOT inlined — domain/Claude-only, stay path-refs)
```
**`config/agents/codex/SOUL.delta.md`** — add actionable skills section: inventory root `.claude/skills/`, "consult the Skill index in AGENTS.runtime.md; workspace `.claude/skills/` wins over `.agents/skills/` and plugins", name the mandatory lifecycle skills (issue-planning-mode, pre-completion-cleanup-audit). (This flows into BOTH codex runtimes via emit; that's fine — the instruction is provider-appropriate. Only the index+rules append is AGENTS-only.)

### Phase C — Weekly consistency check (#2841 standing check)

> **REVISED per review F2/F6/F8:** pin exact cron ids that exist on `origin/main`; freshness must NOT use file mtime (a fresh `git pull` resets mtime → stale content looks fresh, and it contradicts the "no timestamps in body" determinism rule); single machine owns the issue-upsert to avoid a concurrent-create race; create the label before first use; note `harness-lean-out` overlap.

```
run hermes-consistency-check.sh (capture PASS/WARN/FAIL) — now also asserts cross-provider.md (Phase A F7)
check dream: last cron log rc + deadletter jsonl line count (#2845)
check read-back freshness (F8): NOT mtime. Use the bridge cron log's last-run rc/date
  (logs/orchestrator/memory-bridge/) — the bridge is what regenerates the slice. Assert a successful
  run within 8 days. (mtime is checkout-time on a fresh clone — unreliable.)
check SOUL drift: diff each config/agents/*/SOUL.runtime.md (+ codex AGENTS.runtime.md) vs a fresh
  build-soul-runtime build (drift = committed != rebuilt)
check bridges declared in schedule-tasks.yaml — EXACT ids (verified on main): provider-dream-bridge,
  hermes-claude-bridge (+ -win variants)
render matrix -> docs/orchestrator-consistency/<date>-matrix.md  (git-tracked; NOT reports/ — gitignored)
if any FAIL: upsert ONE rolling issue by label `consistency-drift` (edit body if open issue exists, else create)
exit nonzero on FAIL so cron-health flags it
```
**Pre-req:** create the `consistency-drift` label (Phase C step 0) before the upsert can `--label` it.
**`schedule-tasks.yaml`** — entry `consistency-weekly-check`, `schedule: "0 6 * * 0"` (Sun 06:00), **machines `[dev-primary]` ONLY** (single owner — avoids the two-machines-same-minute concurrent-create race, F6; dev-primary is the canonical/leader host). `is_claude_task: false`.
**Overlap note (F2):** `harness-lean-out` (Mon 03:30) already audits memory bloat — the weekly check should *reference/complement* it, not duplicate the bloat audit.

---

## TDD Test List

| Test | Verifies |
|---|---|
| test_curate_excludes_claude_only | claude-only-category entries dropped from slice |
| **test_curate_keeps_shared_entries** (F4) | negative test: a SHARED entry whose text mentions "browser" is NOT dropped |
| test_curate_titles_not_bodies | contribute description/title lines, not full bodies |
| test_curate_codex_cap | codex sink ≤ ~7KB; truncates at ENTRY boundary (no mid-entry cut) |
| test_curate_hermes_cap | hermes sink ≤ ~2KB |
| **test_curate_single_oversize_entry** (F5) | one entry > cap → DROP-AND-WARN + omitted-marker, never mid-entry cut |
| **test_curate_machine_invariant** (F1) | reads ONLY tracked `.claude/memory/` snapshot → identical output regardless of `$HOME` auto-memory; never touches `$HOME/.claude/projects` |
| test_curate_idempotent | same tracked input → byte-identical output (stable sort, no timestamps) |
| test_curate_managed_header | output carries do-not-hand-edit header |
| test_soulruntime_skill_index | AGENTS.runtime.md gains a Skill index with one line per SKILL.md |
| test_soulruntime_inlines_universal_rules | coding-style + patterns inlined into AGENTS.runtime.md; goal-invocation NOT inlined |
| **test_soulruntime_codex_soul_unchanged** (F3) | codex `SOUL.runtime.md` byte-unchanged while `AGENTS.runtime.md` grows |
| test_soulruntime_claude_unchanged | Claude SOUL.runtime.md not bloated by Codex-only additions |
| test_weekly_matrix_emitted | matrix written to git-tracked docs/orchestrator-consistency/ |
| test_weekly_freshness_not_mtime (F8) | freshness derives from bridge cron-log run, not file mtime (fresh-clone mtime doesn't false-pass) |
| test_weekly_drift_upserts_single_issue | 2 consecutive drift runs → 1 issue (body updated), not 2 (mock gh) |
| test_weekly_label_created_before_use (F6) | `consistency-drift` label ensured before `--label` use |
| test_weekly_clean_no_issue | all-PASS run opens no issue, exit 0 |
| test_weekly_exit_nonzero_on_fail | any FAIL → exit nonzero |

---

## Acceptance Criteria
- [ ] Phase A: `curate_readback_slice.py` tests pass; `config/agents/codex/MEMORY.runtime.md` generated + committed by the bridge; `~/.hermes/memories/cross-provider.md` written locally (caps respected); Codex read-instruction in SOUL.delta; Hermes load path verified.
- [ ] Phase B: `AGENTS.runtime.md` gains skill index + inlined universal rules; Claude runtime unchanged; SOUL.delta skills-instruction added.
- [ ] Phase C: weekly check emits matrix, upserts single rolling drift issue, exit-nonzero on FAIL; declared in schedule-tasks.yaml; `setup-cron.sh --dry-run` renders it.
- [ ] No regression: existing bridge/build-soul/cron behavior intact.
- [ ] Review artifacts posted; summary comments on #2841 + closed children.

---

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (fresh-context subagent) | **MAJOR** | F1 [CRITICAL] slice sourced from per-machine untracked auto-memory → cross-machine churn; F2 stale resource-intel (cron ids); F3 codex AGENTS/SOUL runtime emitted identically → divergence unspecified; F4 denylist wrong polarity (fails open / drops shared); F5 single-oversize-entry undefined; F6 weekly upsert concurrency + label bootstrap; F7 Hermes load untestable as written; F8 mtime freshness fragile + contradicts no-timestamp rule |
| Codex / Gemini | UNAVAILABLE | cross-provider dispatch blocked from Claude-Code session (#2721/#2715); T3 degraded to single-author + fresh-context per `feedback_permission_gate_blocks_cross_review` |

**Overall:** PASS after revision (MAJOR → all 8 findings incorporated; re-review recommended at code stage).

**Revisions made:**
- **F1:** slice sourced ONLY from git-tracked `.claude/memory/` (machine-invariant) + Codex-slice commit gated to a single machine (ace-linux-1); Hermes local sink on every machine. Determinism test added (`test_curate_machine_invariant`).
- **F2:** verified the cron ids exist on `origin/main` (`provider-dream-bridge`, `hermes-claude-bridge`); pinned exact ids; flagged `harness-lean-out` overlap.
- **F3:** Phase B changed to a post-emit append targeting `AGENTS.runtime.md` only; test pins codex `SOUL.runtime.md` unchanged.
- **F4:** denylist → allowlist by SHARED_SOUL/delta category (structured, not substring); negative test added.
- **F5:** single-oversize-entry → drop-and-warn + marker; test added.
- **F6:** weekly check on `[dev-primary]` ONLY (no concurrent-create race); label created before use; tests added.
- **F7:** concrete Hermes verification + probe §3 extended to assert `cross-provider.md`.
- **F8:** freshness from bridge cron-log run, not mtime; test added.

---

## Risks and Open Questions
- **Risk:** the CLAUDE_ONLY denylist is heuristic — a mis-filter could drop a genuinely-shared learning or leak a Claude-only note. Mitigation: denylist is small + explicit; a test pins it; slice carries a "regenerate with curate_readback_slice.py" header so it's never hand-trusted.
- **Risk:** Hermes may not auto-load `cross-provider.md` — Phase A must verify empirically before claiming the Hermes read-back works (don't assume).
- **Risk:** `bridge-hermes-claude.sh` now writes a repo-tracked file (MEMORY.runtime.md) on every run → adds to the per-machine commit; staggering from #2846 already mitigates the cross-machine race, but confirm the slice is deterministic so identical content doesn't create churn commits.
- **Risk:** char-cap truncation must cut at entry boundaries, not mid-entry (test pins this).
- **Open:** Phase sequencing — A → B → C, each its own PR? (Recommended: yes; A unblocks the weekly check's read-back-freshness assertion in C.)
- **Open:** weekly check `consistency-drift` label — create it as part of Phase C.

## Complexity: T3
Systemic — 3 subsystems (memory bridge, soul-runtime build, cron), 2 provider runtimes touched, new shared library + new cron job. Lands as 3 sequenced PRs, each independently gated (plan inherited, per-PR TDD + review + completeness).
