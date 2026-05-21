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
11. Treat delegation/dispatch strategy as an independent decision from tier-1 repo placement. Do not justify broad local cloning primarily by "delegation friction" unless a separate approved delegation plan explicitly makes local clones a requirement. Repo placement decisions should stand on repo/data locality, canonical source of truth, storage footprint, sync/backup risk, licensed tooling, and machine role.
12. If the user says "start with A then B then C," preserve that order in both the issue bodies and the final response. Create or verify the full requested issue set when asked for "each machine," but make the decision agenda explicit so review starts with the first machine.
13. When adding recommendation comments after issue creation, keep them evidence-tiered:
    - `live-verified` for machines probed directly in the current session,
    - `remote-verified` for machines checked over SSH or equivalent,
    - `registry-based / needs GUI verification` for licensed Windows or offline machines that are not reachable from the control plane.
    Do not collapse these into a single confidence level.
14. Recommendation comments should propose a minimal baseline repo set plus conditional/on-demand repos, with rationale by machine capability. They are recommendations for user decision, not implementation approval. Keep the issue in the decision/planning intake state (normally `status:needs-plan`) until a canonical plan artifact and adversarial review exist; never convert a repo-placement decision or recommendation comment into `status:plan-approved` without explicit user approval.
15. When the user responds with numbered decisions/corrections, record those decisions back onto the corresponding machine issues in the same order before doing any operational repo work. Preserve user constraints as first-class placement rules, not as side notes. Examples of durable decision constraints:
    - data locality: `worldenergydata` belongs on `ace-linux-1` when it needs `/mnt/ace` data access, unless a separate data-access design exists for another machine;
    - licensed/client scope: licensed Windows machines may be deliberately narrow (for example ACMA/client-related work plus OrcaFlex) and should not become broad tier-1 mirrors by default.
