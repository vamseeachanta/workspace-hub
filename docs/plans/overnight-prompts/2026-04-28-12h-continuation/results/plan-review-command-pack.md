# Plan-review command pack — Lane C3 (ace-linux-1, 12h continuation)

> **Status:** drafts only. None of these commands have been executed by ace1 lane.
> **Companion artifact:** [`ace1-plan-review-hardener.md`](ace1-plan-review-hardener.md)
> **Mode:** planning/review only. Lane prompt rule 4: "draft command/comment pack rather than mutating".
> **Live state re-check before any execution:** every `gh issue view` MUST be re-run immediately before posting; states drift.

---

## Safety preamble

For any command in this pack:

1. Re-run `gh issue view <NNN> --json state,labels,updatedAt` and confirm: still OPEN, still carries the label set this comment assumes, no comment newer than 30 minutes that would invalidate this one.
2. Confirm the body file referenced (`/tmp/2NNN-body.md`) was authored by the operator who is about to post; do **not** post bodies authored in a different session without re-reading them.
3. **No** `gh issue edit ... --add-label` or `--remove-label` commands appear in this pack. Label moves are user-gated per lane prompt rule 1.
4. **No** force pushes, deletes, or destructive ops. All commands are read or comment-only.
5. Per `feedback_gh_issue_close_silent_comment_drop`: never combine `--comment` with a `gh issue close`; if the issue is CLOSED, posting a `gh issue comment` is the safer surface.

---

## Command 1 — #2510 — sustained-MAJOR governance escalation

### Body file: `/tmp/2510-body.md`

```markdown
## Plan-review hardening — 2026-04-28 ace-linux-1

After the r13 patch wave the plan is structurally complete but carries three substantive issues that should resolve **before** r14 is run, not after another review round:

### Hard blockers

1. **Duplicate r13 rows in Adversarial Review Summary.**
   Lines 321-326 of `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` list each r13 provider twice with internally inconsistent reasons (e.g. Claude r13 says "0-byte artifact" at line 321 and "CLI stalled" at line 324). Reviewers cannot tell which is authoritative.
   **Patch:** collapse to a single row per provider; keep the latest (line 324-326) framing.

2. **Per-layer round-trip count rule is adversarially defeatable.**
   Line 190 lets the implementer choose between exact-equality and "documented bounded range" by re-classifying a layer as fracturable. No rule fixes which layers are which, no rule caps the bounded range. A widening implementer can defeat the gate.
   **Patch:** enumerate `substrate`/`die`/`bump_array`/`route_keepout` and pin which use exact equality. For any bounded range, declare a hard cap (e.g., expected_count + 5%, no looser).

3. **Layer-key JSON encoding is non-deterministic.**
   Line 188 accepts both `{"layer": int, "datatype": int}` and string `L<L>_D<D>`. The metadata test only requires "deterministic keys" — does not pin one encoding.
   **Patch:** pin to integer-fields-only object, record in plan and test.

### Process blocker (per the plan's own §367 governance rule)

4. **Sustained-MAJOR loop violation.**
   The plan codifies (§367): "If the next wave returns only review-state/tooling MAJORs and no substantive CAD/test blockers, park the issue with a GitHub blocker/minority-report summary or ask the user whether to accept the residual risk; do not keep silently grinding through unlimited prose-only reviews."

   r12 and r13 returned predominantly state-sync/retrieval-defect MAJORs. r14 should be the **last** review wave before park-or-approve, and the pre-condition should be recorded in the plan **before** fanout — not retroactively after another MAJOR.

   **Patch:** add a "r14 termination clause" to the plan: if r14 returns only state-sync/retrieval defects (no substantive new CAD/test defect), this plan is auto-promoted to user-approval-pending regardless of MAJOR/MINOR verdicts.

### Recommended next step

Apply patches 1-3 inline + add the §4 termination clause. Then run r14 once. Do **not** queue r15.

Implementation remains blocked. Issue stays at `status:plan-review`. No label changes from this comment.
```

