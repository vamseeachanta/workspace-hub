# WRK-1035 — Captured User Thoughts (staging for WRK-1035.md)

> **Action on exit**: Append `## User Notes` section to `.claude/work-queue/pending/WRK-1035.md`
> containing all 15 thoughts below. No other files to edit. No commits required.

---

## Captured thoughts — 2026-03-08

### 1. Stage jumping problem
Work item stages are jumping ahead into future stages without satisfying current stage gates.
This is a core compliance failure pattern that needs dedicated detection and enforcement.

### 2. Stage-level hooks — key idea
Should there be stage-level hooks that **definitely run** — not just skill-language rules?
AI agents are "dumbing themselves" (ignoring the skill). Hook-level enforcement is more reliable.

Candidate hook triggers to consider:
- `/checkpoint` — document all notes for the current work item + session logs. Addresses
  compaction/context-loss problems that are persisting across sessions.
- Resume work item — hooks to restore context after compaction or session break.
- Outcome of WRK-1036 (clean up of stale "Team Agents") — incorporate findings.
- Missing `Human_SESSION` review: agents are seeking user review when it is not a Human_Session
  context — this needs detection and blocking.
- Missing 1 stage and jumping ahead — systematic detection of stage-skip patterns.
- Any other consistent rules surfaced by log analysis.

### 3. Default rule adherence gap
If a violation is addressed by an existing default rule, we should:
- Review session logs to understand **why** the rule was not adhered to.
- Either tighten the skill language, or add a hook backstop.
The mere existence of a rule is insufficient — the enforcement mechanism matters.

