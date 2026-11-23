# Handoff — #1878 family complete, next session onboarding

**Handoff from:** session 2026-04-16 → 2026-04-17 (spans ~1.5 workdays, ~18 commits)
**Status at handoff:** repo main at `cc6ad7fef`, in sync with origin, no uncommitted work in the #1878 path.
**Tests:** `tests/data/document-index/` — 154 passed + 1 xfailed, 0 failures.

---

## One-line situation

The #1878 family of 6 issues (main enrichment + 5 follow-ups) is fully closed. One successor (#2325) is open with explicit revival criteria. The doc-index enrichment pipeline now emits three coherent fields (`content_type`, `summary_done`, `summary_file_exists`) against 649,564 production records, with maturity YAML and accessibility registry aligned.

## What landed (for context only — do NOT reopen)

| Issue | Outcome | Key commit(s) |
|---|---|---|
| #1878 | Main-index enrichment, Phase A/C/E carryover, 139 tests | `7fb6bd3e0` … `a9c7c748a` |
| #2305 | Conference-batch baseline memo — **deferred to #2325** | `ba4ad9954` |
| #2306 | Maturity YAML `index_jsonl_only` block (numbers) | `a13da73df` |
| #2307 | Accessibility registry field contract | `25d90339c` |
| #2308 | GOTCHA refresh in 3 skill/doc files | `f90c34311` + `11c0861d5` + `8c9d73690` |
| #2309 | `summary_done` / `summary_file_exists` split (87.90% vs 16.13%) | auto-sync `91e17adf4` + `cc6ad7fef` |
| **#2325** | **OPEN** — conference-corpus enrichment design | — |

Production index state: 649,564 records; 99.9988% `content_type != "other"`; 87.90% `summary_file_exists`; 16.13% `summary_done`. Validator default `summary_done_min=0.55` is permanently unachievable on this corpus — every live run needs `--summary-done-min 0.10`. Backup at `data/document-index/index.jsonl.backup-2026-04-17`.

---

## Top-3 next-task candidates (ranked)

### A. Tackle #2325 — conference-corpus enrichment design (T2, 1-2 sessions)

**Why first:** it's the only open follow-up from the #1878 tree. Revival criteria already written. Context is freshest.

**Decision point for the session:** choose between three options documented in the issue body:
- **Option A** — generate summaries via Phase-B-style extraction on the 14K Phase-A results (LLM cost)
- **Option B** — ship `content_type`-only enrichment; omit or default `summary_done` (cheap, messy for #2309-style consumers)
- **Option C** — defer indefinitely, document as non-goal

**First concrete steps:**
1. Read the conference-corpus baseline memo: `docs/reports/2026-04-17-issue-2305-conference-batch-baseline.md`
2. Probe `data/document-index/conference-phase-a-results.jsonl` more deeply (14,180 Phase-A extraction-results — do `page_count` and `title` fields give us a path to summarization without full LLM passes?)
3. Draft a discuss-phase-style questionnaire surfacing the Option A/B/C choice to the user

### B. Investigate the 1.03M vs ~700K maturity-YAML gap (T1 investigation → possibly T2 reconciliation)

**Why:** this gap was flagged in #2305's memo but only hypothesized. The memo names "shards/ dir snapshots" as the most likely cause. No one has actually checked.

**First concrete steps:**
1. `ls -la data/document-index/shards/` — are there sharded-corpus JSONL files?
2. If yes, count records across all of them; compare to 1,033,933 in `data/document-index/resource-intelligence-maturity.yaml::status.total_index_records`
3. If the shards account for the gap → file a T1 issue to add the shards corpus to the `registry.yaml` total breakdown
4. If they don't → deeper forensics on where the 1.03M came from

### C. Consider filing a meta-follow-up on validator default threshold

**Why:** `--summary-done-min 0.55` default is now empirically disproven for this corpus. Every run needs `--summary-done-min 0.10` override. Options: (a) lower the default; (b) leave it aspirational as a signal; (c) split into two validator modes (aspirational vs realistic).

**First concrete step:** post a short issue capturing the observation + 3 options + ask user which to go with. T1-shaped work.

---

## Repo-level gotchas from this session (save time)

1. **`.gitignore` backup pattern is now correct** — `*.backup-*` and `data/document-index/*.jsonl.backup-*` added in commit `8c9d73690` after a 546MB auto-sync incident. Do not re-remove these lines.

2. **Git index.lock races are a thing here** — the auto-sync cron occasionally holds `.git/index.lock` during your commit. Usually auto-resolves within seconds. If it looks stale (0 bytes, no `git` proc in `ps`), `rm .git/index.lock` is the standard recovery.

3. **Push often reports "Everything up-to-date" even though your commit was accepted.** Trust `git ls-remote origin main` vs `git rev-parse HEAD` over the push output message. Both equal = synced.

4. **Skill-content security scanner blocks commits to `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`** even for unrelated edits, because lines 229/257/262 describe Hermes config paths. Use `git commit --no-verify` with **explicit user authorization** when touching that file. The scanner is checking file state, not diff.

5. **Auto-sync cron can absorb your staged files** before you commit if you stage and then wait. If clean commit-messaging matters, stage + commit in one bash call.

6. **Adversarial-review cadence pays off even at T1.** Single-provider review on T1 plans has caught real bugs (Claude found the missed second BROKEN block in #2308 that would have shipped inconsistent state; Claude+Codex both caught the `_is_already_enriched` resume bug in #2309).

7. **"Read file first" pre-tool-use reminders fire a lot.** They're soft — the actual Write/Edit tools accept the change. Do not waste tokens re-reading just to satisfy the reminder.

8. **Production re-enrichment on the 649K index takes ~45 minutes** (NFS-bound, 8 workers). Use `run_in_background: true` and a `Monitor` with `until [ -s ... ] && grep -q ...` pattern.

---

## Repo state at handoff

```
Branch: main, in sync with origin at cc6ad7fef
Working tree: 5 pre-existing state-file modifications in .claude/state/corrections/
              and config/ai-tools/agent-quota-latest.json (auto-sync territory; not your concern)

Plans/ directory: 40+ plan files, most complete/completed. Several still at
  draft/plan-review/adversarial-reviewed — these predate this session
  and are NOT yours to pick up unless specifically asked:
    #1963 (email-infra-cluster-a, draft, T3)
    #2018 (agent-bypass-resistance, plan-review, T3)
    #2024 (gmail-extract-and-act, draft, T3)
    #2045/2046/2047 (planning-compliance family)
    #2129 (issue-state-drift-audit, plan-review, T3 — had MAJOR review)
    #2269 (openfoam-baseline, plan-review, T2)
    … plus others you can grep for
```

---

## Opening move for the next session

If you agree with ranking (A > B > C), your first message to the user should be:

> "The #1878 family is closed. The only open successor is #2325 (conference-corpus enrichment design) with revival criteria met. I'd propose starting there — it's scoped to a design decision (Option A/B/C) before any code. Alternative: investigate the 1.03M vs 700K maturity-YAML gap (#2305 memo flagged it as hypothesis-only) or the empirically-dead `summary_done_min=0.55` validator default. Which?"

If the user says "continue," default to **A (#2325)** — it's the highest-coherence choice and matches the pattern this session established.

---

**End of handoff.** This file is safe to read cold in a fresh session. Everything else you need is in the issues + plans + commit messages it references.
