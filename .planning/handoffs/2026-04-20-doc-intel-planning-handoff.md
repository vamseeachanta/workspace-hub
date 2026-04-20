# Next-Session Prompt — Doc-Intel Planning Continuation (2026-04-20)

> Paste this into a fresh Claude Code session at `/mnt/local-analysis/workspace-hub` to continue the llm-wiki / resource-intelligence / cross-review planning work from 2026-04-20.

---

## One-paragraph context

The previous session reviewed the llm-wiki/doc-intelligence portfolio, filed 11 new GitHub issues (#2392–#2406), drove 3 of them through 3 cross-provider review iterations each (all returning MAJOR×2), identified two structural infrastructure gaps (#2405 review-sandbox verification access + #2406 Codex dispatch-stdin hang), and landed v3/v2 plans. **All work is durable on `origin/main`.** The session ended at iteration caps with real plan defects fixed and two follow-on infrastructure issues filed.

## Where to start reading

- **This handoff:** `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md`
- **README plan index:** `docs/plans/README.md` rows for issues 2392–2406
- **Operating model (still the authority for everything):** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- **Updated plan template with §Evidence:** `docs/plans/_template-issue-plan.md`

## Current issue state (verify with `gh issue view <n>` before acting)

| Issue | Title (abbrev.) | State | Plan | Cross-review |
|---|---|---|---|---|
| **#2392** | wiki coverage-gap detector | CLOSED | v3 preserved | 3 iter, all MAJOR — blocked by #2405 |
| **#2393** | embeddings-index (umbrella) | CLOSED | v1 preserved | rescoped → #2402 + #2403 |
| **#2394** | retrieval-augmented planner | CLOSED | v2 preserved | 3 iter, all MAJOR — blocked by #2405 |
| **#2395** | eCFR ingestion | CLOSED | v2 preserved | 3 iter, all MAJOR — blocked by #2405 |
| **#2396** | MCP server (umbrella) | CLOSED | v1 preserved | rescoped → #2400 + #2401 + #2404 |
| **#2400** | MCP server core | OPEN | no plan | awaits user scope approval |
| **#2401** | MCP multi-agent registration | OPEN `status:plan-approved` | no plan | blocked on #2400 |
| **#2402** | embeddings build+query | OPEN `status:plan-approved` | **v1 drafted** (not yet reviewed) | dispatch pending |
| **#2403** | embeddings model-selection spike | OPEN `status:plan-approved` | **v2 drafted** | iter-2 Gemini-only (Codex timeout ×2) |
| **#2404** | MCP audit log + allowlist | OPEN | no plan | awaits user scope approval |
| **#2405** | review-sandbox repo access (META) | OPEN `status:plan-approved` | **v3 drafted** (iter-3 final) | iter-3; Codex blocked by #2406 |
| **#2406** | fix Codex dispatch-stdin hang | OPEN | no plan | new; priority:high; blocks reliable future reviews |

## Critical infrastructure blockers

1. **#2406 (Codex dispatch hang):** `scripts/review/submit-to-codex.sh` hangs on "Reading additional input from stdin..." for substantial plan files. Exit 124 at both 300s and 600s timeouts. Gemini reviews work fine. Until #2406 lands, cross-review is effectively Claude-self + Gemini only.
2. **#2405 Class B convergent finding (self-circular):** every plan's review returns MAJOR citing "unverified claims" because the sandbox can't check live state. Resolves when #2405 implements the pre-verification attestation. Until then, approve-with-caveats or wait.

## Iteration caps already consumed

Per `issue-planning-mode` skill — 3 iterations max per issue:
- #2392: 3/3 (closed)
- #2394: 3/3 (closed)
- #2395: 3/3 (closed)
- **#2405: 3/3** (v3 on main; cannot iterate further per cap)
- **#2403: 2/3** (v2 on main; one more available)
- **#2402: 0/3** (no review yet)

## Recommended first actions for next session — in priority order

### Action 1: Implement #2406 (highest leverage, short)
**Why first:** unblocks reliable Codex reviews for every other plan from this point forward.
**How:**
1. Read `scripts/review/submit-to-codex.sh` lines 162–180 (`run_codex_exec` function).
2. Hypothesis: `codex exec "$prompt_text"` overflows argv for large prompts → CLI falls back to stdin read → hangs.
3. Fix: pass prompt via stdin instead of argv (`echo "$prompt_text" | codex exec --skip-git-repo-check ...`).
4. Regression test: 20K-char prompt must not hang.
5. Draft plan → review (will now actually complete because the fix itself is small) → implement.

### Action 2: Implement #2405 v3 (unblock everything else)
**Why second:** resolves the Class B "unverified claims" circular finding.
**How:**
1. Read v3 plan at `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md`.
2. Create `scripts/review/attest-plan-claims.sh` per plan pseudocode (now bug-fixed per iter-2 Gemini findings).
3. Modify `submit-to-codex.sh` and `submit-to-gemini.sh` to prepend attestation to prompt.
4. Update `scripts/review/prompts/plan-review.md` to instruct reviewers to prefer `## Attested Evidence` over plan text.
5. Update `.claude/skills/coordination/issue-planning-mode/SKILL.md` review-stance contract.
6. Regression test: re-dispatch a v3 plan → Codex should NOT flag "unverified claims" any more.

### Action 3: Cross-review #2402 (Gemini-only until #2406 lands)
**Why:** #2402 v1 is drafted but never reviewed. Dispatch Gemini-only now; repeat with Codex after #2406.
**How:**
1. `bash scripts/review/submit-to-gemini.sh --file docs/plans/2026-04-20-issue-2402-embeddings-build-index.md --prompt "$(cat /tmp/adversarial-plan-review-prompt.md)" > scripts/review/results/2026-04-20-plan-2402-gemini.md`
2. Apply findings inline in v2 if MAJOR.

### Action 4: If user approves #2400 and #2404
Draft plans for each, following the v3 pattern (§Evidence block, §Identity Contract, §Tier Assignment, §Threat Model, §AC↔Test Map, embedded `gh`/`ls` output).

### Action 5: Re-file #2392/#2394/#2395 (after #2405 + #2406 land)
Close comments on those issues contain carry-forward defect catalogs. New plans start with those defects pre-captured; review cycle should converge in 1-2 iterations instead of 3.

## Adversarial review prompt location

Use this for all plan cross-reviews: `/tmp/adversarial-plan-review-prompt.md`

(If absent from a new machine, it's embedded in session messages around message ~15 of the prior conversation — look for "You are an adversarial reviewer. Assume this plan has defects until proven otherwise.")

## Known gotchas (learned this session)

1. **Auto-sync race on `git push`:** workspace-hub auto-syncs every 5-15 minutes. `git push origin main` frequently fails with "cannot lock ref". Always `git stash push -u`, `git pull --rebase`, `git stash pop`, `git push` — even for safe-path commits.
2. **Plan paths that don't exist were cited in v1 #2393:** `data/document-index/code-registry.yaml` does NOT exist; real path is `data/design-codes/code-registry.yaml`. Use §Evidence `ls` to verify before citing.
3. **`scripts/data/doc_intelligence/` already exists** with 30+ files. Do not claim to create it; use it.
4. **eCFR public rate limit is 1,000 req/hour (≈16/min), not 60/min.** v1 #2395 had this 4× over-spec.
5. **Iteration cap enforcement:** `scripts/review/cross-review.sh` consults `.claude/work-queue/assets/<WRK>/review-iteration.yaml` — for GH-only issues (no WRK), caps aren't auto-enforced, but workflow policy still requires manual enforcement at 3.
6. **Codex sandbox has NO repo access.** This is the #2405 premise. Until fixed, inline evidence in plans helps but doesn't fully satisfy reviewers.
7. **Gemini remained reliable** across 5+ dispatches — substantive findings (budget-exhaustion logic defect, readlink flag-injection, identity contract gaps). Trust it as the effective single reviewer until #2406 lands.
8. **Plan template §Evidence subsection** was added in this session at commit `4226f8695`. All new plans must use it.
9. **`#2405 v3` Pseudocode fixes from iter-2 Gemini were applied but no iter-3 review ran** because Codex hung + iteration budget was spent. Next session's first #2405 cross-review will effectively be iter-3 resumption.

## Commits this session (chronological — on `main`)

```
5b4c347cd — docs(plans): 5 initial doc-intel plans + Claude self-reviews
43f608f10 — docs(plans): 10 iter-1 cross-review artifacts (MAJOR×10)
27821dafa — docs(plans): v2 rewrites #2392/#2394/#2395 + split #2393/#2396
07c7d3250 — docs(plans): iter-2 artifacts (MAJOR×6)
4226f8695 — docs(plans): v3 rewrites + template §Evidence section
4de4294a4 — docs(plans): close #2392/#2394/#2395 blocked by #2405 (final ledger)
d067a4d51 — docs(plans): #2405 plan (v1) — pre-verification attestation
11ac126b1 — docs(plans): #2403 plan — embeddings model-selection spike
5c9923acf — docs(plans): #2405 v2 + iter-1 artifacts
a20575ace — docs(plans): #2405 v3 + #2403 v2 — Gemini iter-2/iter-1 fixes
a78b5631f — docs(plans): #2402 plan — embeddings build+query
```

## Memory relevance

Load at session start if not already auto-loaded:
- `feedback_adversarial_review_stance.md` — every prompt must force defect-hunting
- `feedback_cross_provider_review_payoff.md` — Codex finds non-overlapping defects vs Claude
- `feedback_codex_needs_pushed_artifact.md` — push to GH before `codex exec`
- `feedback_codex_sandbox_write_blocked.md` — Codex can't write files from sandbox
- `feedback_merge_race_silent_revert.md` — verify merged content matches branch tip
- `feedback_retry_loop_reset_hazard.md` — `git reset HEAD -- .` in retry loops under auto-sync can strip staged edits
- `project_doc_intel_operating_model.md` — #2205 parent + children tree
- `project_hermes_codex_quota.md` — cost sensitivity

## First-message template for next session

```
Continuing doc-intel planning from 2026-04-20. Context in
.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md.

First task: [pick one — Action 1 (#2406 Codex fix), Action 2 (#2405 impl),
Action 3 (dispatch #2402 review), Action 4 (plan #2400/#2404), or Action 5
(re-file #2392/#2394/#2395)].

If unclear which first, default to Action 1 (#2406) — smallest scope,
unblocks everything downstream.
```

## Session exit condition

All session artifacts durable on `origin/main` commits `5b4c347cd` through `a78b5631f`. No uncommitted session state. Next session can start clean.
