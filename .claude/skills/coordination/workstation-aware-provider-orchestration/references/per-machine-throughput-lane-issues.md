# Per-machine throughput lane issue pattern

Use this reference when workstation planning starts drifting into repo placement or housekeeping. The durable lesson is to make each machine issue a throughput lane activation issue, not a recurring debate about canonical infrastructure.

## Trigger

The user asks to create or update GitHub issues for each machine and decide what work/repo footprint belongs on each machine, especially in a multi-provider setup.

## Correct framing

Treat repo placement, memory layout, skills, artifact paths, output formats, and cross-repo file structure as canonical infrastructure unless the user explicitly asks for a narrow enforcement fix. The per-machine issue should answer:

1. Which provider(s) will run on this machine?
2. What workload class does this machine own?
3. What readiness check blocks dispatch?
4. What already-approved batch should route here first?
5. What proof shows useful throughput happened?

## Issue title pattern

```text
throughput(workstations): activate <machine> provider/machine lane
```

Examples:

```text
throughput(workstations): activate ace-linux-1 provider/machine lane
throughput(workstations): activate ace-linux-2 provider/machine lane
throughput(workstations): activate licensed-win-1 provider/machine lane
throughput(workstations): activate licensed-win-2 provider/machine lane
```

## Body skeleton

```markdown
## Purpose
Activate `<machine>` as a throughput lane in the multi-machine / multi-provider execution system.

This issue is not a repo-placement or file-structure debate. Repo placement, memory shape, skill layout, artifact format, and cross-repo structure are canonical infrastructure. The decision here is useful execution throughput.

## Starting role
- Machine role: `<control-plane | Linux worker | licensed Windows worker | overflow worker>`
- Provider fit: `<Claude/Codex/Gemini/...>`
- Workload class: `<orchestration | bounded implementation | tests/fixes | recon | licensed solver work>`

## Readiness checks
- Host reachability:
- GitHub auth / mutation boundary:
- Provider CLI/auth:
- Repo/worktree state:
- Tool/software readiness:

## First approved batch candidate
- `<issue URL>` — reason:

## Proof of throughput
- Dispatch ledger row:
- Validation command/log:
- Issue comment/evidence artifact:
- Stop/fallback condition:
```

## Label pattern

Use deterministic routing labels:

- `cat:ai-orchestration`
- `cat:operations`
- `domain:ai-orchestration`
- `domain:workstations`
- `domain:agent-cost-tracking`
- `machine:<host>`
- lifecycle label such as `status:needs-plan`, `status:plan-review`, or `status:plan-approved`

## Close or avoid broad governance side-quests

If a newly created issue becomes broad canonical-infra housekeeping and the user’s goal is throughput, close it as not planned or narrow it to an enforcement defect. Do not keep it active just because it is related to machines.

## Next logical step after issue creation

After per-machine lane issues exist, do not create another broad governance issue. Instead:

1. Refresh provider telemetry / routing scorecard.
2. Find already-approved work with provider/machine fit.
3. Start with the control-plane lane (`ace-linux-1` by default).
4. Produce or update a dispatch ledger mapping issue → provider → machine → validation evidence → stop condition.
5. Route overflow to worker lanes only after readiness is verified.
