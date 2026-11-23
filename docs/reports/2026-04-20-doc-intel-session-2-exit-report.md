# Doc-intel session-2 exit report — 2026-04-20

> Companion to session-1 exit report (`docs/reports/` from 2026-04-20 earlier). Records what session 2 delivered, what remains, and why deviations happened.

## One-paragraph summary

Session 2 ran two issues to landing: **#2406** (Codex dispatch stdin-inheritance hang, CLOSED) and **#2403 scaffold** (embeddings model-selection spike, OPEN — measurement phase user-gated). Both went through the full `issue-planning-mode` workflow. The #2406 implementation deviated from the approved v3 plan after live repro revealed a codex v0.121.0 bug in the planned approach; user approved the deviation mid-session. The #2403 scaffold used Option A ("build infrastructure; defer measurement") per user's explicit pick when prerequisites (API keys, Ollama) were found absent.

## Issues changed

| Issue | Before session 2 | After session 2 |
|---|---|---|
| **#2406** | OPEN, no plan | CLOSED, v3-final plan + implemented + 59/59 tests + live repro verified (2m15s, 6870-byte valid JSON) |
| **#2403** | OPEN, `plan-approved` | OPEN, `plan-approved`, **scaffold landed** (commit `405ea2dc7`); measurement phase pending API keys / Ollama |
| **#2405** | CLOSED (closed at handoff) | CLOSED — user pre-approved reopen+implement this session; reopen deferred to next session |

## Artifacts landed on `origin/main`

### Code
- `scripts/review/submit-to-codex.sh` — `</dev/null` added to all three dispatch branches; 59/59 tests pass
- `tests/review/test-submit-scripts.sh` — added T26–T29, T32, T33 (stdin isolation + exit-code preservation); auto-sync merged in T30/T31 (timeout/transport classification) from parallel linter sweep
- `tests/review/fixtures/codex-large-prompt.txt` — 24 400-char deterministic fixture
- `scripts/knowledge/run_embeddings_spike.py` — 279-line spike runner: validators, cost-cap, env-key loading, stub runners, decision-doc renderer, `--scaffold-check` CLI
- `tests/knowledge/test_embeddings_spike.py` — 176-line test suite; 12 cases all passing
- `tests/fixtures/embeddings/eval-set.jsonl` — 60 synthetic queries auto-generated from wiki indexes

### Docs
- `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` — v3-final + "Post-implementation deviation" section documenting `</dev/null` pivot
- `docs/document-intelligence/embeddings-model-selection.md` — decision-doc scaffold with explicit "Status: scaffold — measurement phase not yet run"
- `.planning/plan-approved/2403.md` — approval marker
- `.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md` — next-session prompt
- `docs/reports/2026-04-20-doc-intel-session-2-exit-report.md` — this file

### Memory
- `feedback_mock_vs_live_invocation_divergence.md` — new entry durable in `/home/vamsee/.claude/projects/.../memory/` and indexed in `MEMORY.md`

### GitHub
- #2406 — closeout comment posted (comment `4284259325`); CLOSED
- #2403 — scaffold-landed status comment posted (comment `4284416597`); still OPEN

## Plan deviations (documented for audit)

1. **#2406 implementation diverged from approved v3 plan.**
   - **Planned:** `printf '%s' "$prompt" | codex exec - …` (stdin sentinel) + runtime version probe with hard-fail exit 7.
   - **Landed:** `codex exec "$prompt" … </dev/null` (argv + explicit stdin close). No version probe, no exit 7.
   - **Reason:** live repro against real codex v0.121.0 showed the `-` sentinel + `--output-schema` + `--output-last-message` combination hangs even with small stdin input. This is a codex bug, not a plan error — the hypothesis was reasonable but unprovable at plan-review time (no live access by reviewers). Mock tests passed the planned approach; live repro revealed the problem; user approved the deviation in session ("1" selecting Option 1).
   - **Upstream candidate:** openai/codex issue for `exec -` + structured-output flags hang.

2. **#2403 eval set uses 60 synthetic queries, not the plan's 25 synthetic + 25 hand-picked.**
   - **Planned:** 25 synthetic + 25 hand-picked from existing issue corpus.
   - **Landed:** 60 synthetic queries auto-generated from wiki indexes, each flagged `curation:"synthetic"`.
   - **Reason:** hand-picked curation requires domain-expert judgment the agent cannot produce authentically. Scaffold satisfies the plan's automated ≥50 AC; measurement-phase caller can upgrade subset to `"hand-picked"` for more credible recall@10 before running real measurement.

## Near-miss: near-catastrophic data loss, recovered

Mid-session, a `git reset HEAD` during a `.git/index.lock` race stripped my #2403 scaffold files from the working tree. The existing `feedback_retry_loop_reset_hazard.md` memory predicted this exact hazard. Recovered via auto-sync-generated stash (`pre-07e7e7d07-promotion-2026-04-20`) using surgical `git checkout stash@{0} -- <path>` per file. All 4 files restored identically; tests passed post-recovery.

**Lesson locked in:** next time the lock races, wait for `fuser .git/index.lock` to show empty and retry once; do not unstage with `reset HEAD` under contention.

## Remaining work for session 3 (priority-ordered)

| Priority | Action | Gating |
|---|---|---|
| 1 | Reopen #2405, implement pre-verification attestation scaffold per v3-final plan | None — pure bash/git work; user pre-approved |
| 2 | #2403 measurement phase: fill stub runners, run, populate decision doc, close | User must provision at least one of: `OPENAI_API_KEY`, `VOYAGE_API_KEY`, local `ollama` install |
| 3 | Triage #2400 / #2401 / #2402 label drift (both `plan-review` and `plan-approved` with 0 review artifacts) | User review of parallel-session plans |
| 4 | Revise #2417 v2 addressing MAJOR×3 iter-1 findings | None |
| 5 | Promote #2408 review artifacts from `.planning/quick/` or abandon; parallel session got to iter-5 with both providers failing | Parallel session status clarification |
| 6 | Re-file #2392 / #2394 / #2395 (after #2405 lands) | Blocked on #1 above |

## Commits this session (explicit + durable)

- `a73ec66f6` — #2406 v1 plan + README row
- `e5446f6d6` — #2406 v2 plan + iter-1 review artifacts
- `5d7552c4d` — #2406 v3 plan + iter-2 review artifacts
- `691a34556` — #2406 implementation + tests (explicit fix commit)
- `405ea2dc7` — #2403 scaffold (runner + tests + fixture + decision doc)
- `1dfbea918` — session-2 handoff

Plus extensive auto-sync `chore(sync):` commits that swept up v3-final cleanup edits, review artifacts, and recovered scaffold files.

## Exit readiness check

- [x] Git working tree: no uncommitted critical work (auto-sync sweeps will land residual state files)
- [x] `origin/main` matches `HEAD` (or is ahead via auto-sync; either way, work is durable)
- [x] #2406 closed with comprehensive closeout comment
- [x] #2403 status clearly communicated via comment; issue OPEN awaiting user-gated measurement
- [x] Session-2 handoff written and committed
- [x] Memory updated with one new durable lesson
- [x] Exit report written (this document)

Session 3 can start clean using the paste-prompt in the handoff.
