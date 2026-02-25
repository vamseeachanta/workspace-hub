# Claude Model Selection - Quick Reference Card

> **Print this and keep it visible while working!**
> **Full guide:** @docs/AI_AGENT_USAGE_OPTIMIZATION_PLAN.md

---

## 🎯 Model Selection Decision Tree

```
┌─────────────────────────────────┐
│ NEW TASK                        │
└─────────┬───────────────────────┘
          │
    ┌─────┴─────┐
    │           │
  WORK      PERSONAL
    │           │
    ▼           ▼
  COMPLEX     SIMPLE
    │           │
    ▼           ▼
  OPUS       HAIKU

  STANDARD → SONNET
```

---

## 🚦 Quick Decision Guide

### USE OPUS (30% of tasks)

✅ Multi-file refactoring (>5 files)
✅ Architecture decisions
✅ Complex algorithm design
✅ Security-critical code review
✅ Cross-repository coordination
✅ Performance optimization strategies

**Example:** "Design the authentication system architecture for our multi-tenant application"

---

### USE SONNET (40% of tasks)

✅ Standard feature implementation
✅ Code review (single PR)
✅ Documentation writing
✅ Test generation
✅ Bug fixing (standard complexity)
✅ Configuration updates

**Example:** "Implement user login with JWT authentication following existing patterns"

---

### USE HAIKU (30% of tasks)

✅ File existence checks
✅ Simple grep/search operations
✅ Quick status updates
✅ Log analysis (pattern matching)
✅ Template generation
✅ Format validation
✅ Summary generation

**Example:** "Check if tests/test_auth.py exists and show its structure"

---

## 📊 Current Usage Targets

| Model | Target | Alert At |
|-------|--------|----------|
| **Opus** | 30% | N/A (use freely) |
| **Sonnet** | 40% | **>60% = Warning** |
| **Haiku** | 30% | <20% = Underused |

**Check usage:** https://claude.ai/settings/usage

---

## 🏷️ Repository Tiers

### Work Repos (Higher Quality)

**Tier 1** (Production): Use **60% Opus**, 30% Sonnet, 10% Haiku
- digitalmodel, energy, frontierdeepwater

**Tier 2** (Active): Use **30% Opus**, 50% Sonnet, 20% Haiku
- aceengineercode, assetutilities, worldenergydata

**Tier 3** (Maintenance): Use **10% Opus**, 30% Sonnet, 60% Haiku
- doris, saipem, OGManufacturing

### Personal Repos (Efficiency Focus)

**Tier 1** (Active): Use 20% Opus, **40% Sonnet**, 40% Haiku
- aceengineer-admin, aceengineer-website

**Tier 2** (Experimental): Use 5% Opus, 25% Sonnet, **70% Haiku**
- hobbies, sd-work, acma-projects

**Tier 3** (Archive): Use 0% Opus, 20% Sonnet, **80% Haiku**
- investments, sabithaandkrishnaestates

---

## ⚡ Quick Optimization Tips

1. **Batch similar tasks** → Reduces context switching overhead
2. **Context-first prompts** → Provide all info upfront, fewer iterations
3. **Ask questions first** → Let AI clarify before implementing
4. **Check usage before starting** → Plan model distribution for session
5. **Use lower model first** → Can always upgrade if needed

---

## 🚨 Emergency Protocols

### If Sonnet >80%

```
⛔ STOP using Sonnet immediately
✅ Switch to Opus for critical work
✅ Switch to Haiku for everything else
📅 Defer non-urgent work to Tuesday
```

### If Session >80%

```
⏸️  Pause AI tasks
⏰ Wait for session reset (~3-4 hours)
📦 Batch work for next session
```

### If Overall >80%

```
📅 Defer all non-critical work
⚠️  Enable "Extra usage" ONLY if critical
📊 Review what caused spike
```

---

## 📝 Before Every Task Checklist

- [ ] Check usage at https://claude.ai/settings/usage
- [ ] Note Sonnet percentage
- [ ] Assess task complexity (Simple/Standard/Complex)
- [ ] Select appropriate model (Haiku/Sonnet/Opus)
- [ ] Provide context-first prompt

---

## 🔗 Quick Commands

```bash
# Check usage
./scripts/monitoring/check_claude_usage.sh check

# View today's summary
./scripts/monitoring/check_claude_usage.sh today

# View recommendations
./scripts/monitoring/check_claude_usage.sh rec

# Log a task
./scripts/monitoring/check_claude_usage.sh log sonnet digitalmodel "Feature work"
```

---

## 📖 Full Documentation

- **Optimization Plan:** @docs/AI_AGENT_USAGE_OPTIMIZATION_PLAN.md
- **Agent Guidelines:** @docs/modules/ai/AI_AGENT_GUIDELINES.md
- **Usage Patterns:** @docs/modules/ai/AI_USAGE_GUIDELINES.md

---

**Last Updated:** 2025-01-09
**Weekly Reset:** Tuesday at 3:59 PM
**Target:** Sonnet <60%, Overall <70%
