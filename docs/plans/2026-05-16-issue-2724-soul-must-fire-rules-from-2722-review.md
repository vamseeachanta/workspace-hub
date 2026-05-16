# Plan for #2724: feat(soul): add 5 cross-provider must-fire rules derived from #2722 review wave

> **Status:** draft
> **Complexity:** T1.5 (text-only single-file addition, but load-bearing across 4 providers — T3 review)
> **Date:** 2026-05-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2724
> **Review artifacts:** `scripts/review/results/2026-05-16-plan-2724-{claude,codex,gemini}.md` (to be created)

---

## Resource Intelligence Summary

### Existing repo code

- **`config/agents/SHARED_SOUL.md`** (109 lines, commit `a798e31b8`) — current Must-Fire Rules section is lines 47-63 with 13 existing rules. New rules inserted after line 63 will be rules #14-#18. Format is bullet items: `**Title.** description with citation (citation-ref)`. Each existing rule references either a `feedback_*` memory key or a workspace-hub issue number `#NNNN`.
- **`scripts/agents/build-soul-runtime.sh`** (verified working 2026-05-16 via preflight drift check; assembles SHARED + delta into 5 runtime artifacts).
- **`scripts/enforcement/check-soul-runtime-drift.sh`** (3041 B, returns 0 currently — proven by preflight in `whoami`-prompt session start).
- **`scripts/agents/install-soul-runtime.sh`** (87 lines) — manages live symlinks `~/.hermes/SOUL.md` → `config/agents/hermes/SOUL.runtime.md`, `~/.codex/AGENTS.md` → `config/agents/codex/AGENTS.runtime.md` (2 active per Phase 5 of #2719; codex/SOUL.md and gemini/SOUL.md dropped as no-ops).
- **`config/agents/{claude,codex,gemini}/SOUL.delta.md`** + **`config/agents/hermes/SOUL.md`** — provider-specific deltas; this plan does NOT modify any delta, only SHARED.

### Standards

Not applicable — meta-discipline rule addition, no engineering standards involved. But per Codex r2 #7 from #2722, the `cat:harness` retrieval bundle applies:

- **`docs/standards/CONTROL_PLANE_CONTRACT.md`** — read 2026-05-16T23:30Z. The new rules are durable artifacts in `config/agents/SHARED_SOUL.md` (tracked, propagated via `build-soul-runtime.sh`). Runtime symlinks remain per-machine transient state. The path through control plane is correct.
- **`docs/standards/AI_REVIEW_ROUTING_POLICY.md`** — read 2026-05-16T23:30Z. Three-provider review default applies; T1.5 complexity (text-only) maps to T2 minimum, but the load-bearing nature (every future agent action on this repo) justifies T3.
- **`.claude/rules/patterns.md`** — Level-3 enforcement gradient (pre-commit hook) is the strongest tier. New rules above are at Level-0 (prose); migration path to higher tiers is per-rule and out of scope here.

### LLM Wiki pages consulted

Not applicable — no domain-knowledge dependency.

### Documents consulted

- **#2722** ([closed 2026-05-16 via commit `340af0021`](https://github.com/vamseeachanta/workspace-hub/commit/340af0021)) — origin of all 5 findings. T3 review artifacts at `scripts/review/results/2026-05-16-plan-2722-{claude,codex,gemini}.md` are the primary evidence base.
  - Codex r2 finding #1: active-merge skip threat-model inversion → Rule 3 (self-blocking generalization).
  - Codex r2 finding #2 ≈ Claude r1 #4 ≈ Gemini r2 #3: TOCTOU on whitelist source → Rule 3 (self-blocking generalization).
  - Claude r1 #3: per-file blanket exempt as backdoor → Rule 3.
  - Claude r1 #1: "3 landed PRs" factual error → Rule 2 (verify coverage assumptions).
  - Claude r1 #5: path resolution unspecified → Rule 2 (verify coverage).
  - Gemini r2 #1: self-blocking plan file → Rule 3.
  - Gemini r2 #2/#6: worktree-incompatibility → Rule 1 (generalizable promotion: this would have caught #2722 design before review).
  - Gemini r2 #8: filename word-splitting → Rule 1 (generalizable promotion).
  - Aggregate: 26 of 29 review findings were generalizable but only landed in the #2722 plan, not in any SOUL/rule layer → Rule 1.
- **`feedback_cross_provider_review_payoff`** — validated empirically by #2722's 29 findings with only 3 overlap. Anchors the T3 default in the plan's review specification.
- **`feedback_check_parallel_work`** + **`feedback_dispatching_parallel_agents`** + **`feedback_parallel_agent_write_only_pattern`** + **`feedback_parallel_subagent_shared_target_manifest_deferral`** + **`feedback_subagent_write_phantom`** — backstop for Rule 5 (parallel subagent dispatch). These memories already exist; Rule 5 references them and makes the bias-toward-parallel explicit at the must-fire layer.
- **`feedback_n_night_blocker_promote_to_replan`** — adjacent precedent for Rule 2 (claim-vs-reality verification at the operational layer).

### Gaps identified

- No promotion path from "review caught it once" to "next plan in same domain knows about it" → addressed by Rule 1.
- No empirical-coverage check before "applies to all N" claims → addressed by Rule 2.
- No design-time check that an enforcement script wouldn't block its own artifacts → addressed by Rule 3.
- No explicit bias-toward-action rule for already-authorized work → addressed by Rule 4.
- Parallel-subagent dispatch is documented in feedback memories but not surfaced at must-fire-rule layer → addressed by Rule 5.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-16T23:30Z via `gh issue view`):
- `#2724` — OPEN, `status:needs-plan` — title matches.
- `#2722` — CLOSED, closed via commit `340af0021`.
- `#2723` — OPEN, dead-code follow-on filed earlier today.
- `#2719` — CLOSED.

