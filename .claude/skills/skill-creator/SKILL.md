---
name: skill-creator
description: Create new Claude Code skills with proper structure, documentation, and best practices. Use when building custom skills for specific domains, workflows, or organizational needs.
---

# Skill Creator Skill

## Overview

This skill guides the creation of new Claude Code skills. Skills are specialized instruction sets that enhance Claude's capabilities for specific domains, tasks, or workflows.

## Skill Anatomy

### File Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md           # Required: Main skill definition
    └── resources/         # Optional: Supporting files
        ├── templates/
        ├── examples/
        └── data/
```

### SKILL.md Structure

```markdown
---
name: skill-name
description: One-line description of what this skill does and when to use it.
---

# Skill Title

## Overview
Brief explanation of the skill's purpose and capabilities.

## When to Use
- Scenario 1
- Scenario 2
- Scenario 3

## Instructions
Detailed instructions for how to apply the skill.

## Examples
Concrete examples of the skill in action.

## Best Practices
Guidelines for effective use.

## Related Skills
Links to complementary skills.
```

## Skill Design Principles

### 1. Clear Triggering

The `description` field is crucial—it determines when the skill activates:

**Good descriptions:**
```yaml
description: Create professional presentations with python-pptx. Use for slide decks, pitch presentations, and visual reports.
```

**Bad descriptions:**
```yaml
description: A skill for presentations.  # Too vague
description: This skill helps you...     # Starts with filler
```

**Tips for descriptions:**
- Start with an action verb
- Include specific use cases
- Mention key technologies/tools
- Keep under 200 characters

### 2. Progressive Disclosure

Structure content from general to specific:

```markdown
## Overview
High-level purpose (always loaded)

## Quick Start
Fastest path to value

## Detailed Instructions
Comprehensive guidance

## Advanced Usage
Edge cases and optimization

## Reference
Complete API/options reference
```

### 3. Actionable Content

Every section should guide action:

```markdown
## Bad: Conceptual only
CSS is a styling language for web pages.

## Good: Actionable
To style a button with hover effects:
\`\`\`css
.button {
    background: #007bff;
    transition: background 0.2s;
}
.button:hover {
    background: #0056b3;
}
\`\`\`
```

## Creating a New Skill

### Step 1: Define the Skill Scope

Answer these questions:
1. What specific problem does this skill solve?
2. Who is the target user?
3. What inputs does it expect?
4. What outputs does it produce?
5. What tools/technologies does it use?

### Step 2: Write the Frontmatter

```yaml
---
name: lowercase-kebab-case
description: Action-oriented description with use cases. Use for X, Y, and Z.
---
```

**Naming conventions:**
- Use lowercase with hyphens: `api-testing`, `data-viz`
- Be descriptive but concise
- Avoid generic names like `helper` or `utils`

### Step 3: Structure the Content

#### Overview Section

```markdown
## Overview

[1-2 sentences explaining what this skill enables]

**Key Capabilities:**
- Capability 1
- Capability 2
- Capability 3
```

#### Instructions Section

```markdown
## Instructions

### [Task Category 1]

[Step-by-step instructions]

\`\`\`language
// Code example
\`\`\`

### [Task Category 2]

[More instructions with examples]
```

#### Examples Section

```markdown
## Examples

### Example 1: [Scenario Name]

**Input:** [What user provides]

**Process:** [What skill does]

**Output:** [What user receives]

\`\`\`
// Complete working example
\`\`\`
```

### Step 4: Add Supporting Materials

If needed, create resources:

```
skill-name/
├── SKILL.md
└── resources/
    ├── templates/
    │   └── starter.template
    ├── examples/
    │   └── complete-example.py
    └── config/
        └── defaults.yaml
```

Reference them in SKILL.md:
```markdown
See [starter template](resources/templates/starter.template) for a quick start.
```

## Skill Templates

### Technical Skill Template

