---
name: brand-review
type: command
plugin: marketing
source: https://github.com/anthropics/knowledge-work-plugins
---

# /brand-review - Review Content Against Brand Guidelines

Review marketing content against brand voice, style guidelines, and messaging standards. Flag deviations and provide specific improvement suggestions.

## Usage

```
/brand-review <content to review>
```

## Inputs

1. **Content to review**: pasted text, file path, knowledge base reference, or URL
2. **Brand guidelines**: auto-detected from configuration, or requested from user

## Review Dimensions

### With Brand Guidelines
- **Voice and Tone**: Does content match defined brand voice attributes?
- **Terminology and Language**: Are preferred brand terms used correctly?
- **Messaging Pillars**: Does content align with defined value propositions?
- **Style Guide Compliance**: Grammar, formatting, and punctuation per style guide

### Without Brand Guidelines (Generic Review)
- **Clarity**: Is the main message clear within the first paragraph?
- **Consistency**: Is tone and terminology consistent throughout?
- **Professionalism**: Free of errors, appropriate for audience?

### Legal and Compliance Flags (Always Checked)
- Unsubstantiated claims (superlatives without evidence)
- Missing disclaimers
- Comparative claims that could be challenged
- Regulatory language concerns
- Testimonial issues
- Copyright concerns

## Output Format

### Summary
Overall assessment, top strengths, and most important improvements

### Detailed Findings

| Issue | Location | Severity | Suggestion |
|-------|----------|----------|------------|

Severity: High (contradicts brand / compliance risk), Medium (inconsistent), Low (minor style issue)

### Revised Sections
Before/after for top 3-5 highest-severity issues

### Legal/Compliance Flags
Separate list with recommended actions
