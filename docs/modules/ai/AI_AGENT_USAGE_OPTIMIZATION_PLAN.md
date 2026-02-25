# AI Agent Usage Optimization Plan

> **Purpose:** Optimize Claude usage across 26 repositories to maximize efficiency and stay within usage limits
> **Current Status:** Sonnet usage at 79% (high), overall at 52%
> **Target:** Reduce Sonnet usage to <60%, maintain overall <70%
> **Version:** 1.0.0
> **Last Updated:** 2025-01-09

## Executive Summary

Your workspace-hub manages 26 repositories (15 Work, 11 Personal) with heavy reliance on Claude 3.5 Sonnet (79% of weekly limit). This plan provides a strategic framework to:

1. **Distribute model usage** intelligently across Opus, Sonnet, and Haiku
2. **Optimize prompt patterns** for efficiency and reduced iterations
3. **Implement monitoring** to track and prevent limit breaches
4. **Deploy standards** consistently across all repositories

**Expected Impact:**
- **-30% Sonnet usage** (79% → <55%)
- **+25% efficiency** through better model selection
- **-40% back-and-forth** through optimized prompts
- **+60% reproducibility** through standardized patterns

---

## Quick Start: Immediate Actions

**Step 1: Install Tools** (2 minutes)
```bash
# Tools are already installed in workspace-hub
# Verify they're executable:
ls -lah ./scripts/monitoring/suggest_model.sh
ls -lah ./scripts/monitoring/check_claude_usage.sh
```

**Step 2: Check Current Usage** (1 minute)
```bash
# Check Claude usage dashboard
# → Visit: https://claude.ai/settings/usage
# → Note your Sonnet percentage

# Or use the monitoring script:
./scripts/monitoring/check_claude_usage.sh check
```

**Step 3: Get Model Recommendation for Your Next Task** (30 seconds)
```bash
# Before starting any task, get intelligent recommendation:
./scripts/monitoring/suggest_model.sh <repo-name> "<your task description>"

# Example:
./scripts/monitoring/suggest_model.sh digitalmodel "Add user authentication"
# → Analyzes task → Recommends model → Explains reasoning → Optionally logs
```

**Step 4: Use Recommended Model** (Your work time)
- Use the recommended model (Opus/Sonnet/Haiku)
- If you override, note why (helps refine the system)
- The tool optionally logs your selection for tracking

**Step 5: Review Daily** (2 minutes at end of day)
```bash
# Check today's model distribution:
./scripts/monitoring/check_claude_usage.sh today

# Goal: 30% Opus / 40% Sonnet / 30% Haiku
```

**🎯 That's it!** The suggest_model.sh tool automates 80% of the decision-making. You focus on your work.

**📖 Full Documentation:**
- Quick reference card: @docs/CLAUDE_MODEL_SELECTION_QUICK_REFERENCE.md
- Automation guide: @docs/AI_MODEL_SELECTION_AUTOMATION.md
- Implementation roadmap: @docs/AI_OPTIMIZATION_IMPLEMENTATION_SUMMARY.md

---

## 1. Model Selection Strategy Matrix

### 1.1 Task-Based Model Selection

| Task Type | Model | Rationale | Usage Limit |
|-----------|-------|-----------|-------------|
| **Complex reasoning & planning** | Opus | Best for multi-step logic, architecture decisions | 30% of tasks |
| **Code generation & review** | Sonnet | Fast, high quality for standard coding | 40% of tasks |
| **Quick queries & summaries** | Haiku | Sufficient for simple tasks, 5x faster | 30% of tasks |
| **Documentation writing** | Sonnet | Balance of quality and speed | Included in 40% |
| **Test generation** | Haiku | Pattern-based, can use faster model | Included in 30% |
| **Refactoring analysis** | Opus | Complex decision-making required | Included in 30% |

### 1.2 Repository Category Guidelines

#### Work Repositories (15 repos) - Higher quality priority

