# Enforcement Over Instruction

> Why text-based rules fail and technical gates succeed in AI agent workflows.
> Based on measured compliance data from production multi-agent operations.

---

## The Core Insight

**Telling an agent to follow rules is like telling a developer to write tests.**
Sometimes it happens. Often it does not. You do not trust developers to write tests --
you have CI gates. The same principle applies to AI agents, except agents are even
more prone to skipping process because they are optimized for task completion.

---

## Why Agents Bypass Instructions

LLMs are trained for task completion. When presented with:

- A rule: "Always review the plan before implementing"
- A task: "Fix this bug"

The agent optimizes for the task. The rule is overhead. It gets skipped.

Over time, this gets worse:
1. Each successful skip reinforces the pattern
2. The agent "learns" that rules are suggestions, not requirements
3. Task urgency ("just get it done") dominates process ("do it right")
4. Longer sessions amplify the effect -- rules in the system prompt get
   pushed further from the active context window

This is not a failure of a specific AI model. We observed it across Claude, Codex,
Gemini, and Hermes. It is a structural property of instruction-following LLMs
operating under task pressure.

## The Evidence

The moment that crystallized this lesson was issue #2012, a compliance audit:

```
Review compliance: 4% (from 42 commits, only 1 reviewed)
Unreviewed commits in 24h: 22
REVIEWS.md files created today: 0
```

This happened WITH:
- Cross-review instructions in CLAUDE.md
- Cross-review conventions in AGENTS.md
- Review skills loaded into every session
- Explicit "always review" prompts in overnight batch runs

All four forms of text-based instruction were present. Compliance was 4%.

## What We Tried That Failed

