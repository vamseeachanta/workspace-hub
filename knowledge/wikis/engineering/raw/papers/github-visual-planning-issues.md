# Archived Skill: `github-visual-planning-issues`

Original path: `/home/vamsee/.hermes/skills/github/github-visual-planning-issues`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-visual-planning-issues`
Consolidation date: 2026-04-29

---

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
   - If the issue is travel/season/date-sensitive, explicitly separate current-realistic expectations from seasonal/historical expectations (e.g., tulips, fall color, clear beach water, waterfall flow).

2. **Search for duplicates / related issues**
   - Use `gh issue list --repo <owner/repo> --state all --search "key terms" --json number,title,state,url`.
   - Reuse the old issue if it substantially covers the new request; otherwise create a replacement and cross-link.

3. **Collect source-backed visuals and official links**
   - Prefer official destination/vendor pages, repository assets, or credible pages that expose direct image URLs.
   - For travel/destination planning, capture both: (a) the official destination planning link, and (b) a direct preview image URL suitable for GitHub markdown.
   - Browser flow: navigate to source page → `browser_get_images` → choose images with meaningful `alt`, width/height, and stable URLs.
   - If direct images are hard to retrieve, inspect OpenGraph/Twitter metadata (`og:image`, `og:title`, `description`) with a small script and cite the source URL.
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
   - For travel/scenic issues, add a realistic season/timing board so photos do not create false expectations:
     - what scenery is probable in spring/summer/fall/winter;
     - what depends on live conditions (bloom reports, rainfall/waterfall flow, beach surf/water clarity, wildfire/haze, crowds, mosquitoes, closures);
     - which images are representative marketing/source photos versus exact same-week conditions.
   - If the user asks for seasonal photos, make the unit explicit before/while posting: **one photo per season per issue** means 4 total previews (spring/summer/fall/winter), while **four photos per season** means 16 previews per issue. When the request is ambiguous, prefer a compact 4-total four-season board first and state the interpretation; offer expansion to 16 if they want deeper review.
   - For broad trip portfolios, apply the same four-season preview standard consistently to legacy/general issues, parent route issues, and dedicated child destination issues so no review link lacks visual seasonal context.
   - Add an explicit verification rule: before booking, check recent visitor photos from the last 30–90 days, official alerts/closures, weather, and the exact lodging/listing photos.

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

8. **For portfolios, create a navigable issue tree**
   - If a user asks for multiple destinations/options, create one parent/portfolio issue per major route/state/category and one dedicated child issue per destination when individual review links are useful.
   - Back-link every child to its parent and post a parent comment listing all child GitHub issue links so the parent becomes the navigation hub.
   - Keep each child issue focused on one destination/route: official planning link, why consider it, realistic preview photo, best timing, caveats, and a short decision checklist.
   - For alternate travel/state portfolios, include a quick comparison/ranking dimension such as scenic-probability, drive reality from the origin, weather/season risk, and lodging feasibility.
   - When the user needs family/stakeholder review order, post a master ranked index plus a small ranking comment on each child issue. Make links visibly clickable, not just raw URLs buried in text:
     - master index format: `| Rank | Destination | GH link |` with rows like `[Open issue #NN](https://github.com/OWNER/REPO/issues/NN)`;
     - per-issue ranking comment format: `| Field | Value |` with `Overall rank`, `Destination`, `GH link`, and `Review tier`;
     - include plain-text fallback URLs below the table, because some chat/browser contexts hide or de-emphasize Markdown links;
     - after posting, verify mechanically that every target comment contains the visible-link heading, its own issue URL, and the master ranking URL.
   - If an already-posted index/comment has hidden or hard-to-see links, patch the existing GitHub comment with `gh api -X PATCH repos/OWNER/REPO/issues/comments/COMMENT_ID --input body.json` rather than adding duplicate correction comments.
   - Keep titles class-readable and shell-safe: `Travel Plan: <Origin> to <Destination or Region> scenic trip` or `Destination: <Name>, <State>`.
   - After bulk creation/commenting, verify coverage mechanically, e.g. loop through issue numbers and test whether body/comments contain `<img src=` or markdown images, then inspect a sample of rendered issue comments.

9. **Comment on the superseded or parent issue**
   - If the old issue is stale/seasonal, add a short comment with the new issue link and why it supersedes the old one.
   - If the new issues are alternatives to an existing route/portfolio, add a short index/ranking comment to the existing issue with all new links.
   - Leave old issues open unless the user asked to close them or closeout policy is clear.

## Minimal checklist

- [ ] Prior issue inspected.
- [ ] Duplicate/related issue search completed.
- [ ] Labels inspected/reused.
- [ ] Visuals have direct URLs and source links.
- [ ] Seasonal/current-condition caveats added when visuals are time-sensitive.
- [ ] Visuals have direct URLs and source links.
- [ ] Official planning links are included for each option/destination.
- [ ] Seasonal/date-sensitive expectations are stated when timing affects enjoyment.
- [ ] If seasonal photos are requested, the issue/comment clearly states whether it is 4 total previews (one per season) or 16 previews (four per season).
- [ ] For trip portfolios, every legacy/general, parent, and child destination issue has comparable seasonal visual context.
- [ ] Body written via `--body-file`.
- [ ] Title avoids problematic shell metacharacters.
- [ ] New issue verified after creation.
- [ ] For parent/child portfolios, parent issue has a link-index comment to all child issues.
- [ ] For alternate travel/state portfolios, each child has scenic-probability, drive-reality, timing/weather caveats, and lodging-feasibility notes.
- [ ] Superseded or parent issue commented with replacement/alternative links.
