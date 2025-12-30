# AI Tool Usage Assessment

Assess and report on AI tool subscriptions, usage patterns, and cost-effectiveness.

## Trigger

User asks to assess AI tools, review AI subscriptions, or analyze AI tool usage.

## Instructions

When triggered, perform the following assessment:

### 1. Subscription Inventory

Review current paid memberships from `docs/AI_development_tools.md`:

| Service | Plan | Monthly Cost | Annual Cost |
|---------|------|--------------|-------------|
| Claude (Anthropic) | Max Plan | $106.60 | $1,279.20 |
| OpenAI | ChatGPT Plus | $21.28 | $255.36 |
| Google AI | Pro | $19.99 | $239.88 |
| GitHub Copilot | Pro | $8.88/mo | $106.60 |
| **TOTAL** | | **$156.75** | **$1,881.04** |

### 2. Tool Usage Analysis

Assess each tool category:

**Primary AI Assistants:**
- Claude Max: Code generation, complex reasoning, long-context tasks
- OpenAI Plus: Alternative perspective, GPT-4o access, DALL-E
- Google AI Pro: Gemini access, Google ecosystem integration

**Development Tools:**
- GitHub Copilot: Inline code completion, IDE integration
- Claude-flow: Multi-agent orchestration
- Factory.ai: Automated droids for CI/CD
- Google Antigravity: Agent-first IDE (in evaluation)

### 3. Generate Assessment Report

Create report at `reports/ai-tool-assessment/assessment-YYYYMMDD.md` with:

```markdown
# AI Tool Usage Assessment - [DATE]

## Executive Summary
- Total monthly spend: $X
- Primary tools in active use: [list]
- Tools underutilized: [list]
- Recommended actions: [list]

## Subscription Status
[Table of all subscriptions with renewal dates if known]

## Usage Patterns
[Analysis of which tools are used for what purposes]

## Cost-Effectiveness Analysis
| Tool | Cost/Month | Usage Level | Value Rating |
|------|------------|-------------|--------------|
| ... | ... | High/Medium/Low | 1-5 stars |

## Overlap Analysis
[Identify redundant capabilities across tools]

## Recommendations
1. [Keep/Cancel/Downgrade recommendations]
2. [Usage optimization suggestions]
3. [New tools to consider]

## Next Review Date
[Set quarterly review schedule]
```

### 4. Questions to Ask User

Before generating report, ask:
1. Which tools have you used most this month?
2. Are there specific tasks where one tool excels?
3. Any tools you haven't used in 30+ days?
4. New capabilities you need that current tools lack?

## Output

- Assessment report in `reports/ai-tool-assessment/`
- Updated `docs/AI_development_tools.md` if status changes
- Summary printed to console

---

## Version History

- **1.0.0** (2024-10-15): Initial release with subscription inventory, usage analysis, cost-effectiveness reporting, recommendation framework