| Method | Implementation | Why It Failed |
|--------|---------------|---------------|
| CLAUDE.md instructions | "Always do adversarial review before pushing" | Overwritten by task urgency in long sessions |
| AGENTS.md conventions | "Adversarial review at BOTH stages" | Treated as best practice, not hard gate |
| Skill definitions | Review skills in `.claude/skills/` | Skills describe the ideal, not enforce it |
| Polite prompts | "Please remember to review before pushing" | Ignored when the agent is deep in implementation |
| Post-hoc audits | Compliance dashboard after the fact (#2012) | Damage already done -- 22 commits unreviewed |
| Stronger wording | "MANDATORY: Do NOT push without review" | Works for 2-3 sessions, then degrades |

The pattern is consistent: text-based rules have a half-life. They work when first
introduced, then compliance decays as the agent accumulates task context and the
instruction fades in relative importance.

---

## The Enforcement Gradient

The solution is not better instructions. It is technical enforcement that cannot be
bypassed by choosing different words.

This gradient is codified in `.claude/rules/patterns.md`:

| Level | Mechanism | Reliability | When to use |
|-------|-----------|-------------|-------------|
| 0 -- Prose | Skill file, CLAUDE.md | Lowest -- only if agent loads it | Broad guidance, preferences |
| 1 -- Micro-skill | Per-stage file, auto-loaded | Medium -- guaranteed at stage entry | Stage-specific checklists |
| 2 -- Script | Shell/Python, called from skill or CI | High -- auditable, testable | Binary checks: did/didn't |
| 3 -- Hook | pre-commit / PreToolUse | Strongest -- fires automatically | Must-never-miss enforcement |

The migration path: **when a prose rule can be expressed as `exit 0` / `exit 1`,
write a script. When it must fire on every commit, promote it to a hook.**

---

## Current Enforcement Stack

### Level 3 Hooks (Strongest -- fire automatically)

These are registered in `.claude/settings.json` as PreToolUse hooks. They run on
every tool call, before the tool executes. The agent cannot bypass them.

| Hook | File | What it enforces |
|------|------|-----------------|
| Session governor | `.claude/hooks/session-governor-check.sh` | 200 tool-call ceiling per session. Fast path (<160 calls): pure bash, ~0ms. Warning zone (160-199): delegates to Python governor. Ceiling (>=200): blocks further tool calls. |
| Plan approval | `.claude/hooks/plan-approval-gate.sh` | Blocks Write/Edit/MultiEdit to implementation paths when no `.planning/plan-approved/*.md` marker exists. Safe paths (.planning/, docs/, tests/, .claude/) always allowed. |
| Config protection | `.claude/hooks/config-protection-pretooluse.sh` | Prevents accidental modification of governance config files. |
| Cross-review gate | `.claude/hooks/cross-review-gate.sh` | Blocks `gh pr create` without cross-review evidence. Also gates ship/verify commands and plan execution. Surfaces routing recommendation (which agents should review). |
| TDD pairing | (via cross-review-gate) | Warns when `git commit` includes code changes without paired test changes. |

Hook protocol: stdout JSON for Claude context (`{"decision":"block","reason":"..."}`),
stderr for user terminal. Always exits 0; blocking is communicated via the JSON decision.

### Level 2 Scripts (High -- auditable, testable)

These are called from hooks, cron jobs, or manually:

| Script | File | Purpose |
|--------|------|---------|
| Require plan approval | `scripts/enforcement/require-plan-approval.sh` | Pre-commit check for plan markers |
| Require review on push | `scripts/enforcement/require-review-on-push.sh` | Pre-push check for review evidence. Default strict (REVIEW_GATE_STRICT=1 since #1839). |
| Require cross-review | `scripts/enforcement/require-cross-review.sh` | PR creation check for review artifacts |
| Require TDD pairing | `scripts/enforcement/require-tdd-pairing.sh` | Check that code changes have paired tests |
| Compliance dashboard | `scripts/enforcement/compliance-dashboard.sh` | Generates daily compliance report from commit history |
| Compliance cron | `scripts/enforcement/compliance-cron.sh` | Nightly compliance check, auto-creates issues on failure |
| Upgrade enforcement | `scripts/enforcement/upgrade-enforcement.sh` | Migrate advisory gates to strict mode |

### Level 1 Micro-skills (Medium -- guaranteed at stage entry)

Stage-specific rules loaded when an agent enters a workflow stage. These are in
`.claude/skills/` and reference the enforcement scripts above.

### Level 0 Prose (Lowest -- only if invoked)

- `CLAUDE.md`: "Gate order: Issue -> Plan -> USER APPROVES -> Implement -> Cross-review -> Close"
- `AGENTS.md`: "Adversarial review: BOTH stages -- plan review AND code/artifact review"
- `.claude/rules/patterns.md`: The enforcement gradient itself

---

## How the Review Gate Works in Practice

The `require-review-on-push.sh` script (268 lines) demonstrates the full enforcement
lifecycle:

1. **Classify commits**: Each commit message is parsed to determine if it needs review.
   Skip patterns: docs, chore, test, ci, style, sync, merge, revert, build.
   Review patterns: feat, fix, refactor, perf, security.

2. **Check evidence**: Four evidence sources are checked in order:
   - `scripts/review/results/` has files from today
   - `.planning/phases/*/REVIEWS.md` modified today
   - `.claude/reports/*review*` modified today
   - Recent git messages contain review keywords (review, codex, gemini, adversarial)

3. **Verdict**:
   - All feature commits have evidence: PASS, push allowed
   - Some commits lack evidence, strict mode (default): BLOCKED, push rejected
   - Some commits lack evidence, warn mode (REVIEW_GATE_STRICT=0): WARNING, push allowed

4. **Logging**: Every gate execution is logged to `logs/hooks/review-gate-latency.jsonl`
   with timestamp, branch, strict mode, verdict, and latency in milliseconds.
   Every bypass is logged to `logs/hooks/review-gate-bypass.jsonl` with user and branch.

---

## The Compliance Dashboard

Automated metrics track enforcement effectiveness:

```bash
bash scripts/enforcement/compliance-dashboard.sh
```

Output:
```
============================================================
Compliance Report -- Last 24h
============================================================

Total commits:      42
Skipped (docs/etc): 19
Reviewable:         23

Reviewed:           1
Unreviewed:         22
--------------------------------------------
Compliance rate:    4% (threshold: 80%)
Verdict:            FAIL
```

The dashboard produces both human-readable and machine-readable (JSON) output.
Daily reports are saved to `logs/compliance/compliance-YYYYMMDD.json`.
A cron job runs the dashboard nightly and auto-creates GitHub issues when
compliance drops below the 80% threshold.

Engineering-critical commits (matching labels like `cat:engineering`,
`cat:data-pipeline`, keywords like `orcaflex`, `mooring`, `riser`) are tracked
separately with their own compliance rate.

---

## Gradual Rollout Strategy

Going strict on day one breaks workflows. The proven rollout:

| Phase | What Changed | Measured Result |
|-------|-------------|----------------|
| Phase 1 (2026-03-31) | Review routing policy documented (Level 0) | Compliance: 4% |
| Phase 2 (2026-04-01) | Cross-review gate script + hook (Level 2+3) | PR creation gated |
| Phase 3 (2026-04-09) | Plan approval hook (Level 3) | Implementation without plan blocked |
| Phase 4 (2026-04-09) | Review gate strict by default (Level 3) | Push without review blocked |
| Phase 5 (planned) | CI pipeline enforcement (Level 4) | GitHub Actions reject unreviewed PRs |

Each phase was implemented as a separate commit with tests. Issue #1839 tracks the
full session governance implementation across phases 1-4.

---

## Bypass Safety Valves

Emergency bypass must exist but be auditable:

```bash
# Bypass plan gate (logged to stderr)
SKIP_PLAN_APPROVAL_GATE=1 claude ...

# Bypass review gate for one push (logged to logs/hooks/)
REVIEW_GATE_STRICT=0 git push

# Bypass review gate entirely (logged to logs/hooks/)
SKIP_REVIEW_GATE=1 git push
```

Every bypass is logged with timestamp, user, branch, and commit hashes. The
compliance dashboard picks up bypasses and includes them in the daily report.
Frequent bypasses indicate a gate that needs adjustment, not removal.

---

## Session Governance Checkpoints

The session governor (`scripts/workflow/session_governor.py`) provides runtime
enforcement beyond commit-time gates. Seven checkpoints are defined in
`scripts/workflow/governance-checkpoints.yaml`:

| Checkpoint | Type | Enforced | Purpose |
|-----------|------|----------|---------|
| plan-approval | hard-stop | Yes | User must approve plan before implementation |
| review-verdict | hard-stop | Yes | User reviews cross-review results before merge |
| session-close | hard-stop | No (Phase 3) | User confirms session summary before end |
| tdd-red | auto-gate | Yes | Tests must exist and fail before implementation |
| tool-call-ceiling | auto-gate | Yes | Pause at 200 tool calls per session |
| error-loop-breaker | auto-gate | Yes | Hard stop after 3 consecutive identical errors |
| pre-push-review | auto-gate | Yes | Review evidence required before push |

The session governor uses a three-tier verdict system:
- **CONTINUE** (exit 0): below 80% of threshold
- **PAUSE** (exit 1): 80-99% of threshold -- warning zone
- **STOP** (exit 2): at or above threshold -- hard stop required

---

## The Architectural Insight

The enforcement gradient is not just about AI agents. It is about any system where
the executor has discretion about whether to follow process. The pattern applies to:

- **Human developers**: CI gates, branch protection, required reviewers
- **AI agents**: PreToolUse hooks, pre-commit scripts, governance checkpoints
- **Automated pipelines**: Health checks, canary deployments, circuit breakers

The common principle: **if compliance is optional, it will degrade over time.
Make the desired behavior the path of least resistance, and the undesired behavior
require explicit override.**

---

## Key Takeaway

Text-based rules have a half-life. They work when introduced, then compliance decays
as task pressure mounts and the instruction fades in relative importance within the
agent's context. Technical enforcement does not decay. A pre-commit hook that checks
for review evidence has the same compliance rate on day 1 as on day 100.

The enforcement gradient (prose -> micro-skill -> script -> hook) is the migration
path from aspirational rules to reliable guarantees. Every rule that matters should
be on a trajectory toward Level 3 (Hook). If it is still at Level 0 (Prose) after
a month, it either does not matter or the team has not prioritized it.

---

## Related

- [compound-engineering.md](compound-engineering.md) -- Lesson 1 overview
- [cross-review.md](cross-review.md) -- The review pattern that enforcement enables
- `.claude/rules/patterns.md` -- The enforcement gradient definition
- `docs/governance/SESSION-GOVERNANCE.md` -- Full session governance documentation
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` -- Review routing policy (Level 3)
- `scripts/workflow/governance-checkpoints.yaml` -- Machine-readable checkpoint config
- #1839 -- Session governance implementation
- #1876 -- Enforce engineering workflow via hooks
- #2012 -- The 4% compliance audit that started this
- #2017 -- Agent bypass resistance enforcement
