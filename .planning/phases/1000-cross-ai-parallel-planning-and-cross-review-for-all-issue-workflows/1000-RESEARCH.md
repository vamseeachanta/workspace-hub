# Phase 1000: Cross-AI Parallel Planning and Cross-Review — Research

**Researched:** 2026-03-29
**Domain:** Multi-AI orchestration, bash parallel process management, PLAN.md structured merge
**Confidence:** HIGH

## Summary

This phase extends two existing GSD capabilities — planning and review — with parallel multi-AI modes. The codebase already has all the building blocks: per-provider CLI invocation scripts (`claude-review.sh`, `codex-review.sh`, `gemini-review.sh`), a sequential cross-review loop (`cross-review-loop.sh`), a review skill (`review.md`) that already invokes all three CLIs and produces `REVIEWS.md`, and a planning skill (`plan-phase.md`) that spawns a single `gsd-planner` agent. The work is integration, not invention — wire existing invocation patterns into parallel dispatch, add a structured plan merge step, and expose mode toggles.

All three CLI tools are confirmed available on the target machine: Claude Code 2.1.87, Codex CLI 0.116.0, Gemini CLI 0.35.1. Supporting tools (jq 1.7, Node 22.22.1) are also available. The existing `behavior-contract.yaml` already defines the Route A/B/C complexity classification and `two_of_three_approve` semantics needed for tiered gates. The `agent-delegation-templates.md` needs a `phase_0_plan` block for each task type. The `routing-config.yaml` needs cross-plan/cross-review mode flags per tier.

