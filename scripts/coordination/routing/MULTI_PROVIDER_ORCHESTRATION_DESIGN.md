# Multi-Provider AI Orchestration System Design

> **Version:** 1.0.0
> **Date:** 2025-01-11
> **Status:** Design Complete - Ready for Phase 1 Implementation
> **Providers:** OpenAI Codex, Google Gemini, Claude 3.5 Max

## Executive Summary

Building on the success of Phase 1 (Claude-only model selection with usage awareness), Phase 2 extends the orchestration system to intelligently coordinate work across three independent AI providers with distinct specializations, rate limits, and pricing models.

**Key Improvement:** From single-provider optimization to multi-provider cost/performance optimization with 300% performance gains through concurrent execution (batchtools integration).

**Design Principles:**
- Extend Phase 1 patterns (hard blocking, intelligent fallback, audit trail) to multi-provider
- Maintain provider independence (three separate tracking files, rate limit management)
- Cost-aware routing (pricing differences: $0.0015-$0.006 per 1K tokens)
- Leverage 54-agent pool for optimal task execution
- Enable concurrent multi-provider execution via batchtools

---

## 1. Architecture Overview

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                           │
│        (Task description + execution context)               │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────▼────────────┐
    │   Task Classifier       │
    │ (Keyword scoring)       │
    │ ├─ CodeX keywords       │
    │ ├─ Gemini keywords      │
    │ └─ Claude keywords      │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Provider Usage Checker                    │
    │ (Combination cache per provider)            │
    │ ├─ /config/codex_usage.json                 │
    │ ├─ /config/gemini_usage.json                │
    │ └─ /config/claude_usage.json                │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Provider Filter (Hard Blocking)           │
    │ (Enforce rate limits & capacity thresholds) │
    │ ├─ CodeX: 3000 req/min, 500K tokens/min    │
    │ ├─ Gemini: 100 req/min, 100K tokens/min    │
    │ └─ Claude: 1000 req/min, 300K tokens/min   │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Provider Recommender                      │
    │ (Intelligent fallback cascade)              │
    │ ├─ Primary provider available? Use it       │
    │ ├─ Primary blocked? Use lowest-cost available│
    │ └─ All blocked? Recommend lowest-cost + ETA │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Cost Optimizer                            │
    │ (Route to cheapest appropriate provider)    │
    │ ├─ Task cost estimation                     │
    │ ├─ Daily budget tracking                    │
    │ └─ Cost-aware fallback ranking              │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Agent Dispatcher                          │
    │ (Select from 54-agent pool)                 │
    │ ├─ Provider specialization match            │
    │ ├─ Task type specialization match           │
    │ └─ Agent availability check                 │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Concurrent Executor (batchtools)          │
    │ (Execute with performance optimization)     │
    │ ├─ Batch similar tasks                      │
    │ ├─ Parallel execution (300% gains)          │
    │ └─ Progress aggregation                     │
    └────────────┬────────────────────────────────┘
                 │
    ┌────────────▼────────────────────────────────┐
    │   Audit Trail Logger                        │
    │ (JSONL format - provider_recommendations.jsonl)│
    │ ├─ Provider selection reasoning             │
    │ ├─ Cost tracking                            │
    │ ├─ Execution time metrics                   │
    │ └─ Success/failure outcomes                 │
    └────────────┬────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │  Final Result  │
         │  + Metrics     │
         └────────────────┘