**File existence** (`ls -la` 2026-05-16T23:30Z):
- EXISTS: `config/agents/SHARED_SOUL.md` (109 lines, will become ~125 lines after additions).
- EXISTS: `scripts/agents/build-soul-runtime.sh` (verified working in preflight).
- EXISTS: `scripts/enforcement/check-soul-runtime-drift.sh` (verified 0-exit in preflight).
- EXISTS: `scripts/review/results/2026-05-16-plan-2722-{claude,codex,gemini}.md` — review evidence base.

**Line excerpts** (`sed -n N,Mp config/agents/SHARED_SOUL.md`, current state):

`config/agents/SHARED_SOUL.md:46-63` (Must-Fire Rules section ending point — insertion goes after line 63):
```
# Must-Fire Rules (per-message reinforcement)

These rules fire on every action; violating them produces real incidents documented in memory feedback files.

- **Never self-label `status:plan-approved`.** ...
- **No local task IDs.** ...
- ... [11 more rules] ...
- **Subagent Write phantom hazard.** Subagents can report `Write` success while the file doesn't land; main session must `ls` before believing. (`feedback_subagent_write_phantom`)
```

**Gap proofs**:
- `grep -c "Promote generalizable" config/agents/SHARED_SOUL.md` → 0 (rule does not exist).
- `grep -c "Verify coverage assumptions" config/agents/SHARED_SOUL.md` → 0.
- `grep -c "block their own artifacts" config/agents/SHARED_SOUL.md` → 0.
- `grep -c "Proactively take up" config/agents/SHARED_SOUL.md` → 0.
- `grep -c "Use subagents for parallel" config/agents/SHARED_SOUL.md` → 0.
- All 5 are net-new; no risk of conflict with existing rules.

**Reproduction proofs**:

N/A — governance / meta-discipline addition; no runtime failure to reproduce. The empirical evidence base IS the #2722 review wave (already verifiable via the 3 review artifacts at `scripts/review/results/2026-05-16-plan-2722-*.md`).

<!-- Source count: SHARED_SOUL.md current (1) + 3 #2722 review artifacts (2) + AI_REVIEW_ROUTING_POLICY.md (3) + CONTROL_PLANE_CONTRACT.md (4) + 5 feedback memories (5). Far above ≥3 minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-16-issue-2724-soul-must-fire-rules-from-2722-review.md` |
| Canonical SHARED file | `config/agents/SHARED_SOUL.md` (modified: 13 → 18 must-fire rules) |
| Build script | `scripts/agents/build-soul-runtime.sh` (re-run, no modification) |
| Drift check | `scripts/enforcement/check-soul-runtime-drift.sh` (re-run for verification) |
| Regenerated artifacts | `config/agents/{claude,codex,gemini,hermes}/SOUL.runtime.md` + `config/agents/codex/AGENTS.runtime.md` |
| Plan review — Claude | `scripts/review/results/2026-05-16-plan-2724-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-16-plan-2724-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-16-plan-2724-gemini.md` |
| Plans index update | `docs/plans/README.md` (row added) |

