# Claude Rules Integration Plan

## Overview

This document outlines the strategy for integrating obra's software engineering best practices into the Workspace Hub Claude configuration while maintaining existing SPARC/Claude Flow orchestration capabilities.

## Analysis

### Current CLAUDE.md Structure
The existing CLAUDE.md files (both root and `.claude/` versions) focus on:
- **AI Orchestration**: SPARC methodology, Claude Flow, agent coordination
- **Parallel Execution**: Batching operations, concurrent agent spawning
- **File Organization**: Directory structure, HTML reporting standards
- **MCP Integration**: Tool categories, workflow patterns
- **Agent OS**: Product documentation references

### Obra's Rules Structure
Obra's CLAUDE.md emphasizes:
- **Software Engineering Principles**: YAGNI, simplicity, maintainability
- **Test-Driven Development**: Mandatory TDD workflow
- **Collaboration Guidelines**: Direct communication, pushing back on bad ideas
- **Code Quality**: Naming conventions, comments, version control
- **Systematic Debugging**: Root cause analysis framework
- **Memory Management**: Journal usage for learning

## Integration Strategy

### Approach: Complementary Sections
The two rule sets are **complementary** rather than conflicting:
- **Obra's rules** = HOW to write code, debug, and collaborate
- **Existing rules** = HOW to orchestrate AI agents and organize projects

### Merged Structure

```
CLAUDE.md
├── Part 1: Core Engineering Principles (Obra's Rules)
│   ├── Foundational Rules
│   ├── Collaboration Guidelines
│   ├── Design Philosophy (YAGNI, TDD)
│   ├── Code Quality Standards
│   ├── Debugging Framework
│   └── Memory Management
│
├── Part 2: AI Orchestration & Workflow (Existing Rules)
│   ├── Concurrent Execution Patterns
│   ├── SPARC Methodology
│   ├── Claude Flow Integration
│   ├── Agent Coordination
│   └── File Organization
│
└── Part 3: Project-Specific Context (Agent OS)
    ├── Product Context
    ├── Development Standards
    └── Workflow Instructions
```

## Implementation Plan

### Phase 1: Create Unified Template
1. **Prepend Obra's rules** to existing CLAUDE.md
2. **Add clear section headers** to distinguish rule categories
3. **Maintain all existing content** - no deletions
4. **Add integration notes** explaining how sections work together

### Phase 2: Deploy to Workspace Hub
1. Update `/mnt/github/workspace-hub/CLAUDE.md`
2. Update `/mnt/github/workspace-hub/.claude/CLAUDE.md`
3. Test with sample development tasks

### Phase 3: Create Propagation System
1. Create script: `modules/automation/propagate_claude_rules.sh`
2. Integrate with existing command propagation system
3. Add to git-management workflows

### Phase 4: Documentation
1. Update `docs/CLAUDE_INTERACTION_GUIDE.md` with integrated rules
2. Add examples showing both rule sets in action
3. Create troubleshooting guide for rule conflicts (if any)

## Key Integration Points

### 1. TDD + SPARC Workflow
**Obra's TDD**: Write failing test → Implement → Refactor
**SPARC TDD**: Specification → Pseudocode → Architecture → Refinement → Completion

**Integration**: SPARC provides the high-level workflow; Obra's TDD provides the micro-level implementation discipline within the Refinement phase.

### 2. Version Control
**Obra's Rules**: Frequent commits, WIP branches, pre-commit hooks
**Existing Rules**: Git hooks management, batch operations

**Integration**: Obra's rules define the discipline; existing rules provide the automation tooling.

### 3. Code Quality
**Obra's Rules**: Naming conventions, comment standards, no duplication
**Existing Rules**: File organization, modular design

**Integration**: Obra's rules define quality standards; existing rules define organizational structure.

### 4. Collaboration
**Obra's Rules**: Direct feedback, push back on bad ideas, no sycophancy
**Existing Rules**: Agent coordination, memory sharing, task orchestration

**Integration**: Obra's rules apply to human-AI collaboration; existing rules apply to multi-agent coordination.

## Rule Precedence

When rules overlap, follow this precedence:
1. **Security/Safety Rules**: Highest priority (both rule sets agree)
2. **Obra's Core Principles**: For code quality, TDD, naming, comments
3. **SPARC/Agent Rules**: For orchestration, file organization, workflows
4. **Project-Specific Rules**: Agent OS standards override globals

## Testing Strategy

### Validation Checks
1. **TDD Compliance**: Verify test-first workflow in sample feature
2. **SPARC Integration**: Run full SPARC pipeline with new rules
3. **Agent Coordination**: Test multi-agent tasks with unified rules
4. **File Organization**: Verify no conflicts with directory structure

### Sample Scenarios
1. Implementing new feature with TDD + SPARC
2. Debugging production issue with systematic framework
3. Collaborating with multiple agents on complex task
4. Propagating rules to new repository

## Deployment Checklist

- [ ] Create unified CLAUDE.md template
- [ ] Backup existing CLAUDE.md files
- [ ] Deploy to workspace-hub root
- [ ] Deploy to workspace-hub `.claude/`
- [ ] Create propagation script
- [ ] Update documentation
- [ ] Test with sample development task
- [ ] Document any edge cases or conflicts

## Success Criteria

1. **No Rule Conflicts**: All sections coexist without contradictions
2. **Improved Code Quality**: TDD discipline enforced in all development
3. **Maintained Orchestration**: SPARC/Claude Flow workflows still functional
4. **Easy Propagation**: One-command deployment to new repositories
5. **Clear Documentation**: Developers understand when to apply each rule set

## Future Enhancements

1. **Repository-Specific Overrides**: Allow repos to customize rules
2. **Rule Validation**: Automated checks for rule compliance
3. **Interactive Guide**: CLI tool to query relevant rules for context
4. **Metrics Dashboard**: Track adherence to coding standards