```

### 1.2 Provider Profiles

Each provider has distinct characteristics that influence routing decisions:

```json
{
  "providers": {
    "codex": {
      "name": "OpenAI Codex",
      "specializations": ["code_generation", "code_review", "refactoring", "debugging"],
      "strong_keywords": ["implement", "generate", "refactor", "fix", "debug", "optimize"],
      "weak_keywords": ["reasoning", "analysis", "strategy", "planning"],
      "rate_limits": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 500000,
        "cost_per_1k_tokens": 0.002,
        "cost_per_request": 0.00001
      },
      "hard_block_threshold": 85,
      "cost_tier": "budget",
      "fallback_order": [1, 2]
    },
    "gemini": {
      "name": "Google Gemini",
      "specializations": ["analysis", "reasoning", "research", "documentation", "explanation"],
      "strong_keywords": ["analyze", "explain", "research", "understand", "document"],
      "weak_keywords": ["generate_code", "syntax", "implementation"],
      "rate_limits": {
        "requests_per_minute": 100,
        "tokens_per_minute": 100000,
        "cost_per_1k_tokens": 0.0015,
        "cost_per_request": 0.00002
      },
      "hard_block_threshold": 80,
      "cost_tier": "budget",
      "fallback_order": [0, 2]
    },
    "claude": {
      "name": "Claude 3.5 Max",
      "specializations": ["complex_reasoning", "architecture", "design", "strategic_planning", "multi_step"],
      "strong_keywords": ["architecture", "design", "strategy", "planning", "complex"],
      "weak_keywords": ["quick", "simple", "check", "status"],
      "rate_limits": {
        "requests_per_minute": 1000,
        "tokens_per_minute": 300000,
        "cost_per_1k_tokens": 0.006,
        "cost_per_request": 0.00003
      },
      "hard_block_threshold": 80,
      "cost_tier": "premium",
      "fallback_order": [0, 1]
    }
  }
}
```

---

## 2. Task Classification Engine

### 2.1 Classification Algorithm

```bash
# Pseudo-code for task classification
FUNCTION classify_task(task_description):
    task_lower = LOWERCASE(task_description)

    # Provider scoring (0-100)
    codex_score = 0
    gemini_score = 0
    claude_score = 0

    # Keyword matching (provider-specific strength keywords)
    FOR each keyword in codex_strong_keywords:
        IF keyword in task_lower:
            codex_score += 15

    FOR each keyword in gemini_strong_keywords:
        IF keyword in task_lower:
            gemini_score += 15

    FOR each keyword in claude_strong_keywords:
        IF keyword in task_lower:
            claude_score += 15

    # Word count adjustment
    word_count = COUNT_WORDS(task_description)
    IF word_count > 100:
        claude_score += 10  # Complex reasoning
    IF word_count < 10:
        codex_score += 5   # Simple task, code-focused

    # Task length impact
    char_count = COUNT_CHARACTERS(task_description)
    IF char_count > 500:
        gemini_score += 10  # Analysis of complex problem
        claude_score += 5

    # Penalty for weak keywords (presence in task suggests poor fit)
    FOR each keyword in codex_weak_keywords:
        IF keyword in task_lower:
            codex_score -= 10

    FOR each keyword in gemini_weak_keywords:
        IF keyword in task_lower:
            gemini_score -= 10

    FOR each keyword in claude_weak_keywords:
        IF keyword in task_lower:
            claude_score -= 10

    # Normalize scores (0-100)
    scores = NORMALIZE([codex_score, gemini_score, claude_score])

    # Determine primary and fallback providers
    primary_provider = PROVIDER_BY_HIGHEST_SCORE(scores)
    fallback_chain = SORTED_BY_SCORE(scores, exclude=primary_provider)

    RETURN {
        "primary_provider": primary_provider,
        "primary_score": scores[primary_provider],
        "fallback_chain": fallback_chain,
        "all_scores": {
            "codex": scores["codex"],
            "gemini": scores["gemini"],
            "claude": scores["claude"]
        }
    }