```yaml
# digitalmodel, energy, frontierdeepwater, etc.
primary_model: Opus     # 60% of work tasks
fallback_model: Sonnet  # 30% of work tasks
quick_tasks: Haiku      # 10% of work tasks

use_cases:
  - Architecture decisions: Opus
  - Production code: Opus or Sonnet
  - Documentation: Sonnet
  - Quick checks: Haiku
```

#### Personal Repositories (11 repos) - Efficiency priority

```yaml
# aceengineer-admin, hobbies, investments, etc.
primary_model: Sonnet   # 50% of personal tasks
fallback_model: Haiku   # 40% of personal tasks
complex_only: Opus      # 10% of personal tasks

use_cases:
  - Prototyping: Sonnet or Haiku
  - Experiments: Haiku
  - Production features: Sonnet
  - Complex algorithms: Opus
```

### 1.3 Model Selection Decision Tree

```
┌─────────────────────────────────────┐
│ Is this a Work repository?          │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO (Personal)
    │           │
    ▼           ▼
┌─────────┐  ┌──────────┐
│ Complex │  │ Simple   │
│ task?   │  │ task?    │
└─┬───┬───┘  └─┬───┬────┘
  │   │        │   │
 YES  NO      YES  NO
  │   │        │   │
  ▼   ▼        ▼   ▼
┌─────┐┌──────┐┌─────┐┌──────┐
│OPUS ││SONNET││SONNET││HAIKU │
└─────┘└──────┘└─────┘└──────┘
```

### 1.4 Task Complexity Assessment

**Use Opus for:**
- Multi-file refactoring across >5 files
- Architectural pattern decisions
- Complex algorithm design (>100 lines)
- Cross-repository coordination planning
- Security-critical code review
- Performance optimization strategies

**Use Sonnet for:**
- Standard feature implementation
- Code review (single PR)
- Test generation
- Documentation writing
- Bug fixing (standard complexity)
- Configuration updates

**Use Haiku for:**
- File existence checks
- Simple grep/search operations
- Quick status updates
- Log analysis (pattern matching)
- Template generation
- Format validation
- Summary generation (<500 words)

---

## 2. Prompt Pattern Optimization

### 2.1 Eliminate Ineffective Patterns

#### ❌ Anti-Pattern: Description-Only Requests

```
BAD: "Can you describe what this script does?"
Result: No actionable output, wastes tokens
Rating: ⭐ (loses 20% time)
```

#### ✅ Optimized Pattern: Execution-Ready Requests

```
GOOD: "Prepare YAML input for this script and provide the execution command."
Result: Working configuration + executable command + actual results
Rating: ⭐⭐⭐⭐⭐ (saves 90% time)
```

### 2.2 Batch Operations Template

**Use this pattern for cross-repository work:**

```markdown
I need to perform the following operations across multiple repositories:

## Scope
- Repositories: [list or "all work" or "all personal"]
- Operation type: [commit/sync/test/build/deploy]

## Configuration
```yaml
operation: batch_commit
scope: work_repositories
config:
  message: "Update dependencies to latest"
  auto_push: true
  run_tests: true
```

## Expected Output
- Status report per repository
- Aggregate success/failure metrics
- Next actions if any failures

Prepare the complete workflow with:
1. Pre-flight checks
2. Execution commands
3. Verification steps
```

### 2.3 Context-First Prompts

**Provide all context upfront to reduce back-and-forth:**

```markdown
## Task Context
- Repository: digitalmodel (Work)
- Complexity: Medium
- Time sensitivity: Production hotfix
- Dependencies: None
- Testing required: Yes

## Specifications
[Full specifications here]

## Output Format
[Exact format needed]

## Constraints
[Any limitations]

Generate [specific deliverable] following this context.
```

### 2.4 Question-Driven Approach (MANDATORY)

**Per AI_AGENT_GUIDELINES.md:**

```markdown
I need to implement [feature/fix/update].

Before proceeding, please ask clarifying questions about:
1. Ambiguous requirements
2. Implementation approach options
3. Trade-offs (performance vs simplicity)
4. Edge cases and error handling
5. Testing strategy

Wait for my responses before generating code.
```

