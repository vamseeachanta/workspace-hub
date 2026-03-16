---
name: memory-management-decoding-user-input-tiered-lookup
description: 'Sub-skill of memory-management: Decoding User Input (Tiered Lookup)
  (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Decoding User Input (Tiered Lookup) (+3)

## Decoding User Input (Tiered Lookup)


**Always** decode shorthand before acting on requests:

```
1. CLAUDE.md (hot cache)     → Check first, covers 90% of cases
2. memory/glossary.md        → Full glossary if not in hot cache
3. memory/people/, projects/ → Rich detail when needed
4. Ask user                  → Unknown term? Learn it.
```

Example:
```
User: "ask todd to do the PSR for oracle"

CLAUDE.md lookup:
  "todd" → Todd Martinez, Finance ✓
  "PSR" → Pipeline Status Report ✓
  "oracle" → (not in hot cache)

memory/glossary.md lookup:
  "oracle" → Oracle Systems deal ($2.3M) ✓

Now Claude can act with full context.
```


## Adding Memory


When user says "remember this" or "X means Y":

1. **Glossary items** (acronyms, terms, shorthand):
   - Add to memory/glossary.md
   - If frequently used, add to CLAUDE.md Quick Glossary

2. **People:**
   - Create/update memory/people/{name}.md
   - Add to CLAUDE.md Key People if important
   - **Capture nicknames** - critical for decoding

3. **Projects:**
   - Create/update memory/projects/{name}.md
   - Add to CLAUDE.md Active Projects if current
   - **Capture codenames** - "Phoenix", "the migration", etc.

4. **Preferences:** Add to CLAUDE.md Preferences section


## Recalling Memory


When user asks "who is X" or "what does X mean":

1. Check CLAUDE.md first
2. Check memory/ for full detail
3. If not found: "I don't know what X means yet. Can you tell me?"


## Progressive Disclosure


1. Load CLAUDE.md for quick parsing of any request
2. Dive into memory/ when you need full context for execution
3. Example: drafting an email to todd about the PSR
   - CLAUDE.md tells you Todd = Todd Martinez, PSR = Pipeline Status Report
   - memory/people/todd-martinez.md tells you he prefers Slack, is direct
