---
name: data-context-extractor-step-1-load-existing-skill
description: 'Sub-skill of data-context-extractor: Step 1: Load Existing Skill (+3).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Step 1: Load Existing Skill (+3)

## Step 1: Load Existing Skill


Ask user to upload their existing skill (zip or folder), or locate it if already in the session.

Read the current SKILL.md and reference files to understand what's already documented.


## Step 2: Identify the Gap


Ask: "What domain or topic needs more context? What queries are failing or producing wrong results?"

Common gaps:
- A new data domain (marketing, finance, product, etc.)
- Missing metric definitions
- Undocumented table relationships
- New terminology


## Step 3: Targeted Discovery


For the identified domain:

1. **Explore relevant tables**: Use `~~data warehouse` schema tools to find tables in that domain
2. **Ask domain-specific questions**:
   - "What tables are used for [domain] analysis?"
   - "What are the key metrics for [domain]?"
   - "Any special filters or gotchas for [domain] data?"

3. **Generate new reference file**: Create `references/[domain].md` using the domain template


## Step 4: Update and Repackage


1. Add the new reference file
2. Update SKILL.md's "Knowledge Base Navigation" section to include the new domain
3. Repackage the skill
4. Present the updated skill to user

---