### 2.5 Model-Specific Prompt Templates

#### Opus: Complex Decision Prompts

```markdown
[OPUS TASK]

## Problem Statement
[Complex problem requiring multi-step reasoning]

## Decision Points
1. [Option A vs Option B]
2. [Trade-off analysis needed]
3. [Long-term implications]

## Expected Output
- Detailed analysis
- Recommended approach with rationale
- Implementation roadmap
- Risk assessment

Please think step-by-step through this architectural decision.
```

#### Sonnet: Standard Implementation Prompts

```markdown
[SONNET TASK]

## Feature
[Clear feature specification]

## Implementation Requirements
- [Specific requirement 1]
- [Specific requirement 2]

## Code Standards
Follow: @docs/standards/FILE_ORGANIZATION_STANDARDS.md

## Tests Required
Unit + Integration

Generate production-ready code with tests.
```

#### Haiku: Quick Task Prompts

```markdown
[HAIKU TASK - Quick Response Needed]

Check if the following files exist:
- src/module/feature.py
- tests/test_feature.py
- docs/api/feature.md

Output: JSON with file paths and existence status.
```

---

## 3. Repository-Specific Strategies

### 3.1 Work Repositories (High Priority)

#### Tier 1: Production Critical (Use Opus primarily)
- **digitalmodel** - Full-stack application (Rails + React)
- **energy** - Energy analytics platform
- **frontierdeepwater** - Marine engineering analysis

**Strategy:**
- 70% Opus, 20% Sonnet, 10% Haiku
- All production code reviewed with Opus
- Architecture changes require Opus approval
- Testing strategy designed with Opus

#### Tier 2: Development Active (Use Sonnet primarily)
- **aceengineercode** - Engineering code library
- **assetutilities** - Asset management utilities
- **worldenergydata** - Energy data analysis

**Strategy:**
- 30% Opus, 50% Sonnet, 20% Haiku
- Feature development with Sonnet
- Complex refactoring with Opus
- Quick utilities with Haiku

#### Tier 3: Maintenance Mode (Use Haiku primarily)
- **doris**, **saipem**, **OGManufacturing**
- Occasional updates only

**Strategy:**
- 10% Opus, 30% Sonnet, 60% Haiku
- Haiku for routine updates
- Sonnet for feature additions
- Opus only for major changes

### 3.2 Personal Repositories (Efficiency Priority)

#### Tier 1: Active Development
- **aceengineer-website**, **aceengineer-admin**
- Personal projects with regular updates

**Strategy:**
- 20% Opus, 40% Sonnet, 40% Haiku
- Prototype with Haiku, refine with Sonnet
- Opus for critical decisions only

#### Tier 2: Experimental
- **hobbies**, **sd-work**, **acma-projects**
- Learning and experimentation

**Strategy:**
- 5% Opus, 25% Sonnet, 70% Haiku
- Maximize Haiku usage for speed
- Sonnet for complex implementations
- Opus rarely needed

#### Tier 3: Archives
- **investments**, **sabithaandkrishnaestates**
- Minimal activity

**Strategy:**
- 0% Opus, 20% Sonnet, 80% Haiku
- Haiku for everything unless complexity demands Sonnet

---

## 4. Usage Monitoring System

### 4.1 Real-Time Monitoring Dashboard

Create a usage tracking script:

```bash
#!/bin/bash
# scripts/monitoring/claude_usage_monitor.sh

# Track Claude usage per repository and model
# Outputs: Daily/weekly reports

# Model usage breakdown
OPUS_USAGE=$(get_opus_usage)
SONNET_USAGE=$(get_sonnet_usage)
HAIKU_USAGE=$(get_haiku_usage)

# Alert thresholds
if [ "$SONNET_USAGE" -gt 70 ]; then
    echo "⚠️  Sonnet usage at ${SONNET_USAGE}% - switch to Opus/Haiku"
fi

# Generate report
cat > reports/claude_usage_$(date +%Y%m%d).md << EOF
# Claude Usage Report - $(date +%Y-%m-%d)

## Model Distribution
- Opus: ${OPUS_USAGE}%
- Sonnet: ${SONNET_USAGE}%
- Haiku: ${HAIKU_USAGE}%

## Recommendations
$(generate_recommendations)
EOF
```

