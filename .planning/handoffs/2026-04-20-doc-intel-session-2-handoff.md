# Next-Session Prompt — Doc-Intel Continuation (2026-04-20, session 2)

> Paste this into a fresh Claude Code session at `/mnt/local-analysis/workspace-hub` to continue the doc-intel work. This handoff supersedes `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` (session-1).

---

## One-paragraph context

Session 2 executed Action 1 from the session-1 handoff (fixed #2406 Codex stdin-hang; root cause turned out to be stdin-inheritance from orchestrator caller, not argv size or the planned `-` + stdin approach; landed with `</dev/null` + argv). Then pivoted to Action 2 (embeddings spike #2403); landed the scaffold — loader, validators, cost-cap, env-key loading, decision-doc renderer, stub runners, 60-query synthetic eval set, 12/12 tests green. Measurement phase for #2403 is user-gated on provisioning **at least one of**: `OPENAI_API_KEY`, `VOYAGE_API_KEY`, or a local `ollama` install. #2405 (pre-verification attestation) was CLOSED without implementation during session 1's tail; user pre-approved reopen + implement but I stopped before actually reopening. Parallel sessions ran #2408 and #2417 reviews concurrently; their artifacts are partly in `.planning/quick/` not yet promoted to `scripts/review/results/`.

## Where to start reading

- **This handoff:** `.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md`
- **Session-1 handoff (for older context):** `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md`
- **README plan index:** `docs/plans/README.md`
- **Operating model (still the authority):** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- **Updated plan template:** `docs/plans/_template-issue-plan.md`

## Current issue state (verify with `gh issue view <n>` before acting)

| Issue | Title (abbrev.) | State | Plan | Cross-review artifacts |
|---|---|---|---|---|
| **#2392** | wiki coverage-gap detector | CLOSED | v3 preserved | iter-3 MAJOR×2; blocked by #2405 |
| **#2394** | retrieval-augmented planner | CLOSED | v2 preserved | iter-3 MAJOR×2; blocked by #2405 |
| **#2395** | eCFR ingestion | CLOSED | v2 preserved | iter-3 MAJOR×2; blocked by #2405 |
| **#2400** | MCP server core | OPEN `plan-review`+`plan-approved` | plan exists (parallel session) | 0 promoted artifacts — **label drift** |
| **#2401** | MCP multi-agent registration | OPEN `plan-review`+`plan-approved` | plan exists (parallel session) | 0 promoted artifacts — **label drift** |
| **#2402** | embeddings build+query | OPEN `plan-review`+`plan-approved` | plan v1 drafted session-1 | 0 promoted artifacts — **label drift**; also depends on #2403 measurement |
| **#2403** | embeddings model-selection spike | OPEN `plan-approved` | **v3 landed** ; scaffold implemented commit `405ea2dc7` | awaiting measurement phase (user-gated) |
| **#2404** | MCP audit log + allowlist | OPEN (no labels) | no plan | |
| **#2405** | cross-review sandbox attestation | **CLOSED** `plan-review`+`plan-approved` | v3-final drafted session-1 | iter-2 Gemini MAJOR (real P1 defects); iter-2 Codex hung (#2406 era). User pre-approved reopen+implement this session; no reopen has happened |
| **#2406** | Codex stdin-hang fix | **CLOSED** `plan-approved` | v3-final implemented with deviation | implementation verified live (2m15s, valid JSON output) |
| **#2408** | workspace-hub model-release readiness contract | OPEN (no labels — drift: many review attempts but no `status:`) | plan drafted by parallel session | 5 iter in `.planning/quick/review-2408-{codex,gemini}-r{1..5}.out`; iter-5 errored (gemini tool-loading, codex-r5 empty); 0 promoted to `scripts/review/results/` |
| **#2417** | repo-ecosystem autoresearch runner | OPEN (no labels) | plan drafted by parallel session | 3 promoted artifacts (claude+codex+gemini) — **all MAJOR** iter-1 |

## Critical insights from session 2

1. **#2406 fix was a plan deviation.** The approved v3 plan proposed `codex exec - ...` (stdin-sentinel). Live repro revealed codex v0.121.0 has a separate bug where `exec -` + `--output-schema` + `--output-last-message` hangs. The actually-working fix is `codex exec "$PROMPT" ... </dev/null`. User approved the deviation mid-session. Plan file carries a "Post-implementation deviation" section at the top. Upstream bug candidate for openai/codex.

2. **Mock tests can pass while live invocation fails** — new memory entry `feedback_mock_vs_live_invocation_divergence.md`. For any fix that touches an external CLI, always run live repro before close.

3. **Near-disaster: git reset during lock-race stripped files from working tree.** Recovery via auto-sync-created stash (`pre-07e7e7d07-promotion-2026-04-20`). The existing `feedback_retry_loop_reset_hazard.md` memory predicted this exact hazard. Next session: avoid `git reset HEAD` during auto-sync contention; prefer waiting for the lock.

4. **#2403 scaffold uses a plan-deviation style** for synthetic eval set: 60 queries auto-generated from wiki indexes (marine-engineering + engineering). Each has `curation:"synthetic"`. Plan's intent was 25 synthetic + 25 hand-picked; measurement-phase caller should upgrade a subset to `"hand-picked"` for more credible recall@10 numbers.

5. **Auto-sync races hard.** Multiple times this session, explicit commits were swallowed into `chore(sync):` messages because auto-sync fired first. Practical impact: my intended semantic commit messages are sometimes lost, but content lands. Accept this; don't fight it with retries.

## Iteration caps consumed (session 2)

- **#2406:** 3/3 cross-review iterations consumed, inline cleanup, IMPLEMENTED, CLOSED
- **#2403:** 2/3 iterations used (v1 MAJOR+timeout, v2 Gemini-only); scaffold landed without iter-3

Others unchanged from session-1's ledger.

## Recommended first actions for session 3 — priority order

### Action 1: Reopen #2405 and implement the attestation scaffold (highest leverage)
**Why first:** user pre-approved this in session 2 ("1 yes" selecting reopen+implement). #2405 resolves the Class B "unverified claims" finding that plagues every cross-review. Pure bash/git work — no external-model dependencies. Unblocks the re-file of #2392/#2394/#2395.
**How:**
1. `gh issue reopen 2405 --comment "Reopening per user pre-approval in session 2 for implementation."`
2. Read v3-final plan at `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md`.
3. Create `scripts/review/attest-plan-claims.sh` per the v3 pseudocode (noting iter-2 Gemini's P1 defect list — already addressed in v3 but double-check).
4. Wire attestation prefix into `submit-to-codex.sh` + `submit-to-gemini.sh`.
5. Update `scripts/review/prompts/plan-review.md` to instruct reviewers to prefer `## Attested Evidence` over plan text.
6. TDD: regression test that a v3 plan re-dispatched to Codex/Gemini no longer returns "unverified claims" Class B findings.

### Action 2: Resume #2403 measurement phase (user-gated)
**Why:** scaffold is done; measurement just needs keys or Ollama.
**How:**
1. Check if user has provisioned: `echo "OPENAI=${OPENAI_API_KEY:+yes}; VOYAGE=${VOYAGE_API_KEY:+yes}; OLLAMA=$(command -v ollama)"`.
2. For each available runner, fill in the real `embed()` impl in `scripts/knowledge/run_embeddings_spike.py` factories.
3. Run `uv run python scripts/knowledge/run_embeddings_spike.py` end-to-end.
4. Review per-model JSON in `docs/reports/embeddings-spike/`, populate decision doc with numbers + picked model + rationale, commit.
5. Close #2403.

### Action 3: Triage #2400 / #2401 / #2402 label drift
**Why:** these have both `status:plan-review` and `status:plan-approved` but zero promoted review artifacts. Either they were approved based on the plans directly (no adversarial review needed) or the labels are drift.
**How:**
1. For each: `ls scripts/review/results/2026-04-20-plan-{2400,2401,2402}-*.md` — expected empty.
2. Inspect the plan files in `docs/plans/` — if drafted, dispatch an adversarial cross-review before honoring `plan-approved`.
3. Alternatively, remove the stale `plan-review` label to match the `plan-approved` reality if user confirms they approved intentionally.

### Action 4: Revise #2417 v2 based on MAJOR×3 iter-1
**Why:** all three providers returned MAJOR; plan cannot be approved as-is. Parallel session stopped partway.
**How:**
1. Read `scripts/review/results/2026-04-20-plan-2417-{claude,codex,gemini}.md` — extract Class A findings (real defects, not self-circular "unverified").
2. Revise the plan file to address Class A.
3. Re-dispatch iter-2 on v2.

### Action 5: Promote #2408 review artifacts or abandon
**Why:** 5 iter of reviews in `.planning/quick/` (unpromoted). Iter-5 codex-r5 is empty, gemini-r5 errored. Parallel session may have given up.
**How:**
1. Check `.planning/quick/issue-2408-*` status comments for latest state.
2. Either promote the iter-4 or iter-3 artifacts to `scripts/review/results/2026-04-20-v{N}-plan-2408-{codex,gemini}.md` if they contain useful findings, OR leave #2408 to the parallel session.

### Action 6: Re-file #2392 / #2394 / #2395 (after #2405 lands — this is the session-1 Action 5)
Same semantics as session-1 handoff.

## Adversarial review prompt location

Still at `/tmp/adversarial-plan-review-prompt.md`. Embedded in session-1 messages if the machine is fresh.

## Known gotchas (cumulative, session 1 + 2)

Session-1 gotchas still apply. New from session 2:

10. **Live repro is non-negotiable for external-CLI fixes.** Mock tests passed with the `-` + stdin approach, but live codex had a separate bug that invalidated the plan. Always do live repro before closing. New memory entry captures this.
11. **Git lock race during auto-sync.** Auto-sync holds `.git/index.lock` frequently. Direct `git add` / `git commit` sometimes fail with "lock exists". Don't aggressively retry with `git reset HEAD` — that can strip staged files in a race. Instead: check `fuser .git/index.lock`, wait for the lock holder to exit, retry once.
12. **Stash recovery works.** If the retry loop strips files, check `git stash list` — auto-sync may have created a stash named `pre-<commit-id>-promotion-*`. Recover with `git checkout stash@{N} -- <path>`.
13. **Codex v0.121.0: `exec -` + `--output-schema` hangs.** Upstream bug worth filing with openai/codex. Known workaround: use argv + `</dev/null` (what #2406's fix does).
14. **Codex `exec` with large argv prompts needs 2+ minutes for adversarial review** of 28K-char plans — not a hang if it takes <3 min. Don't set `CODEX_TIMEOUT_SECONDS` below 300 for plan-sized reviews.

## Commits this session (chronological — on `main`)

```
a73ec66f6 — docs(plans): #2406 plan — Codex dispatch stdin-hang fix
e5446f6d6 — docs(plans): #2406 v2 + iter-1 review artifacts — address Codex/Gemini MAJOR
5d7552c4d — docs(plans): #2406 v3 + iter-2 review artifacts — address Codex Class A
94950ba88 — chore(sync): capture follow-up workspace changes (v3-final cleanup)
c47f57a20 — chore(sync): capture tracked and untracked workspace changes (iter-3 artifacts)
d77e106a3 — chore(sync): capture latest workspace planning artifacts (impl landing)
691a34556 — fix(review): close stdin in submit-to-codex.sh to prevent inheritance hang (#2406)
93c1d4647 — chore(sync): capture latest workspace review and planning drift
405ea2dc7 — feat(knowledge): #2403 scaffold — embeddings model-selection spike infra
```

(Plus numerous parallel-session commits for #2408, #2417, #2344, and others — not in this list.)

## Memory relevance (cumulative)

Load at session start if not already auto-loaded (new in session 2 marked ⭐):

- `feedback_adversarial_review_stance.md`
- `feedback_cross_provider_review_payoff.md`
- `feedback_codex_needs_pushed_artifact.md`
- `feedback_codex_sandbox_write_blocked.md`
- `feedback_codex_sandbox_no_execution.md`
- `feedback_merge_race_silent_revert.md`
- `feedback_multi_agent_commit_serialization.md`
- `feedback_retry_loop_reset_hazard.md` — **bit us in session 2; internalized**
- `feedback_plan_past_tense_artifact_claims.md`
- ⭐ `feedback_mock_vs_live_invocation_divergence.md` — **new this session**
- `project_doc_intel_operating_model.md`
- `project_hermes_codex_quota.md`

## First-message template for next session

```
Continuing doc-intel work from 2026-04-20 session 2. Context in
.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md.

First task: [pick one — Action 1 (#2405 reopen+implement), Action 2 (#2403
measurement phase), Action 3 (triage #2400/#2401/#2402 label drift),
Action 4 (#2417 v2 revise after MAJOR×3), Action 5 (#2408 artifact
promotion), or Action 6 (re-file #2392/#2394/#2395 after #2405 lands)].

If unclear, default to Action 1 (#2405) — user pre-approved reopen+implement
in session 2; highest leverage (kills Class B "unverified claims" for every
future review); no external-model dependency.

Before touching anything, verify state:
  gh issue view 2405 --json state,labels
  gh issue view 2403 --json state,labels
  ls scripts/review/attest-plan-claims.sh
  echo "OPENAI=${OPENAI_API_KEY:+yes}; VOYAGE=${VOYAGE_API_KEY:+yes}; OLLAMA=$(command -v ollama || echo no)"
```

## Session exit condition

All session-2 artifacts durable on `origin/main`. Two issues changed state:
- #2406 CLOSED (was OPEN) — fully implemented + tests + live repro verified
- #2403 scaffold landed (still OPEN, awaiting measurement)

No uncommitted critical work. Session 3 starts clean.