16. Use `gh issue comment --body-file` for multiline recommendation or decision-capture comments, then re-query or use the returned comment URL before claiming the comment landed.
17. If cleanup/pre-completion audit finds unrelated dirty worktree residue, report it as blocking dispatchability or closeout only; do not clean, commit, or co-mingle it with the repo-placement decision unless the user approves that separate cleanup.
18. When the user selects or starts the first machine for deeper planning, transition only that machine issue into a canonical plan artifact. Keep the other machine issues as decision issues unless separately directed. The first-machine plan should preserve the repo-operation boundary: classify repos as required/optional/reference/not-planned, cite live evidence and constraints, and explicitly exclude clone/move/delete/sync work until the plan passes review and user approval.
19. If the first-machine decision exposes physical checkout normalization work (for example sibling checkouts vs nested checkouts under `workspace-hub/`), open or reuse a separate execution/planning issue for the relocation/cleanup work and link it back to the machine decision issue. Do not fold physical moves into the decision issue, and do not perform moves/deletes during reconnaissance. In recommendations, classify duplicate checkouts by role: `primary working checkout`, `protected secondary with untracked artifacts`, `clean duplicate candidate`, or `absent/needs placement decision`.
20. Before drafting or re-drafting a machine placement plan, verify every cited authority path exists. For workspace-hub workstation placement, prefer the live workstation registry (`config/workstations/registry.yaml` when present) as the single source of truth rather than inventing per-machine config files. If a referenced policy/contract path is missing, either find the real successor or mark it as a gap; do not let fabricated paths enter the plan.
21. If adversarial review artifacts are part of the issue gate and a provider times out or fails before producing a substantive verdict, write an explicit `UNAVAILABLE`/timeout artifact in the durable review results path instead of leaving an empty `.err` or silently omitting the provider. The issue comment should separate actual `MAJOR` findings from unavailable-provider status.
22. If the plan artifact is drafted but adversarial review has not run, leave the issue in the planning intake state and post a progress comment with artifact paths and the remaining gate. Do not label it `status:plan-review` until review artifacts exist and blocking findings are resolved or explicitly surfaced for user decision.
23. Final chat/report output should be a compact ordered list of clickable GitHub issue links plus any creation/reuse gaps. Avoid a long narrative; the next action is user decision on the first machine.
24. If the session creates a companion harness/worktree/repo-placement report artifact, treat it as evidence, not closeout by itself. Report the artifact path and live git status (`tracked`, `modified`, `untracked`, `committed/pushed`) explicitly. If unrelated dirty worktree state prevents a clean commit, leave the artifact uncommitted, say so plainly, and do not claim repository-state closure.
25. When a sibling tier-1 layout has just been established or verified, post a live sibling inventory to the first machine issue before moving to the next machine. Include at minimum repo name, absolute path, branch, short HEAD, remote, ahead/behind, tracked dirty state, and whether it is nested under the harness repo. This turns the first machine into the baseline evidence record without making current checkouts the desired-state authority.
26. After the first-machine sibling inventory, the next decision checkpoint is registry reconciliation, not clone/move/delete work. Compare the live inventory to the repo-tracked workstation registry/manifest and classify each repo for that machine as `required`, `optional`, `reference-only`, or `not planned`; preserve any harness repo dirty/ahead-behind state as a dispatch blocker to resolve separately.
27. Use the first machine's verified sibling layout as a reference pattern for subsequent machines, but do not mirror it blindly. For secondary Linux or licensed machines, collect live reachability/storage/tool/license facts first, then recommend a minimal local repo set plus network/reference-only access where appropriate. Network access to a primary machine is acceptable for read-only shared data/reference artifacts, but should not be treated as default for write-heavy Git operations, builds, tests, or parallel agent worktrees. Keep any agent-delegation rationale in a separate delegation/dispatch decision thread; the repo-placement issue may link to it but should not inherit its assumptions automatically.
28. After one machine's placement plan is approved and implemented, close that machine transactionally before shifting focus: record the registry mutation, test that locks the expected absolute repo paths/layout, validation command output, pushed commit(s), issue comment evidence, and final issue state/labels. Then start the next machine from a fresh decision checkpoint rather than assuming the same registry entry should be copied.
29. For the next machine in sequence, the first useful recommendation comment should be a narrow live-facts memo: SSH/reachability, candidate repo roots, existing `workspace-hub` checkout location, presence/absence of target tier-1 repos, disk headroom by candidate root, and tool/runtime observations. Recommend the repo root and minimal repo set from those facts, but explicitly wait for user decision before mutating the repo-tracked workstation registry or planning physical clone/relocation work.
30. If the session parks machine-placement work after drafting local plan artifacts but before adversarial review, make the handoff gate-explicit: list each issue URL, local plan path, current live gate label (`status:needs-plan`, `status:plan-review`, etc.), and the exact next gated action. Do not imply that a recommendation comment or draft plan is equivalent to `status:plan-review`; the correct next step is adversarial review on the first executable machine/normalization plan, then promotion only after review artifacts exist.
31. When context is compacted or resumed mid-machine sequence, avoid duplicate issue creation by first treating the most recent issue URLs and plan paths as candidate state to verify. The restart response should be a compact ordered state table, not a new planning narrative: current issue, evidence posted, gap/blocker, and recommended next action.
32. Before closing or handing off machine decision issues, verify that every plan/checklist artifact linked from `docs/plans/README.md` is actually tracked and pushed (`git ls-tree -r HEAD -- <path>` and remote HEAD check). Do not let the index reference untracked local artifacts. If unrelated staged changes are present, unstage and commit only the decision artifacts; preserve unrelated dirty work and report it separately.
33. Close pure decision issues only after the user decision is recorded, the artifact is tracked/pushed, and implementation is explicitly handed off to a separate approved-plan issue. If live machine evidence is unavailable (for example Windows GUI-only hosts), move the issue to `status:blocked` with a GUI-verification blocker instead of pretending registry evidence is readiness evidence.

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
