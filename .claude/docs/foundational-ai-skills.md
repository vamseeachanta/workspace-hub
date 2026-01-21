# Foundational AI Skills (Applies To All Agents)

These concepts guide how agents should gather context and challenge ideas.

## 1) Context Engineering

**Concept:** The more high-quality information and context about your situation, goals, what you've tried, what didn't work, data, and constraints you provide, the higher-quality answers you get.

**Template (context-first over "perfect prompts"):**

```text
You are a top 0.1% expert in FIELD, helping me with TASK

CONTEXT:
- bullet list of relevant info, data, attempts, and outcomes

CONSTRAINTS:
- bullet list of limits, preferences, deadlines, tools, etc.

Ask me clarifying questions, one at a time, until you are 95% confident you can complete the task successfully.
```

**Agent notes:**
- Ask for missing context before acting.
- Use one question at a time; stop when confidence is >= 95%.

## 2) Sparring Partners

**Concept:** Stop using AI for surface-level answers. Use AI to understand what questions you should have been asking.

**Action:** Ask the AI to act as a critic or skeptic.

**Example request:**

```text
Tear my idea apart and find my blind spots.
```

**Agent notes:**
- Encourage counter-arguments, edge cases, and failure modes.
- Compare answers across multiple models and look for convergence and divergence.
