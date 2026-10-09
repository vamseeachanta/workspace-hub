

Current authority: the originating task request or established standing authority authorizes implementation after proportionate planning, TDD and adversarial review; no separate user plan approval, approval label or local marker is required. Honor explicit planning-only limits, unresolved domain decisions and blocking findings. Consequential actions require matching action/destination authority: implementation authority alone does not authorize publication, deployment, access changes, destructive actions or outreach. Reuse existing authorization and preserve owner-controlled approval history without self-labeling.
# Interactive review-thread mode

Use this when a GitHub issue is intentionally serving as the discussion surface before a plan can be finalized.

## Trigger

- User says they need to discuss the work interactively and asks to see the GitHub issue.
- Issue body requests force-by-force, endpoint-by-endpoint, table-by-table, or acceptance-criterion-by-acceptance-criterion review before implementation.
- The planning state is not ready for implementation because user decisions are still being captured in comments.

## Preferred response shape

1. **Live issue link first** — provide the clickable GitHub issue URL immediately.
2. **Current state** — open/closed, labels, parent/source issue if relevant.
3. **Known decisions** — concise bullets only, grounded in existing issue comments.
4. **Next comment prompts** — grouped in the order the user should respond.
5. **Gate status** — honor the requested interactive planning/review scope. State that subsequent implementation requires reviewed scope and task authority, not separate plan approval.

## Operational pitfall

Do not turn a simple "show me the issue so I can comment" request into a broad resource-intel fan-out. Fetch the issue and comments, return the link and comment-ready map, then continue deeper inspection only after the user has the discussion surface.

## B1528 proj-a example pattern

For an engineering force-calculation revision issue, the comment-ready map should be force-by-force:

- coordinate/sign convention and CoG reference;
- surge force `X`;
- sway force `Y`;
- heave force `Z`, if retained/reported;
- roll moment `K`;
- pitch moment `M`;
- yaw moment `N`;
- resultant/component comparison tables and plots;
- report wording, assumptions, limitations, and traceability.

When the user has already clarified defaults, surface them compactly before the remaining prompts. Example categories:

- default case values;
- sweep/range values;
- sign convention;
- coefficient/source basis;
- calculation method;
- artifact destinations.
