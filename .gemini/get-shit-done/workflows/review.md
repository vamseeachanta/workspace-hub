<purpose>
Cross-AI peer review — invoke external AI CLIs to independently review phase plans.
Each CLI gets the same prompt (PROJECT.md context, phase plans, requirements) and
produces structured feedback. Results are combined into REVIEWS.md for the planner
to incorporate via --reviews flag.

This implements adversarial review: different AI models catch different blind spots.
A plan that survives review from 2-3 independent AI systems is more robust.
</purpose>

<process>

<step name="detect_clis">
Check which AI CLIs are available on the system:

```bash
# Check each CLI
command -v gemini >/dev/null 2>&1 && echo "gemini:available" || echo "gemini:missing"
command -v claude >/dev/null 2>&1 && echo "claude:available" || echo "claude:missing"
command -v codex >/dev/null 2>&1 && echo "codex:available" || echo "codex:missing"
```

Parse flags from `$ARGUMENTS`:
- `--gemini` → include Gemini
- `--claude` → include Claude
- `--codex` → include Codex
- `--all` → include all available
- No flags → include all available

If no CLIs are available:
```
No external AI CLIs found. Install at least one:
- gemini: https://github.com/google-gemini/gemini-cli
- codex: https://github.com/openai/codex
- claude: https://github.com/anthropics/claude-code

Then run /gsd:review again.
```
Exit.

If only one CLI is the current runtime (e.g. running inside Claude), skip it for the review
to ensure independence. At least one DIFFERENT CLI must be available.
</step>

<step name="gather_context">
Collect phase artifacts for the review prompt:

```bash
INIT=$(node "/mnt/local-analysis/workspace-hub/.gemini/get-shit-done/bin/gsd-tools.cjs" init phase-op "${PHASE_ARG}")
if [[ "$INIT" == @file:* ]]; then INIT=$(cat "${INIT#@file:}"); fi
```

Read from init: `phase_dir`, `phase_number`, `padded_phase`.

Then read:
1. `.planning/PROJECT.md` (first 80 lines — project context)
2. Phase section from `.planning/ROADMAP.md`
3. All `*-PLAN.md` files in the phase directory
4. `*-CONTEXT.md` if present (user decisions)
5. `*-RESEARCH.md` if present (domain research)
6. `.planning/REQUIREMENTS.md` (requirements this phase addresses)
</step>

<step name="build_prompt">
Build a structured review prompt:

```markdown
# Cross-AI Plan Review Request

You are reviewing implementation plans for a software project phase.
Provide structured feedback on plan quality, completeness, and risks.

## Project Context
{first 80 lines of PROJECT.md}

## Phase {N}: {phase name}
### Roadmap Section
{roadmap phase section}

### Requirements Addressed
{requirements for this phase}

### User Decisions (CONTEXT.md)
{context if present}

### Research Findings
{research if present}

### Plans to Review
{all PLAN.md contents}

## Review Instructions

Analyze each plan and provide:

1. **Summary** — One-paragraph assessment
2. **Strengths** — What's well-designed (bullet points)
3. **Concerns** — Potential issues, gaps, risks (bullet points with severity: HIGH/MEDIUM/LOW)
4. **Suggestions** — Specific improvements (bullet points)
5. **Risk Assessment** — Overall risk level (LOW/MEDIUM/HIGH) with justification

Focus on:
- Missing edge cases or error handling
- Dependency ordering issues
- Scope creep or over-engineering
- Security considerations
- Performance implications
- Whether the plans actually achieve the phase goals

Output your review in markdown format.
```

Write to a temp file: `/tmp/gsd-review-prompt-{phase}.md`
</step>

<step name="invoke_reviewers">
Determine review mode based on route tier. Read cross_modes from routing-config.yaml:

```bash
# Determine if parallel review is enabled for this tier
# Default to STANDARD if tier not specified
REVIEW_TIER="${REVIEW_TIER:-STANDARD}"
PARALLEL_REVIEW=$(python3 -c "
import yaml
with open('config/agents/routing-config.yaml') as f:
    cfg = yaml.safe_load(f)
print(cfg.get('cross_modes', {}).get('cross_review', {}).get('$REVIEW_TIER', 'true'))
" 2>/dev/null || echo "true")
```

