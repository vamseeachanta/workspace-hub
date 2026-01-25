---
name: doc-coauthoring
description: Collaborate on documents with tracked changes, suggestions, and iterative refinement. Use for reviewing drafts, providing editorial feedback, and collaborative document development.
version: 2.0.0
category: communication
last_updated: 2026-01-02
related_skills:
  - internal-comms
  - brand-guidelines
  - skill-creator
---

# Document Co-Authoring Skill

## Overview

This skill enables effective document collaboration through tracked changes, structured feedback, and iterative refinement workflows. It applies to any document type requiring review and revision.

## When to Use

- Reviewing and editing drafts
- Providing structured editorial feedback
- Collaborative document development
- Technical document review
- Business document refinement
- Any multi-revision document workflow

## Quick Start

1. **Choose collaboration mode** (suggestion, track changes, comment, rewrite)
2. **Categorize feedback** (content, structure, style, technical)
3. **Follow review phases** (initial read, detailed review, summary)
4. **Use version control** for document iterations
5. **Provide actionable feedback** with specific solutions

```markdown
<!-- Suggestion Mode -->
Original text here
--> **Suggested:** Revised text with improvements

**Reason:** Brief explanation of why this change improves the document.

<!-- Track Changes Mode -->
~~deleted text~~ **added text**

<!-- Comment Mode -->
[COMMENT: Your feedback here]
```

## Collaboration Modes

### 1. Suggestion Mode

Provide non-destructive suggestions that the author can accept or reject.

**Format:**
```markdown
Original text here
--> **Suggested:** Revised text with improvements

**Reason:** Brief explanation of why this change improves the document.
```

**Example:**
```markdown
The system processes data efficiently.
--> **Suggested:** The system processes up to 10,000 records per second with 99.9% accuracy.

**Reason:** Adding specific metrics makes the claim more credible and verifiable.
```

### 2. Track Changes Mode

Show exactly what was modified with clear before/after.

**Format:**
```markdown
~~deleted text~~ **added text**
```

**Example:**
```markdown
The meeting will be held ~~on Monday~~ **Tuesday at 2pm** in the main conference room.
```

### 3. Comment Mode

Add contextual feedback without changing text.

**Format:**
```markdown
[COMMENT: Your feedback here]
```

**Example:**
```markdown
Our Q3 revenue exceeded expectations by 15%. [COMMENT: Consider adding comparison to Q2 for context]
```

### 4. Section Rewrite Mode

Propose complete rewrites of sections.

**Format:**
```markdown
---
**ORIGINAL SECTION:**
[Original text]

**PROPOSED REWRITE:**
[New version]

**CHANGES MADE:**
- Change 1
- Change 2
- Change 3
---
```

## Feedback Categories

### Content Feedback

Address substance and accuracy:
- **[FACT CHECK]:** Verify accuracy of claims
- **[CLARITY]:** Improve understanding
- **[COMPLETENESS]:** Add missing information
- **[RELEVANCE]:** Remove or relocate off-topic content

### Structure Feedback

Address organization:
- **[FLOW]:** Improve logical progression
- **[ORDER]:** Suggest reordering
- **[HEADING]:** Recommend section breaks
- **[TRANSITION]:** Improve connections between sections

### Style Feedback

Address writing quality:
- **[TONE]:** Adjust formality/voice
- **[CONCISION]:** Reduce wordiness
- **[WORD CHOICE]:** Suggest better alternatives
- **[CONSISTENCY]:** Maintain uniform style

### Technical Feedback

Address formatting and mechanics:
- **[GRAMMAR]:** Fix grammatical errors
- **[PUNCTUATION]:** Correct punctuation
- **[FORMATTING]:** Adjust presentation
- **[CITATION]:** Add or fix references

## Review Workflow

### Phase 1: Initial Read-Through

```markdown
## First Pass Review

**Document:** [Document Name]
**Reviewer:** [Name]
**Date:** [Date]

### Overall Impressions
- Strengths: [What works well]
- Areas for improvement: [Main concerns]
- Key questions: [Clarifications needed]

### Priority Issues
1. [Most important issue]
2. [Second priority]
3. [Third priority]
```

### Phase 2: Detailed Review

```markdown
## Detailed Review

### Section: [Section Name]

**Line/Paragraph:** [Reference]
**Issue Type:** [Category from above]
**Current Text:** [Original]
**Suggested Text:** [Revision]
**Rationale:** [Why this change]
**Priority:** [High/Medium/Low]

---

[Repeat for each issue]
```

### Phase 3: Summary Feedback

```markdown
## Review Summary

### Changes Made
- [X] items edited directly
- [X] suggestions requiring author decision
- [X] comments for consideration

### Recommended Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

### Questions for Author
1. [Question needing clarification]
2. [Decision required]
```

## Collaborative Techniques

### The Sandwich Method (for sensitive feedback)

```markdown
**What's working:** [Positive observation]
**Suggestion:** [Constructive feedback]
**Potential:** [Encouraging forward look]
```