### 4.2 Usage Tracking Metadata

Add to all AI-generated code:

```python
# AI Metadata
# Generated by: Claude 3.5 Sonnet
# Date: 2025-01-09
# Task: Feature implementation
# Tokens used: ~2500
# Repository: digitalmodel
```

### 4.3 Weekly Usage Review

**Tuesday Review Process** (limits reset Tuesday at 3:59 PM):

```markdown
## Weekly Claude Usage Review

### Current Metrics
- [ ] Check usage at https://claude.ai/settings/usage
- [ ] Document Opus usage: ____%
- [ ] Document Sonnet usage: ____%
- [ ] Document Haiku usage: ____%

### Analysis
- [ ] Identify high-usage repositories
- [ ] Review task types consuming most tokens
- [ ] Assess model selection effectiveness

### Adjustments
- [ ] Update model selection rules if needed
- [ ] Adjust repository tier classifications
- [ ] Optimize high-frequency prompts

### Next Week Planning
- [ ] Set target distribution: Opus 30%, Sonnet 40%, Haiku 30%
- [ ] Identify tasks to shift to lower-cost models
- [ ] Schedule complex work for early week
```

### 4.4 Automated Alerts

**Setup alerts for:**

```yaml
alerts:
  sonnet_high:
    threshold: 70%
    action: "Switch to Opus/Haiku for remaining tasks"
    notify: email

  session_high:
    threshold: 80%
    action: "Batch remaining work or pause until reset"
    notify: terminal

  weekly_approaching:
    threshold: 85%
    action: "Defer non-critical work to next week"
    notify: email + terminal
```

---

## 5. Implementation Roadmap

### Phase 1: Immediate Actions (Week 1)

- [x] Analyze current usage (DONE: 79% Sonnet, 52% overall)
- [x] Create optimization plan (THIS DOCUMENT)
- [ ] Configure model selection in workspace CLI
- [ ] Add usage tracking to `repository_sync`
- [ ] Create weekly review checklist
- [ ] Update CLAUDE.md with model selection rules

**Deliverables:**
- Model selection strategy (Section 1)
- Prompt templates (Section 2)
- Usage monitoring script (Section 4.1)

### Phase 2: Deployment (Week 2)

- [ ] Deploy optimized prompts to top 5 work repositories
- [ ] Train team (if applicable) on model selection
- [ ] Implement usage dashboard
- [ ] Set up automated alerts
- [ ] Document repository-specific strategies

**Deliverables:**
- Updated `.claude/` configuration per repo
- Usage tracking dashboard
- Alert system operational

### Phase 3: Optimization (Weeks 3-4)

- [ ] Review first week results
- [ ] Adjust model distribution based on data
- [ ] Refine prompt templates
- [ ] Expand to remaining repositories
- [ ] Establish weekly review cadence

**Deliverables:**
- Usage reduction report
- Refined model selection rules
- Best practices documentation

### Phase 4: Continuous Improvement (Ongoing)

- [ ] Weekly usage reviews every Tuesday
- [ ] Monthly optimization analysis
- [ ] Quarterly strategy updates
- [ ] Community feedback integration

**Metrics to Track:**
- Model distribution (target: 30/40/30)
- Sonnet usage trend (target: <60%)
- Task completion efficiency
- Token consumption per task type

---

## 6. Quick Reference Guide

### Daily Decision Flowchart

```
New Task → Check Repository Tier → Assess Complexity → Select Model
    ↓              ↓                      ↓                  ↓
Work/Personal   Tier 1/2/3          Simple/Medium/Complex  Haiku/Sonnet/Opus
```

