# Author verification log — plan for #3711

**This is a measurement record, not a review.** An independent adversarial review of
`docs/plans/2026-07-30-issue-3711-host-independent-identity-inventory.md` is still required.

- **Date:** 2026-07-30
- **Commit under measurement:** `3fe934da9` (`origin/main`) — verified identical on both hosts
- **Hosts:**
  - `[mac]` `macbook-portable`, Darwin 25.5.0, `/Users/krishna/Developer/ws/workspace-hub`, git 2.55.0, CPython 3.14.6
  - `[ace1]` `ace-linux-1` / `dev-primary`, Linux 7.0.0-28-generic, `/mnt/local-analysis/workspace-hub`, CPython 3.11.14
- **Prototype:** `scripts/review/results/2026-07-30-plan-3711-prototype/` (committed on this branch)
- **Write safety:** nothing was written into either checkout. The only mutation anywhere was inside a
  throwaway `git clone --shared` under the session scratchpad, which was never pushed and is not
  reachable from any ref. No `crontab` write, no `setup-cron.sh`, no `cron_apply.py --apply`.

---

## 1. Root cause — `cron_render.py:87`

```
$ sed -n '84,88p' scripts/cron/cron_render.py
def workspace_hub_path(workspace_hub: str | Path | None = None) -> Path:
    """Return the checkout path used for render-time $WORKSPACE_HUB expansion."""
    override = workspace_hub or os.environ.get("WORKSPACE_HUB")
    return Path(override).expanduser().resolve() if override else REPO_ROOT
```

```
$ [ace1] uv run --with pyyaml python proto_3711.py /mnt/local-analysis/workspace-hub
=== host=Linux node=ace-linux-1 root=/mnt/local-analysis/workspace-hub ===
[A] dev-primary   declared: /mnt/local-analysis/workspace-hub
[A] dev-primary   today .resolve():    /mnt/local-analysis/workspace-hub                     faithful=True
[A] dev-primary   proposed lexical:    /mnt/local-analysis/workspace-hub                     faithful=True
[A] dev-secondary declared: /mnt/local-analysis/workspace-hub
[A] dev-secondary today .resolve():    /mnt/local-analysis/workspace-hub                     faithful=True
[A] dev-secondary proposed lexical:    /mnt/local-analysis/workspace-hub                     faithful=True
[A] gpu-claw      declared: /home/undi/ws/workspace-hub
[A] gpu-claw      today .resolve():    /home/undi/ws/workspace-hub                           faithful=True
[A] gpu-claw      proposed lexical:    /home/undi/ws/workspace-hub                           faithful=True

$ [mac] uv run --with pyyaml python proto_3711.py /Users/krishna/Developer/ws/workspace-hub
=== host=Darwin node=Vamsees-MacBook-Air.local root=/Users/krishna/Developer/ws/workspace-hub ===
[A] dev-primary   today .resolve():    /mnt/local-analysis/workspace-hub                     faithful=True
[A] dev-secondary today .resolve():    /mnt/local-analysis/workspace-hub                     faithful=True
[A] gpu-claw      today .resolve():    /System/Volumes/Data/home/undi/ws/workspace-hub       faithful=False
[A] gpu-claw      proposed lexical:    /home/undi/ws/workspace-hub                           faithful=True
```

`gali-linux-compute-1` has `workspace_root: None` and is skipped (contributes 0 rows).

**Confirms the brief:** `gpu-claw` is the single poisoned row on macOS.

## 2. `--check` disagrees between hosts

```
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ACE1_CHECK_EXIT=0

$ [mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ERROR: stale identity inventory: /Users/krishna/Developer/ws/workspace-hub/docs/reports/issue-3475-command-identity-inventory.json
MAC_CHECK_EXIT=1
```

## 3. The committed inventory on `main` is correct — a latent defect, not a manifest one