**Example:**
```markdown
**What's working:** Your executive summary clearly states the problem and proposed solution.
**Suggestion:** Consider adding a brief cost-benefit analysis to strengthen the business case.
**Potential:** With that addition, this proposal would be very compelling for stakeholders.
```

### Options-Based Feedback

Present alternatives rather than single suggestions:

```markdown
**Current:** [Original text]

**Option A:** [Revision 1]
- Pros: [Benefits]
- Cons: [Drawbacks]

**Option B:** [Revision 2]
- Pros: [Benefits]
- Cons: [Drawbacks]

**Recommendation:** [Which option and why]
```

### Questioning Technique

Guide improvements through questions:

```markdown
**Questions to consider:**
1. Who is the primary audience for this section?
2. What action do you want readers to take?
3. Is the supporting evidence sufficient for skeptical readers?
4. How does this connect to the previous section?
```

## Document Types & Specific Guidance

### Technical Documents

**Focus areas:**
- Accuracy of technical details
- Completeness of procedures
- Clarity for target audience expertise level
- Consistency of terminology

**Common issues:**
```markdown
[JARGON]: "Leverage the API endpoint" --> "Use the API endpoint"
[ASSUMPTION]: This assumes reader knows X. Add brief explanation or link.
[MISSING STEP]: Step 3 and 4 have a gap--what happens between them?
```

### Business Documents

**Focus areas:**
- Clear value proposition
- Supporting evidence for claims
- Professional tone
- Call to action

**Common issues:**
```markdown
[VAGUE]: "Significant improvement" --> "23% improvement in processing time"
[PASSIVE]: "Mistakes were made" --> "The team identified three errors"
[WEAK CLOSE]: End with clear next steps or call to action
```

### Marketing Content

**Focus areas:**
- Audience engagement
- Brand voice consistency
- Compelling narrative
- SEO considerations (if applicable)

**Common issues:**
```markdown
[BENEFIT]: Feature stated, but what's the customer benefit?
[PROOF]: Claim needs testimonial, case study, or data
[CTA]: Add clear call to action
```

## Version Control

### Naming Convention

```
document_v1.0_draft.md
document_v1.1_reviewed.md
document_v1.2_author-revisions.md
document_v2.0_final.md
```

### Change Log

```markdown
## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-15 | Alice | Initial draft |
| 1.1 | 2025-01-16 | Bob | Review feedback |
| 1.2 | 2025-01-17 | Alice | Incorporated feedback |
| 2.0 | 2025-01-18 | Alice | Final version |
```

## Execution Checklist

- [ ] Completed initial read-through
- [ ] Noted overall impressions and priorities
- [ ] Performed detailed section-by-section review
- [ ] Categorized feedback (content, structure, style, technical)
- [ ] Used appropriate collaboration mode
- [ ] Provided specific, actionable suggestions
- [ ] Included rationale for changes
- [ ] Created summary with next steps
- [ ] Updated version control
- [ ] Communicated timeline for next revision

## Error Handling

### Common Issues

**Issue: Author feels overwhelmed by feedback**
- Cause: Too many suggestions at once
- Solution: Prioritize top 3-5 issues, address others in later rounds

**Issue: Feedback is ignored**
- Cause: Not actionable or unclear rationale
- Solution: Be specific, explain "why", offer solutions not just problems

**Issue: Revision cycle never ends**
- Cause: Scope creep or perfectionism
- Solution: Define "done" criteria upfront, limit revision rounds

**Issue: Conflicting feedback from multiple reviewers**
- Cause: No clear decision owner
- Solution: Designate final decision maker, use RACI matrix

## Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Feedback Clarity | > 90% actionable | Ratio of accepted to clarification-needed |
| Revision Rounds | <= 3 | Count from draft to final |
| Review Turnaround | < 48 hours | Time from receipt to feedback |
| Author Satisfaction | > 4/5 | Post-review survey |

## Best Practices

### For Reviewers

1. **Be specific**: Point to exact text, not vague areas
2. **Be constructive**: Offer solutions, not just problems
3. **Prioritize**: Distinguish critical from nice-to-have
4. **Explain reasoning**: Help author learn and decide
5. **Respect voice**: Preserve author's style where appropriate

### For Authors

1. **Consider all feedback**: Even if not accepting
2. **Ask clarifying questions**: Before dismissing suggestions
3. **Track decisions**: Note why changes were accepted/rejected
4. **Thank reviewers**: Acknowledge contribution

### For Both

1. **Agree on process**: Establish review expectations upfront
2. **Set timelines**: Clear deadlines for each review round
3. **Use consistent tools**: Same markup/format for all feedback
4. **Communicate changes**: Notify when versions are ready

## Related Skills

- [internal-comms](../internal-comms/SKILL.md) - Writing communications
- [brand-guidelines](../brand-guidelines/SKILL.md) - Voice consistency
- [skill-creator](../../builders/skill-creator/SKILL.md) - Documentation patterns

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with collaboration modes, feedback categories, review workflow, document type guidance, version control
