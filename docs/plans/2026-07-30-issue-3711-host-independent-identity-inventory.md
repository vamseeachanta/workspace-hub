# Plan for #3711: Host-Independent Cron Identity Inventory

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3711
> **Client:** N/A
> **Lane:** lane:claude
> **Blocks:** [#3709](https://github.com/vamseeachanta/workspace-hub/issues/3709) commits 2-4
> (declared a hard blocking prerequisite by that plan's FIX 2)
> **Review artifacts:** `scripts/review/results/2026-07-30-plan-3711-verification-log.md` (author
> verification log — a measurement record, not a review); independent adversarial review REQUIRED
> before any approval
> **Verification prototype (committed):** `scripts/review/results/2026-07-30-plan-3711-prototype/`

---

## Tense convention

Everything this plan **proposes** is written in the future tense. Everything in a `Today's status`
or `Evidence` position is a **measurement**, written as a measurement, with the command and the host
that produced it. `[mac]` = `macbook-portable`, Darwin 25.5.0, `/Users/krishna/Developer/ws/workspace-hub`.
`[ace1]` = `ace-linux-1` / `dev-primary`, `/mnt/local-analysis/workspace-hub`. **Both hosts were at
`3fe934da9` (`origin/main`) on 2026-07-30**, and every row below was run on **both**.

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_render.py:84-87` — `workspace_hub_path()`. Line 87 is
  `return Path(override).expanduser().resolve() if override else REPO_ROOT`. **This is the whole
  defect.** Two independent host dependencies live in that one expression: `.resolve()` (walks the
  running host's filesystem) and `.expanduser()` (substitutes the running host's `$HOME`).
- `scripts/cron/build-cron-identity-inventory.py:96-100` — `_build_machine()` reads each machine's
  registry `workspace_root` and feeds it to `build_ownership_context(..., workspace_hub=...)`, which
  reaches `workspace_hub_path` via `cron_render.build_context` (`cron_render.py:98`). The declared
  root of **another machine** is therefore resolved against **this** machine's filesystem.
- `scripts/cron/cron_identity.py:186-224` — `build_ownership_context`; `:114-142` —
  `validate_inventory_inputs`, the existing fail-closed structural validator. It checks catalog and
  registry shape. Measured: it contains exactly **1** mention of `workspace_root`
  (`grep -c workspace_root scripts/cron/cron_identity.py` → `1`, and that one is the fallback lookup
  at `:193`, not a validation). **There is no declared-root validation anywhere.**
- `scripts/enforcement/scheduler_mutation_delegation.py:112-123` — `_validate_inventory_digest`.
  Hashes the git-index bytes of eight **source** files and compares to `inventory["input_digest"]`.
  It never looks at `inventory["identities"]`.
- `scripts/enforcement/check-scheduler-mutation-surfaces.py:88-99` — `read_index_records`, the
  git-index blob reader the checker already uses. `:328` calls it. The contents check this plan
  proposes will consume exactly this `records` dict.
- `config/workstations/registry.yaml` — 7 machines. Measured
  (`uv run --with pyyaml python -c '…'`):

  | machine_id | os | workspace_root |
  |---|---|---|
  | `dev-primary` | linux | `/mnt/local-analysis/workspace-hub` |
  | `dev-secondary` | linux | `/mnt/local-analysis/workspace-hub` |
  | `gpu-claw` | linux | `/home/undi/ws/workspace-hub` |
  | `gali-linux-compute-1` | linux | `None` |
  | `ace-win-1` / `ace-win-2` | windows | `D:\workspace-hub` |
  | `macbook-portable` | macos | `/Users/krishna/Developer/ws/workspace-hub` |

  Only the four `os: linux` rows reach the inventory (`build-cron-identity-inventory.py:70`).
  `gali-linux-compute-1` has no `workspace_root` and contributes 0 rows.
- `config/scheduled-tasks/mutation-surfaces.yaml:273` —
  `source_digest: c56754bf219306ffd78777f465c4257a5481e09929e98dad99abba30cec9dffc`, cross-checked
  against `inventory["input_digest"]` at `scheduler_mutation_delegation.py:97`.

### Documents consulted

- `gh issue view 3711` — the required scope: resolve without touching the filesystem, **or** fail
  closed; add a regression test rendering `gpu-claw`'s `/home/undi/ws` root from a macOS-like
  environment; survey the other `scripts/cron/` generators.
- `gh issue view 3709` — the consumer. `plan_cutover` can classify a line as owned and delete it;
  identity data is an input to that decision.
- `docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md` (branch
  `plan/3709-managed-block-classification-v3`), **FIX 2** — records the same root cause at
  `cron_render.py:87`, chooses "sequence #3711 first" over "guard around it", and records the
  residue: *"`_validate_inventory_digest` still validates the inventory's inputs, not its contents.
  A hand-edited `identities` array carrying a correct `input_digest` still passes the checker … will
  be filed as a follow-on."* **This plan adopts that follow-on as its own second half**, because it
  is the only thing that makes #3711's fix enforceable rather than advisory.
- `docs/plans/_template-issue-plan.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` —
  section set, header fields, and the mandatory Step 1.5 reproduction.
- PR #3710, commits `a60e50d80` (wrong claim) → `7ac7ce445` (retraction) — the near-miss.
- **No relevant drive files.** `scripts/data/drive-index-search/search.py` indexes client documents;
  this is a harness-internal defect with no document surface.

### Standards

Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — `Client: N/A`.

### Gaps identified

- No lexical (filesystem-free) normalisation of a declared `workspace_root` exists.
  `grep -rn declared_workspace_root scripts/ tests/` → **0 hits**.
- No validation that a declared `workspace_root` is renderable. `validate_inventory_inputs` has none.
- No pure-document entry point to the builder. `grep -rn build_from_documents scripts/ tests/` →
  **0 hits**; `build()` takes three `Path`s.
- No contents validation in the enforcement checker.
  `grep -rn _validate_inventory_contents scripts/ tests/` → **0 hits**.
- **No host guard of any kind in the builder.**
  `grep -c 'platform\|Darwin\|sys.platform\|uname\|hostname' scripts/cron/build-cron-identity-inventory.py`
  → **0**. Confirms the issue's claim: the only OS-adjacent logic is `row.get("os") == "linux"` at
  line 70, which filters *registry rows*, not the executing host.

---

## Reproduction Evidence

All output below was produced on 2026-07-30 at `3fe934da9` by the committed prototype
`scripts/review/results/2026-07-30-plan-3711-prototype/proto_3711.py`. Full transcripts, including
the isolated-clone poisoning demonstration, are in
`scripts/review/results/2026-07-30-plan-3711-verification-log.md`.

### R1 — the defect, on both hosts

```
$ [ace1] uv run --with pyyaml python proto_3711.py /mnt/local-analysis/workspace-hub
[A] gpu-claw declared:            /home/undi/ws/workspace-hub
[A] gpu-claw today .resolve():    /home/undi/ws/workspace-hub                          faithful=True

$ [mac] uv run --with pyyaml python proto_3711.py /Users/krishna/Developer/ws/workspace-hub
[A] gpu-claw declared:            /home/undi/ws/workspace-hub
[A] gpu-claw today .resolve():    /System/Volumes/Data/home/undi/ws/workspace-hub      faithful=False
[A] dev-primary   today .resolve(): /mnt/local-analysis/workspace-hub                  faithful=True
[A] dev-secondary today .resolve(): /mnt/local-analysis/workspace-hub                  faithful=True
```

**`gpu-claw` is the single poisoned row**, confirming the brief. `/home` is a macOS firmlink;
`/mnt` is not.

### R2 — `--check` disagrees between hosts

```
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ACE1_CHECK_EXIT=0

$ [mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ERROR: stale identity inventory: …/docs/reports/issue-3475-command-identity-inventory.json
MAC_CHECK_EXIT=1
```

### R3 — the committed inventory on `main` is correct; this is a latent defect

```
[ace1] [B] today: generated == committed: True        rows differing: []
[mac]  [B] today: generated == committed: False
       rows differing: [('gpu-claw','equality-report'), ('gpu-claw','equivalence-sentinel'),
                        ('gpu-claw','repository-sync')]
       rows per machine (both hosts): {dev-primary: 56, dev-secondary: 14, gpu-claw: 3}  total 73
```

Exactly 3 of 73 rows differ, all `gpu-claw`, matching the brief's per-machine counts.

### R4 — the nastiest property: a correct digest over wrong rows

```
[mac] [B] today input_digest == committed input_digest : True
[mac] [B] => wrong rows can carry a correct digest      : True
```

The digest is `hashlib.sha256` over eight source-file byte streams and is therefore
**host-independent**; the rows are not.

### R5 — the enforcement checker accepts the poisoned artifact (isolated clone, never pushed)

```
$ [mac] git clone --shared --no-checkout <repo> /tmp/…/clone && git -C … checkout main
clone HEAD: 3fe934da9
$ [mac] cd /tmp/…/clone && uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py
 docs/reports/issue-3475-command-identity-inventory.json | 2 +-
$ [mac] git add docs/reports/issue-3475-command-identity-inventory.json
$ [mac] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
POISONED_CHECKER_EXIT=0                     <-- the checker PASSES a wrong inventory
$ [mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
POISONED_SELFCHECK_EXIT=0                   <-- and --check now passes ON THE MAC too
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py \
           --check --output /tmp/poisoned-inventory.json
ERROR: stale identity inventory: /tmp/poisoned-inventory.json
ACE1_CHECK_POISONED_EXIT=1                  <-- only ace1 disagrees, and nothing runs ace1
```

This is PR #3710's exact failure mode, reproduced end to end. Once a Mac commits the poison, the
Mac's own `--check` goes green permanently and the enforcement gate never objects. **The only thing
that would have caught it is a Linux run that nothing requires.**

### R6 — a second, independent host dependency on the same line: `expanduser()`

A `~`-declared `workspace_root` is silently expanded to the **running user's** home — wrongly on
*both* hosts, since `gpu-claw`'s owner is `undi`:

```
[mac]  [F] declared=~/ws/workspace-hub  ->  /Users/krishna/ws/workspace-hub   faithful=False
[ace1] [F] declared=~/ws/workspace-hub  ->  /home/vamsee/ws/workspace-hub     faithful=False
[both] [F] today: silently host-expanded, no error raised -> True
[both] [F] today, ~user-declared root -> <RuntimeError: Could not determine home directory.>
```

The last line matters: a `~undi/...` root raises `RuntimeError`, which is **not** in
`main()`'s caught tuple (`OSError, TypeError, ValueError, yaml.YAMLError`) nor in `_build_machine`'s
(`KeyError, TypeError, ValueError`), so it escapes as an uncaught traceback. This is why lexical
normalisation **alone** is not sufficient and a declared-root guard is still required.

### R7 — the enforcement checker runs on macOS today

```
$ [mac] git --version                                        -> git version 2.55.0
$ [mac] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
MAC_CHECKER_EXIT=0
$ [ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
CHECKER_EXIT=0
```

**This supersedes the caveat carried in #3709's issue body** ("could not be executed on macOS (local
git lacks `cat-file --batch-command -Z`)"). Local git is now 2.55.0 and the checker exits 0 on both
hosts. It matters here because the guard this plan proposes lives inside that checker: it will
actually run on the host that authors the commit.

---

## Design

### Recommendation: **(c) — lexical normalisation, a fail-closed declared-root guard, and an enforceable contents check**

Three parts, in dependency order. Parts 1 and 2 are the issue's (a) and (b); part 3 is what makes
either of them a control rather than a hope.

**D1 — resolve without touching the filesystem (the issue's option (a)).**
A new `cron_render.declared_workspace_root(value)` will normalise a registry-declared root
**lexically only**:

```python
def declared_workspace_root(value: str | Path) -> PurePosixPath:
    """Normalise a registry-declared workspace_root as declared data.

    Deliberately touches no filesystem: no expanduser(), no resolve(), no stat().
    A declared root belongs to the machine that declared it, not to this host.
    """
    return PurePosixPath(os.path.normpath(str(value)))
```

`workspace_hub_path()` will delegate to it for **any** explicit override (registry value or
`$WORKSPACE_HUB`) and will keep returning `REPO_ROOT` when there is no override, so the running
host's own checkout is unaffected.

Measured effect — the whole point of the change:

```
[mac]  [B] PROPOSED: generated == committed: True      (was False)
[ace1] [B] PROPOSED: generated == committed: True      [B] PROPOSED == today: True
```

**Byte-identical to the Linux-rendered baseline on macOS, and byte-identical to today's output on
Linux.** The identity rows do not move; only the host dependence disappears.

*Does anything downstream depend on symlink resolution?* Measured no. `workspace_hub_path` has
exactly two references in the whole repo (`grep -rn workspace_hub_path scripts/ tests/` →
`cron_render.py:84` definition, `cron_render.py:98` use). `build_context` consumes it as
`hub / FULL_VARIANT_LOG` and `str(hub)` — both are `PurePosixPath`-safe, proven by the byte-identical
regeneration above. No caller performs `.exists()`, `.is_dir()`, or any other concrete-`Path`
operation on the returned value. `cron_render.main()` never passes `workspace_hub`, and
`setup-cron.sh` queries only `--field machine_id|schedule_variant|os` (`setup-cron.sh:42-53`), never
`workspace_hub`, so the shell entry point is untouched.

**D2 — fail closed on a root that still cannot be rendered faithfully (the issue's option (b),
reduced to its irreducible residue).**
Lexical normalisation is faithful for an absolute, already-normal POSIX path and **only** for such a
path. `~/…` (R6) and `a/../b` are not. A new `validate_declared_workspace_roots(registry)` will
return one structural error per offending Linux machine, wired into
`cron_identity.validate_inventory_inputs`, so `build()` raises `ValueError` and `main()` returns 1
**naming the machine**. The guard will also reject the known Darwin firmlink projection
`/System/Volumes/Data/...` on an `os: linux` row; that cheap structural check covers the exact
registry-source poison the independent reviewer demonstrated without turning the validator into a
general machine-truth oracle:

```
[both hosts] [C3] guard on a '~'-declared root:
  [('gpu-claw', '~/ws/workspace-hub', 'workspace_root is not an absolute POSIX path')]
[both hosts] [C3] guard on a non-normal root:
  [('gpu-claw', '/home/undi/../undi/ws/workspace-hub', 'workspace_root is not in normal form')]
[both hosts] [C3] guard on a Darwin-firmlink projection for a Linux row:
  [('gpu-claw', '/System/Volumes/Data/home/undi/ws/workspace-hub',
    'linux workspace_root must not use the macOS firmlink target prefix')]
[both hosts] [C3] unfaithful declared roots in today's registry.yaml: []
```

The guard is a **pure function of `registry.yaml` bytes**. That is the property that makes it
enforceable: the checker can evaluate it from the git index for *every* machine, on *any* host,
without probing anything.

**D3 — a pure document core for the builder.**
`build(catalog_path, registry_path, classes_path)` will be split. A new
`build_from_documents(catalog, registry, classes)` will take **parsed documents** and return
`{"machines", "identities", "unsupported", "collisions"}`; `build()` will become a thin wrapper that
reads the three files, computes `input_digest` from bytes, and merges. No behaviour change — this is
purely the seam D4 needs.

**D4 — the enforcement checker will validate inventory *contents*, not only the input digest.**
`scheduler_mutation_delegation._validate_inventory_contents(inventory, records, errors)` will parse
the three config documents from **git-index bytes** (already in `records`), call
`build_from_documents`, and compare `identities` and `machines` against the committed inventory.
A mismatch appends to `errors`, which is what makes the checker exit non-zero.

Measured with the committed prototype `contents_check.py`:

```
[mac]  clean repo      : regenerated=73 committed=73 contents_match=True    EXIT=0
[ace1] clean repo      : regenerated=73 committed=73 contents_match=True    EXIT=0
[mac]  poisoned clone  : contents_match=False   EXIT=1
  REJECT: identity inventory rows do not match a host-independent regeneration:
    [('gpu-claw','equality-report'), ('gpu-claw','equivalence-sentinel'), ('gpu-claw','repository-sync')]
```

**The prototype rejects the exact PR #3710 artifact, from the exact host that produced it**, while
`_validate_inventory_digest` passes it (R5).

### Is the guard genuinely enforceable? Yes — and here is the argument, not the assertion

| Requirement | How D4 meets it | Measured |
|---|---|---|
| Runs without anyone choosing to run it | It is inside `check-scheduler-mutation-surfaces.py`, already a required gate at every commit of this chain and of #3709 (its Implementation Sequencing step 5). | — |
| Runs on the host that authored the commit | The checker exits 0 on **both** hosts today. The macOS blocker recorded on #3709 is stale: git 2.55.0 supports `cat-file --batch-command -Z`. | R7 |
| Its verdict does not depend on the host | After D1 the regeneration is a pure function of the eight digest sources' bytes. The prototype returns the same verdict on Darwin and Linux for the same index. | D4 block above |
| It reads what will be committed, not what happens to be on disk | It consumes `read_index_records`' git-index blobs, the same source `_validate_inventory_digest` already uses. | `check-scheduler-mutation-surfaces.py:88-99, 328` |
| Failure is loud and blocking | Appending to `errors` is the checker's existing non-zero mechanism. | — |
| It cannot be satisfied by an artifact-only lie | The check recomputes the rows from trusted git-index source bytes; it does not compare the artifact to itself. A hand-edited `identities` array, or a Mac-rendered artifact-only poison carrying a matching `input_digest`, is rejected. | R5 vs D4 |

**The executed surface is itself pinned.** `_validate_inventory_contents` will import
`build-cron-identity-inventory.py`, whose import closure is exactly `cron_identity.py` →
`cron_render.py` → `yaml` (measured: `cron_identity.py:6` imports only from `cron_render`, and
`cron_render.py:14-21` imports only stdlib plus `yaml`; `cron_transaction.py` and
`cron_line_model.py` are digest sources but are **not** executed by the builder). **All three
executed modules are members of the eight-file digest set**
(`scheduler_mutation_delegation.py:113-118`). So worktree-vs-index divergence in the executed code
cannot silently widen the check: `build()` derives `input_digest` from worktree bytes while
`_validate_inventory_digest` derives it from index bytes, so any divergence trips the **existing**
digest error first. The failure direction is closed, not open.

**Covered versus uncovered failure modes.** Covered: stale generated inventory, hand-edited
`identities`/`machines`, artifact-only Mac poison, an artifact carrying a correct `input_digest` but
rows that do not regenerate from the staged sources, non-absolute or non-normal Linux roots, and the
known Darwin firmlink target prefix on Linux rows. Uncovered: a bad-but-internally-consistent edit to
trusted registry source bytes that is outside those cheap structural rules, honestly regenerated with
the matching `source_digest`. The contents check validates artifact/source agreement, not the physical
truth of every registry root. Full source-truth validation would require per-machine policy or remote
attestation for every declared root, which is out of proportion to #3711 and remains code-review
residue.

**Stated honestly — what this does not close.** The checker executes code imported from the
worktree, a pre-existing property (`scheduler_mutation_delegation.py:89-91` already does this). The
digest cross-check bounds it as argued above but does not eliminate it. Closing it entirely would
require executing the index bytes in a sandbox, which is out of proportion to this issue. This plan
records the residue rather than claiming it resolved.

### Rejected alternatives

| Option | Why rejected |
|---|---|
| **(a) alone — lexical normalisation, no guard, no contents check** | It fixes the defect and leaves nothing that would notice its return. `cron_render.py` is a digest source, so re-introducing `.resolve()` forces a regeneration — and R5 proves a Mac regeneration is *self-consistent* and passes the gate. (a) alone is a fix without a tripwire, on a path #3709 shows can delete live cron lines. |
| **(b) alone — refuse to write on a host that cannot render another machine's root** | It is a permanent refusal, not a fix: the Mac could never regenerate the inventory again, which re-imposes exactly the ace1-only authorship constraint #3709's r2 review called MAJOR for being unenforceable. It also cannot be evaluated from registry bytes — it must probe the running filesystem — so CI can never check another host's verdict. As a *residue* over (a) (D2) it is cheap and pure; as the primary remedy it is worse than the disease. |
| **A `platform.system() == "Darwin"` refusal** | Misidentifies the defect. The failure is "a declared root resolves to something else", not "macOS". A `/home` bind-mount, an autofs `/mnt`, or a symlinked checkout on a Linux box produces identical poison and a Darwin check misses all three. It is also untestable in CI, which runs Linux. |
| **`os.path.normpath()` then `.resolve()`, or `Path.resolve(strict=False)`** | Still touches the filesystem, so still host-dependent. `strict=False` is already the default and is exactly what produced the poison. |
| **Compare `.resolve()` output against the declared value and warn** | Advisory. `--check` already *is* that comparison, and R5 shows it goes green on the poisoning host the moment the poison is committed. |
| **An AST attestation over `cron_render.py` asserting "no `.resolve()` in the declared-root path"** | Kept as a **cheap secondary** (row 7) but rejected as the primary control. #3709's v3 documents at length that AST-shape predicates are defeated by aliasing — `os.path.realpath`, `Path.absolute()`, `os.stat`, a helper in another module. The contents check is semantic and cannot be aliased around: it compares the produced bytes. |
| **Regenerating the inventory inside CI and diffing** | Equivalent in strength but strictly more expensive and located outside the mutation-safety contract, where `.claude/rules/scheduler-mutation-safety.md`'s fail-closed clause already lives. D4 reuses the gate that is already mandatory. |

### Survey: does any other `scripts/cron/` generator share this host dependence?

The issue asks. Measured (`grep -rn '\.resolve()\|realpath\|expanduser' scripts/cron/*.py`), 15 hits,
classified:

| Site | Verdict |
|---|---|
| `cron_render.py:87` | **The defect.** Renders another machine's declared root through this host. Fixed by D1/D2. |
| `cron_render.py:24` `REPO_ROOT = Path(__file__).resolve().parents[2]` | **Latent, out of scope.** Host-dependent, but only as the *no-override* default — it never renders another machine's root. It would matter for a checkout that itself sits behind a symlink. Recorded as a follow-on, not fixed here, because changing it changes rendering for the local host and is not needed to close #3711. |
| `build-cron-identity-inventory.py:44` `path.resolve().relative_to(ROOT.resolve())` | **Not host-dependent in effect.** Both sides are resolved, so the logical name is stable. Proven: `input_digest` is identical on both hosts (R4). |
| `build-cron-identity-inventory.py:14-15,30`, `cron_apply.py:41`, `cron_transaction.py:20`, `cron-audit.py:34`, `validate-schedule.py:11,16`, `gemini-nightly-batch.py:32` | **Not host-dependent.** All are `Path(__file__).resolve()` module-anchoring. |
| `cron_runtime.py:32,38,326,336` | **Not host-dependent in the #3711 sense.** `resolve_controlled_path` is a traversal guard over the *running host's own* workspace; resolution there is the security property. It is also Linux-only (`/proc`). |
| **Divergence noted, not fixed:** `cron_render.main()` (`:222`) calls `build_context(args.machine, registry=registry)` with **no** `workspace_hub`, so the CLI's `--field workspace_hub` reports `$WORKSPACE_HUB`/`REPO_ROOT`, not the registry `workspace_root` the inventory records. Measured harmless today: `setup-cron.sh` queries only `machine_id`, `schedule_variant`, `os` (`:42-53`) and refuses remote machines outright (`:58-61`). Recorded as a follow-on. |

**Conclusion: `cron_render.py:87` is the only generator that renders another machine's declared path
through the running host's filesystem.** Two follow-ons are recorded above; neither is required to
close #3711.

---

## Pseudocode

```python
# scripts/cron/cron_render.py
def declared_workspace_root(value: str | Path) -> PurePosixPath:
    """Normalise a registry-declared workspace_root as declared data.
    Touches no filesystem: no expanduser(), no resolve(), no stat(). #3711."""
    return PurePosixPath(os.path.normpath(str(value)))


def workspace_hub_path(workspace_hub: str | Path | None = None) -> Path | PurePosixPath:
    override = workspace_hub or os.environ.get("WORKSPACE_HUB")
    return declared_workspace_root(override) if override else REPO_ROOT


# scripts/cron/cron_identity.py
def validate_declared_workspace_roots(registry: object) -> list[str]:
    """#3711: a declared root must be renderable without consulting this host."""
    errors = []
    for machine_id, row in sorted((registry.get("machines") or {}).items()):
        if not isinstance(row, dict) or row.get("os") != "linux":
            continue
        declared = row.get("workspace_root")
        if declared is None:
            continue
        text = str(declared)
        if not text.startswith("/"):
            errors.append(f"{machine_id}: workspace_root must be an absolute POSIX path "
                          f"renderable without this host ({text!r}) [#3711]")
        elif str(declared_workspace_root(text)) != text:
            errors.append(f"{machine_id}: workspace_root must be in normal form "
                          f"({text!r}) [#3711]")
    return errors


def validate_inventory_inputs(catalog, registry):
    ...
    errors.extend(_validate_registry_root(registry))
    errors.extend(validate_declared_workspace_roots(registry))   # NEW
    return errors


# scripts/cron/build-cron-identity-inventory.py
def build_from_documents(catalog: dict, registry: dict, classes: dict) -> dict:
    """Pure core: parsed documents in, identity rows out. No Path, no filesystem."""
    schema_errors = validate_inventory_inputs(catalog, registry) + validate_state_classes(...)
    if schema_errors:
        raise ValueError("; ".join(schema_errors))
    machines = sorted(m for m, row in (registry.get("machines") or {}).items()
                      if row.get("os") == "linux")
    rows, unsupported, collisions, bound_legacy = [], [], [], set()
    for machine_id in machines:
        _build_machine(catalog, registry, classes, machine_id, rows, unsupported,
                       collisions, bound_legacy)
    _append_unbound_legacy(classes, bound_legacy, unsupported)
    return {"machines": machines, "identities": rows,
            "unsupported": unsupported, "collisions": collisions}


def build(catalog_path, registry_path, classes_path) -> dict:
    """Thin path-reading wrapper. Unchanged output."""
    catalog, registry, classes = (yaml.safe_load(p.read_text(encoding="utf-8"))
                                  for p in (catalog_path, registry_path, classes_path))
    core = build_from_documents(catalog, registry, classes)
    union = [catalog_path, registry_path, classes_path, *SOURCE_PATHS]
    return {"schema_version": 1, "input_digest": input_digest(union), **core}


# scripts/enforcement/scheduler_mutation_delegation.py
def _validate_inventory_contents(inventory, records, errors):
    """#3711: certify the inventory's ROWS, not only its input digest.
    Regeneration is host-independent after #3711's cron_render fix, so this
    verdict is the same on every POSIX host for the same git index."""
    try:
        catalog = yaml.safe_load(records[b"config/scheduled-tasks/schedule-tasks.yaml"])
        registry = yaml.safe_load(records[b"config/workstations/registry.yaml"])
        classes = yaml.safe_load(records[b"config/workstations/harness-state-classes.yaml"])
        core = _load_inventory_builder().build_from_documents(catalog, registry, classes)
    except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"identity inventory contents could not be regenerated: {exc}")
        return
    for field in ("machines", "identities", "unsupported", "collisions"):
        if inventory.get(field) != core[field]:
            errors.append(f"identity inventory {field} do not match a host-independent "
                          f"regeneration from index bytes [#3711]")


def validate_identity_inputs(root, registry, records, errors):
    ...
    inventory = _validate_inventory_bytes(records, errors)
    _validate_inventory_digest(inventory, records, errors)
    _validate_inventory_contents(inventory, records, errors)      # NEW
    ...
```

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3711-host-independent-identity-inventory.md` |
| Author verification log | `scripts/review/results/2026-07-30-plan-3711-verification-log.md` |
| Verification prototype (committed) | `scripts/review/results/2026-07-30-plan-3711-prototype/proto_3711.py` |
| Contents-check prototype (committed) | `scripts/review/results/2026-07-30-plan-3711-prototype/contents_check.py` |
| Headline / guard prototype (committed) | `scripts/review/results/2026-07-30-plan-3711-prototype/proto_ef.py` |
| Prototype runbook | `scripts/review/results/2026-07-30-plan-3711-prototype/README.md` |
| Independent plan review (required) | `scripts/review/results/2026-07-30-plan-3711-<provider>-r1.md` |
| Blocked consumer plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md` |
| Renderer (the defect) | `scripts/cron/cron_render.py` |
| Inventory builder | `scripts/cron/build-cron-identity-inventory.py` |
| Ownership context + validators | `scripts/cron/cron_identity.py` |
| Digest chain / enforcement | `scripts/enforcement/scheduler_mutation_delegation.py` |
| Enforcement entry point | `scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| Machine registry | `config/workstations/registry.yaml` |
| Mutation surface registry | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Identity inventory (generated) | `docs/reports/issue-3475-command-identity-inventory.json` |
| Generated safety report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| New renderer tests | `tests/cron/test_cron_render_declared_root.py` |
| New enforcement tests | `tests/enforcement/test_identity_inventory_contents.py` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A cron identity inventory whose contents will be a pure function of the bytes of its declared
inputs: a renderer that will treat a registry `workspace_root` as declared data and never resolve it
against the running host; a fail-closed validator that will refuse to build, naming the machine,
when a declared root cannot be rendered faithfully by lexical normalisation alone; a pure
document-in/rows-out core for the builder; and an enforcement check that will regenerate the
identity rows from git-index bytes and reject any committed inventory whose rows disagree — closing
the "correct `input_digest` over wrong `identities`" hole that let PR #3710's macOS-authored claim
pass the gate.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/cron/cron_render.py` | Add `declared_workspace_root`; `workspace_hub_path` will delegate to it for any explicit override. Removes `.expanduser()` and `.resolve()` from the declared-root path (line 87). **Digest source** — forces an inventory regeneration in the same commit. |
| Modify | `scripts/cron/cron_identity.py` | Add `validate_declared_workspace_roots`; call it from `validate_inventory_inputs`. **Digest source.** |
| Modify | `scripts/cron/build-cron-identity-inventory.py` | Extract `build_from_documents(catalog, registry, classes)`; `build()` becomes a path-reading wrapper. No output change. **Digest source.** |
| Modify | `scripts/enforcement/scheduler_mutation_delegation.py` | Add `_validate_inventory_contents`; call it from `validate_identity_inputs`. **Not** a digest source. |
| Create | `tests/cron/test_cron_render_declared_root.py` | Rows 1, 2, 3, 5, 6, 7, 12. |
| Create | `tests/enforcement/test_identity_inventory_contents.py` | Rows 8, 9, 10, 11. |
| Create | `tests/cron/fixtures/gpu-claw-identity-rows-linux-baseline.json` | The three Linux-rendered `gpu-claw` rows, committed as the baseline row 3 compares against. Extracted from `main`'s inventory, not re-derived. |
| Modify | `docs/reports/issue-3475-command-identity-inventory.json` | Regenerate. Measured: **only `input_digest` will change** — `identities` are byte-identical on Linux before and after ( `[ace1] [B] PROPOSED == today: True` ). |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Refresh `resolved_dispositions[0].source_digest` (line 273) to the new `input_digest`, per the cross-check at `scheduler_mutation_delegation.py:97`. No new surface row. |
| Modify | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Regenerate via `--render-html`. |
| Modify | `docs/plans/README.md` | Index row. |

**Not changed:** `scripts/cron/cron_transaction.py`, `scripts/cron/cron_line_model.py`,
`scripts/cron/cron_apply.py`, `scripts/cron/cron-audit.py`, `scripts/cron/setup-cron.sh`,
`scripts/enforcement/scheduler_mutation_attestations.py`,
`scripts/enforcement/scheduler_mutation_contract.py` (stays at 400 lines; `ATT_SOURCES` gains no
entry — measured: no attestation targets `cron_render.py`), `config/workstations/registry.yaml`
(measured: today's four Linux roots already pass the proposed guard — `[C3] … -> []` on both hosts),
any crontab.

---

## TDD Test List

Every row states its status **on today's `main` at `3fe934da9`**, on the host that makes the
measurement meaningful, with the command that produced it. `PROTO` =
`scripts/review/results/2026-07-30-plan-3711-prototype/proto_3711.py`, `PROTO_EF` = `proto_ef.py`,
`CC` = `contents_check.py`; all three are committed on this branch so a reviewer runs the author's
prototype rather than reimplementing the contract.

| # | Test name | File | What it will verify | Expected | Today's status on `main` + proving command |
|---|---|---|---|---|---|
| 1 | `test_declared_root_under_a_symlink_renders_unchanged` | `test_cron_render_declared_root.py` | A declared root beneath a real symlinked directory (the portable stand-in for the macOS `/home` firmlink) renders to itself. Builds `tmp/Volumes/Data/home/undi/ws/workspace-hub` and `tmp/home -> tmp/Volumes/Data/home`. | `build_context(...)["workspace_hub"] == declared` | **RED on BOTH hosts.** `[ace1]` `uv run --with pyyaml python PROTO <root> /tmp/proto3711fx` → `[C1] today build_context workspace_hub: /tmp/proto3711fx/Volumes/Data/home/undi/ws/workspace-hub`, `[C1] today faithful: False`. `[mac]` identical shape. Requires no Mac. |
| 2 | `test_declared_root_render_touches_no_filesystem` | `test_cron_render_declared_root.py` | With `Path.resolve`, `Path.expanduser`, `os.path.realpath`, `os.stat` and `os.lstat` all monkeypatched to raise, rendering every registry Linux root completes. | no exception | **RED on BOTH hosts.** `PROTO` → `[C2] today: FAIL (declared workspace_root render touched the filesystem)` on `[ace1]` and `[mac]`. This is the design assertion: it is red today for exactly the reason the issue was filed. |
| 3 | **`test_gpu_claw_rows_are_identical_under_a_darwin_firmlink_resolver`** | `test_cron_render_declared_root.py` | **HEADLINE.** With `Path.resolve` replaced by a fake reproducing the *measured* macOS behaviour (`/home/X → /System/Volumes/Data/home/X`), regenerating the full inventory equals the committed Linux baseline, and `gpu-claw`'s three rows equal the committed fixture. | generated bytes `==` committed inventory | **RED on BOTH hosts.** `[ace1]` `uv run --with pyyaml python PROTO_EF /mnt/local-analysis/workspace-hub` → `[E] today, fake-Darwin resolver: generated == committed baseline -> False`; rows differing `[('gpu-claw','equality-report'),('gpu-claw','equivalence-sentinel'),('gpu-claw','repository-sync')]`; `[E] input_digest still matches -> True`. `[mac]` identical. With D1: `[E] PROPOSED … -> True` on both. **No Mac required in CI.** |
| 4 | `test_committed_inventory_regenerates_on_this_host` | `test_cron_render_declared_root.py` | The committed inventory regenerates byte-identically on whatever host runs the suite — the pytest form of `--check`. | equal | **RED on `[mac]` (the meaningful host), GREEN on `[ace1]`.** `[mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check` → `ERROR: stale identity inventory`, exit **1**. `[ace1]` same command → exit **0**. Declared: the ace1 result is not a change-proof; the mac result is. |
| 5 | `test_tilde_declared_workspace_root_is_rejected_not_expanded` | `test_cron_render_declared_root.py` | A `~`-declared root makes `build()` raise and `main()` return 1, naming the machine — instead of silently expanding to the running user's home. | `SystemExit`/return 1 naming `gpu-claw` | **RED on BOTH hosts.** `PROTO_EF` → `[mac] [F] ~/ws/workspace-hub -> /Users/krishna/ws/workspace-hub faithful=False`; `[ace1] [F] -> /home/vamsee/ws/workspace-hub faithful=False`; `[F] today: silently host-expanded, no error raised -> True` on both. |
| 6 | `test_non_normal_declared_workspace_root_is_rejected` | `test_cron_render_declared_root.py` | `/home/undi/../undi/ws/workspace-hub` is refused, naming the machine, rather than silently collapsed. Also covers `~user` roots, which today escape as an uncaught `RuntimeError`. | return 1 naming `gpu-claw` | **RED on BOTH hosts.** No declared-root validation exists: `grep -c workspace_root scripts/cron/cron_identity.py` → `1` (the `:193` fallback lookup, not a check); `grep -rn declared_workspace_root scripts/ tests/` → 0 hits. `PROTO_EF` → `[F] today, ~user-declared root -> <RuntimeError: Could not determine home directory.>` on both hosts — uncaught by `main()`'s `(OSError, TypeError, ValueError, yaml.YAMLError)`. |
| 7 | `test_workspace_hub_path_has_no_filesystem_call_in_its_ast` | `test_cron_render_declared_root.py` | Cheap structural tripwire: the AST of `workspace_hub_path` + `declared_workspace_root` contains no `resolve`/`expanduser`/`realpath`/`stat`/`absolute` call. Explicitly **secondary** to row 9 — see the rejected-alternatives note on AST aliasing. | no such call | **RED on BOTH hosts.** `sed -n '87p' scripts/cron/cron_render.py` → `return Path(override).expanduser().resolve() if override else REPO_ROOT` — two banned calls on one line. |
| 8 | `test_build_from_documents_takes_documents_not_paths` | `test_identity_inventory_contents.py` | `build_from_documents(catalog, registry, classes)` exists, its parameters are exactly those three, and it returns the four core keys with no `Path` in its signature. | signature matches | **RED on BOTH hosts.** `grep -rn build_from_documents scripts/ tests/` → **0 hits**; today `build()` takes three `Path`s (`build-cron-identity-inventory.py:59`). |
| 9 | **`test_checker_rejects_an_inventory_whose_rows_do_not_regenerate`** | `test_identity_inventory_contents.py` | **The enforceable guard.** Given index records carrying the PR #3710 poisoned inventory, `validate_identity_inputs` appends an error, so the checker exits non-zero. | ≥1 error; exit ≠ 0 | **RED on BOTH hosts.** `grep -rn _validate_inventory_contents scripts/ tests/` → **0 hits**. And measured live on `[mac]`, in an isolated `git clone --shared`: after staging the macOS-generated inventory, `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` → **exit 0**. The prototype `CC` on the same index → `contents_match=False`, **exit 1**, naming the three `gpu-claw` rows. |
| 10 | `test_correct_input_digest_does_not_certify_wrong_rows` | `test_identity_inventory_contents.py` | Explicit regression pin on the exact hole: an inventory with a *matching* `input_digest` and mutated `identities` must still be rejected. | rejected | **RED on BOTH hosts.** `[mac]` `PROTO` → `[B] today input_digest == committed input_digest: True` **and** `[B] => wrong rows can carry a correct digest: True`. `_validate_inventory_digest` (`scheduler_mutation_delegation.py:112-123`) reads only the eight source blobs and never `inventory["identities"]`. |
| 11 | `test_contents_check_accepts_todays_main_on_any_posix_host` | `test_identity_inventory_contents.py` | Guard against a check that is merely strict: the clean `main` index must pass, on both hosts. Declared a **regression guard**, not a change-proof — but it is the row that would catch a contents check that fails everywhere. | accepted, 73 rows | **RED on BOTH hosts** (the function does not exist — row 9's grep). Prototype behaviour measured: `[mac] CC <repo>` → `regenerated=73 committed=73 contents_match=True EXIT=0`; `[ace1] CC /mnt/local-analysis/workspace-hub` → identical. |
| 12 | `test_every_registry_linux_root_renders_to_itself` | `test_cron_render_declared_root.py` | Every `os: linux` machine with a declared `workspace_root` renders to that exact string. Supersedes #3709 v3's row 22, which was declared a *tripwire* because it could only be green-on-Linux; after D1 it becomes a real assertion that holds everywhere. | all faithful | **RED on `[mac]` (the meaningful host), GREEN on `[ace1]`.** `[mac] PROTO` → `[A] gpu-claw today .resolve(): /System/Volumes/Data/home/undi/ws/workspace-hub faithful=False`. `[ace1] PROTO` → all four faithful. Declared: the ace1 result is not a change-proof. |

**Score: 10 of 12 rows are RED on today's `main` on *both* hosts. Rows 4 and 12 are RED only on
macOS and are declared as such** — they are host-parity rows and cannot be otherwise; both are
additionally covered host-independently by rows 1-3, which are red on Linux. **No row is green on
both hosts today.**

**Existing green gates that will be run and must stay green** (declared green, deliberately not
counted as change-proofs):

| Gate | Status today at `3fe934da9` | Command |
|---|---|---|
| enforcement checker | GREEN, exit 0 on **both** hosts | `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| generated HTML report | GREEN, exit 0 `[ace1]` | `… --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| identity inventory freshness | GREEN `[ace1]` exit 0; RED `[mac]` exit 1 — row 4 | `uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check` |
| existing cron suite | GREEN on `main` `[ace1]`: `284 passed in 25.47s`, re-verified 2026-07-30 on `ace-linux-1` at `ae45d3c81`. The earlier `1 failed, 283 passed` note was a measurement error and must not be whitelisted as pre-existing. | `ssh ace1 'bash -l -s' < <script: cd /mnt/local-analysis/workspace-hub && uv run pytest tests/cron -q>` |
| existing renderer suite | **NOT green on `main`** `[ace1]`: `1 failed, 65 passed in 273.25s` — `test_validate_schedule.py::test_windows_tasks_have_windows_scheduler` already fails at `3fe934da9`. Windows rows are excluded from the inventory at `build-cron-identity-inventory.py:70`; this plan changes neither the catalog nor `validate-schedule.py`. | `uv run pytest scripts/cron/tests -q` |
| existing enforcement suite | **NOT green on `main`** `[ace1]`: `2 failed, 417 passed in 865.11s` — `test_check_skill_index_coherence.py::test_real_repo_passes` and `test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state`. Both are unrelated to the scheduler-mutation contract; the **gate itself** (`check-scheduler-mutation-surfaces.py`) exits 0 on both hosts. | `uv run pytest tests/enforcement -q` |

`test_cron_runtime.py` passes today in `tests/cron`. `test_validate_schedule.py` lives under
`scripts/cron/tests/`, outside both `tests/cron` and `tests/enforcement`; its Windows-scheduler
failure is the lone known cron-renderer-suite failure. The suite acceptance criterion below is
therefore stated as "no new failures relative to the true baseline", not "the suites pass" and not a
phantom `tests/cron` failure that could mask a real regression.

---

## Implementation Sequencing

Each commit will end with `check-scheduler-mutation-surfaces.py` and `--check-html` at exit 0, run
**after** `git add` (the checker reads the git index, not the worktree).

1. **Commit 1 — RED tests and the baseline fixture only.** All 12 rows plus
   `tests/cron/fixtures/gpu-claw-identity-rows-linux-baseline.json`. `tests/` is not a digest source,
   so the gate stays green while 10-12 rows fail.
   *Gate check:* checker exit 0.
2. **Commit 2 — D1 + D2.** `cron_render.declared_workspace_root` and the `workspace_hub_path`
   delegation; `cron_identity.validate_declared_workspace_roots` wired into
   `validate_inventory_inputs`. Both files are digest sources, so the inventory and
   `mutation-surfaces.yaml:273` `source_digest` will be regenerated and the HTML re-rendered **in
   the same commit**. Rows 1-7 and 12 go green. Measured: the regeneration will change **only**
   `input_digest` — the 73 identity rows are byte-identical before and after on Linux.
   *This commit alone closes #3711's stated scope and unblocks #3709.*
3. **Commit 3 — D3 + D4.** `build_from_documents` extraction and
   `scheduler_mutation_delegation._validate_inventory_contents`. The builder is a digest source, so
   the inventory, `source_digest` and HTML will be refreshed again in this commit;
   `scheduler_mutation_delegation.py` is not a digest source. Rows 8-11 go green.

**Implementation host:** commit 1 may be authored anywhere. Commit 2 **will be authored on `ace1`**,
because until it lands the Mac cannot produce a correct inventory (R2/R3) and commit 2 must regenerate
one. From commit 2 onward, generation is host-independent and commit 3 may be authored anywhere —
proven, not asserted, by row 3 and by `[mac] [B] PROPOSED: generated == committed: True`.

**Coordination with #3709.** #3709's plan declares this a blocking prerequisite for its commits 2-4
and permits its commit 1 (RED tests) to land first. After commit 2 here, #3709's row 22 tripwire
(`test_identity_inventory_host_can_render_every_linux_root`) becomes redundant with row 12 here;
#3709 should drop it or re-point it, which is a note for that plan's next revision, not a change this
plan will make.

---

## Acceptance Criteria

- [ ] `workspace_hub_path` will perform **no** filesystem access for a declared `workspace_root` —
      no `resolve()`, no `expanduser()`, no `realpath()`, no `stat()`.
- [ ] Regenerating the identity inventory on macOS will produce bytes **identical** to the
      Linux-rendered baseline; `build-cron-identity-inventory.py --check` will exit 0 on both hosts.
- [ ] Rendering `gpu-claw`'s `/home/undi/ws/workspace-hub` root under an injected macOS-firmlink
      resolver will produce the committed Linux baseline, proven by a test that runs on Linux CI with
      no Mac.
- [ ] A declared `workspace_root` that is not an absolute, normal-form POSIX path will make the
      builder **refuse to write** and exit non-zero, naming the offending machine and citing #3711.
- [ ] `build_from_documents(catalog, registry, classes)` will exist, take parsed documents only, and
      return `machines`, `identities`, `unsupported`, `collisions`.
- [ ] `check-scheduler-mutation-surfaces.py` will regenerate the identity rows from **git-index
      bytes** and reject any committed inventory whose `identities` or `machines` differ — including
      one carrying a correct `input_digest`.
- [ ] The checker will **reject** the PR #3710 poisoned artifact and **accept** today's `main`, with
      the same verdict on macOS and Linux.
- [ ] The regenerated inventory's 73 identity rows will be byte-identical to `main`'s; only
      `input_digest` will change. `mutation-surfaces.yaml` `source_digest` and the safety HTML will be
      refreshed in the same commit as each source change.
- [ ] `uv run pytest tests/cron tests/enforcement scripts/cron/tests -q` on `ace1` will show **no new
      failures** relative to the true baseline — `tests/cron`: `284 passed, 0 failed`
      (`ssh ace1 'bash -l -s' < <script>` with `cd /mnt/local-analysis/workspace-hub && uv run pytest
      tests/cron -q`, re-verified 2026-07-30 at `ae45d3c81`); `scripts/cron/tests`: `1 failed,
      65 passed` (`test_validate_schedule.py::test_windows_tasks_have_windows_scheduler`, outside
      `tests/cron`); `tests/enforcement`: `2 failed, 417 passed`
      (`test_check_skill_index_coherence.py::test_real_repo_passes`,
      `test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state`). The three known
      failures are pre-existing and in modules this plan does not touch. Any `tests/cron` failure is
      new and must block the implementation.
- [ ] `check-scheduler-mutation-surfaces.py` and `--check-html` will exit 0 at every commit.
- [ ] No implementation step will run `crontab` (write), `setup-cron.sh`, `cron_apply.py --apply`,
      `daily-cleanup.sh`, `repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.
- [ ] `scheduler_mutation_contract.py` will stay at 400 lines and `ATT_SOURCES` will gain no entry.

---

## Risks

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-1 | Changing `workspace_hub_path`'s return type from `Path` to `PurePosixPath` breaks a caller that needs a concrete path. | Low | Measured: exactly two references exist in the repo, and the only consumer stores `str(hub)` and does `hub / FULL_VARIANT_LOG`. Byte-identical regeneration on both hosts is the proof. The no-override branch still returns `REPO_ROOT` (a real `Path`). Row 4 and the existing suites will catch a regression. |
| R-2 | A future `registry.yaml` edit introduces a Windows `workspace_root` on an `os: linux` row, and the guard renders `D:\…` as a POSIX path. | Low | The guard rejects any root not starting with `/`, which covers `D:\workspace-hub`. Windows rows are separately excluded at `build-cron-identity-inventory.py:70`. |
| R-3 | The contents check makes the enforcement gate fail for an unrelated reason (e.g. a config edit committed without regenerating), producing gate noise. | Medium | That is the intended behaviour — it is the same class of failure `_validate_inventory_digest` already produces for the same edits, and the error message will name the differing field. Row 11 pins that a clean `main` is accepted, so a check that fails universally is caught. |
| R-4 | The checker imports builder code from the **worktree**, so worktree/index divergence could in principle influence the verdict. | Low | Argued above: all five executed modules are digest sources, and `build()`'s worktree-derived `input_digest` versus the checker's index-derived digest means divergence trips the existing digest error first — closed, not open. Pre-existing (`scheduler_mutation_delegation.py:89-91`) and recorded as residue, not claimed resolved. |
| R-5 | An implementer treats the AST tripwire (row 7) as the guard and weakens the contents check. | Low | The plan states explicitly that row 7 is secondary and defeated by aliasing, and row 9 is the guard. The rejected-alternatives table records why. |
| R-6 | `REPO_ROOT` (`cron_render.py:24`) remains host-dependent for the no-override case. | Low | Out of scope and recorded as a follow-on. It never renders another machine's root, which is #3711's subject. Would matter only for a local checkout sitting behind a symlink. |
| R-7 | `cron_render.main()`'s `--field workspace_hub` reports `$WORKSPACE_HUB`/`REPO_ROOT`, not the registry root. | Low | Measured harmless: `setup-cron.sh` queries only `machine_id`, `schedule_variant`, `os`, and refuses remote machines outright. Recorded as a follow-on. |

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex r2 | MINOR | Design sound; required narrowing the contents-check claim to artifact/source agreement rather than source truth, and corrected the `tests/cron` baseline to `284 passed, 0 failed`. Both corrections are applied in v2. |

The author's own verification is recorded in
`scripts/review/results/2026-07-30-plan-3711-verification-log.md` and is **not** a review. The three
prototype scripts are committed on this branch so a reviewer can re-run the author's contract rather
than reconstruct it — a defect an earlier review in this chain recorded explicitly.
