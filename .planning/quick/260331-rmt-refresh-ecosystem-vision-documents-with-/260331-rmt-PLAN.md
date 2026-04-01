---
phase: quick
plan: 260331-rmt
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/vision/VISION.md
  - .planning/ROADMAP.md
  - digitalmodel/ROADMAP.md
  - .planning/MILESTONES.md
  - .planning/phases/07-solver-verification-gate/07-VALIDATION.md
  - docs/architecture/solver-queue.md
autonomous: true
---

<objective>
Refresh ecosystem vision and planning documents with 8 post-v1.0 improvements: close resolved capability gaps, add measurable L4 indicators, align phase counts, add horizon tags, update validation status, close digitalmodel tech debt item, add WRK rubric scores to backlog, and document the git-based solver queue as a reusable architecture pattern. All documentation updates, no code changes.
</objective>

<tasks>

<task type="auto">
  <name>Task 1: VISION.md post-v1.0 refresh with measurable L4 indicators</name>
  <files>
    docs/vision/VISION.md
  </files>
  <read_first>
    docs/vision/VISION.md
    docs/governance/TRUST-ARCHITECTURE.md
  </read_first>
  <action>
    **Item 1 — Mark trust architecture gap as closed:**
    In the "Capability Gap Analysis" table, update the "Trust architecture formalisation" row:
    - Change "Current state" from "Plan gate + WRK trail exist but are not documented as a governance model" to "Governance model documented in docs/governance/TRUST-ARCHITECTURE.md (WRK-381): action classification (A/B/C), plan gate rules, audit trail format, rollback rules, escalation triggers"
    - Change "Gap" to "Closed (v1.0)"
    - Change "WRK candidates" to "WRK-381 (delivered)"

    **Item 1 — Update "Where We Are" table:**
    In the "Where We Are: Current Repository Missions" table, change workspace-hub's Autonomy Level from "L3" to "L3" (confirm it already says L3; if it says L2-L3, update to L3). Rationale: v1.0 shipped nightly research automation, GSD framework, and solver queue — all L3 capabilities.

    **Item 1 — Add "What v1.0 Proved" section:**
    After the "Where We Are" table (before "## The 6-Level Autonomy Framework"), insert:

    ```markdown
    ### What v1.0 Proved (shipped 2026-03-30)

    The v1.0 Foundation Sprint (6 phases, 21 plans, 5 days) validated three assumptions:

    1. **AI-assisted sprint velocity is real.** 3 new calculation modules (OBS, wall thickness, spectral fatigue) shipped at 90.5% test coverage with standards traceability — each module from zero to production in under one day.
    2. **The traceability chain works end-to-end.** Standard clause to implementation to test to report — demonstrated across DNV-RP-F109, ASME B31.4, and Dirlik/TB spectral methods.
    3. **Cross-machine solver dispatch is viable without SSH.** The git-based pull queue (Phase 7) proved that corporate firewall constraints can be satisfied with a polling architecture — no inbound connections needed.
    ```

    **Item 3 — Add measurable L4 indicators section:**
    After the "## 3-Horizon Roadmap" section (before "## The WRK Scoring Rubric"), insert:

    ```markdown
    ## Measurable L4 Indicators

    Progress toward Level 4 autonomy is tracked by three quantitative metrics:

    | Metric | L3 Baseline (current) | L4 Target | Measurement Method |
    |--------|----------------------|-----------|-------------------|
    | **% solver runs initiated by schedule vs human** | ~0% (all human-initiated) | >50% of routine analyses | Count queue/completed/ jobs by trigger type (manual vs scheduled) |
    | **Time-to-first-result per workflow type** | Hours (human in loop) | <30 min for routine workflows | Timestamp delta: job submission to report generation |
    | **Report drafts needing zero human edits** | ~0% (all reviewed) | >30% of routine reports | Track reports shipped without modification after AI draft |

    These metrics become actionable once the solver queue (Phase 7) is processing jobs regularly. Initial baselining begins with the first OrcaWave batch run.
    ```

    **Update the "Last updated" footer** to: `*Last updated: 2026-03-31 | Post-v1.0 refresh | Maintained in workspace-hub/docs/vision/*`
  </action>
  <verify>
    <automated>grep -c "Closed (v1.0)" docs/vision/VISION.md && grep -c "What v1.0 Proved" docs/vision/VISION.md && grep -c "Measurable L4 Indicators" docs/vision/VISION.md</automated>
  </verify>
  <done>VISION.md updated with closed trust gap, v1.0 proof section, and measurable L4 indicators</done>
</task>

