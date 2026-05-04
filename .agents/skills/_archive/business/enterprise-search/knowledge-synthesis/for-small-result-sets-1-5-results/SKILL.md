---
name: knowledge-synthesis-for-small-result-sets-1-5-results
description: 'Sub-skill of knowledge-synthesis: For Small Result Sets (1-5 results)
  (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# For Small Result Sets (1-5 results) (+3)

## For Small Result Sets (1-5 results)


Present each result with context. No summarization needed — give the user everything:
```
[Direct answer synthesized from results]

[Detail from source 1]
[Detail from source 2]

Sources: [full attribution]
```


## For Medium Result Sets (5-15 results)


Group by theme and summarize each group:
```
[Overall answer]

Theme 1: [summary of related results]
Theme 2: [summary of related results]

Key sources: [top 3-5 most relevant sources]
Full results: [count] items found across [sources]
```


## For Large Result Sets (15+ results)


Provide a high-level synthesis with the option to drill down:
```
[Overall answer based on most relevant results]

Summary:
- [Key finding 1] (supported by N sources)
- [Key finding 2] (supported by N sources)
- [Key finding 3] (supported by N sources)

Top sources:
- [Most authoritative/relevant source]
- [Second most relevant]
- [Third most relevant]

Found [total count] results across [source list].
Want me to dig deeper into any specific aspect?
```


## Summarization Rules


- Lead with the answer, not the search process
- Do not list raw results — synthesize them into narrative
- Group related items from different sources together
- Preserve important nuance and caveats
- Include enough detail that the user can decide whether to dig deeper
- Always offer to provide more detail if the result set was large
