# Plan for #2675: Reverse-prompt repo ecosystem for productive multi-provider work (Claude + Hermes + Codex + Gemini)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-05-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2675
> **Review artifacts:** scripts/review/results/2026-05-12-plan-2675-claude.md | scripts/review/results/2026-05-12-plan-2675-codex.md | scripts/review/results/2026-05-12-plan-2675-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/agents/provider-capabilities.yaml` (v1.1.0, last_updated 2026-02-24) — already declares per-provider `strategy_role`, `consolidation_candidate`, and `consolidation_trigger` for claude/codex/gemini/hermes/openai. **This file is the substrate the reverse-prompted matrix extends, not replaces.**
- Found: `config/agents/routing-config.yaml` (v2.0.0) — already encodes tiers (SIMPLE/STANDARD/COMPLEX/REASONING), routing dimensions with explicit weights, confidence thresholds, and `cross_modes` for plan-vs-review per tier (e.g., `cross_review.COMPLEX: true` requires full 3-of-3).
- Found: `config/agents/model-registry.yaml`, `behavior-contract.yaml`, `drift-policy.yaml`, `skill-graph-index.yaml`, `user-profile.yaml` — round out the agents-config surface.
- Found: `config/ai-tools/agent-capability-scores.yaml` (v 2026-03-13) — 0–10 radar scores per provider across 6 dimensions; explicitly tags Codex as "HARD GATE" and Opus as "quota_risk: HIGH".
- Found: `config/ai-tools/pricing.yaml` — concrete $/M token rates per model (Claude Opus 4.6 $5/$25, Sonnet 4.6 $3/$15, Haiku 4.5 $0.80/$4, Codex o4-mini/gpt-5.4 $0.50/$1.50, Gemini 2.5 Pro $0.075/$0.30).
- Found: `config/ai-tools/subscriptions.yaml` (last_updated 2025-12-23) — Claude Max $106.60/mo + OpenAI Plus $21.28 + Google AI Pro $19.99 + Copilot Pro $8.88/mo = $156.75/mo declared. **Stale**: missing the Codex paid plan ($200/mo per `project_hermes_codex_quota` memory).
- Found: `scripts/review/` — `submit-to-claude.sh`, `submit-to-codex.sh`, `submit-to-gemini.sh`, `cross-review.sh`, `attest-plan-claims.sh`, `plan-review-fanout.sh`, `normalize-verdicts.sh`, `validate-review-output.sh`. The cross-review apparatus is **mature** and the plan must invoke it, not re-tool it.
- Found: `scripts/review/results/` contains 1,444 review-result files (count as of 2026-05-12 post-fanout; earlier survey said 1,437) — empirical cross-provider effectiveness data already exists for retro-fitting outcome thresholds.
- Found: `.claude/skills/ai/` — existing skills include `agent-usage-optimizer`, `provider-utilization-scorecard`, `durable-provider-throughput-dispatch`, `hermes-model-switching`, `provider-session-quota-operations`, `inventory-readiness-provider-dispatch`. These are the plan's building blocks.
- Found: `.claude/hooks/` and `scripts/enforcement/` — Level-3 enforcement is in place for plan-approval (`require-plan-approval.sh`), cross-review (`require-cross-review.sh`, `cross-review-gate.sh`), TDD pairing (`require-tdd-pairing.sh`), and verify-artifacts (`require-verify-artifacts.sh`).
- Found: adapter files `CLAUDE.md` (997B), `AGENTS.md` (1729B), `GEMINI.md` (680B) — all within the 20-line harness limit. **Gap: `CODEX.md` does not exist.**
- Found: provider-specific config dirs all populated: `config/agents/claude/` (populated), `config/agents/codex/` (`config.toml` + state-snapshots), `config/agents/gemini/` (`settings.json` + state-snapshots), `config/agents/hermes/` (`SOUL.md` + `config.yaml.template` + memories/ + patches/). **Correction from earlier draft**: the initial `ls -la` size column read 0 for these dirs, which I mis-interpreted as empty; `git ls-files` confirms 13 tracked files across the three subdirs.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` (cited in #2399 plan) |
| AI review routing policy | done | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (cited in #2399 plan) |
| Model-release readiness contract | in-flight under #2399 (plan still `draft`) | `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` |
| Calc-citation contract | done | `.claude/rules/calc-citation-contract.md` — not directly relevant to this plan; cited as governance precedent |
| Universal coding-style + patterns rules | done | `.claude/rules/coding-style.md`, `patterns.md` |

### LLM Wiki pages consulted

Not applicable. This is a harness/orchestration governance plan, not engineering-knowledge work. No wiki page should be cited as a primary source for the design.

### Documents consulted

- Related issue [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089) — weekly Hermes + AI provider settings review. Operational drift cadence already delivered as `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` (16 comments, 6069 bytes). **Operational; this plan connects strategic design to it.**
- Related issue [#2399](https://github.com/vamseeachanta/workspace-hub/issues/2399) — next-model-release readiness contract. Forward-compatibility for upcoming model changes. **Plan still `draft`; this plan must connect to it, not duplicate it.**
- Related issue [#2549](https://github.com/vamseeachanta/workspace-hub/issues/2549) — Business Brain (`docs/BUSINESS_BRAIN.md`, 13192 bytes) refresh. Onboarding doc cadence. **Documentation-cadence sibling.**
- Related issue [#2657](https://github.com/vamseeachanta/workspace-hub/issues/2657) — Hermes llm-wiki spinout path drift (plan-approved 2026-05-08) — most recent provider-session remediation; useful reference for how plan-vs-execute discipline gets applied to Hermes paths.
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` (root adapters) — current control-plane entry points.
- `.claude/rules/README.md` — universal-rules charter.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (v3.1.0) — defines the planning workflow this plan obeys.
- Memory (provider failure modes already paid for) — 22 feedback files enumerated in the issue body, including `feedback_codex_sandbox_no_execution`, `feedback_gemini_sandbox_overlay_blindness`, `feedback_hermes_active_preflight_check`, `feedback_cross_provider_review_payoff`, `feedback_always_adversarial_review_scale_depth`, `feedback_attestation_enables_contradiction_detection`, `feedback_subagent_write_phantom`, `feedback_codex_sustained_MAJOR_loop`, `feedback_codex_cli_0_124_upstream_regression`.

### Gaps identified

1. **No single document maps outcomes → provider matrix → workflow → failure-modes.** The substrate (capabilities, routing, pricing, scores) is rich but un-connected to *measurable outcomes per work class*.
2. **No `CODEX.md` adapter file** to mirror `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`. The repo has heavy Codex usage (1,437 review results) but no adapter-file entry point. (The #2399 plan also names `.codex/CODEX.md` as a discoverability anchor; either location must be reconciled.)
3. **`config/agents/{codex,gemini,hermes}/` are populated but minimally — not "empty skeletons".** Codex has `config.toml` (274B) + state-snapshots; Gemini has `settings.json` (83B) + state-snapshots; Hermes has `SOUL.md` + `config.yaml.template` + memories/ + patches/. Gap is **not "no content"** — it is **"no behavior-anchored content aligned to the §B provider role matrix"**. The follow-up issue should audit-and-extend, not populate-from-scratch.
4. **`config/ai-tools/subscriptions.yaml` is stale (2025-12-23)** and omits the Codex paid plan. Total cost claim of $156.75/mo understates reality by ~$200/mo.
5. **`config/ai-tools/agent-capability-scores.yaml` predates the 2026-04 and 2026-05 wave of lessons** captured in memory (`feedback_codex_sandbox_no_execution`, `feedback_gemini_sandbox_overlay_blindness`, etc.). Scores reflect pre-incident perception.
6. **Existing routing-config tier definitions (`SIMPLE`/`STANDARD`/`COMPLEX`/`REASONING`) do not name work-class outcomes** — they name token budgets. The reverse-prompted ledger must add an outcome layer on top.
7. **No explicit rule for when *not* to cross-review** (single-author r3 is appropriate when permission gates block dispatch, per `feedback_permission_gate_blocks_cross_review` — but this is not codified in `routing-config.yaml` or any skill).
8. **No durable record of which lessons in memory drove which durable config/script/skill change** — i.e., the feedback memories are organizationally orphaned from the artifacts that implement their mitigations.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-12 via `gh issue view`):
- `#2675` — OPEN — `feat(ai-orchestration): reverse-prompt repo ecosystem for productive multi-provider work (Claude + Hermes + Codex + Gemini)`
- `#2089` — OPEN — `feat(harness): weekly Hermes + AI provider settings review for repo ecosystem`
- `#2399` — OPEN — `feat(ai-orchestration): define next-model-release readiness contract for repo ecosystem`
- `#2549` — OPEN — `chore(business-brain): periodically assess repo work and refresh ecosystem context`
- `#2657` — OPEN — `chore(provider-session): remediate Hermes llm-wiki spinout path drift` (label `status:plan-approved` confirmed)

**File existence** (`ls -la` 2026-05-12):
- EXISTS: `CLAUDE.md` (997B), `AGENTS.md` (1729B), `GEMINI.md` (680B)
- EXISTS: `config/agents/provider-capabilities.yaml`, `routing-config.yaml`, `model-registry.yaml`, `behavior-contract.yaml`, `drift-policy.yaml`, `skill-graph-index.yaml`, `user-profile.yaml`
- EXISTS: `config/ai-tools/pricing.yaml`, `subscriptions.yaml`, `usage-tracking.yaml`, `weekly-utilization.json`, `provider-routing-scorecard.json`, `provider-work-queue.json`, `provider-utilization-weekly.json`, `provider-autolabel-candidates.json`, `agent-quota-latest.json`, `agent-capability-scores.yaml`, `agent-capability-radar.html`, `pricing.yaml`, `mcp-servers.yaml`, `onet-lookup.yaml`, `release-scan-state.yaml`, `continuous-planning-pipeline.json`
- EXISTS: `docs/BUSINESS_BRAIN.md` (13192B), `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` (6069B), `docs/plans/README.md` (109811B), `docs/plans/_template-issue-plan.md` (8844B), `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md`
- EXISTS: `scripts/review/` with `submit-to-{claude,codex,gemini}.sh`, `cross-review.sh`, `attest-plan-claims.sh`, `plan-review-fanout.sh`, and 1,437 entries under `results/`
- MISSING: `CODEX.md` (no adapter file)
- EXISTS but minimally populated: `config/agents/codex/` (2 files + 3 in state-snapshots), `config/agents/gemini/` (1 file + 2 in state-snapshots), `config/agents/hermes/` (2 files + 2 in memories + 2 in patches). Original "empty dir" wording was wrong; corrected this revision.
- MISSING (new — this plan creates): `docs/standards/AI_ECOSYSTEM_DESIGN.md`, `docs/reports/2026-05-12-issue-2675-outcome-ledger.md`, `docs/reports/2026-05-12-issue-2675-provider-role-matrix.md`, `docs/reports/2026-05-12-issue-2675-failure-mode-design-contract.md`, `docs/reports/2026-05-12-issue-2675-followup-issues-list.md`

**Line excerpts**:

`config/agents/provider-capabilities.yaml` lines 47–52 (claude.horizon_2026_h1):
```
    horizon_2026_h1:
      trajectory: improving_rapidly
      gap_to_close: "context window (200K vs 1M Gemini); closing by mid-2026 expected"
      strategy_role: orchestrator_and_executor
      consolidation_candidate: false  # already primary; not at risk
```

`config/agents/routing-config.yaml` lines 76–86 (cross_modes):
```
cross_modes:
  cross_plan:
    SIMPLE: false       # Route A: single planner sufficient
    STANDARD: false     # Route B: single planner (cross-plan optional)
    COMPLEX: true       # Route C: all 3 plan independently, Claude synthesizes
    REASONING: true     # Full ensemble planning
  cross_review:
    SIMPLE: false       # Route A: single-provider review only
    STANDARD: true      # Route B: 2-of-3 cross-review
    COMPLEX: true       # Route C: full 3-of-3 with synthesis
    REASONING: true     # Full 3-of-3 cross-review
```

`config/ai-tools/subscriptions.yaml` lines 95–99 (totals — stale):
```
totals:
  monthly_subscriptions: 156.75
  annual_projection: 1881.04
  currency: "USD"
  last_updated: "2025-12-23"
```

**Gap proofs**:
- `ls -la CODEX.md 2>&1 | head -3` → "No such file or directory" — confirms no Codex adapter at repo root.
- `git ls-files config/agents/codex/ config/agents/gemini/ config/agents/hermes/` → 13 tracked files across all three (corrected from earlier "empty dir" claim).
- `grep -i codex config/ai-tools/subscriptions.yaml | head -3` → no matches in active subscription block — confirms Codex paid plan absent from subscriptions ledger.

**Reproduction proofs**: **N/A — this is a design issue with no runtime failure claim.** Skip is intentional per `issue-planning-mode` Step 1.5.

**Source count: 12 distinct sources cited** (issue body, 5 related issues, 7 config files, 1 ops doc, 1 plan, 1 skill spec, 22 memory feedback files counted as group = ≥3 individually). Minimum 3 satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` |
| Ecosystem design contract (durable) | `docs/standards/AI_ECOSYSTEM_DESIGN.md` |
| Outcome ledger report | `docs/reports/2026-05-12-issue-2675-outcome-ledger.md` |
| Provider role matrix report | `docs/reports/2026-05-12-issue-2675-provider-role-matrix.md` |
| Workflow walk-throughs report | `docs/reports/2026-05-12-issue-2675-workflow-walkthroughs.md` |
| Failure-mode design contract report | `docs/reports/2026-05-12-issue-2675-failure-mode-design-contract.md` |
| Follow-up issues (listed, not filed) | `docs/reports/2026-05-12-issue-2675-followup-issues-list.md` |
| Plan review — Claude | `scripts/review/results/2026-05-12-plan-2675-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-12-plan-2675-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-12-plan-2675-gemini.md` |
| README index row | `docs/plans/README.md` (Plan Index, line ~203) |

---

## Deliverable

A durable `docs/standards/AI_ECOSYSTEM_DESIGN.md` plus five supporting reports under `docs/reports/` that, taken together, declare measurable outcomes per work class, the minimal multi-provider pipeline that produces each outcome, the efficient-usage rules that govern provider selection, and the failure-mode contract that maps each paid-for memory lesson to its durable mitigation — leaving a follow-up-issue list that is **listed, not filed** until user approval at `status:plan-approved`.

---

## Reverse-Prompted Design (in-plan content)

This section materializes the design itself. During execution (Step 6), each block here is promoted to its named artifact in the Artifact Map; the plan file then becomes the audit-trail of how the artifact was derived.

### A. Outcome ledger (≥5 work classes)

The ledger declares *what good output looks like* for each top-level work class the repo runs. Each row pairs an outcome with a *measurable signal* and a *"good enough" threshold*. Signals are deliberately *artifact-based* — they survive review handoffs and audit later.

| Work class | Outcome (what good looks like) | Measurable signal | Good-enough threshold |
|---|---|---|---|
| **Issue planning** | Plan cites ≥3 distinct sources, names concrete gaps, has reproduction proof or N/A justification | `Resource Intelligence Summary` source-count + presence of `Reproduction proofs` block | ≥3 sources AND repro or N/A-marked |
| **Adversarial review** | Each provider verdict cites file paths or quoted claims, no praise/restatement, MAJOR/MINOR returns dominate over rubber-stamp APPROVE | Verdict + per-finding citation density in `scripts/review/results/*` | ≥1 cited finding per provider; APPROVE allowed only with checklist evidence |
| **Implementation execution** | Tests-first, atomic commits per logical change, no `--no-verify`, no self-approve gate breach | Commit log + pre-commit-hook logs + attestation block (per [#2405](https://github.com/vamseeachanta/workspace-hub/issues/2405)) | Zero bypassed hooks; ≥1 failing test before its fix lands |
| **Knowledge/wiki contribution** | Concept pages cite public references (textbooks/DOIs/public manuals), not LinkedIn-only sourcing; aligns to repo licensing | Page frontmatter references; lint pass on `feedback_llm_wiki_concept_pages_need_public_references` rule | All non-vendor concept pages cite ≥1 textbook/DOI/public manual |
| **Comms (issue/PR comments, recruiter routing)** | Single summary comment per issue (per `feedback_gh_issue_comment`); recruiter outreach replied to only when consulting-level + credible (per `feedback_recruiter_engagement`) | Comment count per issue; recruiter-reply log | ≤1 status comment per agent-session per issue |
| **Ops/automation (Hermes/cron/batch)** | Preflight check passes before commit storms; no merge-race silent reverts; agents write-only-shared (commits serialized in main session) | Hermes activity log + `git reflog` audit for race events | 0 silent reverts per week; 0 dual-write commit races per week |
| **Cross-machine readiness** *(referenced from #2089, not owned here)* | Reflected in #2089's weekly checklist | Output of weekly review | Out of scope: owned by #2089 |

**Rationale for 6 rows above** (vs. acceptance criterion of ≥5): every class above has at least one paid-for failure mode in memory. The "cross-machine readiness" row is *listed* to make the boundary with #2089 explicit but is *owned by #2089*, not duplicated here.

### B. Provider role matrix (with fallbacks)

The matrix extends `config/agents/provider-capabilities.yaml`'s `strategy_role` field by *anchoring each role to a work class from the outcome ledger*.

| Work class | Primary | Why primary | Fallback 1 | Fallback 2 | When fallback fires |
|---|---|---|---|---|---|
| Issue planning | **Claude** (Sonnet 4.6 default; Opus 4.6 for Route-C complex) | Long-context multi-source synthesis; orchestrator role; tool-driving in main session (`feedback_claude_in_chrome_session_scoped`) | Hermes | Codex | Claude quota exhausted, or memory-heavy backlog drain (Hermes); never delegate planning to Codex (sandbox cannot execute, per `feedback_codex_sandbox_no_execution`) |
| Adversarial review (T1 — scoped) | **Claude** single-author r3 | Cost-efficient; sufficient when permission gates block dispatch (`feedback_permission_gate_blocks_cross_review`) | — | — | T1 has no fallback; if scope grows mid-review, escalate to T2 |
| Adversarial review (T2 — standard) | **Codex** + **Gemini** | Codex non-overlapping defects vs. Claude (`feedback_cross_provider_review_payoff`); Gemini cheap at scale | Claude (reviewer-of-record) | OpenAI GPT-4.1 | Codex CLI hang (`feedback_codex_cli_0_124_upstream_regression`) → fallback OpenAI; Gemini sandbox overlay blind (`feedback_gemini_sandbox_overlay_blindness`) → verify with `git ls-files` first |
| Adversarial review (T3 — complex) | **Claude** + **Codex** + **Gemini** full 3-of-3 | `routing-config.cross_review.COMPLEX: true` already mandates it | Any 2 of 3 if one provider down | — | Provider unavailability → record explicit failure, continue with available, never auto-approve |
| Implementation execution | **Claude** main session | Tool execution + file writes; Codex cannot write (`feedback_codex_sandbox_write_blocked`); subagent Write phantoms possible (`feedback_subagent_write_phantom`) → main session must `ls` verify | Codex *review-only* | — | Never delegate writes to Codex; never trust subagent Write reports without local verify |
| Knowledge/wiki contribution | **Claude** (drafting) + **Codex** (independent check) | Claude long-context for source synthesis; Codex sandbox can still *read+critique* even when it cannot write | Hermes (overnight batch) | Gemini (large-doc overflow) | — |
| Comms (issue/PR comments) | **Claude** main session | Comment is part of issue-workflow surface; subagent comm phantoms possible | — | — | Never let subagents post comments without main-session re-verify |
| Ops/automation/scheduled | **Hermes** | Skill tooling, delegation, document-heavy workflows (per `provider-capabilities.yaml`); `feedback_hermes_active_preflight_check` requires Hermes to preflight | Claude (manual fallback) | — | If Hermes mid-rebase: pause delegation, never dispatch parallel commits |

**Operational rules baked into the matrix:**

- **No provider owns more than 2 primary roles** without explicit cost/quota justification. Today Claude legitimately owns planning + execution + comms because it is the only one that drives tools in main session — but this is a known concentration risk that the cost/quota follow-up issue must address.
- **Codex is review-only by hard policy.** No Codex file writes, no Codex shell execution. The `submit-to-codex.sh` wrapper enforces this; the matrix reinforces it.
- **Gemini lane requires `git ls-files` ground-truth check before accepting MAJOR file-missing claims.** Encoded as a precondition in the cross-review walkthrough (§ C2).
- **Fallback firing must be logged** (`scripts/review/results/...-fallback.md`) so the weekly review (#2089) can audit whether fallbacks happen often enough to update the matrix.

### C. Workflow walk-throughs (two for v1)

#### C1. Issue planning walk-through

**Ideal output:** A plan file under `docs/plans/YYYY-MM-DD-issue-NNN-*.md` that satisfies §A.outcome-ledger row 1 (≥3 sources, gap list, repro proof or N/A) and is ready for adversarial review.

**Minimal provider pipeline:**

```
1. Claude main session: read issue body, load issue-planning-mode skill
2. Claude main session: Resource Intel survey (parallel Bash + Read tool calls)
3. Claude main session: classify T1/T2/T3
4. [GATE 1] issue-planning-mode skill Step 1.5: reproduce-or-N/A
5. Claude main session: draft plan against docs/plans/_template-issue-plan.md
6. Claude main session: spec self-review (placeholder scan, internal consistency, scope, ambiguity)
7. [GATE 2] user reviews draft
8. → walkthrough C2 (adversarial review)
9. [GATE 3] user approval at status:plan-approved
10. Claude main session: implement (TDD)
```

**Gate checkpoints this passes through** (from existing repo workflows, not new):
- `issue-planning-mode` Step 1 (intake), Step 1.5 (reproduce), Step 2 (draft), Step 3 (review), Step 4 (post+label), Step 5 (user approves), Step 6 (TDD implement)
- `require-plan-approval.sh` (hook) enforces status:plan-approved before writes outside safe paths
- `require-cross-review.sh` (hook) enforces adversarial-review artifacts before push

**Provider choice rationale:** No Hermes, no Codex, no Gemini in planning itself (excluding the review step) — planning is single-session work that requires tool-driving in the main session. Delegating to subagents risks subagent Write phantoms (`feedback_subagent_write_phantom`); delegating to Codex breaks (sandbox cannot execute, `feedback_codex_sandbox_no_execution`); delegating to Gemini risks overlay blindness (`feedback_gemini_sandbox_overlay_blindness`).

#### C2. Adversarial review walk-through (T1 / T2 / T3 depth scaling)

**Ideal output:** ≥1 review artifact per active provider under `scripts/review/results/YYYY-MM-DD-plan-NNN-<provider>.md`, each containing per-finding citations to file paths or quoted plan text, with a structured verdict normalized via `scripts/review/normalize-verdicts.sh`.

**Minimal provider pipeline (per tier):**

```
T1 (scoped, single-provider):
1. Claude review-of-record only
2. Verdict written to scripts/review/results/...-claude.md
3. No fanout; if scope grows, escalate to T2

T2 (standard, 2-of-3):
1. Push plan file to origin (per feedback_codex_needs_pushed_artifact)
2. scripts/review/attest-plan-claims.sh injects evidence block (per #2405)
3. Parallel dispatch:
   - scripts/review/submit-to-codex.sh  (review-only; sandbox-safe prompt)
   - scripts/review/submit-to-gemini.sh (with GEMINI_CLI_TRUST_WORKSPACE=true; per feedback_gemini_trust_env_blocks_reviews)
4. Wait for both; if Codex CLI hangs (feedback_codex_cli_0_124_upstream_regression) fall back to OpenAI
5. Claude reviews the merged-findings file
6. If any MAJOR: revise plan, GOTO 1 (re-attest, re-dispatch)
7. If sustained-MAJOR 3+ rounds from one provider while others MINOR (feedback_codex_sustained_MAJOR_loop): surface consensus-vs-minority decision to user, do NOT auto-cycle

T3 (complex, full 3-of-3 with synthesis):
1. Steps 1–4 from T2, plus Claude as independent third lane
2. scripts/review/render-structured-review.py synthesizes the 3 verdicts
3. Apply T2 step 6 + 7 logic
```

**Gate checkpoints this passes through:**
- `require-cross-review.sh` (hook) — enforces review artifacts before push
- `cross-review-gate.sh` (hook) — gates plan-status promotion
- `issue-planning-mode` Step 3 reviewer-stance contract — every prompt must force defect-hunting, forbid praise/restatement, require evidence per finding

**Provider choice rationale:**
- **Codex is the cross-review hard gate** per `agent-capability-scores.yaml` (badge: `hard gate`) and `provider-capabilities.yaml` (`strategy_role: cross_review_hard_gate`). Its non-overlapping defect detection is the empirically-paid-for value (`feedback_cross_provider_review_payoff`).
- **Gemini is the third lane** for its 1M-token context (large plans fit whole) and free-tier capacity, with the `git ls-files` precondition.
- **Single-author r3 fallback** (`feedback_permission_gate_blocks_cross_review`) is allowed when dispatch is structurally blocked; provenance must be transparent in the artifact.

### D. Efficient-usage rules

**When to invoke each provider:**

| Decision | Rule |
|---|---|
| Planning work (any tier) | Claude main session — never delegate. |
| T1 review | Claude single-author r3 with transparent provenance. |
| T2 review | Codex + Gemini (parallel) → Claude reviews merged findings. |
| T3 review | All three independently → render-structured-review.py synthesis. |
| Implementation writes | Claude main session — verify subagent Write claims by `ls` (`feedback_subagent_write_phantom`). |
| Overnight batch work | Hermes — but preflight `pgrep -af 'git (rebase\|stash push\|commit\|merge\|reset\|checkout)'` first (`feedback_hermes_active_preflight_check`). |
| Wiki/concept page first-drafting | Claude — never LinkedIn-only sourcing (`feedback_llm_wiki_concept_pages_need_public_references`). |
| Recruiter / email triage | Claude main session — apply `feedback_recruiter_engagement` and `feedback_email_cross_noise` filters before drafting. |

**When NOT to invoke a provider:**

- **Don't delegate writes to Codex** — sandbox cannot write (`feedback_codex_sandbox_write_blocked`) or shell-exec (`feedback_codex_sandbox_no_execution`).
- **Don't trust Gemini file-missing MAJOR findings without `git ls-files`** — overlay blindness false-positives (`feedback_gemini_sandbox_overlay_blindness`).
- **Don't dispatch Hermes during user's active git operations** — merge-race silent reverts (`feedback_merge_race_silent_revert`, `feedback_hermes_active_preflight_check`).
- **Don't auto-cycle Codex MAJOR loops** beyond 3 rounds — surface consensus-vs-minority decision (`feedback_codex_sustained_MAJOR_loop`).
- **Don't have subagents drive Chrome** — `mcp__claude-in-chrome__*` is session-scoped (`feedback_claude_in_chrome_session_scoped`).
- **Don't run worktree-isolation for every agent** — 60% timeout rate on large repo (`feedback_worktree_isolation_large_repo_cost`); reserve for agents that must commit themselves.

**When to parallelize vs. serialize:**

- **Parallelize** independent provider reviews (T2/T3).
- **Parallelize** read-only Resource Intel surveys (Bash + Read tool calls in one message).
- **Serialize commits across parallel agents** (`feedback_multi_agent_commit_serialization`, `feedback_parallel_agent_write_only_pattern`): main session commits, subagents write only.
- **Serialize git operations during Hermes activity** (per preflight check).

**When single-author r3 is the right answer:**

- Permission-gate blocks dispatch (`feedback_permission_gate_blocks_cross_review`).
- T1 scope (small, focused).
- Codex + Gemini both unavailable (record both failures explicitly).

**When to escalate T1 → T2 → T3:**

- T1 → T2: scope grew during planning, multi-file changes detected, or first review surfaced unknowns.
- T2 → T3: MAJOR finding from one provider while others MINOR (forces tie-breaker third lane), or `cat:engineering*` / `cat:data-pipeline` label (per `engineering-issue-workflow` skill).

### E. Failure-mode design contract

Each row is a paid-for memory lesson → its durable mitigation surface in the repo. This *connects* the memory feedback files (which today live only in `~/.claude/projects/.../memory/`) to the artifacts that enforce them.

| Memory feedback | Durable mitigation surface |
|---|---|
| `feedback_codex_sandbox_no_execution` | `scripts/review/submit-to-codex.sh` review-only mode; provider matrix forbids Codex implementation work |
| `feedback_codex_sandbox_write_blocked` | Same as above |
| `feedback_codex_needs_pushed_artifact` | `scripts/review/attest-plan-claims.sh` runs after `git push` |
| `feedback_codex_sandbox_fallback_paths` | Codex prompt authorizes `js_repl` + GitHub connector fallback; MAJOR verdicts without fallback-read citation are weakly grounded — flagged in `scripts/review/validate-review-output.sh` |
| `feedback_codex_sustained_MAJOR_loop` | T2 walkthrough step 7 — surface decision after 3 sustained-MAJOR rounds |
| `feedback_codex_cli_0_124_upstream_regression` | T2 walkthrough step 4 — fallback to OpenAI on Codex hang; downgrade-to-0.123.0 documented in #2479 |
| `feedback_gemini_sandbox_overlay_blindness` | T2 walkthrough — `git ls-files` precondition before accepting Gemini MAJOR file-missing claims |
| `feedback_gemini_trust_env_blocks_reviews` | `submit-to-gemini.sh` sets `GEMINI_CLI_TRUST_WORKSPACE=true` (already landed 2026-04-24) |
| `feedback_hermes_active_preflight_check` | Hermes worker scripts call `pgrep -af 'git (rebase\|stash push\|commit\|merge\|reset\|checkout)'` and abort on hit |
| `feedback_multi_agent_commit_serialization` | Main session commits; subagents write only (Provider matrix execution row) |
| `feedback_parallel_agent_write_only_pattern` | Same as above; codified in `gsd-context-monitor.js` |
| `feedback_git_status_lock_storm` | `GIT_OPTIONAL_LOCKS=0 git commit` documented in scripted commit helpers |
| `feedback_cross_provider_review_payoff` | T2 provider matrix mandates Codex + Gemini parallel review |
| `feedback_always_adversarial_review_scale_depth` | Tier-based depth scaling in C2; never skip |
| `feedback_permission_gate_blocks_cross_review` | Single-author r3 with transparent provenance allowed; encoded in C2 fallback |
| `feedback_subagent_write_phantom` | Main session re-verifies subagent writes via `ls` before declaring success |
| `feedback_isolated_clone_dispatch_race` | Subagent in exec-clone checks for parallel-session landing on main workspace before writing |
| `feedback_attestation_enables_contradiction_detection` | `attest-plan-claims.sh` block (per #2405) used in every T2/T3 review |
| `feedback_worktree_isolation_large_repo_cost` | Default `Agent` calls to write-only-shared mode; reserve `isolation: worktree` for must-commit agents |
| `feedback_lane_result_path_outside_sandbox` | Lane results fall back to `docs/sessions/` when sandboxed paths blocked; emit ENV-MISMATCH banner |

**Promotion rule:** every row in this table becomes a one-line entry in `docs/standards/AI_ECOSYSTEM_DESIGN.md` Section "Memory-to-Surface Map" so the lessons stop being organizationally orphaned.

### F. Follow-up issues list (listed, NOT filed)

Per acceptance criterion #7, the plan enumerates downstream work without filing it. These issues will be filed only *after* user approval at `status:plan-approved`.

1. **`chore(ai-tools): refresh subscriptions.yaml with current Codex paid plan`** — fix the $156.75 → ~$356.75/mo drift; add Codex $200/mo entry. Cite `project_hermes_codex_quota` memory.
2. **`feat(ai-orchestration): add CODEX.md adapter file`** — mirror `CLAUDE.md` / `GEMINI.md`; ≤20 lines per `.claude/rules/coding-style.md`; cite memory's Codex-usage rules. Reconcile location with #2399's `.codex/CODEX.md` proposal.
3. **`chore(ai-config): audit + extend config/agents/{codex,gemini,hermes}/ to match the §B role matrix`** — existing minimal content needs auditing against the role matrix; gaps to be filled per provider (Codex: review-only enforcement in `config.toml`; Gemini: `git ls-files` precondition reference; Hermes: preflight contract in `SOUL.md` or `config.yaml.template`). Reference `config/agents/claude/` as the populated template.
4. **`feat(ai-orchestration): cost/quota model + monthly spend envelope`** (deferred from this plan) — concrete monthly target per provider with triggers that change routing; consume `config/ai-tools/usage-tracking.yaml`, `weekly-utilization.json`, `pricing.yaml`.
5. **`feat(ai-orchestration): migration plan for AI_ECOSYSTEM_DESIGN.md adoption`** (deferred from this plan) — day-1 / month-1 / quarter-1 incremental adoption schedule.
6. **`feat(ai-orchestration): workflow walkthrough — knowledge/wiki contribution`** — deferred from this plan; covers `feedback_llm_wiki_*` rules.
7. **`feat(ai-orchestration): workflow walkthrough — execution batch run`** — deferred from this plan; covers Hermes overnight batch + parallel-agent commit serialization.
8. **`chore(ai-tools): refresh agent-capability-scores.yaml from 2026-04/05 incident data`** — scores predate the codex/gemini sandbox lessons; re-score and reference incident memories.
9. **`feat(ai-orchestration): codify "when NOT to cross-review" rule in routing-config.yaml`** — add a tier-tier override field; cite `feedback_permission_gate_blocks_cross_review`.
10. **`feat(ai-orchestration): "Memory-to-Surface" map maintenance contract`** — quarterly refresh of the §E table as new memory lessons land; integrate with `learn-extended` skill.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/AI_ECOSYSTEM_DESIGN.md` | Durable design contract — promoted from this plan's §A–§E |
| Create | `docs/reports/2026-05-12-issue-2675-outcome-ledger.md` | §A standalone for cross-referencing |
| Create | `docs/reports/2026-05-12-issue-2675-provider-role-matrix.md` | §B standalone |
| Create | `docs/reports/2026-05-12-issue-2675-workflow-walkthroughs.md` | §C standalone |
| Create | `docs/reports/2026-05-12-issue-2675-failure-mode-design-contract.md` | §E standalone — anchor for follow-ups |
| Create | `docs/reports/2026-05-12-issue-2675-followup-issues-list.md` | §F as discrete file for the audit trail of "listed, not filed" |
| Update | `docs/plans/README.md` | Add new Plan Index row at line ~203 (most-recent-first ordering) |
| (no change yet) | `config/agents/provider-capabilities.yaml` | Updates deferred to follow-up issue #3 (after approval) |
| (no change yet) | `config/ai-tools/subscriptions.yaml` | Updates deferred to follow-up issue #1 |
| (no change yet) | `CODEX.md` | Creation deferred to follow-up issue #2 |
| (no change yet) | `routing-config.yaml` | Updates deferred to follow-up issue #9 |

**Note:** during execution (Step 6), only the `docs/standards/...`, `docs/reports/...`, and `docs/plans/README.md` paths land. Config-yaml and adapter-file changes are deliberately *not in scope of this plan* — they live in their own follow-up issues so each gets independent plan-review.

---

## TDD Test List

Governance plans deliver documents, not runtime code, so "tests" here are structural lints and content assertions. The execution phase runs them with `scripts/enforcement/` and a small bespoke checker.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_outcome_ledger_min_5_classes` | §A table has ≥5 work classes | `docs/reports/2026-05-12-issue-2675-outcome-ledger.md` | row count ≥5 |
| `test_provider_matrix_has_fallbacks` | §B table column "Fallback 1" populated for every primary | matrix MD | no row with empty Fallback 1 (except T1-by-design) |
| `test_walkthroughs_name_gate_checkpoints` | §C1 and §C2 each cite ≥2 existing repo gates | walkthroughs MD | each section grep matches `issue-planning-mode\|require-plan-approval\|require-cross-review\|cross-review-gate` |
| `test_failure_mode_contract_references_memories` | §E table cites ≥15 distinct feedback files | failure-mode MD | grep `^| \`feedback_` distinct-count ≥15 |
| `test_followups_listed_not_filed` | §F is markdown only; no `gh issue create` was run for these | git log + GitHub state | no new issues filed referencing #2675 as parent except this plan's own comment |
| `test_no_self_approve` | issue #2675 never bears `status:plan-approved` set by this session | `gh issue view 2675 --json labels` + session author audit | label only ever set by user, not in same session as draft |
| `test_no_no_verify` | no commits in this plan's branch used `--no-verify` | `git log --format=%B` grep | zero matches |
| `test_review_artifacts_exist` | all 3 provider review files exist before status:plan-review label | `ls scripts/review/results/2026-05-12-plan-2675-*` | 3 files present (or documented provider-failure substitute) |
| `test_readme_index_row_added` | `docs/plans/README.md` has new row for 2675 | `grep '^| 2675 ' docs/plans/README.md` | exactly 1 match |

---

## Acceptance Criteria

These mirror the issue body's acceptance criteria (#2675):

- [ ] Plan filed at `docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` using the canonical `docs/plans/_template-issue-plan.md` structure
- [ ] Resource Intelligence Summary cites ≥3 distinct sources including #2089, #2399, #2549 and the relevant `.claude/rules/` files (**this plan: 12 sources**)
- [ ] Outcome ledger names ≥5 work classes with measurable signals (**this plan: 6 classes in §A**)
- [ ] Provider role matrix exists with explicit fallbacks per class (**this plan: §B**)
- [ ] Reverse-prompted walk-throughs delivered for *issue planning* (§C1) and *adversarial review* (§C2) — each one names the gate checkpoints it passes through
- [ ] Failure-mode design contract references the feedback memories listed (§E references 20 distinct memories; threshold ≥15)
- [ ] Follow-up issue list enumerates downstream work (cost/quota model, migration plan, remaining walk-throughs) **without filing them yet** (§F: 10 issues listed)
- [ ] Adversarial review at T2 minimum (Claude + Codex + Gemini), per `feedback_always_adversarial_review_scale_depth`
- [ ] Issue marked `status:plan-review` after adversarial review; await user approval at `status:plan-approved` before any follow-up issues are filed or any settings change
- [ ] **No** `--no-verify` commits, **no** self-labeling `status:plan-approved`, **no** Codex-driven file writes (Codex review only, per sandbox limits)
- [ ] Plan TDD Test List checks all pass on the produced artifacts
- [ ] Review artifacts posted to `scripts/review/results/2026-05-12-plan-2675-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

**Wave 1 — dispatched 2026-05-12T16:34 via `scripts/review/plan-review-fanout.sh`** (artifacts at `scripts/review/results/2026-05-12-plan-2675-{claude,codex,gemini}.md`)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | rc=124 — SessionEnd hook (`scripts/session-lifecycle-hook.mjs`) cancelled. Harness regression, not a content verdict. |
| Codex  | UNAVAILABLE | rc=124 — stdin-hang on codex-cli 0.130.0 despite fanout wrapper passing `</dev/null`. Reproduces the 0.124.0 symptom pattern at a later version; possibly a related upstream regression. |
| Gemini | MAJOR — **REJECTED as overlay-blindness false-positive** | 8 findings, all claiming file-missing for files that **are tracked in git**. Verified by `git ls-files` against all 17 cited paths plus 3 cited dirs — every one exists. Memory line 40 (`feedback_gemini_sandbox_overlay_blindness`) explicitly prescribes this rejection. Finding 8 (memory files at `/tmp/llm-wiki/...`) is a hallucination — memory lives at `~/.claude/projects/.../memory/`, verified. |

**Overall result:** NOT-APPROVAL-READY — but for **insufficient cross-review signal**, not content defects.

- T2 minimum (`feedback_always_adversarial_review_scale_depth`) requires Codex + Gemini usable verdicts. Codex unavailable + Gemini rejected = **zero usable provider signal**.
- Per `feedback_codex_sustained_MAJOR_loop` analog (line 34) — when providers fail structurally, surface to user instead of auto-cycling.
- The two CLI failures are harness regressions warranting their own follow-up issues, independent of this plan's content.

Revisions made based on review:
- **Plan defect caught by self-review (not by any provider)**: §RIS gap #3 and the Evidence block incorrectly claimed `config/agents/{codex,gemini,hermes}/` were "empty skeletons"; `git ls-files` confirms 13 tracked files across the three. Corrected at three sites; §F follow-up issue #3 re-scoped from "populate" to "audit + extend".
- Count drift in §RIS for `scripts/review/results/`: 1,437 → 1,444 (drift since plan-draft; updated with timestamp note).
- No content revisions driven by provider findings (none were valid).

Synthesis artifact: `scripts/review/results/2026-05-12-plan-2675-summary.md` documents the rejection rationale.

---

## Risks and Open Questions

- **Risk: matrix concentration on Claude.** Claude legitimately owns planning + execution + comms because it is the only provider that drives tools in main session. This is a known single-point-of-failure on Claude quota. The cost/quota follow-up issue (§F #4) must address whether sustained Claude exhaustion has a credible fallback or whether the answer is "stop and wait."
- **Risk: failure-mode contract assumes memory file paths are stable.** Memory files live under `~/.claude/projects/.../memory/` per machine. The §E table treats them as authoritative; if a memory file is renamed or deleted, the §E row becomes a dangling reference. Mitigation: §F #10 "Memory-to-Surface map maintenance contract."
- **Risk: deferring config-yaml changes to follow-ups means the design is *declarative only* until those issues land.** A reader of this plan + `docs/standards/AI_ECOSYSTEM_DESIGN.md` would see the design, but `routing-config.yaml` would still reflect the old (correct-but-less-explicit) tier definitions. This is intentional — each follow-up gets its own plan-review — but could be confusing.
- **Risk: §C1 walkthrough hard-codes the current `issue-planning-mode` skill version (v3.1.0).** If the skill is updated mid-execution, the walkthrough may drift. Mitigation: walkthrough cites skill **by file path**, so updates flow through; structural tests in TDD list catch material drift.
- **Risk: cross-review for *this* plan is itself subject to the failure modes §E lists.** Codex CLI hang during this plan's own review would force fallback; Gemini overlay blindness on a freshly-written plan file could produce false MAJOR. Mitigation: T2 walkthrough already covers these.
- **Open: where to land `CODEX.md`?** The #2399 plan proposes `.codex/CODEX.md` (hidden directory pattern matching `.gemini/GEMINI.md`); the natural mirror of `CLAUDE.md` is repo-root `CODEX.md`. **The follow-up issue must resolve this with explicit user input.**
- **Open: should the failure-mode contract auto-generate from memory** (e.g., a script reads `~/.claude/projects/.../memory/feedback_*.md` and writes §E)? Lower drift risk but couples the repo to a user-machine path. Defer to §F #10 or a separate spike.
- **Open: should `docs/standards/AI_ECOSYSTEM_DESIGN.md` reference `docs/standards/AI_REVIEW_ROUTING_POLICY.md` as upstream, or supersede it?** Today neither is read; both are governance docs. Suggest reference, not supersede — the routing policy is operational, the design doc is strategic.

---

## Complexity: T3

**T3** — multi-surface governance work touching `docs/standards/`, `docs/reports/`, `docs/plans/README.md`, with ≥6 distinct deliverable artifacts, ≥21 cross-referenced memory feedback files, T2-minimum adversarial review across 3 providers, and 10 enumerated follow-up issues. Justifies T3 by *number of cross-surface dependencies* and *breadth of memory citation*, not by raw line count.