<task type="auto">
  <name>Task 2: ROADMAP.md, MILESTONES.md, digitalmodel ROADMAP.md, and VALIDATION.md updates</name>
  <files>
    .planning/ROADMAP.md
    .planning/MILESTONES.md
    digitalmodel/ROADMAP.md
    .planning/phases/07-solver-verification-gate/07-VALIDATION.md
  </files>
  <read_first>
    .planning/ROADMAP.md
    .planning/MILESTONES.md
    digitalmodel/ROADMAP.md
    .planning/phases/07-solver-verification-gate/07-VALIDATION.md
    .planning/phases/07-solver-verification-gate/07-02-SUMMARY.md
    .planning/phases/07-solver-verification-gate/07-01-SUMMARY.md
  </read_first>
  <action>
    **Item 2 — Add horizon tags to ROADMAP.md phases:**
    In .planning/ROADMAP.md, update Phase 7 heading from:
    `### Phase 7: Solver Verification Gate — OrcFxAPI + remote execution go/no-go`
    to:
    `### Phase 7: Solver Verification Gate — OrcFxAPI + remote execution go/no-go [H1]`

    Add a comment line after each backlog phase title with its horizon tag:
    - Phase 999.1 (Ship Plan CAD Pipeline): add `<!-- H2: geometry reconstruction for autonomous hull lofting -->` after the heading
    - Phase 999.2 (Wind Energy): add `<!-- H2: new engineering domain expansion -->` after the heading
    - Phase 999.3 (CAD/CAM): add `<!-- H2: calculation-to-fabrication pipeline -->` after the heading
    - Phase 999.4 (Autoresearch): add `<!-- H1: AI interface skills for P1/P2 tools -->` after the heading
    - Phase 999.5 (High-Iteration): add `<!-- H1: compounding improvement loop -->` after the heading
    - Pint Unit Conversion: add `<!-- H1: technical debt closure -->` after the heading

    **Item 7 — Add WRK rubric scores to backlog entries:**
    In .planning/ROADMAP.md, add rubric score comments to each backlog phase heading:
    - Phase 999.1: `<!-- WRK rubric: 1/4 (no named gap, no autonomy lift, no SPA loop, no time-to-result) -->`
    - Phase 999.2: `<!-- WRK rubric: 1/4 (no named gap, potential L2→L3 for new domain, no SPA, no time-to-result) -->`
    - Phase 999.3: `<!-- WRK rubric: 0/4 (no named gap, no autonomy lift, no SPA, no time-to-result) -->`
    - Phase 999.4: `<!-- WRK rubric: 3/4 (closes self-healing gap, L3→L4 lift, tightens SPA, reduces time-to-result) -->`
    - Phase 999.5: `<!-- WRK rubric: 4/4 (closes self-healing gap, L3→L4 lift, tightens SPA, reduces time-to-result) -->`

    **Item 6 — Fix MILESTONES.md phase count:**
    In .planning/MILESTONES.md, change:
    `**Phases completed:** 9 phases, 21 plans, 47 tasks`
    to:
    `**Phases completed:** 6 phases, 21 plans, 47 tasks`
    (v1.0 had 6 phases, not 9)

    **Item 4 — Close digitalmodel ROADMAP.md tech debt item 7:**
    In digitalmodel/ROADMAP.md, under "### Category C — Aspirational", update item 7 from:
    `7. **No VISION.md at repo root.** CALCULATIONS-VISION.md exists in `docs/vision/` but the ecosystem-level VISION.md it references does not exist.`
    to:
    `7. ~~**No VISION.md at repo root.**~~ Closed — Phase 6 delivered `docs/vision/CALCULATIONS-VISION.md` as the canonical library vision document (2026-03-29).`

    **Item 5 — Update Phase 7 VALIDATION.md:**
    In .planning/phases/07-solver-verification-gate/07-VALIDATION.md:
    a. Change frontmatter `wave_0_complete: false` to `wave_0_complete: true`
    b. In the Per-Task Verification Map table:
       - Change 07-01-01 Status from `pending` to `green` (plan 01 completed per STATE.md)
       - Change 07-01-02 Status from `pending` to `green`
       - Change 07-02-01 Status from `pending` to `green` (plan 02 completed per summary)
       - Change 07-02-02 Status from `pending` to `green`
    c. In the Wave 0 Requirements checklist:
       - Check off first item: `[x] tests/hydrodynamics/diffraction/test_module_boundary.py`
       - Check off second item: `[x] tests/hydrodynamics/diffraction/conftest.py`
       - Check off third item: `[x] scripts/remote/verify-licensed-win-1.sh` — note: replaced by queue architecture (07-02)
  </action>
  <verify>
    <automated>grep -c "\[H1\]" .planning/ROADMAP.md && grep "6 phases" .planning/MILESTONES.md | head -1 && grep -c "Closed" digitalmodel/ROADMAP.md && grep "wave_0_complete: true" .planning/phases/07-solver-verification-gate/07-VALIDATION.md | head -1</automated>
  </verify>
  <done>ROADMAP.md has horizon tags and WRK scores, MILESTONES.md phase count corrected to 6, digitalmodel tech debt item 7 closed, VALIDATION.md updated with completed items and wave_0_complete: true</done>
