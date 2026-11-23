# Plan for #2618: pre-push config-drift check fails with `ModuleNotFoundError: yaml` under uv ephemeral env

> Status: draft (Team G)
> Complexity: T2
> Date: 2026-05-02
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2618
> Scope: hook-fix only; future-tense throughout

---

## 1. Resource Intelligence Summary

### 1.1 Reproduction confirmed in repo

- `.git/hooks/pre-push:132` invokes `uv run --no-project python "$CONFIG_DRIFT_SCRIPT"` for the harness-changed early path.
- `.git/hooks/pre-push:258` repeats the same invocation in the `RUN_ALL` post-loop path.
- `scripts/quality/check_config_drift.py:29` imports `yaml` at module top — the only non-stdlib dependency in that file (`yaml.safe_load`, `yaml.dump`, `yaml.YAMLError` used on lines 81, 84, 195, 196, 285).
- `pyproject.toml:17` declares `pyyaml>=6.0`. The dependency is resolvable via the workspace venv but `--no-project` deliberately bypasses it.

### 1.2 Full audit of `uv run --no-project python <script>` call sites (11 listed in issue)

| # | File:Line | Script invoked | Imports beyond stdlib? | Currently broken? |
|---|---|---|---|---|
| 1 | `.git/hooks/pre-push:132` | `scripts/quality/check_config_drift.py` | `yaml` (line 29) | YES |
| 2 | `.git/hooks/pre-push:203` | `scripts/testing/check_coverage_ratchet.py` | none (stdlib only: `argparse`, `json`, `os`, `sys`, `datetime`, `pathlib`) | no |
| 3 | `.git/hooks/pre-push:221` | `scripts/quality/check_mypy_ratchet.py` | none (stdlib only) | no |
| 4 | `.git/hooks/pre-push:239` | `scripts/quality/check_complexity_ratchet.py` | none (stdlib only) | no |
| 5 | `.git/hooks/pre-push:255` | (variable definition only — no invocation) | n/a | n/a |
| 6 | `.git/hooks/pre-push:258` | `scripts/quality/check_config_drift.py` (RUN_ALL path) | `yaml` | YES |
| 7 | `scripts/quality/check-all.sh:178` | inline `python -c "import sys,json; json.load(sys.stdin)"` | none | no |
| 8 | `scripts/quality/check-all.sh:189` | inline `python -c` JSON walk | none | no |
| 9 | `scripts/quality/check-all.sh:199` | inline `python -c` JSON count | none | no |
| 10 | `scripts/quality/check-all.sh:335` | inline `python -c` JSON length | none | no |
| 11 | `scripts/quality/check-all.sh:410` | `scripts/quality/api-audit.py` | none (`ast`, `json`, `sys`, `pathlib`) | no |
| 12 | `scripts/quality/check-all.sh:506` | `scripts/quality/check_doc_drift.py` | **`yaml` (line 25)** | **latent bomb** |
| 13 | `scripts/quality/check-all.sh:520` | `scripts/quality/check_mypy_ratchet.py` | none | no |
| 14 | `scripts/quality/check-all.sh:548` | `scripts/quality/check_config_drift.py` | **`yaml`** | **latent bomb** |
| 15 | `scripts/quality/check-all.sh:565` | `scripts/quality/check_complexity_ratchet.py` | none | no |
| 16 | `scripts/quality/check-all.sh:591` | `scripts/quality/quality_gap_report.py` | none (stdlib only) | no |

**Result:** 2 distinct python scripts (`check_config_drift.py`, `check_doc_drift.py`) hit the `--no-project` + `yaml` failure mode. They are referenced from 4 invocation sites total (hook ×2, check-all.sh ×2). All other 12 sites are stdlib-clean.

### 1.3 Hook source-of-truth defect (critical, surfaced by audit)

- `git ls-files | grep -E "hooks/pre-push"` shows **no tracked hook source**. `.git/hooks/pre-push` is the only copy.
- `scripts/enforcement/install-hooks.sh:73-178` only **appends** to an existing `.git/hooks/pre-push`; it never seeds the body that contains lines 132/203/221/239/258. The body (lines 1-267) was hand-crafted on this machine and is per-clone.
- Plan #2203 (`docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md:18`) explicitly documents this gap: tests at `tests/hooks/test_pre_push.py:22` reference `scripts/hooks/pre-push.sh` which **does not exist**.
- `tests/hooks/test_pre_push.py` is therefore red against the live hook on this machine and likely on every other developer machine.
- **Implication:** any "fix" applied only to `.git/hooks/pre-push` is per-clone and will not propagate to fresh worktrees, fresh clones, or other developers. The fix must include a tracked hook source.

### 1.4 `pyproject.toml` and `--no-project` rationale

