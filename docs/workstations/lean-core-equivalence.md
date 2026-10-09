# Lean source contract and Windows to Linux1 continuity

`config/workstations/lean-core-profile.yaml` is a reviewed-source recipe candidate,
not a new machine registry or proof of fleet deployment. Membership comes from
`machines.dev-primary.tier1_baseline.required` in the existing registry. Every
required repository must have exactly one recipe; missing/extra recipes fail.
The snapshot freezes the six tested Windows-pilot commits, selected directories,
hub policy/native-skill digests and the approved sanitized DM working file.
Digests normalize CRLF to LF. Do not equalize whole skill-tree counts or overwrite
live policy, private settings, credentials or machine roles.

## Read-only acceptance command

Use the existing checker and a locally available interpreter with PyYAML:

```sh
python -B scripts/workstations/check-tier1-repo-baseline.py \
  --registry config/workstations/registry.yaml --machine ace-win-2 \
  --repo-root /absolute/isolated/core --footprint-only \
  --core-profile config/workstations/lean-core-profile.yaml \
  --footprint-environment /absolute/existing/environment
```

On Linux1 choose `--machine dev-primary` and explicit existing DM and WED
environment paths. Repeat `--footprint-environment` for every used environment.
On Windows use the existing hub Python interpreter; do not use project sync to
run the checker. Footprint selection uses the contract's registry authority even
when the target machine has no legacy `tier1_baseline.required` entry. The report
records both membership and target machine IDs; it validates the target hostname
or registered alias and OS without changing identity or registry facts.

All six selected roots, Git stores and explicit environments are measured.
Allocation/read/redirect failures keep budget evidence indeterminate. Source
parity checks HEAD, direct-origin identity, every named required file's reviewed
digest and tracked working changes. It rejects staged/index changes and checks
HEAD/status again after inspection. These are sequential local observations,
not an atomic snapshot; stop concurrent writes while collecting acceptance.
Missing members cannot silently become a smaller successful
set. Exit zero means this local source/identity/budget gate passed; it does **not**
qualify an agent, full engine, owner dataset, license, GPU or independent backup.
Run Git inspection under the existing checkout owner's account. An isolated
tool account can encounter Git's ownership guard; treat this as unavailable
inspection. Do not add global trust exceptions or change filesystem permissions.
`agent_runtime_qualified` remains false. Ignored/task files are accounted by the
footprint but their semantic content is outside the pinned source contract.

## Reusable clone recipe

The existing helper accepts an explicit recipe and pin:

```sh
python -B scripts/workstations/clone_profile.py assetutilities \
  --profile lean --destination /absolute/new-core/assetutilities \
  --registry config/workstations/registry.yaml \
  --repos-config /absolute/reviewed-task-origins.conf \
  --baseline-profile config/workstations/lean-core-profile.yaml --dry-run
```

The parent must already exist and each destination must be absent. Dry-run does
not call Git or create destinations. Removing `--dry-run` requires the applicable
session authorization and measured download/disk guards; the helper itself is
not a byte cap. Filtering and selected trees are checked by the existing helper.
If advertised main has moved from the tested pin, it stops before clone. A
clone/preflight race stops before checkout and retains the new destination.
Refresh the reviewed snapshot only after reviewing new source and validation;
do not silently substitute latest main or fetch arbitrary historical objects.

Digitalmodel is `sanitized_existing_only`: profile-based cold clone planning is
blocked because the frozen public-main Git snapshot contains a known credential
blob. Its reviewed current working file must match the approved digest. This
does not declare its existing Git store safe to transfer. Owner revocation alone
does not authorize copying the original value. Reuse existing recoverable work
and resolve a separately reviewed sanitized publication/history strategy before
cold deployment. No Git object rewriting or deleting is included here.

Shared `config/repos.conf` remains unchanged. The caller supplies the exact
reviewed six-origin task config, or the existing bounded local-origin fallback
for absent entries; never override a conflicting legacy mapping implicitly.
Private wiki and personal-sensitive repo membership grants no publication or
raw-evidence ingestion rights. Named hub documentation fixtures are bounded
inputs: the tested pilot recovered exact `docs/plans/README.md` and
`docs/reports/ace-linux-1-tier1-checkout-normalization.html` Git blobs from an
existing owning store. Do not select entire plan/report directories to obtain
two files; retain their exact receipts if sparse profiles are reapplied.

## Existing authorities and machine adapters

Reuse `harness-roles.yaml`, `harness-state-classes.yaml`, the Foundation profile,
`provider_harness_parity.py`, equality collectors and `build-equality-matrix.py`.
This checker does not publish reports, invoke providers, mutate settings or
replace that matrix. Keep its source/footprint receipt beside the existing
provider/behavior evidence. Source equality is one dimension, never a substitute
for a launched-agent or capability test.

