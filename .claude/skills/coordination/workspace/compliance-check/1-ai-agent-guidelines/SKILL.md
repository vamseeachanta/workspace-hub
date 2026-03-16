---
name: compliance-check-1-ai-agent-guidelines
description: 'Sub-skill of compliance-check: 1. AI Agent Guidelines (+3).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. AI Agent Guidelines (+3)

## 1. AI Agent Guidelines


Ensure AI agents follow required workflows:

- Read `user_prompt.md` before implementation
- Ask clarifying questions
- Wait for user approval
- Follow SPARC methodology
- Use TDD practices

**Reference:** [AI_AGENT_GUIDELINES.md](../docs/modules/ai/AI_AGENT_GUIDELINES.md)

## 2. Development Workflow


Ensure proper workflow adherence:

- user_prompt.md -> YAML config -> Pseudocode -> TDD -> Implementation
- Bash-based execution
- Interactive engagement
- Gate-pass reviews

**Reference:** [DEVELOPMENT_WORKFLOW.md](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

## 3. File Organization


Ensure proper directory structure:

- `/src` - Source code
- `/tests` - Test files
- `/docs` - Documentation
- `/config` - Configuration
- `/scripts` - Utility scripts
- `/data` - Data files
- `/reports` - Generated reports

**Reference:** [FILE_ORGANIZATION_STANDARDS.md](../docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md)

## 4. Code Quality Standards


Ensure code meets quality requirements:

- 80%+ test coverage
- Proper logging (5 levels)
- HTML reports with interactive plots
- No static matplotlib exports

**References:**
- [TESTING_FRAMEWORK_STANDARDS.md](../docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md)
- [LOGGING_STANDARDS.md](../docs/modules/standards/LOGGING_STANDARDS.md)
- [HTML_REPORTING_STANDARDS.md](../docs/modules/standards/HTML_REPORTING_STANDARDS.md)
