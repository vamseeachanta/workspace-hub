# Plan: Issue #2606 — `uv sync` hangs at finalize step on Python 3.11 venv

**Tier:** T2 (single-repo, investigation-driven; root cause hypothesized but unconfirmed).
**Status:** plan-draft.
**Tense discipline:** future tense throughout — no shipped work.
**Author:** Team C (parallel planning agent, single-author).

---

## 1. Resource intel

### Repo state (read-only inspection on 2026-05-02)

- `digitalmodel/pyproject.toml`
  - `[build-system]`: `setuptools.build_meta`, `setuptools>=61.0`, `wheel`. Vanilla — no custom build hook.
  - `requires-python = ">=3.11"`, classifiers list 3.11/3.12.
  - `[tool.uv]` block (lines 341–346): `python = "3.11"`, `seed = true`, `compile = true`.
  - `[tool.uv.sources]`: `assetutilities = { path = "../assetutilities", editable = true }` — one editable workspace dep.
  - 100+ pinned deps including heavy native-extension packages: `scipy`, `pandas`, `numpy<2`, `pyvista`, `geopandas`, `pyarrow`, `lxml`, `h5py`, `cryptography`, `pillow`, `pygmt`, `meshio`, `argon2-cffi`, `cx-Oracle`, `pymssql`.
  - No `setup.py`, `setup.cfg`, or `MANIFEST.in` in repo (confirmed absent).
- `digitalmodel/uv.toml`
  - `compile-bytecode = true` (line 15) — duplicates `[tool.uv] compile = true`.
  - `link-mode = "copy"` (forces file copy not hardlink, slower I/O).
  - `concurrent-installs = 5`, `concurrent-builds = 5`.
- `digitalmodel/.python-version`: `3.11`.
- `digitalmodel/.venv/pyvenv.cfg`: uv-managed CPython 3.11.14, uv 0.10.0.
- `digitalmodel/.venv/bin/`: 164 entry points present; `__pycache__` count is ~32k files. Venv is materially populated.
- Local toolchain: `uv 0.10.0` at `/home/vamsee/.local/bin/uv`. Workspace default Python is 3.13 miniforge (no `python3.11` on PATH); uv resolves Python 3.11 via its managed install.

### Hypothesis ranking

| # | Hypothesis | Evidence for | Evidence against | Prior |
|---|---|---|---|---|
| H1 | **Bytecode compilation phase is the hang** | `compile-bytecode = true` AND `compile = true` (double-set); 100+ deps with heavy stdlib-style packages; "Uninstalled 44 packages" log followed by silence is the pattern uv emits *before* a long compile step; ~32k `.pyc` files present in venv. | Compile is normally CPU-bound and finishes; >60s on retry is unusual but not impossible for this dep count. | **High** |
| H2 | Editable install of `../assetutilities` hangs in setuptools build | Editable installs invoke build_meta in subprocess; if assetutilities's setup imports something that blocks (network, GUI, hardware probe), it would hang | assetutilities is in workspace and presumably builds fine in other repos; no custom build_meta override | Medium |
| H3 | Native-extension wheel build subprocess (cffi, argon2-cffi, lxml, h5py, pygmt, pyarrow) | argon2-cffi and pygmt have system-lib dependencies; if a wheel is missing for cpython 3.11.14 on this glibc, fallback to source build can stall on detect step | "venv populated" strongly suggests installs already finished; hang is post-install | Low-Medium |
| H4 | `seed = true` post-step (pip/setuptools/wheel into the venv) hanging | uv `seed = true` runs after main install | Seeding is fast and well-tested in uv 0.10 | Low |
| H5 | Filesystem sync / copy mode finalization (link-mode = "copy" on slow I/O) | `link-mode = "copy"` forces literal copies; on this NTFS-3g-via-FUSE? / overlay path, fsync at end could stall | Workspace at `/mnt/local-analysis` is normal ext4 per memory notes (not the NTFS Elements drive) | Low |
| H6 | uv 0.10.0 known regression on Python 3.11 finalize | Plausible — 0.10.0 is recent | Not verified; need to check uv changelog/issues | Unknown |

**Primary suspect: H1 (bytecode compilation).** The signature "log goes silent after Uninstalled N packages, parent never exits" matches uv's progress-bar-suppressed compile step for a large dep tree. Secondary suspect: H2 (editable assetutilities).

---

## 2. Investigation phase (do this BEFORE any fix)

Goal: confirm or eliminate H1–H6 with non-destructive observation. All commands below are read-only or use timeouts to avoid the hang reproducing indefinitely.

### Step 2.1 — Capture verbose output and process tree

Run from `digitalmodel/` directory in a fresh shell:

```bash
# Run uv sync with verbose flag, timeout, capture stdout+stderr
cd digitalmodel
timeout 120 uv sync -vv 2>&1 | tee /tmp/uv-sync-2606-vv.log
echo "exit=$?"
```