```

### 2.2 Example Classifications

| Task | Primary | Primary Score | Reason |
|------|---------|---------------|--------|
| "Implement user authentication with JWT" | Codex | 92 | Keywords: implement, code generation, authentication pattern |
| "Analyze market trends in energy sector" | Gemini | 88 | Keywords: analyze, research, complex reasoning about domain |
| "Design distributed system architecture" | Claude | 95 | Keywords: design, architecture, complex multi-step strategic planning |
| "Fix the bug in data loader" | Codex | 87 | Keywords: fix, debugging, code-specific issue |
| "Explain OAuth2 flow" | Gemini | 85 | Keywords: explain, documentation, conceptual understanding |

---

## 3. Provider Capacity Management

### 3.1 Independent Usage Tracking

Each provider maintains separate usage tracking with provider-specific hard block thresholds:

```json
// config/codex_usage.json
{
  "timestamp": "2025-01-11T10:30:00Z",
  "requests_used": 2500,
  "requests_limit": 3000,
  "requests_percent": 83,
  "tokens_used": 450000,
  "tokens_limit": 500000,
  "tokens_percent": 90,
  "cost_today": 12.50,
  "daily_budget": 100.00,
  "session_started": "2025-01-11T08:00:00Z"
}
```

### 3.2 Hard Blocking Rules

**Codex (Code Generation Specialist):**
- Block at: ≥85% requests OR ≥90% tokens
- Reason: Highest token consumption; early block prevents overage fees
- Fallback: Gemini (analysis) or Claude (if strategic planning needed)

**Gemini (Analysis Specialist):**
- Block at: ≥80% requests OR ≥85% tokens
- Reason: Low rate limits; restrictive blocking necessary
- Fallback: Codex (if code-related) or Claude (if strategic)

**Claude (Strategic Planning):**
- Block at: ≥80% requests OR ≥80% tokens
- Reason: Premium service; maintain availability for complex tasks
- Fallback: Gemini (analysis) or Codex (implementation)

### 3.3 Filtering Algorithm

```bash
FUNCTION filter_available_providers():
    available = []

    # Check CodeX capacity
    IF codex_requests_percent < 85 AND codex_tokens_percent < 90:
        available.add("codex")

    # Check Gemini capacity
    IF gemini_requests_percent < 80 AND gemini_tokens_percent < 85:
        available.add("gemini")

    # Check Claude capacity
    IF claude_requests_percent < 80 AND claude_tokens_percent < 80:
        available.add("claude")

    # Check daily budget
    FOR provider in available:
        daily_cost = provider.cost_today
        daily_budget = provider.daily_budget
        remaining_budget = daily_budget - daily_cost

        IF remaining_budget < provider.min_cost_per_request:
            available.remove(provider)
            LOG("Provider blocked: budget exceeded")

    RETURN available
```

---

## 4. Provider Recommendation Engine

### 4.1 Decision Tree

```
START: User submits task
│
├─ CLASSIFY task → primary provider + fallback chain
│
├─ CHECK primary provider availability
│  ├─ YES: Use primary provider
│  │       Reason: "Primary provider available"
│  │       Cost estimate, execution time, show alternatives
│  │
│  └─ NO: Check fallback chain
│         │
│         ├─ Fallback 1 available?
│         │  ├─ YES: Use Fallback 1
│         │  │       Reason: "Primary blocked, using fallback"
│         │  │
│         │  └─ NO: Check Fallback 2
│         │         │
│         │         ├─ Fallback 2 available?
│         │         │  ├─ YES: Use Fallback 2
│         │         │  │       Reason: "Both primary and Fallback 1 blocked"
│         │         │  │
│         │         │  └─ NO: ALL BLOCKED
│         │         │         │
│         │         │         ├─ Find lowest-cost available overall
│         │         │         │  Reason: "Emergency: All providers blocked"
│         │         │         │  Show: Time to reset (next hour when rate windows clear)
│         │         │         │  Show: Cost impact
│         │         │         │  Show: Recommended wait time
│         │         │         │
│         │         │         └─ Recommend emergency provider
│
├─ COST COMPARISON
│  ├─ Estimate task cost for recommended provider
│  ├─ Compare to fallbacks (show cost difference)
│  ├─ Show daily budget status
│  └─ Alert if would exceed daily budget
│
├─ SELECT AGENT from 54-agent pool
│  ├─ Match provider specialization
│  ├─ Match task type
│  └─ Check agent availability
│
├─ DISPLAY RECOMMENDATION
│  ├─ Provider: [RECOMMENDED]
│  ├─ Primary score: XX%
│  ├─ Availability: ✅ Available
│  ├─ Cost estimate: $X.XX
│  ├─ Daily budget status: $XX.XX / $YYY.YY used
│  ├─ Alternatives: [Fallback options with costs]
│  └─ Agent: [Selected agent]
│
└─ LOG RECOMMENDATION
   ├─ JSON: provider_recommendations.jsonl entry
   ├─ Task classification scores
   ├─ Cost estimate
   ├─ Provider availability status
   └─ Execution outcome (after completion)

END: Provider selected, agent assigned
```

### 4.2 Output Format

**Minimal User Display:**
```
═══════════════════════════════════════════════════
  Multi-Provider Recommendation
═══════════════════════════════════════════════════

Task Classification:
  Primary: Claude (95%)
  Fallbacks: CodeX (72%), Gemini (68%)

Recommended Provider: CLAUDE
✅ Available (72% capacity)

Cost Estimate: $0.45
Daily Budget: $12.50 / $100.00 (12.5%)