```markdown
---
name: tech-skill-name
description: Technical capability description. Use for specific technical tasks.
---

# Technical Skill Name

## Overview

This skill provides [capability] using [technology/tool].

## Prerequisites

- Dependency 1
- Dependency 2

## Installation

\`\`\`bash
# Installation commands
\`\`\`

## Quick Start

\`\`\`language
// Minimal working example
\`\`\`

## Core Operations

### Operation 1

\`\`\`language
// Code
\`\`\`

### Operation 2

\`\`\`language
// Code
\`\`\`

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| option1 | string | "default" | Description |

## Error Handling

### Common Errors

**Error: [Error Name]**
- Cause: [Why it happens]
- Solution: [How to fix]

## Best Practices

1. Practice 1
2. Practice 2
3. Practice 3
```

### Process Skill Template

```markdown
---
name: process-skill-name
description: Process/workflow description. Use for organizational tasks.
---

# Process Skill Name

## Overview

This skill guides [process type] for [outcome].

## When to Use

- Situation 1
- Situation 2
- Situation 3

## Process Steps

### Step 1: [Name]

[Instructions]

**Checklist:**
- [ ] Item 1
- [ ] Item 2

### Step 2: [Name]

[Instructions]

**Template:**
\`\`\`
[Template content]
\`\`\`

### Step 3: [Name]

[Instructions]

## Templates

### [Template Name]

\`\`\`
[Full template]
\`\`\`

## Examples

### [Scenario]

[Complete worked example]

## Tips

- Tip 1
- Tip 2
- Tip 3
```

### Creative Skill Template

```markdown
---
name: creative-skill-name
description: Creative capability description. Use for design/content creation.
---

# Creative Skill Name

## Overview

This skill enables creation of [output type] with [characteristics].

## Design Principles

### Principle 1: [Name]
[Explanation]

### Principle 2: [Name]
[Explanation]

## Styles & Variations

### Style 1: [Name]
[Description and examples]

### Style 2: [Name]
[Description and examples]

## Creation Process

### Phase 1: [Name]
[Instructions]

### Phase 2: [Name]
[Instructions]

## Technical Implementation

\`\`\`language
// Code for creating the output
\`\`\`

## Quality Checklist

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Inspiration & Examples

[Gallery of examples with explanations]
```

## Skill Quality Checklist

### Content Quality

- [ ] Description clearly states purpose and trigger conditions
- [ ] Overview explains value proposition in 2-3 sentences
- [ ] Instructions are actionable, not just conceptual
- [ ] Examples are complete and runnable
- [ ] Best practices are specific and justified

### Structure Quality

- [ ] Follows progressive disclosure (general → specific)
- [ ] Uses consistent heading hierarchy
- [ ] Code blocks have language tags
- [ ] Tables are properly formatted
- [ ] Lists are parallel in structure

### Usability

- [ ] Can be used without reading entire document
- [ ] Quick start enables immediate value
- [ ] Error scenarios are addressed
- [ ] Edge cases are documented
- [ ] Related skills are referenced

### Technical Accuracy

- [ ] Code examples are tested and work
- [ ] Dependencies are listed
- [ ] Version requirements are specified
- [ ] Installation steps are complete

## Skill Maintenance

### Versioning

Track significant changes:

```markdown
<!-- At end of SKILL.md -->

---
## Version History

- **1.2.0** (2025-01-15): Added new feature X
- **1.1.0** (2024-12-01): Updated examples for tool v2
- **1.0.0** (2024-10-15): Initial release
```

### Deprecation

When retiring a skill:

```yaml
---
name: old-skill-name
description: DEPRECATED - Use new-skill-name instead. [Original description]
---
```

## Integration with Claude Code

### Skill Discovery

Skills are discovered from:
1. `.claude/skills/` in project directory
2. `~/.claude/skills/` for user-level skills

### Skill Loading

- **Metadata**: Always loaded (name, description)
- **Body**: Loaded when skill is triggered
- **Resources**: Loaded on demand

### Best Practices for Performance

1. Keep SKILL.md focused (under 500 lines ideal)
2. Move large examples to resources/
3. Reference external documentation for comprehensive APIs
4. Use code blocks sparingly—quality over quantity
