# Sibling SSoT Post-Landing Follow-Up

Current authority: implementation follows the originating task request or established standing authority after proportionate planning, TDD and adversarial review; no separate plan approval, approval label or local marker is required. Planning-only limits, unresolved domain decisions and action-specific authorization for publication, deployment, access changes, destructive actions and outreach remain binding. Historical approval records stay intact and must not be fabricated or self-labeled.


Use after a sibling SSoT implementation closes with the core memory/skills/tools path fixed but residual repo-contract failures remain.

## Trigger

- The user asks for the "next logical step" after an SSoT landing issue.
- A checker reports remaining sibling repo failures such as missing `AGENTS.md`, missing workspace-hub inheritance text, unresolved skill symlinks, or unclear llm-wiki/client-wiki routing.
- The implementation issue is already closed, so remaining failures must not be smuggled into that closeout.

## Response Pattern

1. **Verify live state before recommending work**
   - Check issue state/labels for the just-closed issue.
   - Check the current checkout status and whether it is dirty/diverged.
   - Inspect open issues with relevant labels/titles before inventing a new issue.

2. **Separate closed acceptance from residual blockers**
   - Treat the closed issue's committed scope as done if closeout evidence exists.
   - Carry residual checker failures forward as intake evidence, not as a reason to reopen unless the issue closeout was false.

3. **Prefer the existing follow-up issue**
   - Search for an open issue that already covers the next architectural layer.
   - For SSoT → llm-wiki/client-wiki follow-on, prefer an existing data/knowledge routing issue (example shape: "lock data/knowledge/result search routing across llm-wiki + llm-wiki-<client> siblings").
   - If no issue exists, draft a narrow follow-up issue/plan rather than widening the closed issue.

4. **Do not implement from a dirty/diverged control-plane checkout**
   - If `/mnt/local-analysis/workspace-hub` is dirty or ahead/behind, recommend a clean worktree or explicit sync/reconcile step first.
   - Preserve unrelated runtime/session artifacts; do not fold them into the follow-up implementation.

5. **Stay inside the plan gate**
   - If the follow-up issue is `status:needs-plan`, draft the plan and run adversarial review.
   - Implement reviewed changes within verified task authority; SSO/access changes require their specific authorized destination and effects, not an approval label or marker.

## Reporting Template

```markdown
Next logical step: <issue/repo/action>

Why:
- <closed issue> landed <core contract>
- residual blockers are <short list>
- <follow-up issue> is the best existing continuation

Guardrail:
- current checkout is <clean/dirty/diverged>; use <clean worktree/reconcile first>
- issue is <status>; verify <task authority/review/domain decisions> before implementation; access changes retain their specific authority
```
