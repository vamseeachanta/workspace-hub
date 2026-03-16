---
name: skills-curation-steps
description: 'Sub-skill of skills-curation: Steps (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Steps (+1)

## Steps


1. **Browse** — visit https://skills.sh/ and identify candidate skills relevant to the
   domain under review (sort by install count for proven picks)
2. **License gate** — before any reuse, inspect the upstream repo's LICENSE file:
   - Permissive (MIT, Apache-2, CC-BY): direct adaptation allowed with attribution
   - Restrictive or unclear: summarize/paraphrase only; do not copy verbatim
   - No license: treat as all-rights-reserved; summarize only
3. **Inspect** — prefer passive review first: read the skills.sh page and raw SKILL.md
   on GitHub. Only use `npx skillsadd <owner/repo>` if runtime inspection is needed,
   and only in a disposable environment (not the live workspace)
4. **Diff against existing** — compare the skills.sh skill with the nearest equivalent
   in `.claude/skills/`:
   - Identify novel patterns (review rubrics, severity matrices, checklists, prompts)
   - Identify overlapping patterns already covered
5. **Route to action**:

| Finding | Action |
|---------|--------|
| Novel patterns + no equivalent skill | Create new skill stub incorporating the patterns |
| Novel patterns + equivalent skill exists | Enhance existing SKILL.md with the novel sections |
| Fully covered by existing skill | Skip — log `skipped: already covered` in curation-log.yaml |
| Partial overlap + gaps | Enhance existing skill; add `see_also` cross-link to upstream source |

6. **Attribute** — add `adopted_from: skills.sh/<owner/repo>` to the skill frontmatter
   (separate field; does not replace the existing `source:` field which tracks creation origin)
7. **Log** — record adoption decision in `curation-log.yaml` under the current run's
   `skills_created` or `skills_updated` count


## Key GitHub Sources


- `obra/superpowers` — general-purpose superpowers skills
- `anthropics/skills` — Anthropic-curated reference implementations
- `wshobson/agents` — agent patterns (code-review-excellence, etc.)

---
