---
name: core-researcher-research-output-format
description: 'Sub-skill of core-researcher: Research Output Format (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Research Output Format (+4)

## Research Output Format


```yaml
research_findings:
  summary: "High-level overview of findings"

  codebase_analysis:
    structure:
      - "Key architectural patterns observed"
      - "Module organization approach"
    patterns:
      - pattern: "Pattern name"

*See sub-skills for full details.*

## Search Patterns


```bash
# Implementation patterns
grep -r "class.*Controller" --include="*.ts"

# Configuration patterns
glob "**/*.config.*"

# Test patterns
grep -r "describe\|test\|it" --include="*.test.*"

# Import patterns
grep -r "^import.*from" --include="*.ts"
```

## Broad to Narrow Strategy


```bash
# Start broad
glob "**/*.ts"

# Narrow by pattern
grep -r "specific-pattern" --include="*.ts"

# Focus on specific files
read specific-file.ts
```

## Dependency Analysis


```typescript
// Track import statements and module dependencies
// Identify external package dependencies
// Map internal module relationships
// Document API contracts and interfaces

dependencies:
  external:
    - express: "^4.18.0"    # HTTP framework
    - passport: "^0.6.0"    # Authentication

*See sub-skills for full details.*

## Documentation Mining


```yaml
# Extract knowledge from:
- Inline comments and JSDoc
- README files and documentation
- Commit messages for context
- Issue trackers and PRs
```
