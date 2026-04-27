---
name: github-visual-planning-issues
description: Create review-friendly GitHub planning issues that supersede stale/seasonal issues and include source-backed image thumbnails for faster human review.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - When a user asks to create a GitHub issue for a trip, plan, portfolio item, or other review artifact where pictures/examples make review easier
  - When an existing issue is stale/seasonal and the user wants a replacement issue rather than editing the old one in-place
  - When a GitHub issue body needs embedded images, candidate options, visual comparison tables, or stay/product/location previews
related_skills:
  - github-issues
  - github-comment-body-file-safety
tags: [github, issues, planning, visuals, markdown, shell-safety]
---

# GitHub Visual Planning Issues

## Class of task

Use this for review-friendly GitHub planning issues where the deliverable is a structured issue body with visual thumbnails and links, especially when replacing or superseding a stale issue.

## Workflow

1. **Inspect the prior issue first**
   - Use `gh issue view <number> --repo <owner/repo> --json number,title,state,url,body,labels,comments`.
   - Identify what is stale, seasonal, duplicated, or still useful.

2. **Search for duplicates / related issues**
   - Use `gh issue list --repo <owner/repo> --state all --search "key terms" --json number,title,state,url`.
   - Reuse the old issue if it substantially covers the new request; otherwise create a replacement and cross-link.

3. **Collect source-backed visuals**
   - Prefer official destination/vendor pages, repository assets, or credible pages that expose direct image URLs.
   - Browser flow: navigate to source page → `browser_get_images` → choose images with meaningful `alt`, width/height, and stable URLs.
   - Do not download/rehost images unless explicitly needed; direct source URLs are enough for GitHub markdown review boards.

4. **Draft a visual review board**
   - Use compact tables with HTML thumbnails for predictable sizing:

```markdown
| Option | Preview | Notes |
|---|---|---|
| Candidate A | <img src="https://example.com/a.jpg" width="260" alt="Candidate A exterior"> | Why this option matters |
```

   - Include source links near the visual table.
   - Use descriptive alt text for review and accessibility.

5. **Use body files, not inline bodies**
   - Write long markdown to `/tmp/<issue-slug>.md`.
   - Create with `gh issue create --body-file /tmp/<issue-slug>.md`.
   - This avoids shell interpretation of markdown, image tags, pipes, parentheses, and backticks.

6. **Avoid title parsing pitfalls**
   - If a title contains `&` or other shell-significant characters, replace with words like `and` or quote carefully.
   - Some terminal wrappers may reject a literal `&` in a foreground command even if shell-quoted.

7. **Create and verify**
   - Create: `gh issue create --repo OWNER/REPO --title 'Title' --body-file /tmp/body.md --label documentation`.
   - Verify: `gh issue view <new-number> --repo OWNER/REPO --json number,title,state,url,labels,body`.
   - Check that image HTML is present and not mangled.

8. **Comment on the superseded issue**
   - If the old issue is stale/seasonal, add a short comment with the new issue link and why it supersedes the old one.
   - Leave the old issue open unless the user asked to close it or closeout policy is clear.

## Minimal checklist

- [ ] Prior issue inspected.
- [ ] Duplicate/related issue search completed.
- [ ] Labels inspected/reused.
- [ ] Visuals have direct URLs and source links.
- [ ] Body written via `--body-file`.
- [ ] Title avoids problematic shell metacharacters.
- [ ] New issue verified after creation.
- [ ] Superseded issue commented with replacement link.