- `pyproject.toml` declares `pyyaml>=6.0` as a base dependency (line 17). Removing `--no-project` (option c) would resolve yaml in the workspace-hub venv.
- However, `uv run` without `--no-project` will (a) trigger venv sync if `uv.lock` is stale, (b) install all base deps including `beautifulsoup4`, `pdfplumber`, `pillow`, `pytesseract` — heavy and slow on a fresh worktree, (c) fail outright if the worktree's `pyproject.toml` is malformed or its `uv.lock` is missing.
- The 11 `uv run --no-project` sites in the hook+check-all.sh plus the 30+ in `scripts/ai/`, `scripts/cron/`, `scripts/automation/` (verified via `grep -rn "no-project"`) form a **deliberate convention**: hot-path tools that must not pay the worktree-sync tax. This convention is the rationale behind `--no-project`. Option (c) breaks the convention for two scripts.

### 1.5 `tomllib` / stdlib feasibility for option (b)

- `check_config_drift.py` reads two YAML inputs (`load_baseline`, `_extract_frontmatter` body) and writes one YAML output (`yaml.dump` line 285).
- `tomllib` (stdlib, 3.11+) is read-only and TOML-only — not a drop-in for YAML. Replacing yaml requires (1) a stdlib YAML reader (none ships with CPython) or (2) a hand-rolled minimal parser, OR (3) switching the on-disk baseline + report formats from YAML to JSON / TOML.
- The baseline file is small flat list of `{repo, file, rule}`; the report is small dict of `{generated_at, summary, findings}`. Both are JSON-isomorphic.
- Option (b) is feasible but invasive: requires (i) format migration of `config/quality/config-drift-baseline.yaml` and any consumers, (ii) updating `_print_text` callers and tests, (iii) coordinating with `check_doc_drift.py` which has the same import.

---

## 2. Decision: Option (a) — `uv run --with pyyaml` — confirmed

Rationale (1-line each):

- **vs (b) stdlib swap:** disturbs an on-disk format consumed by 3 scripts, 1 baseline, 1 cron, 1 test suite — wide blast radius for what is fundamentally an environment hygiene bug.
- **vs (c) drop `--no-project`:** breaks the deliberate "hot-path no sync" convention used at 30+ sites; one stale `uv.lock` on a fresh worktree would fail the push more visibly than today.
- **vs (d) `uv tool install pyyaml`:** out-of-band per-machine state; cannot be verified from a tracked artifact; fails the same way on every new machine until manually run.
- **(a) `--with pyyaml` is:** declarative, in-tree, idempotent, machine-agnostic, costs ~1 s download on first run then cached, and matches uv's documented pattern for inline deps (`uv run --help` shows `--with` is the supported override).

---

## 3. Files to change

### 3.1 New tracked hook source (closes the #2203 gap)

- **CREATE** `scripts/hooks/pre-push.sh` — full body of `.git/hooks/pre-push` lines 1-267 lifted into a tracked file. This is the canonical source `tests/hooks/test_pre_push.py:22` already expects.
- **MODIFY** `scripts/enforcement/install-hooks.sh` — add a Step 0 that copies `scripts/hooks/pre-push.sh` to `.git/hooks/pre-push` (and `chmod +x`) before the existing append steps. Idempotent: only overwrite when content hash differs and the file lacks the appended-gate sentinel comments.

Rationale: without this, the "fix" is per-clone and the next fresh worktree will hit the same bug with the unfixed body.

### 3.2 Hook + check-all.sh edits (the actual yaml fix)

- **MODIFY** `scripts/hooks/pre-push.sh` (and via install-hooks, `.git/hooks/pre-push`):
  - Line 132: `uv run --no-project python` → `uv run --no-project --with pyyaml python` (config drift, harness-changed path)
  - Line 258: same change (config drift, RUN_ALL path)
  - Lines 203, 221, 239: leave as-is (stdlib-clean, verified §1.2)
- **MODIFY** `scripts/quality/check-all.sh`:
  - Line 506: `uv run --no-project python` → `uv run --no-project --with pyyaml python` (`check_doc_drift.py`)
  - Line 548: same change (`check_config_drift.py`)
  - Lines 178, 189, 199, 335, 410, 520, 565, 591: leave as-is (stdlib-clean)

### 3.3 No edits to python sources

`check_config_drift.py` and `check_doc_drift.py` continue to `import yaml`. The `--with pyyaml` declaration on the invocation side is the contract.

### 3.4 Documentation

- **MODIFY** `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` (or the equivalent `--no-verify` policy doc) to add a single line: "Scripts invoked via `uv run --no-project` MUST declare non-stdlib deps via `--with <pkg>`; CI/audit script TBD." This converts the rule from oral history to written policy.

### 3.5 Convention enforcement (level-2 script per `.claude/rules/patterns.md`)

- **CREATE** `scripts/enforcement/check-uv-no-project-deps.sh` — greps for `uv run --no-project [^|]*python\s+(\S+\.py|-c|-)` in `.git/hooks/`, `scripts/`, `.claude/`; for each invocation pointing at a `.py` file, reads the file's top-level imports; if any import is outside stdlib AND the invocation lacks a `--with <pkg>` clause for it, exit 1. Run from `.pre-commit-config.yaml` and from CI nightly.

Rationale: without this, the "latent bomb" in §1.2 will recur the next time someone adds an `import yaml` to a stdlib-only script.

---

## 4. TDD plan

### 4.1 Unit tests (run without push)

