# Machines

Generic layer of the machines map. The data file is `machines.yaml` beside this page. The per-host fleet
table, the readings behind it and every deviation are held in the private detail map: fleet-ops
`docs/knowledge-maps/machines.yaml` (private repository).

Verified 2026-11-27 15:45Z from read-only probes of seven machines. Governing rule:
[`workstation-hygiene.md`](../../.claude/rules/workstation-hygiene.md), with
[`licensed-solver-dispatch.md`](../../.claude/rules/licensed-solver-dispatch.md),
[`soul-deployment-drift.md`](../../.claude/rules/soul-deployment-drift.md) and
[`scheduler-mutation-safety.md`](../../.claude/rules/scheduler-mutation-safety.md).

## Machine classes

| Class | Purpose | AI lanes | Lane cap | Licensed solvers | Count |
|---|---|---|---|---|---|
| owner-desk | Owner's Windows desk: Intake desk, review pages, owner-held work | Claude, Codex | 2 | May hold an Orcina install; scheduled-task path only | 1 |
| solver-host | Windows server for the licensed solvers; Claude desk pass and train workers | Claude | per desk files | Orcina lane and ANSYS lane | 1 |
| linux-lane-host | Codex and Claude lanes, heavy builds, CI runners; one holds the data store | Codex, Claude | 6 and 4; data-disk cap 2 | None (OpenFOAM) | 2 |
| leased-compute | Leased hosts shared with other tenants: Codex lanes, GPU and CFD | Codex on one | one CFD run, 6 cores max | None (OpenFOAM) | 2 |
| portable | Owner's laptop: one Codex job, hand-run reviews; may sleep | Claude, Codex | 1 | None | 1 |
| planned-or-inactive | Registry or routing entries not reached from the probe host | none | 0 | None | 4 |

Machines are reached by MagicDNS name with key authentication. Orcina work never runs over direct SSH; it
goes through the scheduled-task dispatch path.

## Licence lanes

| Lane | Concurrent dispatch slots | Note |
|---|---|---|
| Orcina (OrcaFlex, OrcaWave) | 1 | One Flex seat licenses a session fleet-wide; a job may fan out across cores inside it |
| ANSYS (AQWA) | 2 | Independent of the Orcina lane; both lanes run at once |

## Required runtimes

Policy: one version of each tool on every machine that carries it. Until a ruling pins versions, the fleet
baseline is the newest version already deployed. A missing tool, or one below its minimum, on a class that requires it
fails R06; a version behind the baseline is recorded as an equality deviation.

| Tool | Classes | Minimum or note |
|---|---|---|
| git, gh, uv | all | one version fleet-wide; Python runs through `uv run` |
| python | all | 3.10; not the Windows Store alias; macOS system Python does not qualify |
| node | all | 22 (active LTS or newer) |
| claude, codex | every class that runs AI lanes | one version fleet-wide |
| agy | owner-desk, solver-host, linux-lane-host, portable | Agy plain-English and third-provider reviews; not required for leased-compute |
| pwsh | owner-desk, solver-host | 7 |
| openfoam | linux-lane-host, leased-compute | packaged `openfoamNNNN` environments only |

## Readiness checklist

Every row is checked on every machine. A reading the check cannot take counts as missing, never as passed.
R01 to R12 come from the consistency-run design (fleet-ops PR 776, merged 27 Nov) and the work-architecture cadence;
R13 to R16 come from the hygiene, dispatch and data rules.

| Row | Item | Passes when |
|---|---|---|
| R01 | Identity | Host name matches its registry label and host card; the work root `W` resolves |
| R02 | Reachability | `ssh` by MagicDNS name in batch mode succeeds from the desk hosts within 10 s |
| R03 | Layout | `W` holds only registered repositories, `_wt`, `_pm`, `_backups`, `_archive`, `.claude`; no clones in home folders or drive roots |
| R04 | Structure guides | Every folder in `W` and in each repository, to the guide depth, has a stated purpose |
| R05 | Canonical clones | One clone per repository, on `main`, clean, fast-forwardable, post-reset history |
| R06 | Runtimes | Every required tool for the class is present at or above its minimum; spread against the fleet baseline is an equality deviation, not an R06 fail |
| R07 | Provider contracts | Deployed Claude, Codex, Gemini, Agy and Hermes contract files match `origin/main` |
| R08 | Permissions and settings | Claude permissions and settings equal the fleet-ops set |
| R09 | Consistency run | The 6-hourly bootstrap is scheduled; `W/_pm/consistency/latest.json` is under 6 h old and names its commit |
| R10 | Machine manager | Linux and macOS hosts run the watch and hourly manager; the installed act list equals fleet-ops |
| R11 | Schedules registered | Every scheduled entry of ours is in a schedule register; none failing or orphaned |
| R12 | Work records | Every worktree has a work record; merged work is closed on content evidence |
| R13 | Disk | Every local data volume has at least 10 % free, and the host floor in ECOSYSTEM.md is met |
| R14 | Data placement | Bulk solver output sits on the data store by manifest, with a verified second copy |
| R15 | Licensed dispatch | Licensed solvers start only through the scheduled-task path, within lane slots, after QA pre-flight |
| R16 | Sign-ins | Sign-ins sit in the machine's own credential store; git identity is the noreply address |

## Refresh

Every 6 h on every machine once the consistency run is installed; by hand until then. Probe commands
(machine-neutral) are listed under `refresh.commands` in the data file. Scripts sent from Windows to a Linux
host are saved with LF line endings. Windows paths are never passed to a bash tool.

## Status

Seven machines were probed and four listed entries were not reached. The private map records 41
deviations (27 at the first build, 14 added by the 28 Nov per-machine review). No machine passes R09, because the consistency run is not yet installed, and no machine has a
readiness reading. The other deviations are runtime version spread, disk pressure on two data volumes,
failing or orphaned scheduled entries, and gaps between the register files.

## Open questions

- Should a ruling pin one version per tool in a committed baseline file, or does "newest deployed" stand?
- `config/scheduled-tasks/schedule-tasks.yaml` covers only part of what runs. Which repository owns the
  one register of live schedules?
- R09 depends on the per-machine installation of the fleet-ops PR 776 bootstrap (merged 27 Nov), each after a #577 log.