While running, in a second terminal:

```bash
# Capture process tree of uv (parent + children) every 2s
UVPID=$(pgrep -f 'uv sync' | head -1)
while kill -0 "$UVPID" 2>/dev/null; do
  ps -p "$UVPID" --ppid "$UVPID" -o pid,ppid,stat,wchan,comm,args >> /tmp/uv-2606-pstree.log
  pstree -p "$UVPID" >> /tmp/uv-2606-pstree.log
  echo "---" >> /tmp/uv-2606-pstree.log
  sleep 2
done
```

### Step 2.2 — strace the parent during the hang

If H1 (bytecode compile) is correct, strace will show repeated `openat()` + `write()` to `*.pyc` files. If H2/H3 (subprocess build), strace will show `wait4()` blocked on a child PID.

```bash
# Find PID of the hung uv sync
UVPID=$(pgrep -f 'uv sync' | head -1)
sudo strace -f -p "$UVPID" -e trace=openat,write,wait4,futex,clone -o /tmp/uv-2606-strace.log &
STRACE_PID=$!
sleep 15
kill "$STRACE_PID"
# Examine: tail -200 /tmp/uv-2606-strace.log | grep -E 'pyc|wait4|build'
```

### Step 2.3 — py-spy dump (if uv ships Python; uv is Rust so this won't apply directly, but child processes might be Python)

```bash
# Find any python child processes under uv sync
UVPID=$(pgrep -f 'uv sync' | head -1)
pgrep -P "$UVPID" -a
# For each python child, dump stack:
# pip install py-spy --user  # one-time
# py-spy dump --pid <child_pid>
```

### Step 2.4 — Test H1 directly: disable compile-bytecode

```bash
# Temporary: invoke uv sync with compile disabled via env override
cd digitalmodel
mv uv.toml uv.toml.bak
timeout 120 uv sync --no-compile-bytecode 2>&1 | tee /tmp/uv-sync-2606-nocompile.log
echo "exit=$?"
mv uv.toml.bak uv.toml
```

If `--no-compile-bytecode` exits cleanly and the previous run hung → **H1 confirmed**.

### Step 2.5 — Test H2: skip editable workspace dep

Inspect `../assetutilities/pyproject.toml` for any unusual `build_meta` hook. If suspicious, temporarily comment out the `[tool.uv.sources]` block and re-run with `--frozen` to skip resolution:

```bash
cd digitalmodel
timeout 120 uv sync --frozen 2>&1 | tee /tmp/uv-sync-2606-frozen.log
echo "exit=$?"
```

`--frozen` skips the lock-update step; if it also hangs, the issue is *not* lock-resolution but install/finalize.

### Step 2.6 — Test acceptance option (c): `--frozen` exits cleanly

Already covered in 2.5. If frozen exits cleanly, that's a usable workaround for the local-dev loop, but does not solve fresh-clone CI.

### Step 2.7 — Search uv issue tracker

Out-of-band: search https://github.com/astral-sh/uv/issues for `compile-bytecode hang`, `sync finalize hang`, `0.10.0 hang`. Note any open issue number in plan-update before deciding fix path.

---

## 3. Decision point (after investigation)

Branch on findings:

| Confirmed cause | Fix path | Files changed |
|---|---|---|
| **H1 (compile-bytecode)** | Either (a) flip `compile-bytecode = false` in `uv.toml` and `compile = false` in `pyproject.toml [tool.uv]`, accepting slower first-import; OR (b) leave default and document the wait time in `CONTRIBUTING.md` with expected duration. | `digitalmodel/uv.toml`, `digitalmodel/pyproject.toml`, `digitalmodel/CONTRIBUTING.md` (new) |
| **H2 (editable assetutilities)** | Investigate assetutilities `pyproject.toml` for blocking hook; fix there. Out of scope for this issue — file follow-up issue. | none in digitalmodel |
| **H3 (wheel build)** | Pin a problematic dep to a version with prebuilt wheel for cp311; document system-lib prereq. | `digitalmodel/pyproject.toml` |
| **H4/H5/H6 (other)** | Document workaround; file upstream uv issue with reproducer. | `digitalmodel/CONTRIBUTING.md` (new) |
| **Inconclusive** | Acceptance option (b) only: document workaround and Makefile target. | `digitalmodel/CONTRIBUTING.md` (new), `digitalmodel/Makefile` |

The plan honestly admits: **without running step 2, the fix path cannot be locked down**. This document is plan-only; the user must approve before any of step 2 or step 3 runs against the live tree.

---

## 4. Files to change (provisional, branch-dependent)

Most likely (assuming H1 confirms):

