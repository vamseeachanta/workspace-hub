# Conversational seed issue creation

Use this reference when the user pastes a substantial conversational note, ranking, or recommendation and asks to “create a new gh issue,” “track this,” or “explore this.”

## Pattern

1. **Preserve the pasted seed.** Treat the user's text as source material, not as verified fact. Quote or summarize the key criteria, ranking, and tradeoffs in the issue body so the future thread can reconstruct why the issue exists.
2. **Separate seed facts from agent findings.** Use explicit sections such as `Seed / user-provided framing`, `Working assumptions`, `Exploration lanes`, and `Verification needed`. Do not blur the original pasted recommendation with independently verified research.
3. **Create the issue before broad exploration when requested.** If the user explicitly says to create a new issue and explore, open the tracking issue first with enough structure to hold the work, then add exploration findings as comments. This preserves traceability and avoids losing the seed in transient chat.
4. **Use body/comment files.** Write the issue body and any long exploration comment to `/tmp/*.md` and use `gh issue create --body-file` / `gh issue comment --body-file`; pasted markdown often contains backticks, bullets, quotes, and punctuation that are unsafe in shell inline strings.
5. **Verify rendered state.** After creation and after each substantial comment, re-query with `gh issue view --json number,title,url,labels,body,comments` and verify: title, label, open state, seed framing present, and newest comment contains the intended marker or heading.
6. **Report clickable handles.** Return the issue URL and any important comment URL/anchor if available; avoid only saying “created issue #N.”

## Body shape

```markdown
## Summary
<one-paragraph purpose>

## Seed / user-provided framing
- Reference vibe / baseline: <what the pasted text says>
- Candidate ranking: <ordered list from pasted text>
- Constraints: <drive time, party, pet, budget, etc.>

## Working assumptions
- <origin proxy, date unknown, budget unknown, etc.>

## Exploration lanes
| Lane | Why it might fit | Known tradeoff | Verification needed |
|---|---|---|---|

## Next actions
- [ ] Verify live sources / drive times / availability as applicable
- [ ] Add ranked findings as issue comments
```

## Pitfalls

- Do not silently replace the user’s ranking with your own unless live evidence changes it; if it changes, say why in a comment.
- Do not represent pasted travel/lodging claims as booking-ready evidence unless live source checks were performed.
- Do not make a local-only plan or summary when the user explicitly asked for a GitHub issue; create the durable issue first, then explore.