Alternatives:
  CodeX: $0.12 (85% capacity - high)
  Gemini: $0.18 (78% capacity)

Agent Selected: claude-architect (specialization: system design)

═══════════════════════════════════════════════════

Proceed with Claude via claude-architect agent? (y/n):
```

**Detailed Log Entry (JSONL):**
```json
{
  "timestamp": "2025-01-11T10:30:00Z",
  "task": "Design distributed system architecture for data pipeline",
  "task_classification": {
    "primary_provider": "claude",
    "primary_score": 95,
    "fallback_chain": ["codex", "gemini"],
    "scores": {
      "claude": 95,
      "codex": 72,
      "gemini": 68
    }
  },
  "provider_availability": {
    "claude": {
      "requests": "720/1000 (72%)",
      "tokens": "240000/300000 (80%)",
      "available": true,
      "daily_cost_so_far": "$8.40",
      "daily_budget": "$100.00"
    },
    "codex": {
      "requests": "2550/3000 (85%)",
      "tokens": "459000/500000 (92%)",
      "available": false,
      "reason": "High token usage (92%)"
    },
    "gemini": {
      "requests": "78/100 (78%)",
      "tokens": "85000/100000 (85%)",
      "available": true,
      "daily_cost_so_far": "$1.20",
      "daily_budget": "$50.00"
    }
  },
  "recommendation": {
    "provider": "claude",
    "reason": "Primary provider available, optimal for architectural reasoning",
    "cost_estimate": "$0.45",
    "execution_time_estimate": "30-45 seconds"
  },
  "agent_assigned": {
    "agent_id": "claude-architect",
    "specialization": "system design, architecture planning",
    "model": "claude-3.5-max",
    "reason": "Specialization match + provider specialization"
  },
  "alternatives": [
    {
      "provider": "codex",
      "reason": "Primary blocked (high token usage)",
      "cost": "$0.12",
      "available": false
    },
    {
      "provider": "gemini",
      "reason": "Analysis alternative",
      "cost": "$0.18",
      "available": true
    }
  ]
}
```

---

## 5. Agent Dispatcher Integration

### 5.1 Mapping Providers to Agent Specializations

```json
{
  "provider_to_agents": {
    "codex": [
      "code-generator",
      "code-reviewer",
      "debugger",
      "refactorer",
      "test-generator"
    ],
    "gemini": [
      "analyst",
      "researcher",
      "explainer",
      "documentation-writer",
      "pattern-recognizer"
    ],
    "claude": [
      "architect",
      "strategist",
      "designer",
      "complex-reasoner",
      "planner"
    ]
  },
  "agent_pool_54_agents": {
    "core_development": [
      "coder", "reviewer", "tester", "planner", "researcher"
    ],
    "sparc_methodology": [
      "specification", "pseudocode", "architecture", "refinement"
    ],
    "github_integration": [
      "pr-manager", "code-review-swarm", "issue-tracker"
    ],
    "specialized": [
      "backend-dev", "ml-developer", "cicd-engineer", "system-architect",
      "security-specialist", "performance-optimizer", "data-analyst"
    ],
    "coordination": [
      "hierarchical-coordinator", "mesh-coordinator", "adaptive-coordinator",
      "swarm-manager", "task-orchestrator"
    ]
  }
}
```

### 5.2 Agent Selection Algorithm

```bash
FUNCTION select_agent(provider, task_classification, task_type):
    # Step 1: Get provider's agent specializations
    provider_agents = get_provider_agents(provider)

    # Step 2: Get task-specific agent from 54-agent pool
    task_agents = get_agents_for_task_type(task_type)

    # Step 3: Find intersection (provider + task match)
    candidate_agents = INTERSECTION(provider_agents, task_agents)

    # Step 4: Check availability
    available_agents = FILTER_BY_AVAILABILITY(candidate_agents)

    # Step 5: Select based on score
    selected_agent = SELECT_HIGHEST_SCORE(available_agents)

    RETURN selected_agent

    # Fallback if no perfect match
    IF EMPTY(available_agents):
        selected_agent = SELECT_FROM_POOL(provider_agents, TASK_TYPE)

    RETURN selected_agent