### 4. Audit candidate signals — do not miss
There are good user notes available in audit candidates. These signals must be consumed:
- Session logs in `.claude/work-queue/logs/` and `logs/orchestrator/claude/`
- Evidence artifacts from recently closed WRKs
- User-facing notes in WRK bodies (## User Notes sections)
- Any `audit-candidates` or `future-work.yaml` items referencing compliance gaps

### 5. Scope expansion implied
WRK-1035 scope may need to expand beyond stages 5/7/17 to cover:
- General stage-skip detection (not just user-review stages)
- `/checkpoint` skill or hook
- Human_SESSION detection logic
- WRK-1036 findings integration
Consider upgrading to Route C (complex) or spinning WRK-1036/1037 as parallel tracks.

### 6. `/checkpoint` naming collision — open question
Two different things are both being called "checkpoint" and they are getting confused:
- **Interactive-session `/checkpoint`** — user runs this during a live conversation to snapshot
  notes, WRK state, and session logs mid-session (context compaction safety net).
- **Stage checkpoint** — a within-lifecycle artifact that records stage entry/exit state so a
  WRK can be resumed after a session break (what `checkpoint.yaml` in assets/ does today).

These should either be clearly distinguished by name, or the `/checkpoint` command should
explicitly target one and redirect to the other. Need to decide: are these the same thing,
or two separate commands?

### 7. `/wrk-resume WRK-NNN` vs `/work run WRK-NNN` — open question
What is the difference?
- `/wrk-resume WRK-NNN` — reads `checkpoint.yaml`, prints stage/next_action/context_summary/
  entry_reads. Purpose: **restore context** after a session break before continuing.
- `/work run WRK-NNN` (or `/work run`) — enters the full processing pipeline (session.sh →
  work.sh → plan.sh → execute.sh → review.sh). Purpose: **execute** the next stage of the WRK
  lifecycle from the beginning of that stage.

Possible clarification needed in the SKILL:
- Is `/wrk-resume` always a pre-step before `/work run` when resuming a broken session?
- Or are they alternatives depending on context?
- Should `/work run WRK-NNN` automatically invoke resume logic if a `checkpoint.yaml` exists?

### 8. `/plan` at session start — good pattern
The `/plan` command output is quite good for orienting the session. Should be invoked at the
start of every session as a standard step — shows current plan file, staged notes, and
pending decisions without requiring the agent to re-read the whole WRK file.
Candidate: add `/plan` to session-start skill as a mandatory step when a plan file exists.

### 9. Skill text → scripts: reduce context rot
Skills are too verbose — orchestrators read the full SKILL.md into context, then lose track
of the rules mid-session (context rot). Proposal:
- Extract per-stage procedural steps OUT of the skill into dedicated shell scripts, one per
  stage start and stage end (e.g. `scripts/work-queue/stage-start.sh 5`, `stage-end.sh 5`).
- The skill becomes a thin index: what each stage does + which script to call.
- Scripts are the enforcement layer — they prompt, check artifacts, and gate progress.
- Benefit: skill stays readable (< 200 lines), scripts are callable from hooks, orchestrators
  invoke scripts rather than trying to remember skill prose.

### 10. Stage-tagged approval logging
Each user approval must be logged with its stage number to prevent the orchestrator from
confusing approvals across stages (e.g. treating a Stage 5 approval as satisfying Stage 7).

Proposal:
- Every approval artifact (`user-review-plan-draft.yaml`, `plan-final-review.yaml`,
  `user-review-close.yaml`) must include a `stage: 5 | 7 | 17` field.
- The stage-end script (or gate verifier) checks that the artifact's `stage` field matches
  the stage currently being exited — reject cross-stage re-use.
- Orchestrator confusion pattern to close: agent sees an existing approval artifact and
  assumes it covers the current stage without checking the `stage` field.

### 11. Future stages must never be actively worked ahead of current stage
An agent must not produce artifacts, write evidence, or execute work for a future stage while
the current stage gate is still open.

Important nuance: reruns may leave artifacts from a previous run in future-stage directories.
These are **stale residuals**, not approvals. The agent must:
- Detect and explicitly ignore stale future-stage artifacts when entering a stage.
- Never treat a pre-existing artifact as satisfying the current stage gate.
- Log a note when a stale artifact is found: "Stale artifact from prior run detected at
  stage N — ignoring, gate must be re-satisfied in this run."

The stage-start script should scan for artifacts ahead of the current stage and warn/block
if they appear to have been written in the current session (not a prior run).

### 12. Nomenclature review — eliminate session/stage/phase confusion
Current state causes confusion: "session", "stage", "phase", and "step" are used
interchangeably across skills, scripts, and evidence artifacts, making it hard to know what
layer is being referred to.

Proposed canonical definitions to establish and enforce throughout `work-queue-workflow/SKILL.md`:

| Term | Proposed meaning |
|------|-----------------|
| **WRK session** | A single Claude interactive conversation working on a WRK item (bounded by `/clear` or context reset) |
| **WRK stage** | One of the 20 numbered lifecycle stages (Stage 1 Capture … Stage 20 Archive) |
| **Phase** | A sub-unit within a stage when a stage has multiple distinct steps (e.g. Stage 6 cross-review has 3 phases: Claude / Codex / Gemini) |
| **Step** | A numbered action within a phase or stage, listed in a checklist |
| **Checkpoint** | A snapshot artifact written at the end of a WRK session so the next session can resume (`checkpoint.yaml`) |
| **Resume** | The act of loading a checkpoint into a new WRK session to continue from the last known stage/step — invoked via `/wrk-resume WRK-NNN` before `/work run` |

Expanded table with session vs stage distinction made explicit:

| Term | Scope | Meaning |
|------|-------|---------|
| **WRK session** | Conversation | A single Claude interactive conversation working on a WRK item |
| **Session checkpoint** | Conversation | Snapshot written at end of a WRK session (`checkpoint.yaml`) — captures stage number, next_action, context_summary so the next session can orient quickly |
| **Session resume** | Conversation | Loading a session checkpoint into a new WRK conversation via `/wrk-resume WRK-NNN` before running |
| **WRK stage** | Lifecycle | One of the 20 numbered lifecycle stages (Stage 1 Capture … Stage 20 Archive) |
| **Stage checkpoint** | Lifecycle | ⚠️ CANDIDATE — a mid-stage snapshot artifact if a stage itself is too large for one session; distinct from session checkpoint; not yet implemented — needs analysis |
| **Stage resume** | Lifecycle | ⚠️ CANDIDATE — resuming from a stage checkpoint within a stage (not from the stage beginning); not yet implemented — needs analysis |
| **Phase** | Within a stage | Sub-unit within a stage (e.g. Stage 6: Claude / Codex / Gemini review phases) |
| **Step** | Within a phase | Numbered checklist action within a phase |

Rules:
- Never use "session" to mean "stage" and vice versa.
- "Phase" is only used inside a stage — not as a synonym for stage.
- Scripts, evidence artifact field names, and skill prose must all use the canonical term.
- Audit existing artifact field names (e.g. `session_id` in activation.yaml) for correctness.

**Scripts and slash commands review needed:**
- Audit all work-item-level scripts in `scripts/work-queue/` and slash commands for consistent use of terminology.
- Current `/wrk-resume` operates at session level — name may be misleading if stage-resume is added.
- If stage checkpoint / stage resume are implemented, commands need unambiguous names:
  - `/session-checkpoint` vs `/stage-checkpoint`
  - `/wrk-resume` (session) vs `/stage-resume WRK-NNN --stage N` (stage-level)
- This audit + naming decision is a prerequisite before implementing either candidate.

### 13. Lifecycle HTML — update at stage start, stage end, and on-demand
The lifecycle HTML (`WRK-NNN-lifecycle.html`) is the living record of a work item's life.
It should be regenerated:

1. **Stage start** — as a standard hook when entering any stage; reflects current stage as
   `in_progress`, prior stages as `done`.
2. **Stage end** — as a standard hook when exiting any stage; reflects the completed stage
   as `done` with evidence links.
3. **On-demand mid-session** — user can command a regeneration at any point during a session
   to see the current state without waiting for a stage boundary.

Implementation notes:
- Stage-start and stage-end scripts (from thought 9) should call
  `generate-html-review.py WRK-NNN --lifecycle` as a standard step — not optional.
- The HTML is the single source of truth for "what stage is this WRK at right now" — keeping
  it current makes user review and orchestrator orientation much faster.
- On-demand: add a slash command or work-queue command (e.g. `/work html WRK-NNN`) that
  regenerates and optionally opens the HTML in the browser.
- **Auto-refresh if already open**: if the browser already has the lifecycle HTML open,
  regeneration should trigger a refresh automatically — avoids the user having to switch tabs,
  find the right tab, and manually reload. Prevents context-switching errors (wrong tab, stale
  view). Implementation option: embed a `<meta http-equiv="refresh">` or a lightweight
  file-watch + SSE/WebSocket approach in the generated HTML.

### 14. Statusline — current WRK + stage display
Current statusline shows `[TOP:WRK-125-OrcaFlex module roadmap — ev...]` (top-priority item).
Need a **second statusline segment** (or replace/augment) showing:
- The **active/current WRK** being worked in this session (from `.claude/state/active-wrk`)
- A brief description (title truncated)
- The **current work-item stage** (1–20) and stage name

Example target format: `[WRK:WRK-1035 · Stage 4 Plan Draft]`

Notes:
- The active-wrk state file already exists (set via `set-active-wrk.sh`); stage can be read
  from `checkpoint.yaml` or inferred from evidence artifacts in `assets/WRK-NNN/`.
- TOP segment = highest-priority pending item (planning view); WRK segment = what is being
  actively executed right now (execution view) — these are different and both useful.
- If no active WRK is set, WRK segment should be blank or show `[WRK:none]`.
- statusline skill lives at `.claude/skills/workspace-hub/` (check exact path).

### 15. Orchestrator must always be a team — hard architectural rule
**Every WRK execution session must use a team of agents, not a single monolithic orchestrator session.**

Rationale: context rot is the root cause of most compliance failures — a single long-running
agent loses track of skill rules, stage gates, and approval requirements as context fills up.
Dividing work across agents keeps each agent's context small and focused.

Rule to enforce:
- No WRK should be executed in a single Claude conversation from Stage 1 to Stage 20.
- Each stage (or group of closely related stages) should be a separate agent task.
- The orchestrator's role is task decomposition + team coordination, not direct execution.
- This applies to **any Claude session** — not just orchestrator sessions.

Implementation implications:
- `work-queue-workflow/SKILL.md` should mandate TeamCreate + TaskCreate at the start of
  every WRK execution (after Stage 5 approval).
- `spawn-team.sh` (new, in git status) is likely the entry point — formalize it.
- Session-start skill should check: "Is there an active WRK? If yes, spawn team rather than
  executing directly."
- WRK-1035 itself should serve as the first example of this pattern in practice.

Open design question:
- Should each stage be one Task, or should sub-tasks within a stage be further split?
- Minimum granularity recommendation needed (e.g. "one agent per stage" or "one agent per
  200-line file change").

---

*To apply: write `## User Notes` section into WRK-1035.md with these points, bump scope assessment.*