- **NEW** `tests/hooks/test_pre_push_uv_with_pyyaml.py`:
  - `test_config_drift_invocation_has_with_pyyaml`: regex-asserts that every `uv run --no-project ... check_config_drift.py` line in the tracked `scripts/hooks/pre-push.sh` and `.git/hooks/pre-push` contains `--with pyyaml`.
  - `test_no_yaml_imports_in_stdlib_only_invocations`: for every `uv run --no-project python <script.py>` site in the hook + `check-all.sh`, parse the target python file's top-level imports; assert that if `yaml` (or any non-stdlib name) appears, the invocation has `--with`.
- **NEW** `tests/enforcement/test_check_uv_no_project_deps.py`: drives the new enforcement script with both clean and dirty fixtures.

### 4.2 Integration test — hook-from-fresh-worktree, NO real push

The user already wired `PRE_PUSH_DRY_RUN=1` (hook line 83) — but that exits before the config drift block. We must add a more-targeted dry-run for the config-drift gate alone:

- **MODIFY** `scripts/hooks/pre-push.sh` — introduce `PRE_PUSH_CONFIG_DRIFT_DRY_RUN=1` env var that runs the existing `uv run --no-project --with pyyaml python "$CONFIG_DRIFT_SCRIPT" --help` (which exits 0 cleanly if pyyaml resolves). This exercises the uv invocation path without exercising the actual drift logic. Wire it before line 132 and before line 258.
- **NEW** `tests/hooks/test_pre_push_fresh_worktree.py`:
  - `test_config_drift_resolves_yaml_in_fresh_uv_cache`: creates an isolated `UV_CACHE_DIR=$(mktemp -d)`, runs `bash scripts/hooks/pre-push.sh` with `PRE_PUSH_CONFIG_DRIFT_DRY_RUN=1` and a synthetic `PRE_PUSH_CHANGED_FILES=CLAUDE.md`, asserts exit 0 and absence of `ModuleNotFoundError` in stderr.
  - This is the closest reproducible analogue to "fresh worktree" without running `git push` — uv's resolution of `pyyaml` from a cold cache is the single load-bearing behavior.

### 4.3 No-real-push acceptance check

The plan deliberately does NOT propose running `git push` from a worktree (instructed). The cold-cache integration test in §4.2 is the substitute.

---

## 5. Acceptance criteria

- [ ] `tests/hooks/test_pre_push_uv_with_pyyaml.py` passes — every yaml-importing script's invocation declares `--with pyyaml`.
- [ ] `tests/hooks/test_pre_push_fresh_worktree.py` passes with an empty `UV_CACHE_DIR`.
- [ ] `tests/hooks/test_pre_push.py` (existing) — restored to green by the new tracked source from §3.1, satisfying the #2203-known gap.
- [ ] `bash scripts/enforcement/install-hooks.sh --dry-run` reports no drift after install.
- [ ] `scripts/enforcement/check-uv-no-project-deps.sh` exits 0 on the post-fix tree.
- [ ] (User-validated, manual) `git push` from a `git worktree add /tmp/agent-wt-test` succeeds without `--no-verify`.

---

## 6. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `--with pyyaml` adds ~1 s first-push latency on a cold uv cache | Med | Acceptable; cache is per-user and persistent. Document in §3.4. |
| Lifting `.git/hooks/pre-push` body into `scripts/hooks/pre-push.sh` re-exposes intentional per-machine drift | Low | Diff against existing body before promoting; preserve the appended gates exactly; install-hooks already idempotent on those. |
| `install-hooks.sh` overwriting `.git/hooks/pre-push` clobbers user-local edits | Med | Only overwrite when the existing file lacks a `# managed-by: install-hooks` sentinel; otherwise WARN and exit 1. Add `--force` flag for migration. |
| Future stdlib-only script gains a non-stdlib import; latent bomb returns | High (historical) | §3.5 enforcement script catches this in pre-commit. |
| `uv` version older than the one supporting `--with` arg ordering | Low | `uv run --no-project --with pyyaml python …` is supported since uv 0.4 per uv docs; pin minimum uv version in `scripts/setup/install-uv.sh` if not already. |
| Hidden 17th call site outside `.git/hooks/` and `check-all.sh` | Med | The §3.5 enforcement script scans the entire tree, not just the two listed files. |

---

## 7. Roll-out

1. Land tracked hook source (§3.1) + install-hooks update + new enforcement script — single PR, T2.
2. After merge, every developer runs `bash scripts/enforcement/install-hooks.sh` once to seed `.git/hooks/pre-push` with the fixed body.
3. Document the seeding step in `README.md` "Local setup" or equivalent.

---

## 8. Out of scope

- Migrating `check_config_drift.py` off YAML (option b material).
- Auditing `scripts/ai/`, `scripts/cron/`, `scripts/automation/` `--no-project` sites — they are not in the issue's listed sites and are not on the push hot path. The §3.5 enforcement script will surface defects there once it lands.
- Closing #2203 (worktree-aware tier-1 gate) — distinct issue, distinct decision.
- Closing #2128 (install-hooks chain drift) — adjacent but distinct.