### Command (do not execute without re-verification)

```bash
gh issue comment 2510 --body-file /tmp/2510-body.md
```

**Pre-execution verify:** `gh issue view 2510 --json state,labels,updatedAt` shows `state=OPEN`, `status:plan-review` present, `updatedAt < 30min ago` is OK or unchanged.

---

## Command 2 — #2490 — three plan-content blockers + missing cross-review

### Body file: `/tmp/2490-body.md`

```markdown
## Plan-review hardening — 2026-04-28 ace-linux-1

The 2026-04-27 plan draft is correctly scoped as T1 single-line config but has three blockers before approval:

### Hard blockers

1. **Adversarial review skipped on T1 grounds (process violation).**
   Plan header line 7 says "N/A — T1, adversarial review deferred to user approval gate." Per `.claude/skills/coordination/issue-planning-mode/SKILL.md`, **all** issues require adversarial review before `status:plan-approved`. T1 does not waive the gate.
   **Patch:** run `scripts/review/plan-review-fanout.sh` against this plan before approval. If T1 makes a fanout overkill, document the explicit single-author review under the existing process rather than skipping.

2. **AC4 unverifiable as written.**
   Acceptance criterion line 216-217 ("≥1 success run") is gated on `actual_coverage ≥ 80%` (Risk 1 acknowledges this on line 229-235). The plan does not probe current coverage. If real coverage is in 60-80%, the fix turns `GateStatus.ERROR` into `WARNING`-escalated-to-`FAILURE`. Same red-build outcome.
   **Patch:** either (a) probe current coverage now (one command: `cd digitalmodel && uv run --with pytest-cov python -m pytest --cov=digitalmodel --cov-report=term -q tests/ 2>&1 | tail -5`) and record the value in the plan, OR (b) reword AC4 to "coverage gate is data-driven (PASS/WARN/FAIL), not ERROR" and split the green-build outcome into a follow-up issue.

3. **`--cov=src` may not match digitalmodel's importable package path.**
   Plan line 150 inserts `--cov=src --cov-report=json`. After `pip install -e .`, `sys.path` contains `digitalmodel/`, not `digitalmodel/src/`, so pytest-cov resolves `--cov=src` against import resolution, not the directory tree. The pyproject `[tool.coverage.run] source = ["src"]` works at the coverage-tool layer but not as the pytest-cov flag.
   **Patch:** change to `--cov=digitalmodel --cov-report=json` (importable package name) or omit `--cov=` and rely on pyproject `[tool.coverage.run] source`. Re-verify against `digitalmodel/pyproject.toml [tool.coverage.run]`.

### Soft drift (recommended cleanup)

4. **Plan header says `Status: draft` while GitHub label is `status:plan-review`.** Pick one — the live label is the authority.

5. **Cross-repo execution missing from Files-to-Change.** digitalmodel is a separate git submodule per `.claude/memory/context.md`. Plan does not call out: `cd digitalmodel && git checkout -b chore/coverage-gate-fix-2490 && git add .claude/quality-gates.yaml && git commit && git push origin chore/... && gh pr create -R vamseeachanta/digitalmodel ...`.

### Recommended next step

Patch 1-5 inline, then run cross-review fanout. T1 complexity argues for a single round, not r1-r13 cycling.

Issue stays at `status:plan-review`. No label changes from this comment.
```

### Command

```bash
gh issue comment 2490 --body-file /tmp/2490-body.md
```

---

## Command 3 — #2474 — F1-F3 patches before fanout

### Body file: `/tmp/2474-body.md`

