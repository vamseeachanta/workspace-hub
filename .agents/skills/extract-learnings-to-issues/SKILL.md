---
name: extract-learnings-to-issues
description: Extract unstructured user reflections and learnings, distill core themes, route insights to existing GitHub issues as contextual comments rather than creating duplicates.
version: 1.0.0
---

# Extract Learnings to Issues

Convert unstructured user thoughts, reflections, and learnings into structured, actionable GitHub issue content that enhances existing issues rather than creating noise.

## When to Use

- User shares random thoughts/workflow reflections and wants them "captured"
- User says "put this into issues" or "filter this to repos"
- Post-session learnings that should compound in the repo
- User wants their reflections to "straighten the twisted brain"

## Pattern

### Phase 1: Distill Themes

Parse the unstructured thoughts and extract core themes. Look for:
- Problems/gaps identified
- Insights about what works (secret sauce)
- Proposed improvements or next steps
- Metrics or evidence of problems
- Connections to existing work

### Phase 2: Map to Existing Issues

CRITICAL: Before creating any new issues, search the existing landscape:

```bash
cd /mnt/local-analysis/workspace-hub

# Search by label categories
gh issue list --label cat:harness --state open --limit 10
gh issue list --label cat:platform --state open --limit 10
gh issue list --label domain:knowledge --state open --limit 10

# Search by keywords
gh issue search "keyword1 OR keyword2" --state open --limit 10

# View key issues
gh issue view $NUM 2>/dev/null
```

Map each distilled theme to the most relevant existing issue.

### Phase 3: Route as Comments (NOT New Issues)

Write a body file and add as a comment to the existing issue:

```bash
cat > /tmp/comment_$NUM.md << 'EOF'
## Context Update (date)

[Distilled insight from user's reflection]

[Specific additions to acceptance criteria]
[Related issues to link]
[Quotes from user for context]
EOF

gh issue comment $NUM --body-file /tmp/comment_$NUM.md
```

If no existing issue covers a theme, create a focused new issue with clear acceptance criteria and references.

### Phase 4: Close Any Unnecessary Issues

If you created issues before realizing they're duplicates:

```bash
gh issue comment $NUM --body "Closing as duplicate of #EXISTING - see context added there."
gh issue close $NUM
```

## Key Principles

- ROUTE over CREATE: Always prefer enhancing existing issues
- Quote the user: Preserve their exact words for context
- Be specific: Add actionable acceptance criteria, not just commentary
- Cross-link: Connect related issues explicitly
- Minimize noise: The goal is signal, not issue proliferation