1. **`digitalmodel/uv.toml`** — flip `compile-bytecode = true` → `false` (or remove the line; default is `false`). One-line edit.
2. **`digitalmodel/pyproject.toml`** — remove `compile = true` from `[tool.uv]` block (line 346). One-line delete.
3. **`digitalmodel/CONTRIBUTING.md`** (new file, ~30 lines) — document:
   - `uv sync` may take 60–120s on first run after dependency change (bytecode compile is OFF by default; first-import is JIT-compiled).
   - If sync ever hangs >120s, kill PID, verify `.venv/bin/` is populated, file an issue.
   - Reference link to #2606 for the historical incident.
4. **`digitalmodel/Makefile`** — add a defensive target:
   ```make
   sync-with-timeout:
   	@timeout 180 uv sync || (echo "uv sync timed out after 180s; verify .venv/bin/ contents and report at #2606"; exit 0)
   ```
   This is the kill-after-N-seconds workaround if root cause cannot be eliminated.

If H1 does **not** confirm, this list collapses to just (3) — documented workaround only.

---

## 5. TDD strategy (honest about flake)

A hang-bug is hard to TDD because the failure mode is "process never exits" not "wrong output". Proposal:

- **Smoke-test wrapper** at `digitalmodel/scripts/test-uv-sync-exit.sh`:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  start=$(date +%s)
  timeout 120 uv sync || { echo "FAIL: uv sync did not exit in 120s"; exit 1; }
  elapsed=$(( $(date +%s) - start ))
  echo "uv sync exited in ${elapsed}s"
  test "$elapsed" -lt 120 || exit 1
  ```
- Run this once locally after fix; do **not** wire to CI initially because:
  - It's a costly smoke (downloads, compiles, ~60s minimum).
  - It's environment-sensitive (PyPI availability, disk speed).
  - False positives would burn CI budget.
- If sync stays clean for ~2 weeks (subjective tracking), promote the smoke to a manually-triggered GH workflow.

No pytest test added — testing the venv-creation tool from inside its own venv is circular.

---

## 6. Acceptance criteria (from issue #2606, refined)

- [ ] `cd digitalmodel && timeout 120 uv sync` returns exit code 0 within 120s on a clean venv.
- [ ] **OR** `digitalmodel/CONTRIBUTING.md` exists and contains a clear workaround section referencing #2606, with expected duration and kill-PID procedure.
- [ ] No regression to existing successful sync (i.e., flipping `compile-bytecode` does not break any downstream tooling — verified by running `digital_model --help` from the post-sync venv).

The "OR" branch is acceptable per the issue body's option (b).

---

## 7. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Investigation step 2 reproduces the hang and consumes 2+ minutes per attempt | Certain | Use `timeout 120`. Already accounted for. |
| Root cause inconclusive after step 2; no defensible code fix | Medium | Acceptance option (b) — document workaround. Issue body explicitly permits this. |
| Disabling `compile-bytecode` slows first-import for end users | Low (single-digit ms per module on modern hardware) | Document the tradeoff; first-import compile-on-demand is Python's default. |
| `compile-bytecode = false` triggers a *different* hang (bug elsewhere in uv finalize) | Low | Step 2.4 explicitly tests this; if it hangs too, H1 is wrong and we move to H2/H3. |
| `--frozen` workaround masks lock drift on CI | Medium | Only document `--frozen` for local dev loop, never for fresh-clone or CI. |
| User wants a real code fix, not a doc workaround | Unknown | Surface as open question pre-implementation (see §8). |

---

## 8. Open questions for user (block before implementation)

1. **Doc-workaround vs. code-fix preference?** Issue body lists both as acceptable. Confirm: if H1 confirms, do we flip `compile-bytecode` (small behavior change for all contributors, faster sync) or only document (zero behavior change, slower wait)?
2. **Permission to run step 2 (investigation) against live tree?** Step 2.4 will mutate `uv.toml` temporarily and run a real `uv sync`. Acceptable, or should investigation happen in a worktree?
3. **Out-of-scope: assetutilities editable build hooks.** If H2 confirms, the fix is in `../assetutilities`, not `digitalmodel`. Should that follow-up be filed as a new issue or rolled into #2606?

---

## 9. Out of scope for #2606

- Migrating digitalmodel to Python 3.13 (would test the implicit hypothesis that 3.11 is the trigger, but is a much larger change covered elsewhere).
- Restructuring the dependency list (the 100+ deps are a separate concern; #2606 is about install-tool exit behavior, not bloat).
- Changing build-backend away from setuptools.
- Adding the wrapper script to CI (deferred per §5).

---

## 10. Provenance

- Issue body: read on 2026-05-02 via `gh issue view 2606`.
- pyproject/uv.toml/.python-version: read on 2026-05-02.
- Venv inspection: 164 binaries, ~32k pyc files, uv 0.10.0, CPython 3.11.14.
- No `uv sync` was executed by this planning session (per coordinator instruction; PID 1741351 reproduced the hang earlier today and was killed manually).
