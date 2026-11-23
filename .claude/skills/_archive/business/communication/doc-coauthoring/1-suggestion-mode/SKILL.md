---
name: doc-coauthoring-1-suggestion-mode
description: 'Sub-skill of doc-coauthoring: 1. Suggestion Mode (+3).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Suggestion Mode (+3)

## 1. Suggestion Mode


Provide non-destructive suggestions that the author can accept or reject.

**Format:**
```markdown
Original text here
--> **Suggested:** Revised text with improvements

**Reason:** Brief explanation of why this change improves the document.
```


*See sub-skills for full details.*

## 2. Track Changes Mode


Show exactly what was modified with clear before/after.

**Format:**
```markdown
~~deleted text~~ **added text**
```

**Example:**
```markdown
The meeting will be held ~~on Monday~~ **Tuesday at 2pm** in the main conference room.
```

## 3. Comment Mode


Add contextual feedback without changing text.

**Format:**
```markdown
[COMMENT: Your feedback here]
```

**Example:**
```markdown
Our Q3 revenue exceeded expectations by 15%. [COMMENT: Consider adding comparison to Q2 for context]
```

## 4. Section Rewrite Mode


Propose complete rewrites of sections.

**Format:**
```markdown
---
**ORIGINAL SECTION:**
[Original text]

**PROPOSED REWRITE:**
[New version]

*See sub-skills for full details.*