---

## Deliverable

5 new Must-Fire Rules in `config/agents/SHARED_SOUL.md`, applied to all 4 cross-provider runtime artifacts (hermes/claude/codex/gemini) via `build-soul-runtime.sh`, with drift check passing post-build.

---

## Rule Texts (exact strings to insert)

Insert verbatim after current line 63 of `config/agents/SHARED_SOUL.md`:

```markdown
- **Promote generalizable review findings.** When an adversarial review surfaces a defect class that applies beyond the current plan's scope (worktree-incompatibility, NUL-iteration safety, TOCTOU between working tree and staged blob, threat-model inversion in skip conditions, BSD vs GNU portability), file a follow-on issue OR add a rule to `.claude/rules/` / `SHARED_SOUL.md` so the next plan in the same domain doesn't re-discover it. Tribal knowledge buried in review artifacts has zero retrieval-cost benefit. ([#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) r3+r4 wave: 26 of 29 distinct findings were generalizable but absorbed only into the plan that triggered them — no promotion path until this rule.)
- **Verify coverage assumptions empirically.** Before claiming work "applies to all X" / "installs across N repos" / "covers every machine", enumerate the actual set on the live filesystem and confirm iteration visits each member. Drift probe on 2026-05-16 found only 3 of 7 tier-1 siblings checked out on `ace-linux-1` — per-machine coverage is fundamentally partial; coverage claims must match reality. (`feedback_n_night_blocker_promote_to_replan`-adjacent; [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722) §Acceptance criterion 12.)
- **Enforcement scripts must not block their own artifacts.** When designing a check that fires on staged content (conflict markers, secret patterns, banned strings, regex denials), verify that the plan, tests, and implementation files for that check would themselves pass it — OR carry an explicit forensic-allowlist mechanism. Prefer per-line sentinels (matches `scripts/enforcement/check-no-abs-paths.sh:111` prior art) and path-restricted whole-file sentinels (5-prefix set in `check-no-conflict-markers.sh` precedent); avoid per-file blanket exempts, which are backdoors. (Gemini r2 #1 caught the self-blocking plan-file defect in [#2722](https://github.com/vamseeachanta/workspace-hub/issues/2722); Claude r1 #3 flagged the blanket-exempt backdoor.)
- **Proactively take up authorized work.** When a session opens with clearly actionable state — a `status:plan-approved` issue, a documented carry-forward queue, a session-handoff entry-prompt with preflight commands, or a `whats-next` dispatch — proceed without waiting for an explicit "begin" instruction. Bias toward action on already-authorized work; reserve clarifying questions for genuine ambiguity that changes the action. The never-self-approve gate (above) bounds *authorization* boundaries; everything inside an authorized scope is fair game. Stale waiting burns context-window budget and user time.
- **Use subagents for parallel work.** When facing 2+ independent tasks (research across multiple repos, file discovery, cross-provider review dispatch, audit across N items, fan-out reads), dispatch via parallel `Agent`/`Task` calls in a single message rather than serializing manually. Sequential narration of independent tasks burns the user's context-window budget. Caveat: subagent `Write` phantom hazard still applies — main session must `ls`/verify before trusting subagent success claims. (`feedback_subagent_write_phantom`, `feedback_parallel_agent_write_only_pattern`, `feedback_parallel_subagent_shared_target_manifest_deferral`.)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/agents/SHARED_SOUL.md` | append 5 new bullets after line 63 |
| Re-run | `bash scripts/agents/build-soul-runtime.sh` | regenerate 5 runtime artifacts |
| Auto-modify | `config/agents/hermes/SOUL.runtime.md` | rebuilt artifact |
| Auto-modify | `config/agents/claude/SOUL.runtime.md` | rebuilt artifact |
| Auto-modify | `config/agents/codex/SOUL.runtime.md` | rebuilt artifact |
| Auto-modify | `config/agents/codex/AGENTS.runtime.md` | rebuilt artifact |
| Auto-modify | `config/agents/gemini/SOUL.runtime.md` | rebuilt artifact |
| Verify | `bash scripts/enforcement/check-soul-runtime-drift.sh` | must return 0 post-build |
| Update | `docs/plans/README.md` | add this plan row |

