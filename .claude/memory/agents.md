# Agent Workflow Facts

> Git-tracked. Applies to all AI agents working in this repo on any machine.
> Refreshed by `scripts/memory/bridge-hermes-claude.sh` — edit the template,
> not the generated file.

<!-- BRIDGE:START — do not edit below this line, managed by bridge script -->

## Synced from Hermes Memory (2026-07-09)

### Environment Facts

- ace-linux-2 display: NVIDIA T400 (PCI 81:00.0) uses nvidia-580-open driver. Two failure modes: (1) kernel upgrade without matching linux-modules-nvidia-580-open-$KERN package → 640x480 framebuffer fallback (most common after reboot), (2) KVM EDID drop. Fix script: scripts/operations/system/fix-kvm-display-ace-linux-2.sh. Skill: ace-linux-2-display-troubleshooting.
- Hermes CLI on this machine uses ~/.hermes/config.yaml with many populated skills.external_dirs entries pointing at /mnt/workspace-hub and multiple repo .claude/skills directories; do not assume repo skills are unavailable locally without checking the live config.
- workspace-hub local repos aceengineer-admin, achantas-data, investments, and sabithaandkrishnaestates use SSH GitHub remotes because gh HTTPS token is invalid while SSH auth for git@github.com works.
- software-ops channel: Deckhand-as-software primary, digressions allowed if flagged multidisciplinary and kept threaded. Don’t infer standalone messages belong to prior threads unless obvious; ask if needed. First etiquette violation gets brief advisory; later repeats usually ignored.
- baez Telegram: Deckhand stays within transportation/engineering/economics unless explicitly asked for multi-domain work; confirm before other domains.
- FDAS Telegram deliverables: save under /mnt/local-analysis/llm-wiki-fdas/deckhand-deliverables/YYYY/YYYY-MM-DD/<topic-slug>/ with manifest.yaml, report.html, inputs.yaml, results.yaml side by side; reply with report path plainly on its own line. Report sections: executive summary, objective, inputs & assumptions, methodology, results, conclusions, limitations, references, provenance. Pipeline wall-thickness screens require manifest.yaml design_questions keys exactly buckle_arrestors, alternate_branch, design_basis_caveat; mirror basis in results.yaml/report.html.

### User Profile

- User prefers GitHub issue work to use parallel agents where possible, especially Claude agent teams/delegated subagents for deeper analysis/planning.
- User prefers approved GitHub issue work dispatched via file-based Claude prompt packs with loop/status monitoring and built-in adversarial implementation review.
- When using Claude CLI subprocesses, the user expects the proper `claude -p` invocation format rather than `--print`.
- User wants core engineering work learnings to be made portable across the repo ecosystem and usable on other machines, especially for workflows like OpenFOAM development and Blender animations.
- User may review and approve planning work directly on GitHub issue web pages by applying the `status:plan-approved` label.
- User expects learning passes to actively update class-level skills when there is real signal, preferring loaded/existing umbrella skills plus concise references over narrow one-session skills.
- User prefers interactive local review/rating web apps to include a simple Submit button rather than requiring manual export/download/upload workflows.
- User expects operational CTAs to be explicit and directly executable, including the exact command/message to send and what to do next.


<!-- BRIDGE:END -->

---

## User

Vamsee Achanta — Professional Engineer (P.E.), 23 years experience.
Runs ACE Engineer consulting (aceengineer.com).
Target: $120K/yr retainers, 3-5 clients = $360-600K ARR.
GTM: offshore engineering firms with 10-50 engineers.
Core expertise: OrcaFlex, mooring/riser, FEA, cathodic protection, API 579, Python automation.

## AI Subscriptions

| Agent | Cost | Notes |
|-------|------|-------|
| Claude Max | $200/mo max | Primary planning/orchestration subscription; Claude Code CLI |
| Gemini Google AI Pro | $20/mo | Research/recon and cross-review |
| Codex / OpenAI | Verify authenticated paid account(s) before load planning | Do not assume parallel paid seats without machine/auth evidence |

Context parity = compute parity. Zero waste everywhere.

## Workflow Rules

- **ace-linux-1 control surface**: keep user approvals, launch decisions, GitHub mutations, and cross-lane reconciliation on `ace-linux-1` unless explicit failover is chosen.
- **Overnight batch**: 3 self-contained prompts, one per terminal, zero git contention.
  Always include a git contention avoidance map.
- **Long-running lanes**: prefer named `tmux` sessions or Hermes-tracked background processes with logs under `logs/night-runs/` and prompt packs under `docs/plans/overnight-prompts/`.
- **Adversarial review**: BOTH stages — plan review AND code/artifact review.
  Minimum: Claude + Codex + Gemini all review.