```markdown
## Plan-review hardening — 2026-04-28 ace-linux-1

The 2026-04-26 draft (`docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md`) was reviewed by Claude r1 (verdict MAJOR, 8 findings). Three of those findings are real plan-content blockers and should be patched **before** the cross-review fanout (Codex/Gemini) is run — otherwise both Codex and Gemini will hit the same defects and the issue will repeat the #2510 review-loop pattern.

### Hard blockers (inherited from r1)

1. **F1 — Pseudocode contradicts `ModularModelGenerator` API.**
   Plan line 144 (`native_yaml = ModularModelGenerator(spec_in).generate(tmp_path)`) assumes a single YAML payload. Reality: `ModularModelGenerator.__init__` takes a `spec_file: Path`, not a `ProjectInputSpec`. `.generate(output_dir)` returns `None` and writes a directory: `output_dir/master.yml + includes/*.yml + inputs/parameters.yml`.
   **Patch:** rewrite TDD pseudocode to either (a) call `from_spec(spec_in)` then `.generate(tmp_path)` then walk the include chain via a new `parse_directory()` API, or (b) re-monolith via `format_converter/modular_to_single.py` then reverse-parse. Pick one and update Equivalence Criteria accordingly.

2. **F2 — Schema-version pinning tests nothing.**
   Plan line 121 (`SCHEMA_VERSION_PINNED = "..."  # from a known-good OrcaFlex YAML header`) and the corresponding `test_reverse_parser_raises_on_unknown_schema_version` rest on a key that does not exist in the in-scope artifact stream. The forward generator has no `OrcaFlexVersion` header — it's synthesized in-Python from `spec.yml`. There is nothing to drift.
   **Patch:** drop the schema-pinning test, OR scope it to native OrcaFlex exports (which are out of scope for this issue per the licensed-machine boundary).

3. **F3 — Round-trip is tautological.**
   This is the core defect. `ModularModelGenerator` writes only canonical-spec fields. `OrcaFlexInputParser` reads them back. Empty diff is guaranteed by closure — the round-trip proves serialization symmetry, not OrcaFlex semantic correctness. This is exactly what `single_to_spec.py`'s `actionable_gaps` was designed to prevent. Plan §257 dismisses `single_to_spec.py` as "best-effort" but the new parser does not actually escape the same closure.
   **Patch:** add a **mandatory** real-export negative test: feed `OrcaFlexInputParser` a real OrcaFlex `single.yml` (one of the existing samples in `digitalmodel/docs/domains/orcaflex/library/`) and assert the parser produces a non-empty `unmapped_native_keys` set. Add explicit AC: at least one fixture in the test suite must be an OrcaFlex-export-style single.yml NOT generated by `ModularModelGenerator`.

### Soft cleanup (r1 F4-F8)

4. F4 — fix Artifact Map line 88 self-reference filename (`-proof.md` → no suffix; actual file is `2026-04-26-issue-2474-orcaflex-reverse-parser.md`).
5. F5 — reword "(#520)" reference as "digitalmodel issue #520 (commit `63c1cbdd`)".
6. F6 — add taxonomy enum + `len(reason) >= 30` + CODEOWNERS gate to ignored-fields registry.
7. F7 — raise float `atol` from `0` to `1e-12`; add UTF-8 BOM and CRLF tests.
8. F8 — multi-body decision: include one fixture or explicitly defer.

### Recommended next step

Apply patches 1-8 inline. Then run `scripts/review/plan-review-fanout.sh` for r2 (Claude/Codex/Gemini). Then label `status:plan-review`. Order matters: patch first, then fanout, then label.

Issue stays unlabeled (no `status:plan-review` yet). No label changes from this comment.
```

### Command

```bash
gh issue comment 2474 --body-file /tmp/2474-body.md
```

---

## Command 4 — #2454 — recovery-required notice (plan stranded on local branch)

### Body file: `/tmp/2454-body.md`

```markdown
## Plan-review hardening — 2026-04-28 ace-linux-1

Critical state finding: the 2026-04-23 plan (`docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md`, commit `13e7ecc56`) was committed to local branch `nightly/2454-2457-planwave` but **never pushed**. `git branch --remote` shows no `nightly/2454-2457-planwave` ref. The plan is invisible to GitHub reviewers, Codex MCP, and any operator who didn't hand-checkout that branch.

The 2026-04-23 worker-1 comment notes the push was blocked by the workspace pre-push hook (`yaml` ModuleNotFoundError in `scripts/quality/check_config_drift.py`), and asked for sanctioned-bypass approval that did not return.

### Recovery options

| Option | Steps | Trade-off |
|---|---|---|
| **A: Sanctioned-bypass push** | `GIT_PRE_PUSH_SKIP=1 git push origin nightly/2454-2457-planwave` per `.claude/skills/workspace-hub/worktree-pre-push-bypass-for-tier1-checks/SKILL.md` | Requires user authorization for the env var. |
| **B: Cherry-pick to fresh branch** | `git checkout main && git pull && git cherry-pick 13e7ecc56` | Cleanest; avoids the original push-block. May lose iter-1/iter-2 review-artifact context if those commits aren't picked. |
| **C: Rebase + push** | Fix the `yaml` ModuleNotFoundError in `scripts/quality/check_config_drift.py` (likely needs `uv run` wrapper), then push. | Cleanest long-run; addresses pre-push-hook root cause. |

Recommended: **Option B** (cherry-pick) — fewest unknowns.

### Plan-content blockers (iter-2 MAJOR, still open)

After recovery, three iter-2 MAJORs remain unpatched:

1. Replace `compare()` with `validate(mono, mod) -> list[SectionResult]`, wrap in `ValidationResult` before `to_json()`.
2. Rewrite three test assertions to traverse `sec["diffs"]`, `sec["objects"][*]["diffs"]`, AND `sec["categories"][*]["diffs"]`. List/nested sections were missed.
3. Replace `GroupsBuilder(spec).should_generate()` with `spec.metadata.structure == "generic"` inline check (constructor needs two positional args).

Plus normalize frozen-diff JSON (strip timestamp + absolute paths) for equality.

### Recommended next step

dev-primary takes a focused 2h block: cherry-pick to fresh branch + apply iter-3 patches inline + run a fresh single-author r3 review. Do not attempt cross-review fanout until plan is pushed and visible to Codex (per `feedback_codex_needs_pushed_artifact`).

Issue stays unlabeled. No label changes from this comment.
```

### Command

```bash
gh issue comment 2454 --body-file /tmp/2454-body.md
```

---

## Command 5 — #2509 — surface user-decisions blocking fanout

### Body file: `/tmp/2509-body.md`

```markdown
## Plan-review hardening — 2026-04-28 ace-linux-1

A draft plan exists at `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` (status `draft`, T3, wave-2 overnight) but has not been adversarially reviewed and was never commented on this issue.

### Verified critical state at planning time

Local host has **zero EDA tools** — `which` probes confirmed: docker, podman, openlane, openroad, yosys, iverilog, magic, netgen all MISSING. The plan correctly pivots to documentation-first replay design that exits 0 when tools absent, anchored on issue AC1 ("replay committed sample artifacts") allowance.

Sibling chain:
- #2508 — CLOSED — KB + job-skill matrix
- #2511 — CLOSED — establishes `scripts/semiconductor/`, `tests/semiconductor/`, `data/semiconductor/<feature>/` layout this plan adopts
- #2510 — `status:plan-review` (in r13 cycling)

### Pre-review user-decision blockers

Two decisions block fanout and should be resolved before this plan can be reviewed:

1. **Execution order:** defer to KB-recommended order #2508 → #2511 → #2510 → #2509 → #2512?
2. **Binary-artifact commit policy:** `.gds`/`.def` outputs at <2.5MB committed inline, vs. Git LFS, vs. external-download-with-hash?

### Recommended next step

User resolves decisions (1) and (2) → patch plan accordingly → run `scripts/review/plan-review-fanout.sh` → label `status:plan-review`.

Implementation blocked. No label changes from this comment.
```

### Command

```bash
gh issue comment 2509 --body-file /tmp/2509-body.md
```

---

## Commands 6, 7, 8 — #2473, #2472, #2516 plan-skeleton seeds

These three issues lack any plan on disk. The body files below seed an inline plan skeleton but stop short of committing one — the lane is planning-only, and this is intake refinement, not approval-track plan authoring.

### Body file: `/tmp/2473-body.md`

See [`ace1-plan-review-hardener.md` §5.2](ace1-plan-review-hardener.md) for the full skeleton — reproduce verbatim into the body file.

```bash
gh issue comment 2473 --body-file /tmp/2473-body.md
```

### Body file: `/tmp/2472-body.md`

See [`ace1-plan-review-hardener.md` §5.3](ace1-plan-review-hardener.md) — reproduce verbatim.

```bash
gh issue comment 2472 --body-file /tmp/2472-body.md
```

### Body file: `/tmp/2516-body.md`

See [`ace1-plan-review-hardener.md` §5.4](ace1-plan-review-hardener.md) — reproduce verbatim.
Add explicit dependency callout: this issue is **parent-blocked** by #2513.

```bash
gh issue comment 2516 --body-file /tmp/2516-body.md
```

---

## Command 9 — #2513 — plan-skeleton seed

### Body file: `/tmp/2513-body.md`

See [`ace1-plan-review-hardener.md` §5.5](ace1-plan-review-hardener.md) — reproduce verbatim.
Add: this catalogue is the prerequisite for #2516's flexible-pipe mechanics work.

```bash
gh issue comment 2513 --body-file /tmp/2513-body.md
```

---

## Command 10 — #2507 — umbrella status note (NO MUTATION RECOMMENDED)

#2507 is the umbrella issue for the semiconductor career lane. A draft umbrella plan already exists at `docs/plans/2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md` per `docs/plans/README.md` row 342, and the original 2026-04-26 comment from the issue author already lists the child tree.

**No comment recommended.** The next time #2507 needs a status update is when one of the children (#2508/#2509/#2510/#2511/#2512) ships or fails. Until then, the umbrella issue is correctly tracking via labels and the existing comment.

---

## Pre-execution checklist (run before posting any of the above)

```bash
# 1. Re-check live state for every focus issue
for n in 2510 2490 2509 2474 2473 2472 2516 2513 2454; do
  gh issue view $n --json number,state,labels,updatedAt | jq -c '{n:.number,s:.state,u:.updatedAt,l:[.labels[].name]}'
done

# 2. Confirm no parallel session has already commented in the last 30 min
for n in 2510 2490 2509 2474 2473 2472 2516 2513 2454; do
  gh issue view $n --json comments | jq --arg n "$n" -r '[.comments[].createdAt]|max|"#\($n): latest=\(. // "none")"'
done

# 3. Confirm none of the body files are stale (re-author within current session if older than 1h)
ls -lt /tmp/2*-body.md 2>/dev/null

# 4. If anything looks wrong → DO NOT POST. Update the body file or skip the issue.
```

---

## End-of-pack notes

- All 10 commands are drafted. **None executed by ace1 lane.**
- Lane prompt rule 4 obeyed: "draft command/comment pack rather than mutating".
- Lane prompt rule 1 obeyed: no implementation/code changes for unapproved issues.
- Lane prompt: no force push, hard reset, secret handling, or destructive cleanup.
- Per `feedback_inline_gh_issue_url`: when posting in chat (e.g. handoff summary), render bare issue tokens as Markdown hyperlinks (`#2510` → `[#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510)`). Inside the comment bodies above, GitHub renders `#2510` natively, so bare tokens are correct in body files.

Operator: review each body file by reading it back from `/tmp/` before posting. Re-run the live state probe in §"Pre-execution checklist". Post one comment at a time and verify each one rendered correctly (`gh issue view <N> --json comments | jq '.comments[-1].body[0:200]'`) before moving to the next.