---

## TDD Test List

This is text-only + propagation; no new pytest cases. Verification is via the existing drift check:

| Verification | Command | Expected |
|---|---|---|
| Pre-modification drift | `bash scripts/enforcement/check-soul-runtime-drift.sh` | exit 0 (baseline clean) |
| Post-modification, pre-rebuild | same command | exit 1 (drift detected — SHARED changed, runtime stale) |
| Post-rebuild | same command | exit 0 (drift resolved) |
| Live symlinks reflect change | `grep -c "Promote generalizable" ~/.hermes/SOUL.md ~/.codex/AGENTS.md` | both → 1 |
| Existing enforcement suite | `uv run python -m pytest tests/enforcement/` | 88/88 pass (no regression) |

---

## Acceptance Criteria

- [ ] 5 new Must-Fire Rules text appears in `config/agents/SHARED_SOUL.md` at the verbatim positions specified above.
- [ ] `bash scripts/agents/build-soul-runtime.sh` regenerates all 5 runtime artifacts without error.
- [ ] `bash scripts/enforcement/check-soul-runtime-drift.sh` returns 0 post-build.
- [ ] Live runtime symlinks (`~/.hermes/SOUL.md`, `~/.codex/AGENTS.md`) contain all 5 new rule strings (verified via `grep -c`).
- [ ] No regression: `uv run python -m pytest tests/enforcement/` returns 88 passed (or equivalent prior-count + delta).
- [ ] T3 adversarial plan review: Claude + Codex + Gemini all submit verdicts to `scripts/review/results/2026-05-16-plan-2724-{claude,codex,gemini}.md` (or documented UNAVAILABLE per `feedback_permission_gate_blocks_cross_review`).
- [ ] All MAJOR findings from review absorbed via r3 inline OR explicitly disagreed/discounted with reasoning.
- [ ] Closing commit references `Closes #2724`, `Refs #2722, #2719`.

---

## Adversarial Review Summary

<!-- Filled after Step 4 (review wave) completes. Currently PENDING. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — review wave in flight.

Revisions made based on review:
- (to be populated after r1/r2/r3 complete)

---

## Risks and Open Questions

- **Risk: SOUL bloat.** Adding rules to a per-message-reinforcement file dilutes attention; the existing 13 rules already approach the cognitive-load ceiling. Mitigation: each new rule is empirically grounded in a recent incident, AND each cites a specific feedback memory or issue for further context (depth on demand, not in the rule body). Long-form discussion stays in feedback memories.
- **Risk: rule #4 (proactive work pickup) tension with rule #1 (never-self-approve).** Could be misread as "always pick up and finish". Mitigation: rule explicitly says "bounds *authorization* boundaries"; clarifying-question-only-when-ambiguity-changes-action. Same-shape as existing `Act when the next step is obvious` (Operating Posture line 26).
- **Risk: rule #5 (subagent parallel) interacts with `feedback_isolated_clone_dispatch_race` and `feedback_multi_agent_commit_serialization`.** Mitigation: rule references the parallel-write-only and shared-target-manifest patterns explicitly; the constraints on git-lock contention remain via the existing must-fire rule on pathspec commits.
- **Open question: should rule #2 promote to a Level-2 script** (`scripts/enforcement/check-coverage-claim.sh` that scans plans for "all N" claims and verifies)? Out of scope here; can be a follow-on issue if pattern recurs.
- **Open question: should rule #1 promote to a Level-3 hook** (post-review-result hook that detects "MAJOR finding repeated across providers" and prompts for SOUL/rule promotion)? Out of scope; follow-on.

---

## Complexity: T1.5

**T1.5** — text-only single-file change + mechanical rebuild + drift verification. **But** the change is load-bearing across 4 providers and every future agent action, so T3 review applied (not the T1-text-only default). Estimated time: 15-30 min including reviews; absorption of MAJOR findings could extend to 45-60 min.
