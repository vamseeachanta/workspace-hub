# Research Template: skill-design
# ABOUTME: Guide for nightly researcher — what to investigate about agent skill design
# Used by: scripts/cron/gsd-researcher-nightly.sh (Saturday rotation)

## Research Focus Areas

### 1. Anthropic Claude Skill Authoring Patterns
- Latest CLAUDE.md / AGENTS.md authoring conventions from Anthropic
- Recommended file structures for agent instructions
- Changes to how Claude Code reads and applies skill files
- New directives, pragmas, or metadata fields

### 2. AGENTS.md and CLAUDE.md Community Best Practices
- Emerging patterns from open-source repos using AGENTS.md
- Directory-scoped vs. root-level skill placement
- Inheritance and override patterns (root → subdirectory)
- How teams organize multi-skill repositories

### 3. Agent Skill Specification Standards
- Any formal spec for agent skill files (beyond Anthropic's docs)
- Cross-vendor skill formats (OpenAI Codex, Google Jules, etc.)
- Interoperability patterns between agent frameworks

### 4. Progressive Disclosure Patterns
- Layered complexity in skill definitions (beginner → expert)
- Context-window-aware skill loading strategies
- Conditional inclusion based on task type or domain
- Skill summarization and compression techniques

### 5. Skill Testing and Evaluation
- How to test that agent skills produce expected behavior
- Evaluation frameworks for skill effectiveness
- Regression testing approaches for skill changes
- Metrics: task completion rate, instruction adherence, hallucination rate

### 6. Multi-Agent Skill Coordination
- Skill sharing between orchestrator and sub-agents
- Avoiding conflicting instructions in multi-agent setups
- Delegation patterns: which skills go to which agent tier
- Context passing and skill inheritance across agent boundaries

## Output Format

Follow the standard research output format:

```
# Research: skill-design — YYYY-MM-DD

## Key Findings
- Finding 1 with source/reference
- Finding 2 ...
- (3-5 findings)

## Relevance to Project
- How each finding affects workspace-hub skill architecture

## Recommended Actions
- [ ] Actionable item (promote to PROJECT.md / create issue / ignore with reason)
```