### Model Selection Cheat Sheet

| Repository | Task | Model | Why |
|------------|------|-------|-----|
| digitalmodel | Architecture | Opus | Complex decisions |
| digitalmodel | Feature code | Sonnet | Standard quality |
| digitalmodel | Status check | Haiku | Quick query |
| hobbies | Prototype | Haiku | Speed matters |
| hobbies | Refactor | Sonnet | Needs quality |
| energy | Data analysis | Opus | Complex logic |

### Usage Optimization Checklist

**Before Starting Work:**
- [ ] Check current usage at claude.ai/settings/usage
- [ ] Note Sonnet percentage
- [ ] Plan model distribution for session
- [ ] Batch similar tasks together

**During Work:**
- [ ] Use Haiku for quick queries
- [ ] Reserve Sonnet for standard implementations
- [ ] Use Opus only for complex decisions
- [ ] Batch related questions

**End of Session:**
- [ ] Review usage increase
- [ ] Update usage log
- [ ] Plan next session if approaching limits

---

## 7. Success Metrics

### Target Metrics (4 weeks)

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Sonnet usage | 79% | <60% | Weekly limit check |
| Overall usage | 52% | <70% | Weekly limit check |
| Session efficiency | 40% | <60% | Session completion |
| Model distribution | Unbalanced | 30/40/30 | Weekly breakdown |
| Task success rate | Unknown | >90% | Manual tracking |

### Key Performance Indicators

1. **Usage Efficiency**
   - Tokens per task (lower is better)
   - Tasks completed per session (higher is better)
   - Back-and-forth iterations (lower is better)

2. **Model Distribution**
   - Opus: 30% of tasks
   - Sonnet: 40% of tasks
   - Haiku: 30% of tasks

3. **Quality Metrics**
   - First-time success rate (no refinement needed)
   - Code review pass rate
   - Test coverage maintenance

4. **Cost Efficiency**
   - Stay within weekly limits
   - Reduce need for "Extra usage"
   - Maintain or improve output quality

---

## 8. Compliance Integration

### Enforce Via CLAUDE.md

**Add to root CLAUDE.md:**

```markdown
## Model Selection Rules (MANDATORY)

Follow the model selection strategy in @docs/AI_AGENT_USAGE_OPTIMIZATION_PLAN.md

**Quick Rules:**
- **Opus:** Complex decisions, architecture, multi-file refactoring
- **Sonnet:** Standard implementations, code review, documentation
- **Haiku:** Quick queries, status checks, simple operations

**Usage Monitoring:**
- Check usage before starting work: claude.ai/settings/usage
- If Sonnet >70%, switch to Opus/Haiku
- Batch similar tasks for efficiency
```

### Propagate Across Repositories

Use compliance propagation:

```bash
./scripts/compliance/propagate_claude_config.py \
    --include-model-selection \
    --scope all
```

---

## 9. Training & Documentation

### Team Training (if applicable)

**Session 1: Model Selection**
- When to use Opus vs Sonnet vs Haiku
- Task complexity assessment
- Cost vs quality trade-offs

**Session 2: Prompt Optimization**
- Context-first prompts
- Batch operations
- Question-driven approach

**Session 3: Usage Monitoring**
- Checking limits
- Interpreting usage reports
- Adjusting strategy

### Documentation Updates

- [ ] Update AI_AGENT_GUIDELINES.md with model selection
- [ ] Add model selection to DEVELOPMENT_WORKFLOW.md
- [ ] Create quick reference card (print/post)
- [ ] Add FAQ section to this document

---

## 10. Emergency Protocols

### If Sonnet Limit Reached (>90%)

**Immediate Actions:**
1. **Stop all Sonnet tasks** immediately
2. **Switch to Opus** for critical work tasks
3. **Use Haiku** for personal/experimental repos
4. **Defer non-urgent work** until Tuesday reset
5. **Enable "Extra usage"** ONLY if critical deadline

### If Overall Limit Reached (>90%)