</task>

<task type="auto">
  <name>Task 3: Create solver-queue.md architecture reference document</name>
  <files>
    docs/architecture/solver-queue.md
  </files>
  <read_first>
    .planning/phases/07-solver-verification-gate/07-02-PLAN.md
    .planning/phases/07-solver-verification-gate/07-02-SUMMARY.md
    queue/job-schema.yaml
    scripts/solver/submit-job.sh
    scripts/solver/process-queue.py
  </read_first>
  <action>
    Create `docs/architecture/solver-queue.md` (new file) documenting the git-based pull queue pattern as a reusable architecture reference. Structure:

    ```markdown
    # Solver Queue — Git-Based Pull Queue Architecture

    > Reusable pattern: asynchronous job dispatch across firewall-separated machines using git as the transport layer.

    ## Problem

    Corporate firewalls block inbound connections to licensed solver machines (e.g., OrcaFlex on Windows). Traditional SSH-based push models fail. A pull-based architecture using git as the message bus satisfies the constraint: only outbound connections from the solver machine are needed.

    ## Architecture

    [Describe the flow: dev-primary commits YAML job to queue/pending/, pushes to GitHub. Licensed-win-1 polls via git pull every 30 minutes (Task Scheduler), processes pending jobs with OrcFxAPI, moves results to queue/completed/ or queue/failed/, pushes back.]

    ### Data Flow

    ```
    dev-primary                    GitHub                    licensed-win-1
    ──────────                    ──────                    ──────────────
    submit-job.sh ──push──>  queue/pending/job.yaml
                                                     <──pull── Task Scheduler (30 min)
                                                              process-queue.py
                                                              OrcFxAPI execution
                             queue/completed/job.yaml <──push── results + logs
    poll for results <──pull──
    ```

    ### Components

    | Component | Location | Purpose |
    |-----------|----------|---------|
    | `scripts/solver/submit-job.sh` | dev-primary | Creates job YAML, validates, commits to queue/pending/, pushes |
    | `scripts/solver/process-queue.py` | licensed-win-1 | Polls pending/, runs solver, moves to completed/ or failed/ |
    | `scripts/solver/setup-scheduler.ps1` | licensed-win-1 | One-time Task Scheduler setup for 30-min polling |
    | `queue/job-schema.yaml` | repo root | Documents the YAML job format |

    ### Job Lifecycle

    pending/ --> [processing] --> completed/ (success) or failed/ (error)

    ### Key Design Decisions

    1. Git as transport (not SSH, not HTTP API) — zero infrastructure beyond existing repo
    2. Pull-based polling (not push) — satisfies corporate firewall constraint
    3. YAML job files (not database) — human-readable, git-diffable, auditable
    4. PyYAML optional with fallback parser — minimal dependencies on solver machine
    5. Python 3.9+ compatibility — matches OrcFxAPI support range

    ## Reuse Pattern

    This pattern applies to any scenario where:
    - A compute resource is behind a firewall that blocks inbound connections
    - Job throughput is low enough for 30-minute polling latency
    - Git is available on both sides
    - Jobs are describable as small YAML files

    Potential future applications: CFD job dispatch to dev-secondary, FEA batch runs, any licensed-tool automation.

    ## References

    - Phase 7 Plan 02: `.planning/phases/07-solver-verification-gate/07-02-PLAN.md`
    - Phase 7 Summary: `.planning/phases/07-solver-verification-gate/07-02-SUMMARY.md`
    - Memory: `project_solver_queue_architecture.md`
    ```

    Adapt the above template with accurate details from the plan and summary files. Keep it concise — under 80 lines.
  </action>
  <verify>
    <automated>test -f docs/architecture/solver-queue.md && wc -l docs/architecture/solver-queue.md</automated>
  </verify>
  <done>docs/architecture/solver-queue.md created documenting the git-based pull queue as a reusable architecture pattern</done>
</task>

</tasks>
