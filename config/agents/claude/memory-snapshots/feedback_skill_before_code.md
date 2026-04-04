---
name: feedback_skill_before_code
description: Always build/update a skill BEFORE writing implementation code — user has repeatedly asked for this workflow and it keeps being ignored
type: feedback
---

Build the skill first, then implement. The user has emphasized this multiple times.

**Why:** Skills capture the approach, patterns, and design decisions BEFORE code is written. Without a skill, implementation proceeds without a documented methodology, making it harder to review, reuse, and iterate. The POC approach of learning on 10 sheets first was good — but the learning should flow into a skill BEFORE scaling.

**How to apply:** For any new feature or capability:
1. Research the landscape (libraries, patterns, prior art)
2. Write/update the relevant skill with the chosen approach
3. THEN implement code following the skill
Never jump straight to coding. If a skill exists, update it with new learnings. If none exists, create one first.
