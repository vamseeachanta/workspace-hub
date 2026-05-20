# Machine repo-placement decision issues

Use when the user asks to decide which tier-1 repositories belong on each workstation or licensed machine.

## Trigger

- Requests like: "create a gh issue for each machine", "decide what tier-1 repos will be on each machine", or "start with ace-linux-1 then ace-linux-2 then licensed-win-1".
- Workstation placement/routing decisions where current checkouts must not be treated as the decision source of truth.

## Pattern

1. Search existing issues first by machine name and repo-placement/throughput terms. If a suitable machine issue already exists, reuse/update it rather than creating a duplicate.
2. Create one GitHub issue per machine rather than one umbrella-only issue when no suitable per-machine issue exists.
3. Sequence issues in the user's requested order. Current default ordering:
   - `ace-linux-1`
   - `ace-linux-2`
   - `licensed-win-1`
   - `licensed-win-2`
   - any additional machine explicitly named by the user
4. Each issue should be a decision issue, not an implementation issue. It should ask what tier-1 repos should be present on that machine and why.
5. Include the canonical tier-1 repo set as options/context:
   - `workspace-hub`
   - `digitalmodel`
   - `assetutilities`
   - `worldenergydata`
   - `llm-wiki`
   - `assethold`
   - `aceengineer-website`
   - `aceengineer-strategy`
6. Require live machine/repo facts before final decisions:
   - reachability / access status
   - existing checkout paths
   - remotes and branches
   - dirty state
   - licensed/special software available on that machine
   - storage/performance constraints if relevant
7. Distinguish decision readiness from dispatch readiness. Dirty worktrees, untracked artifacts, or missing readiness probes may block launching work on the machine, but they should not block creating or verifying the decision issue; record them as evidence/blockers.
8. Do not infer desired placement from current checkouts alone. Treat existing checkouts as evidence to classify, not as approval.
9. Cross-link the machine-specific issues to any umbrella workstation architecture, provider-lane, control-plane, or working-copy contract issue when present.
10. Keep issue creation separate from implementation: do not move, sync, delete, clone, or clean repositories while creating the decision issues unless the user separately approves that operational action.
11. If the user says "start with A then B then C," preserve that order in both the issue bodies and the final response. Create or verify the full requested issue set when asked for "each machine," but make the decision agenda explicit so review starts with the first machine.
12. When adding recommendation comments after issue creation, keep them evidence-tiered:
    - `live-verified` for machines probed directly in the current session,
    - `remote-verified` for machines checked over SSH or equivalent,
    - `registry-based / needs GUI verification` for licensed Windows or offline machines that are not reachable from the control plane.
    Do not collapse these into a single confidence level.
13. Recommendation comments should propose a minimal baseline repo set plus conditional/on-demand repos, with rationale by machine capability. They are recommendations for user decision, not implementation approval.
14. When the user responds with numbered decisions/corrections, record those decisions back onto the corresponding machine issues in the same order before doing any operational repo work. Preserve user constraints as first-class placement rules, not as side notes. Examples of durable decision constraints:
    - data locality: `worldenergydata` belongs on `ace-linux-1` when it needs `/mnt/ace` data access, unless a separate data-access design exists for another machine;
    - licensed/client scope: licensed Windows machines may be deliberately narrow (for example ACMA/client-related work plus OrcaFlex) and should not become broad tier-1 mirrors by default.
15. Use `gh issue comment --body-file` for multiline recommendation or decision-capture comments, then re-query or use the returned comment URL before claiming the comment landed.
16. If cleanup/pre-completion audit finds unrelated dirty worktree residue, report it as blocking dispatchability or closeout only; do not clean, commit, or co-mingle it with the repo-placement decision unless the user approves that separate cleanup.
17. When the user selects or starts the first machine for deeper planning, transition only that machine issue into a canonical plan artifact. Keep the other machine issues as decision issues unless separately directed. The first-machine plan should preserve the repo-operation boundary: classify repos as required/optional/reference/not-planned, cite live evidence and constraints, and explicitly exclude clone/move/delete/sync work until the plan passes review and user approval.
18. If the first-machine decision exposes physical checkout normalization work (for example sibling checkouts vs nested checkouts under `workspace-hub/`), open or reuse a separate execution/planning issue for the relocation/cleanup work and link it back to the machine decision issue. Do not fold physical moves into the decision issue, and do not perform moves/deletes during reconnaissance. In recommendations, classify duplicate checkouts by role: `primary working checkout`, `protected secondary with untracked artifacts`, `clean duplicate candidate`, or `absent/needs placement decision`.
19. Before drafting or re-drafting a machine placement plan, verify every cited authority path exists. For workspace-hub workstation placement, prefer the live workstation registry (`config/workstations/registry.yaml` when present) as the single source of truth rather than inventing per-machine config files. If a referenced policy/contract path is missing, either find the real successor or mark it as a gap; do not let fabricated paths enter the plan.
20. If adversarial review artifacts are part of the issue gate and a provider times out or fails before producing a substantive verdict, write an explicit `UNAVAILABLE`/timeout artifact in the durable review results path instead of leaving an empty `.err` or silently omitting the provider. The issue comment should separate actual `MAJOR` findings from unavailable-provider status.
21. If the plan artifact is drafted but adversarial review has not run, leave the issue in the planning intake state and post a progress comment with artifact paths and the remaining gate. Do not label it `status:plan-review` until review artifacts exist and blocking findings are resolved or explicitly surfaced for user decision.
22. Final chat/report output should be a compact ordered list of clickable GitHub issue links plus any creation/reuse gaps. Avoid a long narrative; the next action is user decision on the first machine.

## Suggested issue title shape

`decision(workstations): choose tier-1 repo placement for <machine>`

## Suggested issue body sections

- Summary
- Machine
- Decision needed
- Current observed state, if known
- Tier-1 repos to consider
- Machine-specific capabilities/constraints
- Acceptance criteria
- Related issues

## Acceptance criteria template

- [ ] Current machine reachability and installed-agent/runtime status are verified.
- [ ] Existing tier-1 checkouts on the machine are inventoried with path, remote, branch, and dirty state.
- [ ] Each tier-1 repo is classified as `required`, `optional`, `reference-only`, or `not planned` for this machine.
- [ ] Any repo that is already present but not planned is assigned a safe disposition path: keep/reference, sync, archive, or remove through an approved cleanup plan.
- [ ] Decisions are cross-linked to the working-copy/cleanup contract and any machine orchestration roadmap.