```
[ace1] [B] today: generated == committed: True
[ace1] [B] today rows differing from committed: []
[ace1] [B] today input_digest == committed input_digest: True
[ace1] [B] => wrong rows can carry a correct digest: False

[mac]  [B] today: generated == committed: False
[mac]  [B] today rows differing from committed:
         [('gpu-claw','equality-report'), ('gpu-claw','equivalence-sentinel'), ('gpu-claw','repository-sync')]
[mac]  [B] today input_digest == committed input_digest: True
[mac]  [B] => wrong rows can carry a correct digest: True

[both] generated rows per machine: {'dev-primary': 56, 'dev-secondary': 14, 'gpu-claw': 3} total 73
[both] committed rows per machine: {'dev-primary': 56, 'dev-secondary': 14, 'gpu-claw': 3} total 73
[both] unsupported: []   collisions: []
```

Per-machine counts match the brief exactly. Exactly 3 of 73 rows differ, all `gpu-claw`.

## 4. There is no host guard

```
$ grep -c 'platform\|Darwin\|sys.platform\|uname\|hostname' scripts/cron/build-cron-identity-inventory.py
0
$ sed -n '68,71p' scripts/cron/build-cron-identity-inventory.py
    machines = sorted(
        machine_id for machine_id, row in (registry.get("machines") or {}).items()
        if row.get("os") == "linux"
    )
$ grep -rn 'declared_workspace_root\|build_from_documents\|_validate_inventory_contents' scripts/ tests/
(0 hits each)
$ grep -c workspace_root scripts/cron/cron_identity.py
1                       # the :193 fallback lookup, not a validation
```

## 5. The enforcement checker accepts a macOS-poisoned inventory

Performed in an isolated `git clone --shared --no-checkout` under the scratchpad. Never pushed.

```
$ [mac] git clone -q --shared --no-checkout <repo> $SCR/clone && git -C $SCR/clone checkout -q main
clone HEAD: 3fe934da9
$ [mac] cd $SCR/clone && uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py
$ [mac] git diff --stat
 docs/reports/issue-3475-command-identity-inventory.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
$ [mac] git add docs/reports/issue-3475-command-identity-inventory.json
$ [mac] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
POISONED_CHECKER_EXIT=0
$ [mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
POISONED_SELFCHECK_EXIT=0
```

And the poisoned artifact carried to ace1:

```
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py \
           --check --output /tmp/poisoned-inventory.json
ERROR: stale identity inventory: /tmp/poisoned-inventory.json
ACE1_CHECK_POISONED_EXIT=1
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ACE1_CHECK_COMMITTED_EXIT=0
```

**The role flip is the finding.** Once a Mac commits the poison, the Mac's own `--check` is green
forever and the enforcement gate never objects; only a Linux run — which nothing requires — disagrees.
This is PR #3710 (`a60e50d80` → `7ac7ce445`) reproduced end to end.

## 6. `expanduser()` — a second, independent host dependency on the same line

```
[mac]  [F] declared=~/ws/workspace-hub
[mac]  [F] today workspace_hub_path -> /Users/krishna/ws/workspace-hub   faithful=False
[ace1] [F] today workspace_hub_path -> /home/vamsee/ws/workspace-hub     faithful=False
[both] [F] today: silently host-expanded, no error raised -> True
[both] [F] today, ~user-declared root -> <RuntimeError: Could not determine home directory.>
[both] [F] PROPOSED guard -> [('gpu-claw','~/ws/workspace-hub','workspace_root is not an absolute POSIX path')]
[both] [F] PROPOSED guard on the real registry -> []
```

`RuntimeError` is in neither `main()`'s caught tuple (`OSError, TypeError, ValueError,
yaml.YAMLError`) nor `_build_machine`'s (`KeyError, TypeError, ValueError`), so a `~user` root
escapes as an uncaught traceback. This is why lexical normalisation alone is insufficient and the
declared-root guard (D2) is retained.

## 7. The proposed fix — byte-identical output on both hosts

```
[mac]  [B] PROPOSED: generated == committed: True       (today: False)
[mac]  [B] PROPOSED == today: False
[ace1] [B] PROPOSED: generated == committed: True
[ace1] [B] PROPOSED == today: True                       <-- no identity-row churn on Linux
```

## 8. The headline test, without a Mac (`proto_ef.py`, section E)

`Path.resolve` is replaced by a fake reproducing the **measured** macOS behaviour
(`/home/X → /System/Volumes/Data/home/X`), and the whole inventory is regenerated:

```
[ace1] [E] today, fake-Darwin resolver: generated == committed baseline -> False
[ace1] [E] today, fake-Darwin resolver: rows differing ->
             [('gpu-claw','equality-report'), ('gpu-claw','equivalence-sentinel'), ('gpu-claw','repository-sync')]
