---
name: stakeholder-update
type: command
plugin: product-management
source: https://github.com/anthropics/knowledge-work-plugins
---

# /stakeholder-update - Create Stakeholder Communications

Create tailored stakeholder updates for different audiences and cadences.

## Usage

```
/stakeholder-update [audience] [update type]
```

## Update Types

- **Weekly progress** reports
- **Monthly summaries**
- **Launch announcements**
- **Ad-hoc situational** updates

## Audience Segmentation

- **Executives**: Brief, outcome-focused (under 300 words)
- **Engineering teams**: Technical depth with linked tickets/PRs
- **Cross-functional partners**: Context-appropriate with specific asks
- **External customers**: Benefits-focused, no jargon
- **Board members**: Metrics-driven

## Workflow

### 1. Gather Information

Pull from connected project trackers, chat systems, meeting transcriptions, and knowledge bases when available. Otherwise, ask the user for key updates.

### 2. Structure the Update

- Lead with key information
- Use status indicators (Green/Yellow/Red)
- Match length to audience attention spans
- Include specific, actionable asks rather than vague requests

### 3. Generate the Communication

Follow the stakeholder-comms skill templates for the target audience.

## Key Principles

- The most common mistake is burying the lead
- Frame information around outcomes for executives
- Address bad news directly rather than obscuring it
- Be specific about asks: "Decision on X by Friday" not "support needed"