```

### 5.3 Example Assignments

| Task | Primary | Agent Assigned | Reason |
|------|---------|---|---|
| "Implement authentication" | CodeX | code-generator | Provider specialty (CodeX) + task type (generation) |
| "Design system architecture" | Claude | system-architect | Provider specialty (Claude) + task type (design/planning) |
| "Analyze performance metrics" | Gemini | data-analyst | Provider specialty (Gemini) + task type (analysis) |
| "Review pull request" | CodeX | code-reviewer | Provider specialty (CodeX) + task type (review) |

---

## 6. Concurrent Execution with Batchtools

### 6.1 Batch Optimization Strategy

**Performance Gains:**
- Single execution: 100% baseline
- Batched execution (5 tasks): 300% performance gain (5 tasks in parallel instead of sequential)
- Optimal batch size: 4-10 tasks depending on provider rate limits

### 6.2 Batching Algorithm

```bash
FUNCTION batch_execute_tasks(tasks):
    # Group tasks by provider
    codex_tasks = []
    gemini_tasks = []
    claude_tasks = []

    FOR each task in tasks:
        classification = classify_task(task.description)
        primary_provider = classification.primary_provider

        SWITCH primary_provider:
            CASE "codex":
                codex_tasks.append(task)
            CASE "gemini":
                gemini_tasks.append(task)
            CASE "claude":
                claude_tasks.append(task)

    # Execute provider-specific batches in parallel
    PARALLEL_EXECUTE:
        execute_provider_batch("codex", codex_tasks)
        execute_provider_batch("gemini", gemini_tasks)
        execute_provider_batch("claude", claude_tasks)

    # Aggregate results
    results = COLLECT_ALL_RESULTS()

    RETURN results

FUNCTION execute_provider_batch(provider, tasks):
    # Sub-batch by token cost to avoid rate limits
    batch_size = CALCULATE_BATCH_SIZE(provider, tasks)

    FOR each batch of batch_size in tasks:
        EXECUTE_BATCH_PARALLEL(provider, batch)
        UPDATE_PROVIDER_USAGE(provider)
        LOG_BATCH_EXECUTION(provider, batch)
```

### 6.3 Performance Metrics

| Scenario | Sequential | Parallel | Gain |
|----------|-----------|----------|------|
| 5 small tasks | 25s | 8.3s | 3x faster |
| 10 medium tasks | 120s | 40s | 3x faster |
| 20 complex tasks | 400s | 133s | 3x faster |

**Batchtools Integration:**
- Use `scripts/batchtools/batch_runner.sh` for parallel execution
- Provides job queuing, resource pooling, result aggregation
- Maintains per-provider rate limit compliance

---

## 7. Real-Time Usage Polling

### 7.1 Provider-Specific APIs

**CodeX Usage Polling:**
```bash
# OpenAI API call for current token usage
curl -s https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq '.data.tokens_used_today'
```

**Gemini Usage Polling:**
```bash
# Google Cloud Quotas API
curl -s https://serviceusage.googleapis.com/v1/projects/{project}/services/aiplatform.googleapis.com/quotas \
  -H "Authorization: Bearer $GOOGLE_API_TOKEN" | jq '.quotas[].usage'
```

**Claude Usage Polling:**
```bash
# Anthropic API usage endpoint (when available)
curl -s https://api.anthropic.com/v1/usage \
  -H "x-api-key: $ANTHROPIC_API_KEY" | jq '.usage'
```

### 7.2 Cache Strategy (Per Provider)

- **Cache TTL:** 15 minutes (shorter than Phase 1's 1-hour TTL due to higher volatility)
- **Update Frequency:**
  - Automatic refresh every 15 minutes
  - On-demand refresh when approaching hard block threshold
  - Manual refresh via CLI command
- **Fallback:** Prompt user to manually enter usage if API unavailable

---

## 8. Cost Optimization Engine

### 8.1 Daily Budget Tracking

```json
{
  "daily_budget": {
    "total": "$100.00",
    "allocation": {
      "codex": "$30.00",
      "gemini": "$40.00",
      "claude": "$30.00"
    },
    "current_usage": {
      "codex": "$12.50 (42% of allocated)",
      "gemini": "$8.30 (21% of allocated)",
      "claude": "$15.20 (51% of allocated)"
    },
    "alerts": {
      "50_percent": "$50.00 (PASSED)",
      "75_percent": "$75.00 (WARNING - approaching)",
      "90_percent": "$90.00 (CRITICAL)"
    }
  }
}
```

### 8.2 Cost-Aware Routing

**Decision Factor:** When multiple providers can handle task, route to lowest-cost option

```bash
FUNCTION cost_aware_select_provider(available_providers):
    providers_with_costs = []

    FOR each provider in available_providers:
        task_cost = estimate_task_cost(task, provider)
        providers_with_costs.append({
            provider: provider,
            cost: task_cost,
            remaining_budget: provider.daily_budget - provider.cost_today
        })

    # Sort by cost (lowest first), then by quality (higher score first)
    sorted = SORT_BY([cost ASC, quality_score DESC])

    # Select lowest-cost that won't exceed budget
    FOR each option in sorted:
        IF option.cost <= option.remaining_budget:
            RETURN option.provider

    # If all would exceed budget, recommend cheapest and show impact
    cheapest = sorted[0]
    RETURN cheapest