[ace1] [E] today, fake-Darwin resolver: input_digest still matches -> True
[ace1] [E] PROPOSED, fake-Darwin resolver: generated == committed baseline -> True

[mac]  [E] today, fake-Darwin resolver: generated == committed baseline -> False
[mac]  [E] today, fake-Darwin resolver: rows differing -> (identical to ace1)
[mac]  [E] PROPOSED, fake-Darwin resolver: generated == committed baseline -> True
```

**The headline row is RED on Linux and green under the fix, on both hosts, with no Mac in the loop.**
It also reproduces the exact three poisoned rows on Linux — the fake resolver is faithful to the
measured firmlink behaviour, not an approximation.

## 9. The portable symlink fixture and the no-filesystem assertion (`proto_3711.py`, sections C1/C2)

```
[ace1] [C1] declared:                       /tmp/proto3711fx/home/undi/ws/workspace-hub
[ace1] [C1] today build_context:            /tmp/proto3711fx/Volumes/Data/home/undi/ws/workspace-hub
[ace1] [C1] today faithful:                 False
[ace1] [C1] PROPOSED build_context:         /tmp/proto3711fx/home/undi/ws/workspace-hub
[ace1] [C1] PROPOSED faithful:              True
[mac]  [C1] (identical shape under the scratchpad tmp dir)

[both] [C2] today:    FAIL (declared workspace_root render touched the filesystem)
[both] [C2] PROPOSED: PASS (no filesystem access)
```

C2 monkeypatches `Path.resolve`, `Path.expanduser`, `os.path.realpath`, `os.stat` and `os.lstat` to
raise, then renders a declared root.

## 10. The declared-root guard (`proto_3711.py`, section C3)

```
[both] [C3] unfaithful declared roots in registry.yaml:
          []
[both] [C3] guard on a '~'-declared root:
          [('gpu-claw','~/ws/workspace-hub','workspace_root is not an absolute POSIX path')]
[both] [C3] guard on a non-normal root:
          [('gpu-claw','/home/undi/../undi/ws/workspace-hub','workspace_root is not in normal form')]
```

Today's registry passes the proposed guard unchanged — no `registry.yaml` edit will be required.

## 11. The contents check — feasibility and verdict (`contents_check.py`)

```
$ [mac]  uv run --with pyyaml python contents_check.py /Users/krishna/Developer/ws/workspace-hub
regenerated=73 committed=73 contents_match=True
EXIT=0
$ [ace1] uv run --with pyyaml python contents_check.py /mnt/local-analysis/workspace-hub
regenerated=73 committed=73 contents_match=True
EXIT=0
$ [mac]  uv run --with pyyaml python contents_check.py $SCR/clone     # the poisoned index
regenerated=73 committed=73 contents_match=False
REJECT: identity inventory rows do not match a host-independent regeneration:
  [('gpu-claw','equality-report'), ('gpu-claw','equivalence-sentinel'), ('gpu-claw','repository-sync')]