**If parallel review is enabled (Route B/C/REASONING — default):**

Invoke all selected CLIs in parallel using bash `&` + `wait`. Per D-06, rate limits are independent across providers (Anthropic, OpenAI, Google APIs). Each process writes to its own temp file.

```bash
# Parallel invocation — providers write to independent temp files
# Rate limits are independent per provider (D-06)
REVIEW_TMPDIR=$(mktemp -d "/tmp/gsd-review-parallel-XXXXXX")
trap 'rm -rf "$REVIEW_TMPDIR"' EXIT ERR INT TERM

declare -A REVIEW_PIDS

# Gemini
gemini -p "$(cat /tmp/gsd-review-prompt-{phase}.md)" 2>/dev/null > "$REVIEW_TMPDIR/gemini.md" &
REVIEW_PIDS[gemini]=$!

# Claude (separate session)
claude -p "$(cat /tmp/gsd-review-prompt-{phase}.md)" --no-input 2>/dev/null > "$REVIEW_TMPDIR/claude.md" &
REVIEW_PIDS[claude]=$!

# Codex
codex exec --skip-git-repo-check "$(cat /tmp/gsd-review-prompt-{phase}.md)" 2>/dev/null > "$REVIEW_TMPDIR/codex.md" &
REVIEW_PIDS[codex]=$!

# Wait for all — capture individual exit codes
for provider in "${!REVIEW_PIDS[@]}"; do
  if wait "${REVIEW_PIDS[$provider]}" 2>/dev/null; then
    cp "$REVIEW_TMPDIR/${provider}.md" "/tmp/gsd-review-${provider}-{phase}.md"
    echo -e "  ${GREEN}${provider} review completed${NC}"
  else
    echo -e "  ${YELLOW}${provider} review failed (exit $?)${NC}"
  fi
done
```

**If parallel review is disabled (Route A — SIMPLE):**

Fall back to single-provider sequential invocation (existing behavior, cheapest provider only):

```bash
# Sequential invocation — single provider for Route A
gemini -p "$(cat /tmp/gsd-review-prompt-{phase}.md)" 2>/dev/null > /tmp/gsd-review-gemini-{phase}.md
```

Display progress for both modes:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► CROSS-AI REVIEW — Phase {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mode: {parallel|sequential} (tier: {REVIEW_TIER})

◆ Reviewing with {CLI}... done
◆ Reviewing with {CLI}... done
```

If a CLI fails in parallel mode, log the error and continue — same as current sequential behavior. The write_reviews step already handles missing provider outputs.
</step>

<step name="write_reviews">
Combine all review responses into `{phase_dir}/{padded_phase}-REVIEWS.md`:

```markdown
---
phase: {N}
reviewers: [gemini, claude, codex]
reviewed_at: {ISO timestamp}
plans_reviewed: [{list of PLAN.md files}]
---

# Cross-AI Plan Review — Phase {N}

## Gemini Review

{gemini review content}

---

## Claude Review

{claude review content}

---

## Codex Review

{codex review content}

---

## Consensus Summary

{synthesize common concerns across all reviewers}

### Agreed Strengths
{strengths mentioned by 2+ reviewers}

### Agreed Concerns
{concerns raised by 2+ reviewers — highest priority}

### Divergent Views
{where reviewers disagreed — worth investigating}
```

Commit:
```bash
node "/mnt/local-analysis/workspace-hub/.gemini/get-shit-done/bin/gsd-tools.cjs" commit "docs: cross-AI review for phase {N}" --files {phase_dir}/{padded_phase}-REVIEWS.md
```
</step>

<step name="present_results">
Display summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► REVIEW COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase {N} reviewed by {count} AI systems.

Consensus concerns:
{top 3 shared concerns}

Full review: {padded_phase}-REVIEWS.md

To incorporate feedback into planning:
  /gsd:plan-phase {N} --reviews
```

Clean up temp files.
</step>

</process>

<success_criteria>
- [ ] At least one external CLI invoked successfully
- [ ] REVIEWS.md written with structured feedback
- [ ] Consensus summary synthesized from multiple reviewers
- [ ] Temp files cleaned up
- [ ] User knows how to use feedback (/gsd:plan-phase --reviews)
</success_criteria>