- **Context parity**: Corrections made in one agent must propagate to all others.
- **GTM issue routing**: with GTM messages in view, convert each signal by updating an existing GitHub issue, reopening an existing issue, or opening a new one.
- **Code-readiness loop**: strengthen code with methodologies, standards, tests, and review artifacts before claiming delivery readiness.
- **Legal promotion gate**: before promoting raw-data-derived material into public `llm-wiki` pages or other artifacts, preserve engineering evidence boundaries and run legal sanity review/scan.
- **Autonomous gate evolution**: hard gates remain in force until metrics prove agent rigor is consistently safe; over time, shift routine plan/review/execution/verification cycles from user-managed approval to evidence-threshold approval so the owner focuses on ideas, GTM throughput, and customer/prospect artifacts.
- **Compute lane assignment (plan-time)**: every issue/plan assigns an AI provider lane at planning time, recorded as exactly one `lane:codex` or `lane:claude` label on the GitHub issue (mirrors the `domain:` label rule). Heavy compute — engineering calcs, long-running analysis, large data crunching, bulk build/refactor/migration sweeps — goes `lane:codex` (run via `codex exec`); orchestration, review, small edits, planning, and PR plumbing go `lane:claude`. Quota gate: if codex weekly usage available drops below 10% (statusline shows live codex quota), suspend the codex lane for the rest of that week and run heavy work via Claude. Enforced at dispatch (scripts/dispatch/route.py, #3030): lane:codex cards demote to the default provider when a current-window quota snapshot shows <10% remaining; unknown or cross-reset-stale quota fails open.
- **No local task IDs**: Use GitHub issues directly (`gh issue list`).
- **Issue comments**: Always post a summary comment on every implemented GitHub issue.
- **Parallel work check**: Scan for in-flight sessions before starting GSD work.

## GSD Workflow

GSD is the sole workflow system since 2026-03-25.
- Plans live in `.planning/` within each repo
- Long-duration plans live in `docs/plans/`
- Use `/gsd:*` commands for task management

## Skill System (Hermes)

Hermes maintains 691+ skills at `~/.hermes/skills/` on ace-linux-1.
On non-Hermes machines, consult `.claude/skills/` in this repo for equivalent procedures.


### Harness Throughput Rule

Provider credits are not the current bottleneck. The harness must prioritize preparing plans, running adversarial reviews, executing approved work, and reconciling results so weekly provider limits do not reset unused. Latest user-provided headroom showed Claude weekly capacity still substantial (All models 38% used; Sonnet 7% used) and Codex weekly capacity mostly unused (89% overall remaining; GPT-5.3-Codex-Spark 100% remaining). Preserve enough emergency/approval capacity, but otherwise keep useful lanes fed; the owner can tolerate up to ~2 days of depleted credits near reset if durable work was produced.

### GTM → Knowledge → Code Readiness

GTM messages should update/reopen/create GitHub issues. Raw data and public data sources may feed `llm-wiki` with provenance, data, codes/standards references, and methodology, but public-facing pages/artifacts require legal sanity checks, sanitization, and explicit evidence boundaries. Code readiness comes from converting those methods into tests, fixtures, acceptance criteria, and bounded implementation plans.

### Weekly GTM Target Rule

Establish weekly GTM targets interactively with the owner, then turn them into bounded GitHub issues and agent-executable packets. Current/next seed: week of April 1 should produce vessel capability charts plus a strong brochure sent to all researched vessel contractors; agents should handle contractor research, list hygiene, capability-chart/brochure preparation, evidence-backed claims, and outbound/send tracking. This week should also include a review of the owner's full work pattern to suggest productivity hacks: audit recent sessions, GitHub throughput, GTM artifacts, handoffs, repeated friction points, and tool/provider bottlenecks, then propose changes that reduce owner orchestration time and increase GTM/artifact flow.

## ACE Engineer GTM Context

- `aceengineer-strategy/` — private nested repo with full GTM strategy
- 20+ prospects identified; ICP: offshore firms 10-50 engineers
- Demo reports: `digitalmodel/examples/demos/gtm/` (5 demos, `report_template.py`)
- Job market scanner: `scripts/gtm/job-market-scanner.py` (runs Monday cron)
- GTM control rule: continuous AI work should convert external signals, repo engineering work, and approved issue outputs into client-ready material, but keep engineering evidence boundaries explicit.
- Public-promotion rule: raw data may feed internal code/wiki preparation, but public `llm-wiki` and artifacts must carry provenance plus data/code/standards/methodology separation and pass legal sanity checks.
- Control-surface rule: `ace-linux-1` remains the approval and reconciliation surface while `ace-linux-1` / `ace-linux-2` long-running lanes keep planning, execution, review, and GTM packaging moving in the background.
