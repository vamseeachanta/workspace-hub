# WRK-1405: Learning Infrastructure Assessment for Latest AI Models

## Question
Do we have sufficient learning infrastructure to improve our work with the latest models (Claude 4.5/4.6, Gemini 2.5, Codex)?

## Answer Summary
**Partially.** The architecture is sound but execution is degraded. The nightly pipeline is ~30% functional (shell phases work, Python phases broken). Key feedback loops are stale or disconnected.

## Current State Assessment

### What Works
1. **Session signals collection** — 15 days of continuous JSONL data (Mar 10-25)
2. **Nightly shell phases** — Insights, Reflect, Knowledge, Improve all run successfully
3. **Memory system** — 24 active memories, used in conversations, covers feedback/project/reference types
4. **Work queue lifecycle** — 20-stage pipeline with evidence trail provides rich data
5. **Corrections capture** — 61 correction files accumulated
6. **Multi-provider tooling** — Claude 2.1.83, Codex 0.116.0, Gemini 0.33.1 all available

### What's Broken
1. **Python analysis phases** — 7 of 10 nightly phases consistently FAIL (Quality Signals, Memory Staleness, Correction Trends, WRK Feedback, Candidates, Report Review, Coverage Audit)
2. **Skill scores** — Last updated 2026-02-20 (33 days stale), no ongoing tracking
3. **Learned patterns** — 505 entries, mostly empty (no tool_patterns, no error_patterns, no recommendations)
4. **Nightly pipeline gap** — No reports generated since Mar 19 (6 days)

### What's Missing
1. **Feedback loop measurement** — No mechanism to measure if session N learnings improve session N+1
2. **Model-specific adaptations** — All three providers use same skills/prompts; no tuning for model strengths
3. **Correction → Skill pipeline** — Corrections accumulate but aren't systematically converted to skill improvements
4. **Candidate promotion** — Only 5 candidates vs 61 corrections (8% conversion rate)

## Implementation Plan

### Phase 1: Fix the Broken Pipeline (Priority: HIGH)
**Goal:** Restore nightly learning pipeline to full functionality

1. Debug Python analysis script in cron context (likely missing `yaml` dependency or env issue)
2. Run `comprehensive_learning_pipeline.py` for all 9 phases manually, capture errors
3. Fix environment: ensure `uv run --no-project` has all deps available in cron
4. Verify nightly reports resume with all phases DONE
5. Update skill-scores.yaml from current session data

### Phase 2: Close the Feedback Loop (Priority: MEDIUM)
**Goal:** Measure whether learnings actually improve subsequent sessions

1. Define measurable metrics:
   - Hook violation rate per session (drift counts already captured)
   - One-shot success rate (task completed without corrections)
   - Stage velocity (time per WRK stage, already in stage-timing evidence)
2. Add trend tracking to comprehensive-learning pipeline
3. Create weekly trend report comparing this week vs last week

### Phase 3: Activate Correction → Skill Pipeline (Priority: MEDIUM)
**Goal:** Systematically convert corrections into skill improvements

1. Review 61 corrections for common themes
2. Promote top corrections to skill updates or new micro-skills
3. Automate: when correction count for a pattern > 3, auto-generate candidate

### Phase 4: Model-Specific Tuning (Priority: LOW)
**Goal:** Optimize prompts and skill invocation per provider

1. Document observed differences between Claude/Codex/Gemini behavior
2. Add provider-aware prompt sections where behavior diverges
3. Track per-provider success metrics in skill-scores.yaml

## Acceptance Criteria
- [ ] Nightly pipeline: all 10 phases report DONE
- [ ] Skill scores updated with data from Mar 2026
- [ ] At least one trend metric tracked week-over-week
- [ ] Top 5 corrections promoted to skill improvements

## Estimated Effort
- Phase 1: ~2 hours (debugging + fix)
- Phase 2: ~4 hours (metric definition + implementation)
- Phase 3: ~3 hours (review + promote)
- Phase 4: ~2 hours (documentation + basic tuning)

---

## Industry Research: Best Practices (2025-2026)

Deep research across 4 parallel agents covering Claude Code workflows, AI agent learning infrastructure, advanced Claude Code setups, and competing tools (Cursor, Codex CLI, Gemini CLI, Aider, Continue.dev, Windsurf).

### Verdict: Our Infrastructure is Ahead of Most, But Has Key Gaps

**What we already do that aligns with best practices:**
- File-based memory system (CLAUDE.md + `.claude/rules/` + memory files) — industry standard
- Hook-based enforcement (PreToolUse/PostToolUse) — matches Trail of Bits gold standard pattern
- Multi-provider support (Claude/Codex/Gemini) — rare; most teams use one tool
- 20-stage work queue with evidence trail — more structured than anything found publicly
- Session signals + nightly analysis pipeline — most teams have nothing comparable
- Skill library with SKILL.md format — aligns with Anthropic's official skill specification
- Corrections tracking — matches GitHub Copilot's citation-based memory approach

**What industry leaders do that we don't (yet):**

