---
name: skill-creator
description: Create new Claude Code skills with proper structure, documentation, and best practices. Use when building custom skills for specific domains, workflows, or organizational needs.
version: 2.0.0
category: builders
last_updated: 2026-01-02
related_skills:
  - session-start-routine
  - sparc-workflow
  - mcp-builder
---

# Skill Creator Skill

## Overview

This skill guides the creation of new Claude Code skills. Skills are specialized instruction sets that enhance Claude's capabilities for specific domains, tasks, or workflows.

## Quick Start

1. **Define scope** - Answer: What problem? Who uses it? What outputs?
2. **Create structure** - `.claude/skills/skill-name/SKILL.md`
3. **Write frontmatter** - Name, description, version, category
4. **Add content** - Overview, Instructions, Examples, Best Practices
5. **Test** - Verify skill triggers correctly

```bash
# Create skill directory
mkdir -p .claude/skills/my-new-skill

# Create SKILL.md with template
cat > .claude/skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: Action-oriented description. Use for X, Y, and Z.
version: 1.0.0
category: [builders|tools|content-design|communication|meta]
---

# My New Skill

## Overview
[1-2 sentences explaining purpose]

## Instructions
[Step-by-step guidance]

## Examples
[Concrete examples]
EOF
```

## When to Use

- Building custom skills for specific domains
- Creating reusable workflow templates
- Standardizing organizational processes
- Extending Claude Code capabilities
- Documenting specialized knowledge

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
version: 1.0.0
category: builders
last_updated: 2026-01-02
related_skills:
  - related-skill-1
  - related-skill-2
---

# Skill Title

## Overview
Brief explanation of the skill's purpose and capabilities.

## Quick Start
Fastest path to value.

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

## Error Handling
Common issues and solutions.

## Metrics
How to measure success.

## Related Skills
Links to complementary skills.

## Version History
- **1.0.0** (YYYY-MM-DD): Initial release
```

## Skill Design Principles

### 1. Clear Triggering

The `description` field is crucial--it determines when the skill activates:

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
version: 1.0.0
category: builders
last_updated: 2026-01-02
related_skills:
  - related-skill-1
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
version: 1.0.0
category: builders
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
version: 1.0.0
category: communication
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
version: 1.0.0
category: content-design
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

## Execution Checklist

Before creating a skill:
- [ ] Scope clearly defined (problem, users, inputs, outputs)
- [ ] Name follows kebab-case convention
- [ ] Description is action-oriented with use cases

During creation:
- [ ] Frontmatter complete (name, description, version, category)
- [ ] Overview explains value in 2-3 sentences
- [ ] Quick Start provides immediate value
- [ ] Instructions are actionable, not conceptual
- [ ] Examples are complete and runnable

After creation:
- [ ] Skill triggers correctly when invoked
- [ ] Code examples tested and working
- [ ] Related skills referenced
- [ ] Version history added

## Skill Quality Checklist

### Content Quality

- [ ] Description clearly states purpose and trigger conditions
- [ ] Overview explains value proposition in 2-3 sentences
- [ ] Instructions are actionable, not just conceptual
- [ ] Examples are complete and runnable
- [ ] Best practices are specific and justified

### Structure Quality

- [ ] Follows progressive disclosure (general -> specific)
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

## Error Handling

### Common Errors

**Error: Skill not triggering**
- Cause: Description too vague or doesn't match user intent
- Solution: Rewrite description with specific use cases and action verbs

**Error: Skill content too large**
- Cause: Too much content in single SKILL.md
- Solution: Move large examples to resources/ folder, keep SKILL.md under 500 lines

**Error: Circular skill references**
- Cause: Skills reference each other in loops
- Solution: Review related_skills, ensure DAG structure

**Error: Outdated code examples**
- Cause: Dependencies or APIs changed
- Solution: Test examples regularly, update version history

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
deprecated: true
deprecated_date: 2026-01-02
replacement: new-skill-name
---
```

## Metrics

Track skill effectiveness:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Trigger accuracy | >90% | Skill activates when intended |
| Completion rate | >85% | Users complete skill workflow |
| Error rate | <10% | Failed executions / total |
| Update frequency | Monthly | Last update within 30 days |
| User satisfaction | >4/5 | Feedback ratings |

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
4. Use code blocks sparingly--quality over quantity

## Related Skills

- [session-start-routine](../../meta/session-start-routine/SKILL.md) - Skill library maintenance
- [sparc-workflow](../../development/sparc-workflow/SKILL.md) - Development methodology
- [mcp-builder](../mcp-builder/SKILL.md) - MCP server creation

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; enhanced frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with skill anatomy, design principles, templates, quality checklist