**Primary recommendation:** Build `cross-plan.sh` as a thin bash dispatcher that backgrounds three CLI plan calls, collects outputs, then calls Claude as the synthesis agent to merge plans. Modify `review.md`'s `invoke_reviewers` step from sequential to parallel using bash `&` + `wait`. Add mode detection via `routing-config.yaml` flags so both capabilities activate based on route tier.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Wire into existing GSD lifecycle (discuss -> plan -> execute -> review) as optional modes, not a parallel system. The GSD framework is the sole workflow engine; `behavior-contract.yaml` defines the canonical 6-stage flow.
- **D-02:** Two new capabilities: (a) cross-planning at plan-phase stage, (b) parallel cross-review at review stage. Both are mode toggles on existing skills, not new standalone tools.
- **D-03:** True parallel planning — all three AIs receive the same phase spec + CONTEXT.md and independently produce a PLAN.md. A designated merge agent (Claude, given architecture strength) synthesizes the three into a final plan.
- **D-04:** Adopt ensemble-synthesis with structured diff pre-filtering: parse plans into structured sections, auto-merge agreed elements, only call a synthesis LLM for divergent sections (LangGraph map-reduce pattern adapted to PLAN.md template).
- **D-05:** Each provider plans in isolation (no visibility into others' plans) to avoid anchoring bias.
- **D-06:** Switch review invocation from sequential to true parallel — use bash `&` background processes with `wait`. Rate limits are independent across providers (Anthropic, OpenAI, Google APIs). The sequential constraint in current `review.md` is overly conservative.
- **D-07:** Expected wall-clock improvement: ~65% faster reviews (3 sequential -> 1 parallel batch, gated by slowest provider).
- **D-08:** Tiered review gates based on task complexity, not universal 2-of-3. Route classification uses existing Route A/B/C from behavior-contract.yaml: Route A (simple) = Single-provider review; Route B (medium) = 2-of-3 cross-review; Route C (complex) = Full 3-of-3 with synthesis.
- **D-09:** For cross-planning: always use all 3 providers (the value is in diverse perspectives). For cross-review: tier by complexity per D-08.
- **D-10:** Reuse existing `two_of_three_approve` semantics from behavior-contract.yaml: 2+ APPROVE/MINOR passes; 1 MAJOR + 2 APPROVE still fails; NO_OUTPUT + 2 APPROVE = CONDITIONAL_PASS.
- **D-11:** Extend `scripts/development/ai-review/cross-review-loop.sh` for parallel invocation mode. Create new `scripts/development/ai-plan/cross-plan.sh` for planning dispatch.
- **D-12:** Update `agent-delegation-templates.md` with `phase_0_plan` block for all task types.
- **D-13:** Update GSD skills (`plan-phase.md`, `review.md`) to detect cross-plan/cross-review mode from config and invoke accordingly.

### Claude's Discretion
- Exact synthesis prompt for merging divergent plan sections
- Structured diff algorithm for plan comparison (regex parsing vs JSON intermediate)
- Temp file handling for parallel plan collection
- Progress display during parallel invocations

### Deferred Ideas (OUT OF SCOPE)
- Cross-AI parallel execution (not just planning/review) — separate phase
- Auto-selection of synthesis agent based on task type — future enhancement
- Cost tracking dashboard for cross-AI operations — future phase
</user_constraints>

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|-------------|---------|---------|--------------|
| Claude Code CLI | 2.1.87 | Planning agent + synthesis merge agent + review agent | Available on machine; strongest at architecture per behavior-contract.yaml |
| Codex CLI | 0.116.0 | Planning agent + review agent | Available on machine; strongest at focused code review |
| Gemini CLI | 0.35.1 | Planning agent + review agent | Available on machine; strongest at research/alternative approaches |
| bash (background processes) | 5.x | Parallel invocation via `&` + `wait` | Standard POSIX; no dependency; battle-tested pattern |
| jq | 1.7 | JSON manipulation for plan section comparison | Already used in `cross-review-loop.sh` for iteration records |
| Node.js | 22.22.1 | GSD toolchain (`gsd-tools.cjs`) | Existing runtime for all GSD infrastructure |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| diff/comm | system | Text comparison for plan section auto-merge | When detecting agreed vs. divergent plan sections |
| mktemp | system | Temp directory for parallel plan collection | Each cross-plan invocation creates isolated temp workspace |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| bash `&` + `wait` | GNU parallel | Adds dependency; `&`+`wait` is sufficient for 3 processes |
| jq for section comparison | Node.js script | jq is already a dependency; Node script would need new code but could handle complex PLAN.md parsing better |
| Regex plan parsing | JSON intermediate representation | Regex is fragile if PLAN.md format evolves; JSON IR is more robust but higher effort |

## Architecture Patterns

### Recommended Project Structure
```
scripts/development/
├── ai-review/                        # EXISTING — extend
│   ├── cross-review-loop.sh          # MODIFY: add --parallel flag + parallel invocation mode
│   ├── claude-review.sh              # UNCHANGED
│   ├── codex-review.sh               # UNCHANGED
│   └── gemini-review.sh              # UNCHANGED
├── ai-plan/                          # NEW directory
│   └── cross-plan.sh                 # NEW: dispatch 3 parallel plan invocations, collect, merge

.claude/get-shit-done/workflows/
├── plan-phase.md                     # MODIFY: add cross-plan mode detection + dispatch
├── review.md                         # MODIFY: invoke_reviewers step → parallel mode

.claude/docs/
├── agent-delegation-templates.md     # MODIFY: add phase_0_plan blocks

config/agents/
├── behavior-contract.yaml            # MODIFY: add cross_plan section to task_type_matrix entries
├── routing-config.yaml               # MODIFY: add cross_plan + cross_review mode flags per tier
```

### Pattern 1: Parallel CLI Dispatch with `&` + `wait`
**What:** Background three CLI processes, capture PID and output file, wait for all, then process results.
**When to use:** Both cross-planning and cross-review parallel invocation.
**Example:**
```bash
# Source: Existing review.md invocation patterns + standard bash parallelism
TMPDIR=$(mktemp -d "/tmp/gsd-cross-plan-XXXXXX")

# Dispatch all three in parallel — each writes to its own output file
claude -p "$(cat "$PROMPT_FILE")" --no-input > "$TMPDIR/claude-plan.md" 2>"$TMPDIR/claude-err.log" &
PID_CLAUDE=$!

codex exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" > "$TMPDIR/codex-plan.md" 2>"$TMPDIR/codex-err.log" &
PID_CODEX=$!

gemini -p "$(cat "$PROMPT_FILE")" > "$TMPDIR/gemini-plan.md" 2>"$TMPDIR/gemini-err.log" &
PID_GEMINI=$!

# Wait for all, capture exit codes
wait $PID_CLAUDE; EC_CLAUDE=$?
wait $PID_CODEX; EC_CODEX=$?
wait $PID_GEMINI; EC_GEMINI=$?

# Process results — skip any that failed
for provider in claude codex gemini; do
  eval EC=\$EC_$(echo $provider | tr '[:lower:]' '[:upper:]')
  if [[ $EC -ne 0 ]]; then
    echo "WARNING: $provider failed (exit $EC)" >&2
  fi
done
```

### Pattern 2: Structured Plan Section Extraction for Merge
**What:** Parse PLAN.md files into sections (frontmatter, objective, tasks, must_haves, verification) to enable auto-merge of agreed sections and LLM synthesis of divergent sections.
**When to use:** After collecting three parallel plans, before creating the final merged plan.
**Example:**
```bash
# Extract sections from each plan using awk or sed
# Frontmatter: lines between first and second ---
# Objective: content under <objective>...</objective>
# Tasks: content under <tasks>...</tasks>
# Must-haves: content under <must_haves>...</must_haves>

extract_section() {
  local file="$1" tag="$2"
  sed -n "/<${tag}>/,/<\/${tag}>/p" "$file" | sed '1d;$d'
}

# Compare sections across three plans
# If all three agree (within tolerance) → auto-merge
# If divergent → pass to synthesis LLM
```

### Pattern 3: Synthesis Prompt for Divergent Sections
**What:** When plans diverge on a section, Claude synthesizes the best approach from all three.
**When to use:** After auto-merge identifies divergent sections.
**Example:**
```markdown
# Plan Synthesis Prompt

You are merging three independently-created plans for Phase {N}: {name}.

## Agreed Elements (already merged)
{auto-merged sections}

## Divergent Section: {section_name}

### Claude's version:
{claude_section}

### Codex's version:
{codex_section}

### Gemini's version:
{gemini_section}

## Instructions
Synthesize the best approach. Prefer:
1. The most specific and actionable version
2. The version with better task decomposition
3. Combined insights where approaches complement each other

Output the merged section in the same PLAN.md format.
```

### Pattern 4: Mode Detection via routing-config.yaml
**What:** Cross-plan and cross-review modes are enabled per route tier, read at runtime from config.
**When to use:** In `plan-phase.md` and `review.md` at dispatch time.
**Example:**
```yaml
# Addition to routing-config.yaml
cross_modes:
  cross_plan:
    SIMPLE: false      # Route A: single planner
    STANDARD: false    # Route B: single planner (optional)
    COMPLEX: true      # Route C: all 3 plan independently
    REASONING: true    # Full ensemble
  cross_review:
    SIMPLE: false      # Route A: single-provider review
    STANDARD: true     # Route B: 2-of-3 cross-review
    COMPLEX: true      # Route C: full 3-of-3 with synthesis
    REASONING: true    # Full 3-of-3
```

### Anti-Patterns to Avoid
- **Writing to same output file from parallel processes:** Each background process MUST write to its own uniquely-named temp file. Never share stdout across concurrent processes.
- **Polling for completion instead of using `wait`:** The `wait $PID` idiom blocks until the specific process completes and gives you the exit code. Do not use sleep loops.
- **Hardcoding provider CLI commands:** The existing per-provider scripts (`claude-review.sh`, `codex-review.sh`, `gemini-review.sh`) already abstract CLI invocation. For reviews, use them. For planning, follow the same CLI invocation patterns from `review.md` lines 121-131.
- **Passing one plan's output as context to another plan's prompt:** This violates D-05 (isolation to avoid anchoring bias). Each planner gets only the phase spec + CONTEXT.md.
- **Running synthesis before checking for agreement:** D-04 requires auto-merge of agreed elements first. Only divergent sections go to the synthesis LLM. Calling the synthesis LLM on the entire plan wastes tokens and introduces unnecessary changes.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI invocation abstraction | Custom wrappers per provider | Existing patterns from `review.md` (lines 121-131) | Already tested; `claude -p`, `codex exec`, `gemini -p` with correct flags |
| Verdict normalization | Custom verdict parser | Existing `normalized_verdicts` from `behavior-contract.yaml` | Canonical set: `[APPROVE, MINOR, MAJOR, NO_OUTPUT, CONDITIONAL_PASS, ERROR]` |
| Route classification | Custom complexity scorer | Existing `routing-config.yaml` tier system (SIMPLE/STANDARD/COMPLEX/REASONING) | Already classifies tasks; just read the tier |
| Review consensus logic | Custom 2-of-3 logic | Existing `two_of_three_approve` semantics from `behavior-contract.yaml` codex_fallback section | Edge cases (NO_OUTPUT, CONDITIONAL_PASS) already handled |
| Iteration tracking | Custom tracking format | Existing JSON iteration records from `cross-review-loop.sh` (lines 156-178) | Already handles iteration count, timestamps, status, fix commits |
| Temp directory management | Inline mktemp calls | Standard `mktemp -d` with trap for cleanup | Ensures cleanup on script exit/error |

**Key insight:** Nearly every building block exists. The cross-plan.sh script is the only net-new artifact. Everything else is modification of existing scripts and configs.

## Common Pitfalls

### Pitfall 1: Forgetting to Clean Up Temp Files on Error
**What goes wrong:** If a parallel invocation fails mid-way (e.g., one provider hangs), temp files accumulate in /tmp.
**Why it happens:** Background processes write to temp dirs, but if the parent script exits early, no cleanup runs.
**How to avoid:** Use `trap 'rm -rf "$TMPDIR"' EXIT ERR INT TERM` at the top of `cross-plan.sh` and any modified review functions.
**Warning signs:** /tmp filling up with `gsd-cross-plan-*` directories.

### Pitfall 2: Codex CLI Producing Empty Output (NO_OUTPUT)
**What goes wrong:** Codex CLI sometimes returns empty responses on large diffs or complex prompts — this is a known behavior documented in `behavior-contract.yaml` codex_fallback section.
**Why it happens:** Codex uses o4-mini under the hood; large context can trigger empty responses.
**How to avoid:** For cross-planning: treat Codex NO_OUTPUT as "skip this provider's plan" and merge from the remaining two. For cross-review: use existing `codex_fallback` policy (Claude+Gemini 2-of-2 = CONDITIONAL_PASS).
**Warning signs:** `$TMPDIR/codex-plan.md` exists but is empty or under 50 bytes.

### Pitfall 3: Plan Template Divergence Across Providers
**What goes wrong:** Claude, Codex, and Gemini produce plans in slightly different formats, making structured section extraction fail.
**Why it happens:** Each provider interprets the PLAN.md template differently. Codex may omit XML tags. Gemini may add extra sections.
**How to avoid:** The planning prompt MUST include the exact PLAN.md template with XML tags and explicit "do not add or remove sections" instruction. Validate each plan's structure before attempting merge. Fall back to full-LLM synthesis if structure validation fails.
**Warning signs:** Section extraction returns empty for one or more providers.

### Pitfall 4: Race Conditions in Cross-Review When Writing REVIEWS.md
**What goes wrong:** If the parallel review mode is invoked while a GSD skill is also writing to the phase directory, file conflicts can occur.
**Why it happens:** Background processes + GSD tools both write to the same phase directory.
**How to avoid:** Parallel review processes write to temp files ONLY. The aggregation step (after `wait`) writes the final REVIEWS.md atomically. Use the existing pattern from `review.md` step `write_reviews`.
**Warning signs:** Truncated or corrupted REVIEWS.md files.

### Pitfall 5: Synthesis Prompt Exceeding Context Window
**What goes wrong:** Three full PLAN.md files plus the synthesis prompt exceed the provider's context window.
**Why it happens:** Complex phases can produce plans with 50+ tasks each. Three plans = 150+ tasks in the synthesis prompt.
**How to avoid:** D-04's structured diff pre-filtering solves this. Only divergent sections go to synthesis, not full plans. Additionally, for very large plans, chunk divergent sections and synthesize incrementally.
**Warning signs:** Claude synthesis call returns an error or truncated output.

### Pitfall 6: Sequential Review Comment in review.md Misleading Implementers
**What goes wrong:** The existing `review.md` has a comment "invoke in sequence (not parallel -- avoid rate limits)" at line 117. Implementers might think parallelism was rejected for a good reason.
**Why it happens:** The original comment was overly conservative — rate limits are independent per provider (Anthropic, OpenAI, Google APIs).
**How to avoid:** D-06 explicitly overrides this. Update the comment in review.md to explain that parallel invocation is the new default for Route B/C, with sequential as a fallback.
**Warning signs:** Someone adds the sequential constraint back citing the old comment.

## Code Examples

### CLI Invocation Commands (verified from existing code)

**Claude planning invocation:**
```bash
# Source: review.md line 125-126
claude -p "$(cat "$PROMPT_FILE")" --no-input 2>/dev/null > "$OUTPUT_FILE"
```

**Codex planning invocation:**
```bash
# Source: review.md line 130-131
codex exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" 2>/dev/null > "$OUTPUT_FILE"
```

**Gemini planning invocation:**
```bash
# Source: review.md line 121-122
gemini -p "$(cat "$PROMPT_FILE")" 2>/dev/null > "$OUTPUT_FILE"
```

### Parallel Invocation with Progress Display
```bash
# Source: Pattern derived from execute-phase.md parallel agent pattern
echo -e "${CYAN}Dispatching parallel plans to 3 providers...${NC}"

for provider in claude codex gemini; do
  dispatch_plan "$provider" "$TMPDIR" "$PROMPT_FILE" &
  PIDS[$provider]=$!
  echo -e "  ${BLUE}Started ${provider} (PID ${PIDS[$provider]})${NC}"
done

echo ""
for provider in claude codex gemini; do
  if wait ${PIDS[$provider]} 2>/dev/null; then
    echo -e "  ${GREEN}${provider} completed${NC}"
  else
    echo -e "  ${YELLOW}${provider} failed (exit $?)${NC}"
    FAILURES+=("$provider")
  fi
done
```

### Tier-Based Mode Selection
```bash
# Source: routing-config.yaml tier system + new cross_modes section
get_cross_mode() {
  local tier="$1" mode="$2"
  # Read from routing-config.yaml
  local enabled
  enabled=$(yq ".cross_modes.${mode}.${tier}" config/agents/routing-config.yaml 2>/dev/null || echo "false")
  echo "$enabled"
}

# Usage in plan-phase.md:
TASK_TIER=$(classify_task_tier)  # Returns SIMPLE/STANDARD/COMPLEX/REASONING
CROSS_PLAN_ENABLED=$(get_cross_mode "$TASK_TIER" "cross_plan")
if [[ "$CROSS_PLAN_ENABLED" == "true" ]]; then
  # Dispatch cross-plan.sh
else
  # Single planner (existing behavior)
fi
```

### phase_0_plan Block for agent-delegation-templates.md
```yaml
# New block to add for each task type
# Example: feature/C (complex feature)
task_agents:
  phase_0_plan: [claude, codex, gemini]  # All 3 plan independently; Claude synthesizes
  phase_1: claude   # architecture + spec
  phase_2: codex    # implement modules
  phase_3: claude   # integration wiring
  phase_4: gemini   # cross-review + docs
  phase_5: claude   # merge gate

# Example: feature/A (simple feature)
task_agents:
  phase_0_plan: codex   # Single planner only (per D-09, simple tasks don't cross-plan)
  phase_1: codex    # implement + tests
  phase_2: codex    # cross-review
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sequential 3-CLI review | Parallel 3-CLI review via `&` + `wait` | This phase | ~65% wall-clock speedup on Route B/C reviews |
| Single-planner planning | Ensemble parallel planning with merge | This phase | Diverse perspectives; avoids anchoring bias |
| Universal 2-of-3 review gate | Tiered gates (Route A: 1, Route B: 2-of-3, Route C: 3-of-3) | This phase | Cost/latency proportional to complexity |
| review.md sequential comment | Parallel default | This phase | Removes overly conservative constraint |

**Deprecated/outdated:**
- The comment in `review.md` line 117 "invoke in sequence (not parallel -- avoid rate limits)" is explicitly superseded by D-06.

## Open Questions

1. **Structured diff algorithm choice**
   - What we know: PLAN.md uses XML-tagged sections (`<objective>`, `<tasks>`, `<must_haves>`) which are amenable to regex extraction.
   - What's unclear: Whether regex extraction is robust enough for all PLAN.md variations, or whether a lightweight parser (awk/sed state machine or Node.js) is needed.
   - Recommendation: Start with regex/sed extraction for the known XML tags. If any provider's output breaks the regex, fall back to sending the entire set of plans to the synthesis LLM (graceful degradation). This is Claude's discretion per CONTEXT.md.

2. **Handling partial provider failures in cross-planning**
   - What we know: All 3 providers should plan (D-09), but one might fail.
   - What's unclear: Minimum viable provider count for a valid cross-plan. Is 2-of-3 sufficient? Is 1-of-3 ever acceptable?
   - Recommendation: Require at least 2 successful plan outputs. If only 1 succeeds, fall back to single-planner mode (use that one plan as-is, with a warning). If 0 succeed, error out.

3. **Route tier classification for GSD phases (not WRK items)**
   - What we know: `routing-config.yaml` tiers (SIMPLE/STANDARD/COMPLEX/REASONING) exist for WRK items. GSD phases use a different spec structure.
   - What's unclear: How to classify a GSD phase into a route tier. The CONTEXT.md phase description doesn't have a `task_type` field.
   - Recommendation: Add a `route_tier` field to `.planning/config.json` or detect from ROADMAP.md phase description (heuristic: phases with 1-2 plans = STANDARD, 3+ plans = COMPLEX). Or expose as a flag: `--cross-plan` to force cross-planning mode.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Claude Code CLI | Planning + Review + Synthesis | Yes | 2.1.87 | Cannot substitute (synthesis agent) |
| Codex CLI | Planning + Review | Yes | 0.116.0 | Skip, merge from 2 providers |
| Gemini CLI | Planning + Review | Yes | 0.35.1 | Skip, merge from 2 providers |
| jq | JSON iteration records | Yes | 1.7 | sed/awk (degraded) |
| Node.js | GSD toolchain | Yes | 22.22.1 | Required (no fallback) |
| bash | Parallel process management | Yes | system | Required (no fallback) |
| mktemp | Temp directory creation | Yes | system | Required (no fallback) |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None (all present).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bash + manual verification |
| Config file | none (shell scripts, no test framework config) |
| Quick run command | `bash -n scripts/development/ai-plan/cross-plan.sh` (syntax check) |
| Full suite command | `bash scripts/development/ai-plan/cross-plan.sh --dry-run --phase test` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| (no IDs mapped) | cross-plan.sh dispatches 3 CLIs in parallel | smoke | `bash scripts/development/ai-plan/cross-plan.sh --dry-run` | Wave 0 |
| (no IDs mapped) | review.md parallel mode produces REVIEWS.md | smoke | Manual: run `/gsd:review --phase N` on test phase | Wave 0 |
| (no IDs mapped) | routing-config.yaml cross_modes parsed correctly | unit | `yq '.cross_modes' config/agents/routing-config.yaml` | Wave 0 |
| (no IDs mapped) | agent-delegation-templates.md has phase_0_plan | grep | `grep 'phase_0_plan' .claude/docs/agent-delegation-templates.md` | Wave 0 |

### Sampling Rate
- **Per task commit:** `bash -n` syntax check on modified shell scripts
- **Per wave merge:** Dry-run cross-plan.sh with mock inputs
- **Phase gate:** Full end-to-end cross-plan on a real phase + cross-review verification

### Wave 0 Gaps
- [ ] `scripts/development/ai-plan/cross-plan.sh` — new file, needs creation
- [ ] Dry-run mode for cross-plan.sh (mock CLI calls, verify parallel dispatch logic)
- [ ] Integration test: run cross-plan.sh on a phase with known CONTEXT.md, verify 3 temp files created

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `scripts/development/ai-review/cross-review-loop.sh` — existing review loop, iteration tracking, review ID generation
- Codebase inspection: `.claude/get-shit-done/workflows/review.md` — sequential CLI invocation patterns (lines 117-131), output collection
- Codebase inspection: `.claude/get-shit-done/workflows/plan-phase.md` — planner spawning pattern (step 8), agent model selection
- Codebase inspection: `.claude/get-shit-done/workflows/execute-phase.md` — parallel subagent dispatch with `Task()`, PID-based wait, spot-check fallback
- Codebase inspection: `config/agents/behavior-contract.yaml` — task_type_matrix, two_of_three_approve, normalized_verdicts, codex_fallback
- Codebase inspection: `config/agents/routing-config.yaml` — tier routing (SIMPLE/STANDARD/COMPLEX/REASONING)
- Codebase inspection: `.claude/docs/agent-delegation-templates.md` — role matrix, task_agents maps, invocation patterns
- Codebase inspection: `.claude/docs/provider-behavioral-differences.md` — provider strengths, CLI differences
- Codebase inspection: `docs/modules/ai/CROSS_REVIEW_POLICY.md` — mandatory review policy, iteration loop, verdict definitions
- Environment verification: `claude --version` (2.1.87), `codex --version` (0.116.0), `gemini --version` (0.35.1), `jq --version` (1.7), `node --version` (22.22.1)

### Secondary (MEDIUM confidence)
- CONTEXT.md decision D-06: Rate limits are independent per provider — verified by examining that each CLI hits a different API endpoint (Anthropic, OpenAI, Google)
- CONTEXT.md decision D-07: ~65% faster reviews — estimated from 3 sequential -> 1 parallel (wall-clock = max of 3 durations vs. sum of 3)

### Tertiary (LOW confidence)
- Structured diff approach for PLAN.md merge: regex extraction of XML tags is a heuristic. Robustness depends on how strictly providers follow the template. Needs validation during implementation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools verified present on machine, all patterns from existing codebase
- Architecture: HIGH — extending existing patterns (parallel dispatch is standard bash, merge is new but well-scoped)
- Pitfalls: HIGH — derived from existing codebase issues (Codex NO_OUTPUT already documented, temp file cleanup standard practice)
- Structured diff/merge: MEDIUM — the merge algorithm is new ground; regex vs. parser choice needs implementation validation

**Research date:** 2026-03-29
**Valid until:** 2026-04-29 (stable domain; CLI versions may update but invocation patterns are stable)
