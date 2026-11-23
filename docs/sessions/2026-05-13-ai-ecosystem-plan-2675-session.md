# Session handoff — AI ecosystem plan #2675 (2026-05-12 → 2026-05-13)

> **Session goal** (original `/goal`): "prepare repo ecosystem plan to do the following — review our work ecosystem and reverse prompt how we can make our workflows to utilize claude, hermes, codex, gemini and enable best work productivity, quality, etc.; use the ai provider usage efficiently etc.; without violating the repo workflows; create a gh issue to do this work."
>
> **Outcome**: goal comprehensively met. Ecosystem-design plan filed, reviewed across 3 cross-review waves, revised v1 → v2 → v3, approved, implemented, and 4 of 10 §F follow-ups filed. Two harness bugs surfaced + fixed end-to-end as side-effects. Cross-review apparatus rebuilt mid-session and is now healthier than at start.

---

## What was filed / fixed / closed

### Issues

| # | Title | Final state | Commits |
|---|---|---|---|
| [#2675](https://github.com/vamseeachanta/workspace-hub/issues/2675) | `feat(ai-orchestration): reverse-prompt repo ecosystem for productive multi-provider work` | **CLOSED** as completed | plan v1 `da19310ae`, v2 `a7581e454`, v3 `49507b582`; deliverables `f30a8fe2d` |
| [#2683](https://github.com/vamseeachanta/workspace-hub/issues/2683) | `bug(harness): Claude SessionEnd hook (codex plugin) times out and crashes plan-review-fanout` | **CLOSED** | fix `b61f2c5a3` (CLAUDE_PLUGIN_DIR override; mechanism deviation from approved plan: switched from `--bare` mid-execution after smoke-test exposed auth-incompatibility) |
| [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) | `bug(harness): codex-cli stdin-hang under Claude-Code Bash subprocess` | **CLOSED** | fix `0cd40c6ab` (CLAUDECODE env-guard in `codex_version_guard_check`); plan `59dc11d27`, r3 review same commit |
| [#2697](https://github.com/vamseeachanta/workspace-hub/issues/2697) | §F #1 — `chore(ai-tools): refresh subscriptions.yaml with current Codex paid plan` | OPEN, listed | filed 2026-05-13 |
| [#2698](https://github.com/vamseeachanta/workspace-hub/issues/2698) | §F #5 — `feat(ai-orchestration): migration plan for AI_ECOSYSTEM_DESIGN.md adoption` | OPEN, listed | filed 2026-05-13 |
| [#2699](https://github.com/vamseeachanta/workspace-hub/issues/2699) | §F #8 — `chore(ai-tools): refresh agent-capability-scores.yaml from 2026-04/05 incident data` | OPEN, listed | filed 2026-05-13 |
| [#2700](https://github.com/vamseeachanta/workspace-hub/issues/2700) | §F #10 — `feat(ai-orchestration): "Memory-to-Surface" map maintenance contract` | OPEN, listed | filed 2026-05-13 |

### Durable artifacts landed

| Path | Purpose | Commit |
|---|---|---|
| [`docs/standards/AI_ECOSYSTEM_DESIGN.md`](../standards/AI_ECOSYSTEM_DESIGN.md) | Durable design contract (§A outcome ledger / §B provider matrix / §C walk-throughs / §D efficient-usage / §E failure-mode map of 20 memory→mitigation) | `f30a8fe2d` |
| [`docs/reports/2026-05-12-issue-2675-followup-issues-list.md`](../reports/2026-05-12-issue-2675-followup-issues-list.md) | Live tracker for 10 §F follow-up issues; updates as each is filed | `f30a8fe2d`, `b2a78798e`, `bbd893578` |
| [`docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md`](../plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md) | Source plan, v3 final | `da19310ae` → `a7581e454` → `49507b582` |
| [`docs/plans/2026-05-12-issue-2683-claude-bare-flag-for-fanout.md`](../plans/2026-05-12-issue-2683-claude-bare-flag-for-fanout.md) | T1 plan for #2683; documents mechanism deviation | `fdb86264d` |
| [`docs/plans/2026-05-13-issue-2684-codex-claudecode-env-guard.md`](../plans/2026-05-13-issue-2684-codex-claudecode-env-guard.md) | T1 plan for #2684 | `59dc11d27` |
| 7 review artifacts under `scripts/review/results/` | 3 fanout waves × Claude/Codex/Gemini + 2 synthesis | various |
| 2 r3 reviews | Single-author T1 reviews for #2683 + #2684 | various |

### Harness improvements

| Surface | Change | Commit | Why |
|---|---|---|---|
| `scripts/review/plan-review-fanout.sh` | Claude case branch now uses `env CLAUDE_PLUGIN_DIR=<mktemp -d>` to disable plugin discovery (so codex-plugin SessionEnd hook doesn't fire); `#2683` reference in comment to defend against future cleanup | `b61f2c5a3` | Fixes rc=124 Hook-cancelled crash under headless `claude -p`; preserves keychain auth (unlike `--bare`) |
| `scripts/review/lib/codex-version-guard.sh` | `codex_version_guard_check()` returns rc=3 with INCOMPATIBLE message when `CLAUDECODE=1` (before version probe); message includes operator override hint | `0cd40c6ab` | Fast-fails (~0.033s) in Claude-Code Bash instead of stuck at 600s timeout |
| `scripts/review/tests/mocks/claude` | Captures `ENV.CLAUDE_PLUGIN_DIR` in capture file alongside ARGV/PWD/STDIN | `b61f2c5a3` | Lets regression tests assert the override fired |
| `scripts/review/tests/test_plan_review_fanout.sh` | +3 tests: `test_claude_invocation_sets_plugin_dir_override`, `test_claude_case_branch_documents_2683`, `test_fanout_codex_unavailable_under_claudecode_env`; `run_wrapper_under_mocks` unsets CLAUDECODE by default; 3 other subshells also `unset CLAUDECODE` | `b61f2c5a3`, `0cd40c6ab` | Tests pass under Claude-Code Bash session (where CLAUDECODE=1 propagates); count went 17 → 20 |

---

## Key decisions made (and why)

### Mechanism deviation at #2683 implementation (mid-session)

Approved plan called for `claude --bare -p ...`. Live smoke test exposed that `--bare` disables keychain reads (per `claude --help`: *"OAuth and keychain are never read"*) and requires `ANTHROPIC_API_KEY`, which is **not** set on this machine. Switched to `env CLAUDE_PLUGIN_DIR=<empty-tempdir> claude -p ...` — narrower mechanism (only plugin discovery), no auth impact, no version dependency. **User confirmed deviation in chat** before commit; recorded in plan-2683 §Adversarial Review Summary as "Mechanism deviation discovered at execution time."

**Lesson**: r3 review had verified `--bare` *exists* (via `claude --help | grep -- '--bare'`) but never invoked `claude --bare` to confirm it *works* in this auth env. Classic `superpowers:verification-before-completion` gap — evidence-of-syntax vs. evidence-of-behavior. The smoke test (per the system instructions explicitly requiring it) exposed it pre-commit.

### FORCE_PLAN_GATE=1 bypass usage

Used twice for non-safe-path commits where the user-approval label was set but the local marker file was not:
- #2683 implementation commit `b61f2c5a3`
- #2684 implementation commit `0cd40c6ab`

Each commit message and the pre-commit hook output both record the bypass for audit transparency. Per the issue-planning-mode skill's documented escape hatch ("All bypasses are logged"). For #2675 implementation (`f30a8fe2d`) no bypass was needed — all writes were to `docs/standards/` and `docs/reports/` which are safe paths.

### Wave-3 advancement decision (single-provider verdict)

Wave-3 fanout returned **1 of 3 usable verdicts** (Claude MAJOR with audit-trail-rot findings only; Codex UNAVAILABLE-by-design via #2684; Gemini hit NEW server-side 429 capacity exhaustion on `gemini-3.1-pro-preview`). Advanced [#2675](https://github.com/vamseeachanta/workspace-hub/issues/2675) to `status:plan-review` with **transparent provenance**: single-author wave-3 per `feedback_permission_gate_blocks_cross_review`, both UNAVAILABLE failures documented. User then set `status:plan-approved` and Step 6 (implementation) proceeded.

### Sequential follow-up filing

Per `feedback_parallel_gh_issue_create_reverses_numbers`, all 4 follow-ups filed sequentially: #2697 → #2698 → #2699 → #2700. Issue numbers came back in monotonic order — no number reversal observed. Live tracker (`docs/reports/2026-05-12-issue-2675-followup-issues-list.md`) updated after each filing.

---

## New lessons surfaced (not yet captured to memory)

These observations from the session are worth considering for `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_*.md` entries (deferred — user didn't request explicit memory updates):

1. **Three-wave defect-class trajectory pattern**: harness-broken → content-defects → bookkeeping-rot. Healthy cross-review iteration shows each wave catching a different defect class; if waves start catching the same class repeatedly, the apparatus needs refresh, not the artifact.
2. **Gemini-429 server-side capacity exhaustion** as a fresh failure mode for `gemini-3.1-pro-preview` (distinct from overlay-blindness and stdin-hang). Manifests as `_GaxiosError: [{ \"error\": { \"code\": 429, \"message\": \"No capacity available for model on the server\" ... }]}` — not retriable in-session.
3. **Auto-sync co-commit pattern** (`feedback_autosync_silent_pusher` extension): when retrying a commit during index-lock contention, auto-sync may stage and commit dirty working-tree files *along with* whatever else is being committed concurrently. The diff is right, the message is wrong. Observed in this session at `8705e8507` (R5 inventory commit which silently bundled plan-2675 corrections + 5 review artifacts).
4. **Mechanism-deviation-at-execution-time**: smoke-test in target environment is the gate that catches "approved plan doesn't work in production." Has happened once per session-with-T1-implementation; warrants codifying.
5. **Live-tracker pattern as maintenance-contract proof**: a standalone report (here: `followup-issues-list.md`) that updates as items file is more durable than embedding the same content in a closed issue body. The standards doc's maintenance contract claim becomes evidence-based.

---

## Open work (5 §F follow-ups still listed)

Tracked in [`docs/reports/2026-05-12-issue-2675-followup-issues-list.md`](../reports/2026-05-12-issue-2675-followup-issues-list.md):

| §F # | Title | Why deferred |
|---|---|---|
| #2 | CODEX.md adapter + extend `.claude/rules/coding-style.md` | Open question: repo-root `CODEX.md` vs. hidden-dir `.codex/CODEX.md` per #2399's proposal — needs user call before filing |
| #3 | Audit + extend `config/agents/{codex,gemini,hermes}/` | Depends on #2 (codex/ subdir content informed by CODEX.md adapter shape) |
| #4 | Cost/quota model + halt protocol | Depends on #2697 (accurate subscriptions before envelope design) — defer until #2697 lands |
| #6 | Wiki workflow walkthrough | Independent; lower priority — file when ready to plan |
| #7 | Batch workflow walkthrough | Independent; lower priority — file when ready to plan |
| #9 | "When NOT to cross-review" rule in `routing-config.yaml` | Independent — file when ready to plan |

**Cluster suggestion**: file #2 + #3 as a coupled pair (resolve CODEX.md location first), then #6/#7/#9 as a batch when documentation-completeness sprint scheduled. #4 waits on #2697's landing.

---

## How to pick this up in a future session

Quick orientation for a future-you or different-machine session:

1. Read [`docs/standards/AI_ECOSYSTEM_DESIGN.md`](../standards/AI_ECOSYSTEM_DESIGN.md) — start with §A outcome ledger
2. Check live tracker at [`docs/reports/2026-05-12-issue-2675-followup-issues-list.md`](../reports/2026-05-12-issue-2675-followup-issues-list.md) for current §F state
3. Check open issues: `gh issue list --repo vamseeachanta/workspace-hub --search "in:body 2675 parent" --state open`
4. The cross-review fanout is healthy: `bash scripts/review/tests/test_plan_review_fanout.sh` should return 20/20 PASS
5. If working under Claude-Code Bash session, fanout's Codex leg will fast-fail UNAVAILABLE — that's working as designed (per #2684); re-dispatch from plain terminal via `env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh ...` if you need Codex's verdict

---

## Final session statistics

- **Duration**: ~14 hours wallclock (2026-05-12 evening → 2026-05-13 PM)
- **Commits authored**: 13 (plan-v1/v2/v3, plan-2683, plan-2684, harness fixes, review artifacts, deliverables, follow-up-list updates, this session doc)
- **Issues filed**: 5 (#2675 originally, then #2683, #2684 as harness bugs, then #2697, #2698, #2699, #2700 as §F follow-ups — net 7 issues filed across the session)
- **Issues closed**: 3 (#2675, #2683, #2684)
- **Cross-review waves run**: 3 (against plan-2675); 1 single-author r3 each for plan-2683 + plan-2684
- **Total tests added**: 3 (`test_claude_invocation_sets_plugin_dir_override`, `test_claude_case_branch_documents_2683`, `test_fanout_codex_unavailable_under_claudecode_env`)
- **Fanout test count**: 17 → 20, all green
- **Memory feedback files cited**: 22 in §E + various inline ones in plans/comments
- **Bypass usage**: 2 (`FORCE_PLAN_GATE=1` for #2683 + #2684 implementations; logged)

---

## Acknowledgements (system-prompted)

The session's compounded value came from honoring three things even when they were friction:
1. The user-in-loop approval gate (`feedback_never_offer_to_self_label_plan_approved`) — never self-approved; bypassed only with explicit logging when label-was-set + marker-was-missing.
2. The cross-provider review apparatus (`feedback_cross_provider_review_payoff`) — kept dispatching even when 2-of-3 providers were unavailable; each wave produced signal the prior didn't have.
3. Verification-before-completion (`superpowers:verification-before-completion`) — the smoke test of `claude --bare` is what caught the #2683 mechanism-deviation pre-commit instead of post-merge.

The "wave 1 / wave 2 / wave 3 = harness / content / bookkeeping" trajectory was an emergent property of obeying these three rules in sequence — not designed in advance.