**Immediate Actions:**
1. **Pause all AI tasks** until reset
2. **Review what caused spike** (likely large batch operation)
3. **Plan for next week** with adjusted distribution
4. **Consider upgrading plan** if consistently hitting limits

### If Session Limit Reached (>90%)

**Immediate Actions:**
1. **Wait for session reset** (~3-4 hours)
2. **Batch work** for next session
3. **Use alternative** (local tools) if urgent
4. **Review session efficiency** (were tasks too small/frequent?)

---

## 11. FAQ

**Q: What if I need Sonnet but usage is high?**
A: Consider if Opus could handle the task (often yes for complex work). If not, evaluate urgency vs waiting for weekly reset.

**Q: Can I use Haiku for production code?**
A: Only for simple, well-defined tasks (e.g., generating boilerplate). Review with Sonnet before merging.

**Q: How do I track usage per repository?**
A: Manually log tasks, or use the monitoring script in Section 4.1. Future: integrate with Claude API for automated tracking.

**Q: What if a task is on the border between models?**
A: Err on the side of the lower-cost model first. You can always refine with a higher model if needed.

**Q: Should I batch all tasks for efficiency?**
A: Yes, where logical. Batching reduces overhead, but maintain separate sessions for unrelated work to keep context clear.

**Q: How often should I check usage?**
A: Daily before starting work, and mid-session if working on many tasks.

---

## 12. Appendix

### A. Repository Classification Reference

```yaml
work_repositories:
  tier_1_production: [digitalmodel, energy, frontierdeepwater]
  tier_2_active: [aceengineercode, assetutilities, worldenergydata, rock-oil-field, teamresumes]
  tier_3_maintenance: [doris, saipem, OGManufacturing, seanation, ai-native-traditional-eng, assethold, client_projects, acma-projects, pyproject-starter]

personal_repositories:
  tier_1_active: [aceengineer-admin, aceengineer-website]
  tier_2_experimental: [hobbies, sd-work, acma-projects, achantas-data, achantas-media]
  tier_3_archive: [investments, sabithaandkrishnaestates]
```

### B. Prompt Template Library

Located in: `templates/ai-prompts/`

- `opus_architecture.md` - Architecture decision template
- `sonnet_feature.md` - Feature implementation template
- `haiku_quick.md` - Quick task template
- `batch_operations.md` - Multi-repo batch template

### C. Integration Scripts

```bash
# Check model usage
./scripts/monitoring/check_claude_usage.sh

# Generate usage report
./scripts/monitoring/generate_usage_report.sh --week current

# Optimize prompt for model
./scripts/automation/optimize_prompt.py --model haiku --input prompt.txt

# Bulk update CLAUDE.md
./scripts/compliance/propagate_model_selection.sh --scope all
```

### D. Related Documentation

- [AI Agent Guidelines](modules/ai/AI_AGENT_GUIDELINES.md)
- [AI Usage Guidelines](modules/ai/AI_USAGE_GUIDELINES.md)
- [Development Workflow](modules/workflow/DEVELOPMENT_WORKFLOW.md)
- [Compliance Enforcement](modules/standards/COMPLIANCE_ENFORCEMENT.md)

---

## Summary

This optimization plan provides a strategic framework to reduce Sonnet usage from 79% to <60% while maintaining high-quality outputs across 26 repositories. Key strategies include:

1. **Intelligent model selection** based on task complexity and repository tier
2. **Optimized prompts** that reduce iterations and token consumption
3. **Usage monitoring** to prevent limit breaches
4. **Repository-specific strategies** balancing quality and efficiency
5. **Continuous improvement** through weekly reviews and adjustments

**Expected Outcome:** 30% reduction in Sonnet usage, 25% increase in overall efficiency, while maintaining or improving code quality.

---

**Version:** 1.0.0
**Last Updated:** 2025-01-09
**Next Review:** 2025-01-16 (Tuesday after first week)
**Owner:** Workspace-hub AI Optimization Initiative