```

### 8.3 Cost Alerts

```
⚠️  WARNING: Daily budget at 75% ($75.00 / $100.00)
    Remaining budget: $25.00
    Recommended action: Switch to budget-tier providers (CodeX, Gemini)

🔴 CRITICAL: Daily budget at 90% ($90.00 / $100.00)
    Remaining budget: $10.00
    Recommended action: Defer non-critical tasks to next day
    Next reset: Tomorrow 00:00 UTC
```

---

## 9. Fallback and Recovery Strategies

### 9.1 Graceful Degradation

```
Provider Hierarchy (by quality for complex tasks):
1. Claude (Strategic, complex reasoning)
2. CodeX (Code generation, can delegate to ChatGPT-4 if needed)
3. Gemini (Analysis, good for research/explanation)

Graceful degradation path:
Claude unavailable → CodeX → Gemini
CodeX unavailable → Claude (if reasoning-heavy) or Gemini (if analysis-heavy)
Gemini unavailable → CodeX (if code-focused) or Claude
```

### 9.2 Rate Limit Recovery

When provider is rate-limited:

```bash
FUNCTION handle_rate_limit_error(provider, error):
    # Calculate reset time based on provider
    reset_time = calculate_reset_time(provider, error.retry_after)

    # Log the rate limit hit
    LOG("Rate limit hit: provider=$provider, reset_in=$reset_time")

    # Get fallback provider
    fallback = get_fallback_provider(provider)

    # Retry with fallback
    IF retry_count < MAX_RETRIES:
        RETURN retry_with_provider(task, fallback)
    ELSE
        RETURN queue_task_for_later(task, reset_time)
```

### 9.3 Provider Outage Handling

```
If a provider is completely unavailable:

1. Detect: Multiple consecutive failures (3+ attempts)
2. Log: "Provider outage detected"
3. Route: Send all tasks to healthy providers
4. Alert: Notify user of changed provider
5. Recover: Monitor for provider recovery (polling every 5 min)
6. Resume: Return to normal routing when recovered
```

---

## 10. Audit Trail and Logging

### 10.1 Recommendation Log Format (JSONL)

```json
{
  "timestamp": "2025-01-11T10:30:00Z",
  "session_id": "session-2025-01-11-001",
  "task_id": "task-12345",
  "task_description": "Design distributed system architecture for data pipeline",
  "task_classification": {
    "primary_provider": "claude",
    "primary_score": 95,
    "fallback_chain": ["codex", "gemini"],
    "all_scores": {
      "claude": 95,
      "codex": 72,
      "gemini": 68
    }
  },
  "provider_state_at_recommendation": {
    "claude": {
      "requests_percent": 72,
      "tokens_percent": 80,
      "cost_today": "$8.40",
      "daily_budget": "$100.00",
      "available": true
    },
    "codex": {
      "requests_percent": 85,
      "tokens_percent": 92,
      "cost_today": "$12.50",
      "daily_budget": "$30.00",
      "available": false,
      "block_reason": "tokens_percent >= 90%"
    },
    "gemini": {
      "requests_percent": 78,
      "tokens_percent": 85,
      "cost_today": "$1.20",
      "daily_budget": "$40.00",
      "available": true
    }
  },
  "recommendation": {
    "provider": "claude",
    "provider_reason": "primary available",
    "cost_estimate": "$0.45",
    "agent_assigned": "claude-architect",
    "agent_reason": "system design specialization"
  },
  "execution_metrics": {
    "status": "success",
    "start_time": "2025-01-11T10:30:15Z",
    "end_time": "2025-01-11T10:31:05Z",
    "execution_time_seconds": 50,
    "tokens_used": 8500,
    "cost_actual": "$0.51",
    "cost_estimate_vs_actual": "$0.06 over estimate"
  }
}
```

### 10.2 Log Analysis and Patterns

**Sample Queries:**
```bash
# Provider usage distribution
jq '.recommendation.provider' logs/provider_recommendations.jsonl | sort | uniq -c

