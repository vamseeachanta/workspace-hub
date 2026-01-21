---
name: systematic-debugging
description: Four-phase debugging methodology emphasizing root cause analysis before fixes. Use for bug investigation, preventing random fixes, and systematic problem-solving. Based on obra/superpowers.
version: 1.0.0
category: development
last_updated: 2026-01-19
source: https://github.com/obra/superpowers
related_skills:
  - tdd-obra
  - writing-plans
  - code-reviewer
---

# Systematic Debugging Skill

## Overview

This skill provides a structured four-phase debugging framework emphasizing root cause discovery before attempting fixes. Core principle: "Random fixes waste time and create new bugs. Quick patches mask underlying issues."

## Quick Start

1. **Investigate** - Gather evidence, reproduce consistently
2. **Analyze** - Compare with working patterns
3. **Hypothesize** - Form and test specific theories
4. **Implement** - Fix with test coverage

## When to Use

- Bug reports requiring investigation
- Test failures with unclear causes
- Production incidents
- Performance regressions
- Integration failures
- Any debugging that requires more than 5 minutes

## The Four Phases

### Phase 1: Root Cause Investigation

**Objective:** Understand the problem completely before attempting any fix.

Steps:
1. Examine error messages thoroughly
2. Reproduce the issue consistently
3. Review recent changes (commits, configs, dependencies)
4. Gather diagnostic evidence (logs, traces, metrics)
5. For multi-component systems, add instrumentation at each boundary

**Questions to answer:**
- What exactly is failing?
- When did it start failing?
- What changed recently?
- Can I reproduce it reliably?

### Phase 2: Pattern Analysis

**Objective:** Find working examples and understand differences.

Steps:
1. Locate working examples in the codebase
2. Compare against reference implementations completely
3. Identify differences systematically
4. Understand all dependencies

**Key comparisons:**
- Working vs. broken code paths
- Expected vs. actual behavior
- Known good state vs. current state

### Phase 3: Hypothesis and Testing

**Objective:** Form and validate theories before changing code.

Steps:
1. Formulate a specific hypothesis
2. Design a test for the hypothesis
3. Test with minimal changes (one variable at a time)
4. Verify results before proceeding

**Hypothesis format:**
"The bug occurs because [condition] when [trigger], which causes [symptom]."

### Phase 4: Implementation

**Objective:** Fix the root cause with proper verification.

Steps:
1. Create a failing test case reproducing the bug
2. Implement a single fix addressing the root cause
3. Verify the test passes
4. Verify no other tests broke
5. Document the fix

## Critical Safeguards

### Hard Stop Rule

**If >= 3 fixes fail: STOP and question the architecture.**

When multiple fixes fail, the issue indicates deeper structural problems requiring discussion rather than continued symptom-patching.

### Red Flags (Restart Process)

- Proposing solutions before investigation
- Attempting multiple simultaneous fixes
- Assuming without verification
- Skipping reproduction step
- "It should work" without evidence

## Debugging Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Shotgun debugging | Random changes hoping something works | Systematic investigation |
| Printf debugging only | Incomplete picture | Structured instrumentation |
| Blame the framework | Avoids understanding | Verify framework behavior |
| "Works on my machine" | Environment assumptions | Document exact repro steps |
| Quick patch | Hides root cause | Find and fix actual cause |

## Instrumentation Strategies

### Logging Strategy

```
1. Entry/exit of suspected functions
2. Input/output values at boundaries
3. State changes at key points
4. Timing information for performance issues
```

### Boundary Tracing

For multi-component systems:
```
[Input] -> [Component A] -> [Component B] -> [Output]
   ^            ^               ^              ^
   |            |               |              |
 Check 1     Check 2         Check 3       Check 4
```

Add verification at each boundary to isolate failure point.

## Best Practices

### Do

1. Reproduce before investigating
2. Document investigation steps
3. Test one hypothesis at a time
4. Write regression test for every bug fix
5. Share findings with team
6. Update documentation when environment-related

### Don't

1. Jump to conclusions
2. Make multiple changes at once
3. Fix symptoms instead of causes
4. Skip the hypothesis step
5. Merge fixes without tests
6. Ignore intermittent failures

## Error Handling

| Situation | Action |
|-----------|--------|
| Cannot reproduce | Gather more context, check environment differences |
| Multiple potential causes | Isolate and test each separately |
| Fix breaks other things | Revert, investigate dependencies |
| Root cause unclear after investigation | Escalate, add more instrumentation |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| First-fix success rate | >80% | Fixes that resolve issue first time |
| Regression rate | <5% | Bug fixes causing new bugs |
| Investigation time ratio | >60% | Time spent investigating vs. coding |
| Documentation rate | 100% | Bugs documented with root cause |

## Debugging Checklist

- [ ] Issue reproduced consistently
- [ ] Recent changes reviewed
- [ ] Error messages fully understood
- [ ] Working comparison found
- [ ] Hypothesis documented
- [ ] Single-variable test performed
- [ ] Root cause identified
- [ ] Failing test written
- [ ] Fix implemented
- [ ] All tests pass
- [ ] Fix documented

## Related Skills

- [tdd-obra](../tdd-obra/SKILL.md) - Test-first development
- [writing-plans](../planning/writing-plans/SKILL.md) - Plan implementations
- [code-reviewer](../code-reviewer/SKILL.md) - Code quality review

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from obra/superpowers