EXIT=1
```

Also measured via `proto_3711.py` section D, which regenerates purely from `git cat-file blob :<path>`:

```
[both] [D] index blobs read: 3 sources + inventory
[both] [D] identities regenerated from index == committed identities: True
[both] [D] machines   regenerated from index == committed machines:   True
[both] [D] regenerated row count: 73
```

**The prototype rejects the exact PR #3710 artifact from the exact host that produced it**, while the
shipped `_validate_inventory_digest` passes it (§5).

## 12. The enforcement checker runs on macOS — the #3709 caveat is stale

```
$ [mac] git --version
git version 2.55.0
$ [mac] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py ; echo $?
0
$ [ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py ; echo $?
0
```

#3709's issue body records that the checker "could not be executed on macOS (local git lacks
`cat-file --batch-command -Z`)". That is no longer true, and it matters because the guard this plan
proposes lives inside that checker.

## 13. Baseline test suites on `ace1` at `3fe934da9`

```
$ [ace1] uv run pytest tests/cron -q
FAILED tests/cron/test_cron_runtime.py::test_signal_keeps_lock_until_child_exits
1 failed, 283 passed in 312.30s

$ [ace1] uv run pytest scripts/cron/tests -q
FAILED scripts/cron/tests/test_validate_schedule.py::test_windows_tasks_have_windows_scheduler
1 failed, 65 passed in 273.25s

$ [ace1] uv run pytest tests/enforcement -q
FAILED tests/enforcement/test_check_skill_index_coherence.py::test_real_repo_passes
FAILED tests/enforcement/test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state
2 failed, 417 passed in 865.11s
```

**Recorded honestly: none of the three suites is fully green on `main`.**
Four tests already fail at `3fe934da9`, before any change from this plan:

| Failing test | Module it exercises | Touched by this plan? |
|---|---|---|
| `tests/cron/test_cron_runtime.py::test_signal_keeps_lock_until_child_exits` | `scripts/cron/cron_runtime.py` — signal/lock timing | No. The survey classifies `cron_runtime.py`'s `.resolve()` calls as not host-dependent in the #3711 sense; the file is not in the Files-to-Change table. |
| `scripts/cron/tests/test_validate_schedule.py::test_windows_tasks_have_windows_scheduler` | `config/scheduled-tasks/schedule-tasks.yaml` + `validate-schedule.py` — Windows scheduler routing | No. Windows rows are excluded from the inventory at `build-cron-identity-inventory.py:70`, and this plan changes neither the catalog nor `validate-schedule.py`. |
| `tests/enforcement/test_check_skill_index_coherence.py::test_real_repo_passes` | skill-index coherence | No. Unrelated to the scheduler-mutation contract. |
| `tests/enforcement/test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state` | soul auto-load drift | No. Unrelated to the scheduler-mutation contract. |

All four are named so a reviewer does not attribute them to the change. The plan's acceptance
criterion is therefore **"no new failures relative to this baseline"**, not "the suites pass". None
of the four was investigated further — that is outside #3711's scope, and none is claimed to be
understood here.

Important distinction: the **enforcement gate itself** — `check-scheduler-mutation-surfaces.py`, the
thing this plan proposes to extend — exits **0 on both hosts** (§12). The two `tests/enforcement`
failures are in unrelated modules (skill-index coherence, soul auto-load drift), not in the
scheduler-mutation contract.

## 14. What I could not verify

- **`gpu-claw` itself was never contacted.** Every claim about `/home/undi/ws/workspace-hub` is about
  the *declared* string in `registry.yaml` and how each host renders it. Whether that directory
  exists on the real `gpu-claw`, and whether its installed crontab matches the inventory, is
  untested here. This does not weaken the finding — the defect is precisely that a declared value is
  being resolved against the wrong machine — but the plan makes no claim about `gpu-claw`'s actual
  disk.
- **The proposed code was never written into either checkout.** Every "PROPOSED" measurement is a
  monkeypatch of `cron_render.workspace_hub_path` inside the prototype process. The behaviour is
  measured; the diff is not.
- **`_validate_inventory_contents` was prototyped standalone, not inside the checker.**
  `contents_check.py` reproduces the contract (index blobs → `build_from_documents` → compare) but
  does not exercise `validate_identity_inputs`' error plumbing or the checker's exit path.
- **CI was not exercised.** The claim "row 3 runs on Linux CI with no Mac" rests on the row being
  measured RED on `ace1`, not on a CI run.
- **Windows machines were not rendered.** `ace-win-1`/`ace-win-2` are excluded at
  `build-cron-identity-inventory.py:70`. The plan's R-2 risk about a Windows-shaped root on an
  `os: linux` row is reasoned, not measured.