# Cost tracking by day
jq '.timestamp, .execution_metrics.cost_actual' logs/provider_recommendations.jsonl | paste - - | cut -d'T' -f1 | uniq -c

# Failed recommendations (fallback activations)
jq 'select(.recommendation.provider_reason != "primary available")' logs/provider_recommendations.jsonl | wc -l

# Average execution time by provider
jq '[.recommendation.provider, .execution_metrics.execution_time_seconds] | @csv' logs/provider_recommendations.jsonl | awk -F',' '{sum[$1]+=$2; count[$1]++} END {for (p in sum) print p, sum[p]/count[p]}'
```

---

## 11. Four-Phase Implementation Roadmap

### Phase 1: Infrastructure Setup (Weeks 1-2)

**Deliverables:**
- Provider profile JSON files (codex_profile.json, gemini_profile.json, claude_profile.json)
- Independent usage tracking for three providers (config/*.json files)
- Task classification engine (lib/task_classifier.sh)
- Provider filtering with hard blocking (lib/provider_filter.sh)
- Usage polling integration (three provider API handlers)

**Testing:**
- Verify usage tracking accuracy
- Test classification algorithm against 50+ sample tasks
- Confirm hard block thresholds are enforced

### Phase 2: Routing and Dispatch (Weeks 2-3)

**Deliverables:**
- Provider recommendation engine (lib/provider_recommender.sh)
- Cost estimation and tracking (lib/cost_optimizer.sh)
- Agent dispatcher (lib/agent_dispatcher.sh)
- Multi-provider orchestrator (orchestrate.sh - entry point)
- Integration with 54-agent pool

**Testing:**
- Verify recommendations match task classifications
- Test cost tracking against actual API usage
- Confirm agent assignments

### Phase 3: Optimization & Monitoring (Week 3-4)

**Deliverables:**
- Concurrent execution with batchtools (lib/batch_executor.sh)
- Real-time usage polling (lib/usage_poller.sh)
- Swarm coordination for complex tasks (lib/swarm_coordinator.sh)
- Detailed logging and audit trail
- Monitoring dashboard (HTML interactive reporting)

**Testing:**
- Measure performance gains (target: 3x for batched tasks)
- Verify usage polling accuracy
- Test audit trail JSONL logging

### Phase 4: Advanced Features (Week 4 - Ongoing)

**Deliverables:**
- Predictive planning (estimate costs before execution)
- Adaptive selection (learn from historical success rates)
- Rollback mechanisms (abort if cost exceeds budget)
- A/B testing framework (compare provider recommendations)
- Self-learning optimization (refine task classification over time)

**Testing:**
- Verify predictive accuracy
- Test rollback functionality
- Measure A/B test result reliability

---

## 12. Migration Path from Phase 1

### 12.1 Backward Compatibility

Phase 2 builds on Phase 1 infrastructure:

```
Phase 1 (Claude-only):
  scripts/monitoring/suggest_model.sh
  scripts/monitoring/lib/*.sh
  config/model_usage.json
  logs/recommendations.jsonl

Phase 2 (Multi-provider) adds:
  scripts/routing/orchestrate.sh (new entry point)
  scripts/routing/lib/*.sh (provider-specific helpers)
  config/codex_usage.json (new)
  config/gemini_usage.json (new)
  config/claude_usage.json (migrated from Phase 1)
  logs/provider_recommendations.jsonl (new)

Integration point:
  CLAUDE.md updated to reference both suggest_model.sh (Claude) and orchestrate.sh (Multi-provider)
```

### 12.2 User Experience Flow

**Phase 1 Users:**
```bash
# Continue using Phase 1 (Claude-only, unchanged)
./scripts/monitoring/suggest_model.sh digitalmodel "Implement feature"
→ Recommends Claude model with usage awareness
```

**Phase 2 Early Adopters:**
```bash
# Opt-in to multi-provider orchestration
./scripts/routing/orchestrate.sh digitalmodel "Implement feature"
→ Recommends best provider (Claude, CodeX, or Gemini)
```

**Phase 2 Full Migration:**
```bash
# Both workflows supported for 6 months
# Then suggest Phase 1 → Phase 2 migration
# Update AI_USAGE_GUIDELINES.md with Phase 2 best practices
```

---

## 13. Integration with Existing Infrastructure

### 13.1 54-Agent Pool Mapping

The 54 agents across 23 categories are automatically leveraged:

```
Agent Selection Process:
1. Provider recommender suggests provider (CodeX, Gemini, or Claude)
2. Dispatcher looks up provider's compatible agents
3. Selects from 54-agent pool based on:
   - Task type (code generation, analysis, architecture, etc.)
   - Provider specialization (what agents work best with provider)
   - Agent availability (not already in use)
   - Agent specialization score vs. task
4. Assigns optimal agent to execute task
```

### 13.2 Batchtools Integration

```
Concurrent Execution Benefits:
- Single task: ~30 seconds (baseline)
- 5 tasks batched: ~50 seconds (3x faster per task)
- 10 tasks batched: ~100 seconds (3x faster per task)
- Performance multiplier: 300% (3x speedup)

Usage:
./scripts/batchtools/batch_runner.sh --parallel 5 < task_queue.json
```

### 13.3 CLAUDE.md Updates

```markdown
## Model Selection

### Option 1: Claude-Only (Phase 1)
Use when you have Claude Max credentials and want simplicity.
./scripts/monitoring/suggest_model.sh <repo> "<task>"

### Option 2: Multi-Provider (Phase 2)
Use when you have OpenAI Codex + Google Gemini + Claude credentials.
./scripts/routing/orchestrate.sh <repo> "<task>"

Choose based on your available API credentials and optimization goals.
```

---

## 14. Success Criteria

### 14.1 Phase 2 Complete Implementation

- [ ] All three providers configured and integrated
- [ ] Task classification algorithm operating with >85% accuracy
- [ ] Hard blocking enforced correctly for all three providers
- [ ] Cost tracking accurate (within 5% of actual API bills)
- [ ] Batchtools integration delivering 3x performance gains
- [ ] Audit trail JSONL complete with all metadata
- [ ] 54-agent pool agents correctly assigned
- [ ] Documentation complete and tested
- [ ] Fallback chains working in all scenarios
- [ ] User-facing recommendation output minimal and clear
- [ ] Monitoring dashboard operational with real-time updates
- [ ] Daily budget alerts functioning
- [ ] Swarm coordination for complex tasks tested

### 14.2 Performance Targets

- **Task Classification:** 95%+ accuracy, <100ms execution
- **Recommendation Engine:** <500ms decision time
- **Cost Estimation:** Within 10% of actual cost
- **Concurrent Execution:** 3x performance gain (5 tasks parallel)
- **Audit Logging:** <100ms per log entry
- **Provider Polling:** 15-minute cache invalidation

---

## 15. Conclusion

Phase 2 transforms Workspace Hub from a single-provider optimization system into an intelligent multi-provider orchestration platform. By extending Phase 1's proven patterns (hard blocking, intelligent fallback, audit trail) across three independent providers with distinct specializations, we enable:

1. **Cost Optimization:** Route tasks to lowest-cost appropriate provider
2. **Performance Optimization:** 3x gains through concurrent execution via batchtools
3. **Resilience:** Graceful degradation when providers are capacity-constrained
4. **Intelligence:** Task classification automatically routes to optimal provider
5. **Observability:** Complete audit trail enables historical analysis and optimization
6. **Scalability:** Leverages 54-agent pool for automated agent assignment
7. **User Experience:** Minimal output while detailed logging maintains transparency

The system is designed for incremental adoption—Phase 1 users continue uninterrupted while Phase 2 early adopters gain multi-provider benefits through opt-in CLI (`orchestrate.sh`).

---

**Design Complete - Ready for Phase 1 Infrastructure Implementation**
**Next Step: Create provider profile configurations and usage tracking files**
**Estimated Implementation Timeline: 4 weeks across 4 phases**