#### 1. Self-Verification Loops (HIGH priority gap)
- **Pattern:** Agents close their own feedback loops (run tests → read output → fix → re-verify) instead of routing through humans
- **Source:** Owain Lewis, Anthropic best practices
- **Our gap:** Our hooks enforce rules but don't create autonomous fix loops
- **Action:** Consider Ralph Wiggum-style iterative loops for quality gates

#### 2. Metrics Framework (HIGH priority gap)
- **Industry standard (Augment Code):** Track adoption % → velocity delta → defect density → ROI
- **DORA + SPACE combination** used by 40.8% of teams
- **Agent-specific:** Agent Efficiency Score (AES), Human-Agent Handoff Time
- **Our gap:** We capture raw data (session signals, corrections, stage timing) but don't compute trend metrics
- **Action:** Phase 2 of our plan addresses this — add weekly trend reports

#### 3. Memory Verification Before Storage (MEDIUM priority gap)
- **GitHub Copilot pattern:** Store memories with citations → verify citations at retrieval → self-correct stale memories
- **Measured result:** 7% increase in PR merge rates (90% vs 83%)
- **Our gap:** Our memory system doesn't verify staleness systematically (Phase 3 Python script broken)
- **Action:** Fix memory staleness check; add citation-based verification

#### 4. Glob-Targeted Rules (MEDIUM priority gap)
- **Cursor/Continue/Windsurf pattern:** Rules auto-attach only when matching file types are in context
- **Our gap:** `.claude/rules/` files apply universally — no file-type targeting
- **Action:** Add frontmatter with glob patterns to reduce noise

#### 5. JIT Context Loading (LOW priority gap)
- **Gemini CLI pattern:** Scans for instruction files when tools touch directories — deeply nested components get own rules automatically
- **Our gap:** All rules at root level; nested components don't carry own instructions
- **Action:** Future consideration for complex repos

#### 6. Eval/Benchmark Infrastructure (MEDIUM priority gap)
- **Tools available:** Promptfoo (prompt testing), DeepEval (14+ metrics), Braintrust (observability)
- **Claude Code native:** Skill-creator 2.0 with blind A/B testing and variance analysis
- **Our gap:** skill-eval exists but is manual-only; no systematic benchmarking
- **Action:** Integrate skill-creator 2.0 evals into nightly pipeline

#### 7. Community Skill Sharing (LOW priority gap)
- **Patterns:** antigravity-awesome-skills (1,300+ skills), awesome-agent-skills, Aider conventions repo, Continue Hub
- **Our gap:** Skills are private/internal only
- **Action:** Consider publishing reusable skills; pull useful community skills

### Key External References

**Learning Loops & Memory:**
- [Addy Osmani — Self-Improving Coding Agents](https://addyosmani.com/blog/self-improving-agents/)
- [GitHub Blog — Building an Agentic Memory System for Copilot](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)
- [Martin Alderson — Self-improving CLAUDE.md Files](https://martinalderson.com/posts/self-improving-claude-md-files/)
- [MindStudio — How to Build a Learnings Loop](https://www.mindstudio.ai/blog/how-to-build-learnings-loop-claude-code-skills)

**Hooks & Enforcement:**
- [Trail of Bits — claude-code-config](https://github.com/trailofbits/claude-code-config) (gold standard)
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)
- [Ralph Wiggum — Official Anthropic plugin](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)

**Metrics:**
- [Augment Code — Autonomous Development Metrics](https://www.augmentcode.com/guides/autonomous-development-metrics-kpis-that-matter-for-ai-assisted-engineering-teams)
- [Plandek — DORA Metrics in the Age of AI 2026](https://plandek.com/blog/how-to-measure-dora-metrics-in-the-age-of-ai-2026/)

**Eval Frameworks:**
- [Promptfoo](https://github.com/promptfoo/promptfoo) — prompt testing + red-teaming
- [DeepEval](https://github.com/confident-ai/deepeval) — pytest-like LLM evaluation
- [Skills 2.0 Evals Guide](https://www.pasqualepillitteri.it/en/news/341/claude-code-skills-2-0-evals-benchmarks-guide)

**Competing Tool Patterns:**
- [Cursor Memory Bank Pattern](https://gist.github.com/ipenywis/1bdb541c3a612dbac4a14e1e3f4341ab) — structured project memory
- [Aider Repository Map](https://aider.chat/docs/repomap.html) — graph-ranked automatic context
- [Gemini CLI JIT Context](https://geminicli.com/docs/cli/gemini-md/) — directory-level instruction scanning
- [Windsurf Cascade Context Pipeline](https://mer.vin/2025/12/windsurf-memory-rules-deep-dive/) — weighted context assembly

**Skill Libraries:**
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — 32.3k stars master list
- [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) — 1,300+ skills
- [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) — community-curated

**Agent Memory Systems:**
- [Mem0](https://github.com/mem0ai/mem0) — cloud API, vector similarity
- [Zep](https://www.getzep.com/) — temporal knowledge graph (~85% LoCoMo)
- [Letta/MemGPT](https://www.letta.com/) — LLM-managed memory tiers
- [LangMem SDK](https://blog.langchain.com/langmem-sdk-launch/) — LangGraph memory integration

---
confirmed_by: vamsee
confirmed_at: 2026-03-25T17:30:00Z
decision: passed
