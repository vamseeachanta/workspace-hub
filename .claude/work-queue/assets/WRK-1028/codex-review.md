**VERDICT: REVISE**

**Findings**
- P1: The Stage 7 gate in the plan does not match the current canonical plan gate contract. The proposal gates Stage 7 on `confirmed_by:` in the lifecycle HTML, but the actual validator requires the final plan artifact referenced by `plan_html_review_final_ref` to contain `confirmed_by`, `confirmed_at`, and `decision: passed` before downstream gates pass. If implemented as written, Stage 7 can “pass” locally while `claim-item.sh` / `close-item.sh` still fail the real gate. See [WRK-1028.md#L145](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L145), [verify-gate-evidence.py#L535](/mnt/local-analysis/workspace-hub/scripts/work-queue/verify-gate-evidence.py#L535), [process.md#L94](/mnt/local-analysis/workspace-hub/.claude/work-queue/process.md#L94).
- P1: The Stage 17 gate is attached to the wrong transition/artifact. The plan says Gate 17→18 blocks writes to `reclaim.yaml` until close review approval, but reclaim is conditional continuity recovery, not the normal post-review path. The canonical lifecycle still treats reclaim separately and close readiness is enforced at close, not by forcing reclaim. This would hard-wire the wrong control point. See [WRK-1028.md#L145](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L145), [workflow-gatepass/SKILL.md#L67](/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/workflow-gatepass/SKILL.md#L67), [workflow-gatepass/SKILL.md#L142](/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/workflow-gatepass/SKILL.md#L142).
- P1: The plan introduces a second gate enforcement plane (`gate-check.py` PreToolUse hook) instead of extending the existing canonical one. Current repo policy already says runtime callers must use `verify-gate-evidence.py` with shared activation in `stage5-gate-config.yaml`; no caller may invent private enablement. A hook-only blocker risks split-brain enforcement across agents and wrappers. See [stage5-gate-config.yaml#L7](/mnt/local-analysis/workspace-hub/scripts/work-queue/stage5-gate-config.yaml#L7), [workflow-gatepass/SKILL.md#L52](/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/workflow-gatepass/SKILL.md#L52), [work-queue-workflow/SKILL.md#L97](/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/work-queue-workflow/SKILL.md#L97).
- P1: The plan does not update the repo’s canonical process document, which still declares a 10-stage lifecycle and different stage names. Updating only the two skills leaves the system-of-record inconsistent. This is a governance break, not documentation polish. See [process.md#L8](/mnt/local-analysis/workspace-hub/.claude/work-queue/process.md#L8), [WRK-1028.md#L152](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L152).

- P2: `start-stage.sh` / `exit-stage.sh` are feasible as wrappers, but “spawn Task agent” is underspecified. There is no provider-agnostic runner contract in the plan for Claude/Codex/Gemini, so this is only feasible if reduced to generating a prompt/package plus a human or orchestrator handoff. As written, the shell script owns orchestration it cannot portably perform. See [WRK-1028.md#L131](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L131).
- P2: The contract schema is too small to encode existing mandatory evidence. Current gates require browser-open evidence, publish-to-origin evidence, future-work capture, integrated test counts, and stage-ledger coverage. The proposed 11-field contract plus one generic `blocking_condition` cannot represent those without re-hardcoding stage-specific logic in the scripts, which undermines the “contract-driven” design. See [WRK-1028.md#L126](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L126), [workflow-gatepass/SKILL.md#L113](/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/workflow-gatepass/SKILL.md#L113), [process.md#L146](/mnt/local-analysis/workspace-hub/.claude/work-queue/process.md#L146).
- P2: The context-budget rule uses file size as the stop condition. That is implementable, but it is a poor proxy for actual model context and will likely fail on large HTML artifacts, especially the single lifecycle HTML the plan wants to read repeatedly. Without chunking/slicing rules, heavy stages will stop too often or require manual bypass. See [WRK-1028.md#L60](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L60), [WRK-1028.md#L160](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L160).
- P2: Test coverage is incomplete for the highest-risk behavior. The listed tests only exercise Gate 5 hook behavior; there is no coverage for Gate 7, Gate 17, activation-config interaction, non-WRK false-positive suppression, or compatibility with `claim-item.sh` / `close-item.sh` / `archive-item.sh`. See [WRK-1028.md#L149](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1028.md#L149).

**Assessment**
Completeness: partial. The plan covers the new artifacts and wrapper scripts, but it does not fully account for existing canonical validators, wrapper callers, browser/publish evidence, future-work gating, or the canonical process doc.

Feasibility:
- `start-stage.sh` / `exit-stage.sh`: feasible if scoped to artifact validation, prompt assembly, stage-state updates, and lifecycle HTML updates.
- `gate-check.py` PreToolUse hook: not feasible as the primary cross-agent enforcement mechanism in its current form. It is at best a supplemental guard for one orchestrator; the canonical enforcement point still needs to remain script-level in `verify-gate-evidence.py` and the queue wrappers.

**P1 critical risks**
- Split-brain gate enforcement between hook logic and canonical validator.
- Stage 7 contract mismatch with `verify-gate-evidence.py`.
- Misplaced Stage 17 reclaim gate.
- Failure to update the canonical process source.

**P2 significant risks**
- No portable task-agent spawn contract.
- Contract schema too weak for current evidence semantics.
- File-size context budgeting will be noisy and brittle.
- Insufficient tests for the new control plane.

**Gaps**
- Add explicit migration of [process.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/process.md).
- Define whether stage wrappers extend `verify-gate-evidence.py` or merely feed it; do not create a competing authority.
- Specify Stage 7 and Stage 17 predicates in terms of existing canonical artifacts.
- Add compatibility tests proving `claim-item.sh`, `close-item.sh`, and `archive-item.sh` still pass.
- Define a chunking/selector strategy for large entry artifacts instead of raw file-size gating.
