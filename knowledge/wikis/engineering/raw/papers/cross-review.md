# 3-Agent Cross-Review

> How independent AI reviewers catch failures that self-review misses.
> Running in production since early 2025 -- before "adversarial review" became
> standard terminology in the AI engineering community.

---

## The Problem: Single-Agent Review Blindness

An agent reviewing its own work is structurally incapable of catching certain
classes of errors. This is not a model quality issue. It is a property of the
review context being contaminated by the authoring context.

When Claude writes a plan and then reviews that plan:
- The reasoning that justified each decision is still in context
- Assumptions made during authoring feel like established facts
- Missing requirements are invisible because they were never considered
- Edge cases the author did not think of remain unconsidered

This is the AI equivalent of a developer reviewing their own PR. Sometimes they
catch typos. They almost never catch architectural misalignment.

### The Evidence

Before cross-review enforcement:
- Plans shipped with unstated assumptions about file paths
- Implementation diverged from plans because the same agent rationalized the drift
- Review compliance was 4% (issue #2012) -- agents skipped review entirely when possible
- The few self-reviews that did happen caught surface issues (formatting, naming) but
  missed structural problems (wrong approach, missing edge cases, scope creep)

---

## The Solution: 3 Independent Reviewers

Three different AI agents (Claude, Codex, Gemini) review every plan AND every
artifact. Each reviewer operates in a fresh context, without access to the
authoring session's reasoning.

### Provider Roles

Defined in `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (issue #1515):

| Provider | Primary Role | Review Strengths |
|----------|-------------|-----------------|
| Claude Code | Orchestrator + reviewer | Task framing, scope verification, plan coherence, cross-file consistency |
| Codex | Implementation worker + reviewer | Code correctness, test coverage, implementation bugs, diff analysis |
| Gemini | Adversarial reviewer | Architecture review, large-context research, plan completeness, requirement gaps |

### The Two-Stage Review Model

Cross-review happens at two distinct stages, not just one:

**Stage 1: Plan Review**
```
Claude creates implementation plan
    |
    v
Codex reviews plan --> finds implementation concerns
    |                   "This approach won't handle concurrent access"
    v
Gemini reviews plan --> finds architectural concerns
    |                   "This duplicates logic already in scripts/enforcement/"
    v
Claude updates plan based on both reviews
    |
    v
User approves updated plan --> .planning/plan-approved/<issue>.md
```

**Stage 2: Artifact Review**
```
Codex implements the approved plan
    |
    v
Claude reviews implementation --> checks against plan
    |                             "The plan said 7 checkpoints but only 5 are implemented"
    v
Gemini reviews implementation --> checks architecture
    |                             "This hook should use the same protocol as cross-review-gate.sh"
    v
Issues resolved --> artifact ships
```

Both stages are mandatory. The review routing policy states: "Plans get adversarial
review by ALL agents by default. Code and deliverable artifacts get adversarial
review by ALL agents before completion by default."

---

## Why Different Agents Catch Different Things

Each AI model has characteristic blind spots and strengths. These are not random --
they are consistent enough to be exploitable.

### Observed Specializations

| Failure mode | Best caught by | Why |
|-------------|---------------|-----|
| Plan-implementation drift | Claude | Maintains the plan context, can cross-reference |
| Off-by-one errors in code | Codex | Strong at line-level code analysis |
| Missing edge cases in plan | Gemini | Large context window, good at "what about..." questions |
| Scope creep (doing more than asked) | Any independent reviewer | Fresh context = no investment in existing approach |
| Incorrect file path references | Codex | Good at verifying paths exist in the codebase |
| Architectural inconsistency | Gemini | Can hold entire repo structure in context |
| Unstated assumptions | Any independent reviewer | Author's assumptions are not in the reviewer's context |
| Test coverage gaps | Codex | Specifically good at TDD and test analysis |
| Convention violations | Claude | Has deepest context on repo conventions |

### Why Independence Matters

The key word is "independent." A reviewer operating in the same session as the author
is not independent -- they share the same context contamination. Cross-review works
because:

1. **Fresh context**: Each reviewer starts with only the artifact and the plan, not the
   authoring session's history of dead ends, retries, and rationalizations.
2. **Different training**: Claude, Codex, and Gemini have different training data,
   different model architectures, and different optimization targets. Their blind spots
   do not perfectly overlap.
3. **No sunk cost**: A reviewer with no investment in the current approach is more
   willing to say "start over" than the author who spent 2 hours building it.

---

## Enforcement: How Cross-Review Is Guaranteed

Cross-review is not voluntary. It is enforced at Level 3 (Hook) -- the strongest
enforcement level in the system.

### The Cross-Review Gate

**File:** `.claude/hooks/cross-review-gate.sh` (issues #1537, #1515)

This PreToolUse hook fires on every Bash tool call. It gates four operations:

| Gate | Trigger | What it checks |
|------|---------|---------------|
| PR creation | `gh pr create` | Runs `scripts/enforcement/require-cross-review.sh` -- blocks if no review evidence |
| Ship/verify | `gsd-ship`, `gh pr merge` | Runs `scripts/enforcement/require-verify-artifacts.sh` -- blocks without TDD + review |
| Plan execution | `gsd-execute-phase` | Runs `scripts/enforcement/require-plan-review.sh` -- blocks without plan review |
| TDD pairing | `git commit` | Runs `scripts/enforcement/require-tdd-pairing.sh` -- warns if code lacks paired tests |

### Routing Recommendation

When the cross-review gate fires, it does not just block -- it recommends who should
review. The `scripts/ai/review_routing_gate.py` script analyzes the current diff and
produces a routing recommendation:

```json
{
  "reviewers": ["codex", "gemini"],
  "priority": "high",
  "triggers_matched": ["engineering", "enforcement-script"]
}
```

This recommendation is surfaced to the agent via stderr:
```
[review-routing] Recommended: codex, gemini | Priority: high | Triggers: engineering
```

The agent then knows exactly which reviewers to engage and why.

### Review Evidence Sources

The gate checks four evidence sources (in order):

1. **Review results directory**: `scripts/review/results/` has files from today
2. **Planning REVIEWS.md**: `.planning/phases/*/REVIEWS.md` modified today
3. **Claude reports**: `.claude/reports/*review*` modified today
4. **Git commit messages**: Recent commits mention review, codex, gemini, or adversarial

If any source has evidence, the gate passes. If none do, the gate blocks.

---

## The Review Workflow in Practice

### For Overnight Batch Runs

Every overnight terminal prompt includes a mandatory cross-review step at the end:

```
IMPLEMENTATION CROSS-REVIEW (mandatory):
- After the implementation commit is pushed, capture the committed diff
- Write a self-contained adversarial review prompt
- Run Codex review on the committed diff
- For architecture-heavy streams, also run Gemini review
- If review returns MAJOR findings, fix, recommit, push, rerun reviewer(s)
- Post a brief GH issue comment summarizing implementation and review verdict
```

This is embedded in the skill at
`.claude/skills/software-development/overnight-parallel-agent-prompts/SKILL.md`.

### For Interactive Sessions

During interactive sessions, the GSD framework provides review commands:

```bash
# Request cross-review from Codex
/gsd:review --phase <N> --codex

# Request cross-review from Gemini
/gsd:review --phase <N> --gemini

# Full adversarial review (all agents)
/gsd:review --phase <N> --all
```

### Review Verdicts

Reviews produce one of three verdicts:

| Verdict | Meaning | Action required |
|---------|---------|----------------|
| APPROVE | No issues found | Proceed to ship |
| MINOR | Small issues, non-blocking | Fix recommended but not required |
| MAJOR | Significant issues found | Must fix before shipping |

MAJOR findings require resolution and re-review. This is enforced: the review gate
checks for review evidence, and MAJOR findings without resolution do not count as
passing evidence.

---

## Optional Review Reduction

The default is 3-agent review for everything. Reduction is allowed only in specific
cases, per the routing policy:

| Case | Allowed adjustment |
|------|--------------------|
| User requests faster pass | Claude may reduce to 2-agent review, must document reason |
| Provider unavailable / quota exhausted | Continue with remaining agents, record missing reviewer |
| Purely clerical change | Claude may waive one reviewer with explicit note |

Reduction is never automatic. It requires explicit decision and documentation.

---

## Pre-Push Review Gate

Beyond the PreToolUse hook, there is also a pre-push review gate that fires on
`git push`:

**File:** `scripts/enforcement/require-review-on-push.sh` (268 lines)

This script:
1. Classifies each commit in the push range (feature/fix vs. docs/chore)
2. Checks for review evidence (4 sources, same as cross-review gate)
3. In strict mode (default since #1839): blocks push if feature commits lack evidence
4. Logs every execution to `logs/hooks/review-gate-latency.jsonl`
5. Logs every bypass to `logs/hooks/review-gate-bypass.jsonl`

The pre-push gate and the PreToolUse cross-review gate are complementary:
- PreToolUse gate: fires inside Claude Code sessions, blocks PR creation
- Pre-push gate: fires on `git push` from any source (terminal, CI, agent)

Together they form a defense-in-depth approach where review cannot be skipped
regardless of the execution path.

---

## The Compliance Dashboard

The compliance dashboard (`scripts/enforcement/compliance-dashboard.sh`) tracks
cross-review effectiveness:

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

This dashboard runs via nightly cron (`scripts/enforcement/compliance-cron.sh`) and
auto-creates GitHub issues when compliance drops below the 80% threshold.

Engineering-critical commits are tracked separately with their own compliance rate,
ensuring that the highest-stakes work always has review evidence.

---

## What Cross-Review Catches That Self-Review Does Not

Real examples from this repository:

1. **Session governance implementation (#1839)**: Codex review caught that the
   tool-call ceiling threshold in governance-checkpoints.yaml was set to 5000 while
   the hook was configured for 200 -- a configuration mismatch that would have made
   the YAML config misleading.

2. **Review routing policy (#1515)**: Gemini review identified that the initial
   policy had Gemini as "trigger-only" (only reviewing when specific triggers matched),
   but the user's stated preference was all-agent review at both stages. The policy
   was updated to make Gemini a default reviewer.

3. **Enforcement gradient**: Cross-review of the enforcement scripts identified
   that advisory mode (REVIEW_GATE_STRICT=0) was the default, contradicting the
   stated goal of strict enforcement. This was promoted to strict-by-default in
   phase 2c of #1839.

4. **Overnight batch prompts**: Review of the overnight prompt skill caught multiple
   failure modes that only became apparent when running 5+ terminals:
   `index.lock` errors from concurrent pushes, stdin handling issues with
   `claude -p`, and governance hooks blocking final writes in long sessions.

---

## Scaling Cross-Review

### Current State
- 3 agents (Claude, Codex, Gemini) review by default
- Review at both plan and artifact stages
- Enforced at Level 3 (Hook) for PR creation and push

### Scaling Considerations
- **More agents**: As new AI agents become available, they can be added to the
  review rotation without changing the architecture -- just add them to the routing
  policy and update the gate scripts.
- **Specialized reviewers**: Domain-specific review (e.g., security review, performance
  review) can be routed to the agent with the strongest capabilities in that domain.
- **Review quality tracking**: The compliance dashboard can be extended to track
  not just whether review happened, but whether reviews caught real issues.

---

## Key Takeaway

Cross-review works because it exploits the structural property that independent
reviewers have non-overlapping blind spots. A plan reviewed by Claude, Codex, and
Gemini has been examined through three different lenses, with three different sets
of assumptions, in three fresh contexts. The probability that all three miss the
same issue is far lower than the probability that any single one misses it.

The enforcement is what makes it real. Without the cross-review gate hook, review
compliance was 4%. With it, every PR creation attempt is gated on review evidence.
The combination of independent reviewers and technical enforcement creates a quality
floor that no single agent can achieve alone.

---

## Related

- [compound-engineering.md](compound-engineering.md) -- Lesson 5 overview
- [enforcement-over-instruction.md](enforcement-over-instruction.md) -- Why enforcement makes review reliable
- [multi-agent-parity.md](multi-agent-parity.md) -- How all agents have the context to do effective review
- [orchestrator-worker.md](orchestrator-worker.md) -- Context isolation that enables independent review
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` -- The formal routing policy
- `.claude/hooks/cross-review-gate.sh` -- The enforcement hook
- `scripts/enforcement/require-review-on-push.sh` -- Pre-push review gate
- `scripts/enforcement/require-cross-review.sh` -- PR creation review gate
- `scripts/enforcement/compliance-dashboard.sh` -- Compliance tracking
- `scripts/ai/review_routing_gate.py` -- Routing recommendation engine
- #1515 -- AI review routing policy
- #1537 -- Cross-review enforcement
- #2012 -- The 4% compliance audit
- #1839 -- Session governance (strict review defaults)