| Layer | Common contract | Machine adapter / evidence |
|---|---|---|
| Source | Same reviewed six pins, selected source, policy and required digests | Root paths and actual registry identity; preserve unique branches and dirty work |
| Agent | Same selected instructions, Foundation ownership, native skill/support assets and named behavior | Existing executable/login PATH, supported version, actual selector and behavior evidence; no credentials copied |
| Python | Same named offline baseline behavior | Explicit per-task interpreter and environment; patch versions may differ when tested |
| Data | Existing wiki owner catalogs and repository ownership contracts | Exact owner-relative bounded input, version/digest/units/access and freshness; readable directory is insufficient |
| Capability | Same routing rules and truthful availability | Existing control-plane, simulation, GPU and licensed-dispatch roles; actual solver/license/GPU gates remain distinct |
| Continuity | Reviewed task handoff and reproducible named checks | Preserve unique commits, all worktrees/stashes and dirty/untracked work before any reconciliation; independent screened recovery receipts |

Native Codex sessions default to the hub's existing `.agents/skills`. The five
child `.codex/skills` locators remain historical aliases; Windows flattening is
not repaired by OS policy changes or replicated whole trees. Direct child-root
agent sessions need a reviewed existing Foundation materialization/adapter and
actual loader confirmation. The task-owned Python launcher is only a proposed
entry point; its pending parent activation decision is not supplied by this
broader equivalence contract.

## Deployable next lane: Windows to Linux1

1. Review this unpublished patch/profile and the exact Windows source snapshot.
   Keep the delivered Library HTML untouched; this contract is a separate repo
   deliverable. Linux1 audit reports hub ahead 1/behind 238, tracked dirty work,
   12 hub stashes and multiple worktrees against cached upstream. These counts
   are not fresh remote evidence or permission to reset/pull.
2. Collect the read-only core receipt on Linux1's actual owning root and existing
   DM/WED interpreters. Expect revision/policy differences; do not auto-repair them.
   `/mnt/local-analysis` and `~/ws` resolve to `/mnt/ace/ws`: that shared view is
   not an independent fleet copy or recovery backup.
3. Select one isolated, explicitly named Linux task lane. Dry-run safe repo
   recipes against new destinations; hold DM cold clone as above. Preserve
   unique work separately. Ordinary Git histories may use authorized `/mnt/ace`
   backup only after known-credential exclusions and independent restore checks;
   age alone does not justify abandoning unique commits or dirty work.
4. Reuse Linux1's observed Python 3.11.14 DM environment (NumPy 1.26.4 / PyArrow
   14.0.1) and separate WED environment (NumPy 2.3.3 / PyArrow 19.0.1), subject to
   exact required-package and import/smoke checks. No install is needed merely
   to compare metadata. Windows DM NumPy 2.4.6 violates DM's `<2` constraint;
   WED core needs `>=2.2.6`. No single compliant shared environment exists.
5. After the separate activation decision, confirm actual native selected skills
   and reopen one screened task on Windows and Linux1 with the same exact pins,
   source bindings and named fixtures. Reproduce only the small baseline below.
   Use existing provider readiness evidence to qualify behavior/version/access;
   The later access-worker adapter resolves Linux1 Codex 0.160.0, Claude 2.1.288
   and Gemini 0.62.0 with per-invocation PATH entries; these matching versions
   are not automatic behavior parity. Hermes was discovered separately.

The reviewed access handoff supplies Linux1 CLI directories
`/home/vamsee/.local/bin`, `/home/vamsee/.npm-global/bin`, `/usr/local/bin`,
`/snap/bin`, `/usr/bin`. Apply them only to the child invocation, retaining the
existing account and strict SSH route; no persistent profile edit is required.
The worker's task-local `fleet-adapters.json` and `preflight.py` are observations,
not another machine/data registry. Owner catalogs and ACE/DDE metadata were
readable, while Linux1 BSEE uses `data/bsee` and Windows/Linux2 use
`data/modules/bsee`. Resolve a task's exact owner input before use; do not copy
whole data trees to normalize these paths. Licensed Windows remains unreachable
on the tested route and Muse/Hatch still lacks a verified identity binding.

The supported source baseline is hub checker tests, AU math helpers, DM diagram
tags/geometry, WED units/risk classifiers, AH default/mocked cache TTL and wiki
filesystem coordination. Full scientific engines, live finance, Arrow/Parquet,
DM fatigue/materials/CP/OrcaFlex fixtures, WED BSEE/FDAS data/domain packages and
benchmark CSV remain separately bounded tasks. Existing paths are not data
completeness or usage-rights attestations.

The separate runtime-worker evidence now confirms Linux1 DM and WED canonical
dependency checks and tiny offline Arrow round-trips in their separate existing
environments. Windows DM still fails Arrow and has eight missing distributions
and three dependency mismatches. Keep these observations beside source parity;
do not install packages or declare full task readiness from the source gate.
The runtime worker owns the bounded Windows wheel/install plan and AU pin
resolution. Its canonical probe embeds a dependency snapshot; review its
snapshot against the selected source pin before treating it as that pin's
requirements. The source gate deliberately does not import that duplicated
dependency contract into the machine registry.

Linux2's unique hub/DM history and failed NVIDIA driver, GPU-claw's missing
WED/AH, Mac's missing WED/scientific runtime and unverified agent PATH, unavailable
licensed-Windows route and unverified Muse identity remain subsequent enrollment
gates. Do not repair drivers, networking, credentials or OS policies under this
source contract. Do not label role-specific divergence as common-core failure
or call source parity fleet equivalence.
