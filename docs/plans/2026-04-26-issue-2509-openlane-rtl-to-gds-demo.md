# Plan for #2509: feat(eda): create reproducible OpenLane/OpenROAD RTL-to-GDS demo report

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2509
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2509-claude.md | scripts/review/results/2026-04-26-plan-2509-codex.md | scripts/review/results/2026-04-26-plan-2509-gemini.md (to be produced by adversarial wave)

---

## Resource Intelligence Summary

### Existing repo code

- No existing OpenLane / OpenROAD / Sky130 / GF180 / RTL-to-GDS code or scripts will be found in the repo. `git ls-files | grep -iE 'openlane|openroad|sky130|gf180|rtl'` returns only false positives (`scripts/cron/redact-session-signals.sh`, marine-engineering wiki sources containing the substring `eda`/`ikeda`). No `scripts/semiconductor/` directory exists yet.
- `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` (created by closed sibling #2508) explicitly anchors `#2509` to the `asic-eda-technical-program-role` and `physical-design-eda-flow-learner-track` role families with tools `OpenROAD`, `OpenLane`, `OpenROAD-flow-scripts`, `Yosys`, `Magic`, `KLayout`, `SkyWater SKY130`, `GF180MCU`. This plan must remain consistent with that taxonomy.
- `docs/reports/semiconductor-cad-fem-knowledge-base.md` (created by closed sibling #2508) recommends at line 75 that "the EDA flow lane should focus on literacy and reproducibility: run a tiny open design through an open flow, preserve commands/logs/metrics, and explain each stage" and at line 117 explicitly cautions "do not scope-creep into full ASIC design: keep #2509 educational and evidence-focused." This plan adopts that posture.
- `tests/docs/test_semiconductor_kb.py` already validates the parent taxonomy / KB report from #2508; this plan adds new tests under `tests/semiconductor/` (sibling pattern from in-flight #2511 plan) without modifying existing tests.

### Standards and source limits

| Source / standard family | Status | Finding |
|---|---|---|
| `data/document-index/standards-transfer-ledger.yaml` | exists | `grep -iE 'openroad\|openlane\|sky130\|gf180\|JEDEC\|IPC'` returns no matches; no semiconductor EDA standards are locally ingested. |
| `data/document-index/online-resource-registry.yaml` | exists | `grep -iE 'openroad\|openlane\|sky130\|gf180\|RTL'` returns no matches; this plan's report will cite open-tool URLs directly and note them as taxonomy follow-ups, not as registered resources. |
| `data/design-codes/code-registry.yaml` | exists | Canonical design-code registry (per `docs/document-intelligence/data-intelligence-map.md`); contains no semiconductor / EDA entries. No standards-derived numeric constants are introduced by this plan, so the calc-citation contract (`.claude/rules/calc-citation-contract.md`) does not require Citation emission. |
| JEDEC / IPC | restricted; not locally ingested | #2508 KB §"JEDEC/IPC access limitations" forbids compliance claims. This plan references neither. |
| Open PDK design-rule decks (Sky130, GF180MCU) | external; consumed via OpenLane container artifacts only | This plan does not redistribute PDK files; it documents which PDK the demo targets and references upstream URLs. |

### LLM wiki / knowledge pages consulted

- `knowledge/wikis/` search for `OpenROAD|OpenLane|Sky130|GF180|RTL-to-GDS|VLSI` returns no matches. Consistent with #2508 finding that the semiconductor lane is the first-of-its-kind in this repo. No wiki edits planned.

### Documents consulted

- Issue #2509 body — defines deliverables: container/environment instructions, source design and flow config, generated report and artifact inventory, smoke checks; acceptance criteria explicitly permits "clearly replay committed sample artifacts" if a fresh checkout cannot run the full flow.
- Parent issue #2507 — open umbrella; this plan must respect lane execution order.
- Sibling closed #2508 — knowledge base + taxonomy already exist; this plan reuses them as authoritative anchors and does not duplicate them.
- Sibling open #2510 — Python layout / CAD automation demo (KLayout / GDSFactory). #2509 must not depend on #2510 implementation; both can ship independently against the same KB.
- Sibling open #2511 — package FEM benchmark plan in `docs/plans/2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md`; this plan adopts its established conventions for `scripts/semiconductor/`, `tests/semiconductor/`, and `data/semiconductor/<feature>/`.
- `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` — Wave 2 anchors this exact deliverable: "containerized OpenLane/OpenROAD flow; tiny reference design (counter/FIFO/simple ALU); PDK target Sky130 or GF180MCU; captured reports timing/area/power/DRC/LVS; HTML report".
- External tool docs (status confirmed in #2508 plan, 2026-04-26): OpenROAD docs, OpenROAD-flow-scripts, OpenLane docs, GF180MCU PDK docs all returned HTTP 200; SkyWater PDK GitHub repo accessible. No fresh probe in this session — relying on #2508's evidence record.

### Environment findings (must shape the plan)

- `which docker podman openlane openroad yosys iverilog magic netgen nix-shell` → ALL MISSING on the planning host. Verified 2026-04-26 in this session.
- Implication: the plan must NOT require live container execution as a hard acceptance criterion. Acceptance criterion 1 in the issue explicitly allows "clearly replay committed sample artifacts" as a substitute. The plan therefore commits a small set of representative artifacts produced by an upstream OpenLane CI run (or from the OpenLane example/regression suite) and validates the report and artifact inventory against those committed samples.
- Python tooling available: `uv 0.10.0`, Python 3.13.12 system, Python 3.11.14 in `uv run`. PyYAML present (used by sibling tests). No EDA-specific Python packages required for the smoke tests this plan adds.

### Gaps identified

- No `scripts/semiconductor/` directory; this plan creates the OpenLane/OpenROAD runner + report-generator scripts there.
- No committed RTL source for a tiny educational design (counter / FIFO / simple ALU) anywhere in the repo.
- No committed OpenLane / Sky130 flow configuration anywhere in the repo.
- No committed sample-artifact set (DEF, GDS, timing/area/power/DRC/LVS logs) for any open-PDK design.
- No Markdown / HTML report mapping the artifacts to semiconductor job keywords.
- No tests covering script invocation, artifact-inventory completeness, report claim guardrails (must not claim tapeout / production / JEDEC / IPC compliance), or RTL design-vs-config consistency.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view --json state,title`):
- `#2507` — OPEN — Feature: semiconductor chip-design CAD/FEM career lane
- `#2508` — CLOSED — research(semiconductor): build chip-design CAD/FEM knowledge base and job taxonomy
- `#2509` — OPEN — feat(eda): create reproducible OpenLane/OpenROAD RTL-to-GDS demo report
- `#2510` — OPEN — feat(cad): build Python layout/CAD automation demo for chip/package geometries
- `#2511` — OPEN — feat(fem): create semiconductor package thermal/thermo-mechanical benchmark

**File existence** (verified 2026-04-26 via `ls` / `git ls-files`):
- EXISTS: `docs/roadmaps/chip-design-cad-fem-career-roadmap.md`
- EXISTS: `docs/reports/semiconductor-cad-fem-knowledge-base.md` (133 lines)
- EXISTS: `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml`
- EXISTS: `tests/docs/test_semiconductor_kb.py`
- EXISTS: `docs/plans/2026-04-26-issue-2508-semiconductor-cad-fem-knowledge-base.md`
- EXISTS: `docs/plans/2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md`
- EXISTS: `scripts/review/plan-review-fanout.sh`
- EXISTS: `data/document-index/online-resource-registry.yaml`
- EXISTS: `data/design-codes/code-registry.yaml`
- MISSING (new): `scripts/semiconductor/` (whole directory)
- MISSING (new): `scripts/semiconductor/openlane_demo_runner.sh`
- MISSING (new): `scripts/semiconductor/openlane_demo_report.py`
- MISSING (new): `data/semiconductor/openlane_demo/` (whole directory)
- MISSING (new): `data/semiconductor/openlane_demo/rtl/counter.v`
- MISSING (new): `data/semiconductor/openlane_demo/config.json` (or `.tcl`)
- MISSING (new): `data/semiconductor/openlane_demo/sample_artifacts/` (replay set)
- MISSING (new): `data/semiconductor/openlane_demo/sample_artifacts/MANIFEST.yaml`
- MISSING (new): `tests/semiconductor/test_openlane_demo.py`
- MISSING (new): `docs/reports/semiconductor-openlane-rtl-to-gds-demo.md`

**Tool availability** (verified 2026-04-26 via `which`):
- MISSING: docker, podman, openlane, openroad, yosys, iverilog, magic, netgen, nix-shell
- PRESENT: uv 0.10.0, python3 3.13.12, python (uv-managed) 3.11.14

**Sibling state** (verified 2026-04-26 via `ls .planning/plan-approved/`):
- `2508.md` PRESENT (sibling closed)
- `2511.md` PRESENT (sibling plan-approved)
- `2509.md` ABSENT (this plan is the first artifact for #2509)

**No prior `#2509` review artifacts** (verified 2026-04-26 via `ls scripts/review/results/ | grep 2509`): empty.

**No prior `#2509` issue comments** (verified 2026-04-26 via `gh api repos/vamseeachanta/workspace-hub/issues/2509/comments`): empty.

Source count for retrieval contract: issue body (1) + parent #2507 (2) + sibling #2508 plan + KB report (3) + roadmap (4) + sibling #2511 plan (5) + standards/registry checks (6). ≥3 satisfied.

---

## Verification Log

Each load-bearing claim in this plan and how it was verified during planning. Items marked [UNVERIFIED] could not be confirmed and must be revisited before adversarial review or implementation.

| Claim | Verification command | Result |
|---|---|---|
| Issue #2509 is OPEN with the stated title | `gh issue view 2509 --json state,title,number,labels` | OPEN, exact title match, labels include `cat:engineering`, `cat:research`, `cat:tooling`, `domain:chip-design`, `domain:semiconductor`, `priority:high` |
| Parent #2507 is OPEN | `gh issue view 2507` | OPEN, "Feature: semiconductor chip-design CAD/FEM career lane" |
| Sibling #2508 is CLOSED | `gh issue view 2508 --json state` | CLOSED |
| Sibling #2510, #2511 are OPEN | `gh issue view 2510 --json state` / `gh issue view 2511 --json state` | OPEN / OPEN |
| Roadmap file exists at the cited path | `ls docs/roadmaps/chip-design-cad-fem-career-roadmap.md` | EXISTS |
| KB report explicitly anchors #2509 with "literacy and reproducibility" framing | `grep -nE "2509\|openlane\|openroad" docs/reports/semiconductor-cad-fem-knowledge-base.md` | Lines 4, 17, 29, 30, 53, 54, 75, 77, 99, 101, 103, 112, 117, 133 confirm anchoring |
| Taxonomy YAML maps `#2509` to `asic-eda-technical-program-role` and `physical-design-eda-flow-learner-track` | `grep -nE "2509" data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` | Lines 45, 46, 56 confirm |
| Sibling test file exists with established structure | `ls tests/docs/test_semiconductor_kb.py` then read top 60 lines | EXISTS, uses `Path(__file__).resolve().parents[2]` repo-root pattern, PyYAML, regex guardrails |
| Sibling #2511 plan establishes `scripts/semiconductor/`, `tests/semiconductor/`, `data/semiconductor/<feature>/` convention | Read `docs/plans/2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md` lines 70-80 | Confirmed convention |
| Sibling #2508 plan documents external EDA tool docs reachability | Read sibling plan file lines 95-100 | OpenROAD/OpenROAD-flow-scripts/OpenLane/KLayout/GDSFactory all returned HTTP 200 on 2026-04-26 |
| No existing OpenLane / OpenROAD code in repo | `git ls-files \| grep -iE 'openlane\|openroad\|sky130\|gf180'` | No matches outside marine-engineering false positives (`ikeda`, `waseda`) |
| No existing semiconductor scripts directory | `ls scripts/semiconductor/` | "No such file or directory" |
| Online-resource-registry has no OpenROAD/OpenLane entries yet | `grep -nE "openroad\|openlane\|sky130\|gf180\|RTL" data/document-index/online-resource-registry.yaml` | empty |
| Standards-transfer-ledger has no JEDEC/IPC/EDA entries | `grep -nE "openroad\|openlane\|sky130\|gf180\|JEDEC\|IPC" data/document-index/standards-transfer-ledger.yaml` | empty |
| Calc-citation contract not triggered (no standards-derived numeric constants introduced) | Read `.claude/rules/calc-citation-contract.md` | Demo replays vendor logs and reports them; no calc module emits a standards-derived constant. Contract's "Do NOT apply when" clause covers this case. |
| Plan-review fanout script exists | `ls scripts/review/plan-review-fanout.sh` | EXISTS |
| Plan-approved marker for #2509 does not yet exist | `ls .planning/plan-approved/2509.md` | "No such file or directory" (correct — plan is draft) |
| No prior 2509 review artifacts | `ls scripts/review/results/ \| grep 2509` | empty |
| No prior comments on issue #2509 | `gh api repos/vamseeachanta/workspace-hub/issues/2509/comments --jq '.[].body'` | empty |
| Local environment lacks all relevant EDA tools | `for c in docker podman openlane openroad yosys iverilog magic netgen nix-shell; do which $c; done` | ALL MISSING |
| `uv` available, Python 3.11 in `uv run` | `uv --version` ; `uv run python -c "import sys; print(sys.version)"` | uv 0.10.0; Python 3.11.14 |
| `.gitignore` does not exclude `data/semiconductor/` or `docs/reports/` | `grep -n "data/semiconductor\|docs/reports" .gitignore` | no matching lines (not gitignored) |
| `specs/` is gitignored — do NOT write spec there | `grep -n "specs/" .gitignore` | line 438 confirms |
| Final artifact filename matches this plan's slug placeholder | grep this plan body for the filename: search target = `2026-04-26-issue-2509-openlane-rtl-to-gds-demo` placeholder | Per Wave-1 lesson: any self-reference uses the placeholder `2026-04-26-issue-2509-openlane-rtl-to-gds-demo`; the final committed slug will be set by the user/agent at serialization time and must match `docs/plans/YYYY-MM-DD-issue-2509-2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md`. This plan's working filename is `issue-2509-plan.md` per the dispatch contract. |

[UNVERIFIED] OpenLane upstream regression-suite license / redistribution rules for committed sample artifacts — needs an `LICENSE` check on whichever upstream OpenLane release the sample artifacts are pulled from before commit. Tracked in Risks.

[UNVERIFIED] Whether the OpenLane CI artifact set for the chosen reference design (counter or simple ALU) is small enough to commit (target: <2 MB combined). Will be confirmed during implementation by running `du -sh` on the staged sample-artifacts directory before commit. Tracked in Risks.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2509-2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` (working filename: `issue-2509-plan.md` during overnight wave) |
| RTL source (tiny reference design) | `data/semiconductor/openlane_demo/rtl/counter.v` |
| Flow config (OpenLane JSON or TCL) | `data/semiconductor/openlane_demo/config.json` |
| README explaining the demo | `data/semiconductor/openlane_demo/README.md` |
| Sample-artifacts replay set | `data/semiconductor/openlane_demo/sample_artifacts/` |
| Sample-artifacts manifest (machine-readable inventory) | `data/semiconductor/openlane_demo/sample_artifacts/MANIFEST.yaml` |
| Demo runner script (live path; container-gated) | `scripts/semiconductor/openlane_demo_runner.sh` |
| Report generator (replay-set parser) | `scripts/semiconductor/openlane_demo_report.py` |
| Generated demo report | `docs/reports/semiconductor-openlane-rtl-to-gds-demo.md` |
| Tests | `tests/semiconductor/test_openlane_demo.py` |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2509-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2509-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2509-gemini.md` |
| Index update | `docs/plans/README.md` (new row for #2509) |

---

## Deliverable

A reproducible OpenLane/OpenROAD RTL-to-GDS educational demo for a tiny open RTL design (counter as primary; simple ALU as alternate) targeting the Sky130 open PDK, comprising: committed RTL source, committed flow configuration, a committed replay set of representative flow artifacts (synthesis log, timing summary, area/power summary, DRC/LVS status, DEF, GDS, KLayout-renderable PNG/SVG of the final layout), a runner script that documents container invocation for live execution, a report generator that produces a Markdown report mapping each artifact to semiconductor job keywords, and a TDD-validated artifact inventory.

---

## Pseudocode

### `scripts/semiconductor/openlane_demo_report.py`

```
function main():
    parse_args: --replay-dir (default data/semiconductor/openlane_demo/sample_artifacts/),
                --out (default docs/reports/semiconductor-openlane-rtl-to-gds-demo.md)
    manifest = load_yaml(replay_dir / "MANIFEST.yaml")
    validate_manifest_schema(manifest)         # required keys: design, pdk, flow_version, artifacts[]
    artifact_table = []
    for entry in manifest.artifacts:
        path = replay_dir / entry.path
        assert path.exists(), f"manifest references missing artifact: {entry.path}"
        artifact_table.append({
            kind: entry.kind,                  # synthesis_log | timing_summary | area_power | drc | lvs | def | gds | layout_png
            path: relative_to_repo(path),
            size_bytes: path.stat().st_size,
            sha256: sha256_of_file(path),
            job_keywords: entry.job_keywords,  # mapped from taxonomy YAML
            stage_explanation: entry.stage_explanation,
        })
    metrics = parse_metrics(manifest, replay_dir)
        # extracts numeric fields from synthesis/timing/area logs into a small dict;
        # fail-soft: missing fields recorded as "not parsed" rather than raising.
    render_markdown_report(out_path, manifest, artifact_table, metrics)
        # sections: Overview, How to reproduce live, Replay-set inventory,
        # Stage-by-stage explanation, Metrics summary, Job-keyword crosswalk, Limitations
    return 0

function validate_manifest_schema(manifest):
    require manifest["design"] in {"counter", "simple_alu"}
    require manifest["pdk"]    in {"sky130A", "sky130B", "gf180mcuD"}
    require manifest["flow"]   in {"openlane", "openroad-flow-scripts"}
    require manifest["flow_version"] is non-empty string
    require manifest["artifacts"] is non-empty list
    for entry in manifest["artifacts"]:
        require entry.kind in ALLOWED_KINDS
        require entry.path is relative and does not contain ".."
        require entry.job_keywords is list of taxonomy-known strings
```

### `scripts/semiconductor/openlane_demo_runner.sh`

```
# DOCUMENTATION-FIRST runner:
# - Detects whether docker / podman / nix-shell are available locally.
# - If yes, prints (and optionally executes) the canonical OpenLane invocation:
#       docker run --rm -v "$(pwd)/data/semiconductor/openlane_demo:/openlane/designs/counter" \
#         efabless/openlane:<pinned-tag> flow.tcl -design counter -tag <user-tag>
# - If no, prints a clear "container runtime not available — see report's Replay-set
#   section to inspect committed sample artifacts" message and exits 0.
# - Exit code is 0 in both branches: the script's job is to document, not to gate CI.
# - A separate --check flag prints tool versions without executing flow.
```

### `tests/semiconductor/test_openlane_demo.py`

```
test_manifest_schema_valid:
    load MANIFEST.yaml; assert required keys; assert design/pdk/flow allowed values

test_all_manifest_artifacts_exist_on_disk:
    for entry in manifest.artifacts: assert (replay_dir / entry.path).exists()

test_artifact_kinds_cover_required_stages:
    kinds = {entry.kind for entry in manifest.artifacts}
    required = {"synthesis_log", "timing_summary", "area_power", "drc", "lvs", "def", "gds"}
    assert required.issubset(kinds)

test_report_generator_produces_expected_sections:
    run report generator into a tmp path
    assert each required H2 heading present:
      "Overview", "How to reproduce live", "Replay-set inventory",
      "Stage-by-stage explanation", "Metrics summary", "Job-keyword crosswalk", "Limitations"

test_report_does_not_make_forbidden_claims:
    forbidden = ("tapeout-ready", "production silicon", "JEDEC-compliant",
                 "IPC-compliant", "extracted from JEDEC", "extracted from IPC",
                 "ASIC delivered", "fabrication-qualified")
    for phrase in forbidden: assert phrase not in report_text (case-insensitive)

test_report_links_to_taxonomy_role_families:
    must mention "asic-eda-technical-program-role" and
                 "physical-design-eda-flow-learner-track"

test_runner_script_is_executable_and_documents_replay_path:
    assert os.access(runner, os.X_OK)
    assert "data/semiconductor/openlane_demo/sample_artifacts" in runner.read_text()

test_runner_script_does_not_require_root:
    assert "sudo " not in runner.read_text()

test_rtl_design_matches_config:
    config = json.loads(config.json)
    assert config["DESIGN_NAME"] == "counter"  (or matches the chosen design)
    assert "rtl/counter.v" in config["VERILOG_FILES"]

test_replay_set_size_under_budget:
    total = sum(p.stat().st_size for p in replay_dir.rglob("*") if p.is_file())
    assert total < 2_500_000   # <2.5 MB to keep the repo lean
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `data/semiconductor/openlane_demo/rtl/counter.v` | tiny reference design (4-bit counter) — Verilog source |
| Create | `data/semiconductor/openlane_demo/config.json` | OpenLane flow configuration (DESIGN_NAME, VERILOG_FILES, CLOCK_PORT, CLOCK_PERIOD, FP_CORE_UTIL, etc.) |
| Create | `data/semiconductor/openlane_demo/README.md` | how the demo is structured + live reproduction steps |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/MANIFEST.yaml` | machine-readable inventory of committed artifacts with kind + sha256 + job keywords |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/synthesis.log` | synthesis stage log excerpt |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/timing_summary.txt` | static timing summary excerpt |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/area_power.txt` | area + power summary excerpt |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/drc.txt` | DRC report excerpt |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/lvs.txt` | LVS report excerpt |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/counter.def` | post-route DEF (small) |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/counter.gds` | final GDSII (small) |
| Create | `data/semiconductor/openlane_demo/sample_artifacts/layout.png` | KLayout render of final layout |
| Create | `scripts/semiconductor/openlane_demo_runner.sh` | live-flow runner with documentation-first behavior |
| Create | `scripts/semiconductor/openlane_demo_report.py` | replay-set parser + Markdown report generator |
| Create | `tests/semiconductor/test_openlane_demo.py` | TDD coverage |
| Create | `docs/reports/semiconductor-openlane-rtl-to-gds-demo.md` | the deliverable report |
| Update | `docs/plans/README.md` | add #2509 plan row |
| Update | `docs/reports/semiconductor-cad-fem-knowledge-base.md` | small note linking the new report (optional; only if it strengthens the lane index) |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_manifest_schema_valid` | manifest has required schema | MANIFEST.yaml | parses; design/pdk/flow in allowlist |
| `test_all_manifest_artifacts_exist_on_disk` | every manifest entry resolves | MANIFEST.yaml | all referenced files exist |
| `test_artifact_kinds_cover_required_stages` | replay set covers all flow stages | MANIFEST.yaml | kinds ⊇ {synthesis_log, timing_summary, area_power, drc, lvs, def, gds} |
| `test_report_generator_produces_expected_sections` | report has required sections | runs `openlane_demo_report.py` against replay set | generated MD contains all 7 H2 headings |
| `test_report_does_not_make_forbidden_claims` | report avoids overclaim | generated report text | no forbidden phrases |
| `test_report_links_to_taxonomy_role_families` | report ties to #2508 taxonomy | generated report text | contains both required role-family ids |
| `test_runner_script_is_executable_and_documents_replay_path` | runner is shippable | runner file | mode +x; mentions replay path |
| `test_runner_script_does_not_require_root` | safety guardrail | runner text | no `sudo ` token |
| `test_rtl_design_matches_config` | RTL ↔ config consistency | config.json + rtl/ | DESIGN_NAME and VERILOG_FILES match |
| `test_replay_set_size_under_budget` | repo lean-ness | replay dir | total < 2.5 MB |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/semiconductor/test_openlane_demo.py -v`
- [ ] Existing tests still pass: `uv run pytest tests/docs/test_semiconductor_kb.py -v` (no regressions in #2508 surface)
- [ ] `docs/reports/semiconductor-openlane-rtl-to-gds-demo.md` exists and contains all seven required H2 sections.
- [ ] `data/semiconductor/openlane_demo/sample_artifacts/MANIFEST.yaml` lists at least one artifact for each required flow stage (synthesis, timing, area/power, DRC, LVS, DEF, GDS).
- [ ] `scripts/semiconductor/openlane_demo_runner.sh --check` succeeds (exit 0) on a host where docker / podman are absent (documentation-first contract).
- [ ] Total `data/semiconductor/openlane_demo/` size < 2.5 MB on disk.
- [ ] No forbidden claims (`tapeout-ready`, `production silicon`, `JEDEC-compliant`, `IPC-compliant`, etc.) appear in the report.
- [ ] Report explicitly maps each artifact to ≥1 entry from the `asic-eda-technical-program-role` and/or `physical-design-eda-flow-learner-track` `required_skills` lists in `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml`.
- [ ] License of any vendored sample artifact is recorded in `MANIFEST.yaml` under a `license` key per artifact and in `data/semiconductor/openlane_demo/README.md` under a "Provenance and licensing" section.
- [ ] Plan review artifacts posted at `scripts/review/results/2026-04-26-plan-2509-{claude,codex,gemini}.md`.
- [ ] User approval label `status:plan-approved` set on #2509 + `.planning/plan-approved/2509.md` marker created (gate to implementation; not part of the deliverable itself).

---

## Adversarial Review Summary

PENDING — populated after `scripts/review/plan-review-fanout.sh docs/plans/<final-plan-path>.md` completes the Claude / Codex / Gemini wave. This plan is currently `draft`; do NOT surface for user approval until the wave returns and any MAJOR findings are addressed.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** TBD

Revisions made based on review:
- (none yet — pre-review draft)

---

## Risks and Open Questions

- **Risk:** Vendored sample artifacts may exceed the 2.5 MB budget for a clean repo. Mitigation: prefer the smallest open design (4-bit counter, not simple ALU) for the first commit; spot-check `du -sh` before staging; if over budget, shrink GDS/DEF excerpts or use `git lfs`-style external link with documented hash.
- **Risk:** Sample-artifact license / redistribution rights — OpenLane outputs may carry PDK-derived content with redistribution constraints. Mitigation: use only artifacts from the OpenLane upstream `designs/counter/` reference (which the project already publishes under Apache-2.0) or regenerate from a documented run; record license in `MANIFEST.yaml`. **[UNVERIFIED]** until implementation runs the license check.
- **Risk:** Local environment lacks ALL EDA tools (docker/podman/openlane/openroad/yosys/iverilog/magic/netgen — verified MISSING this session). Mitigation: the documentation-first runner contract is explicitly designed around this; tests verify the runner exits 0 cleanly when tools are absent. The issue's acceptance criterion 1 already permits "clearly replay committed sample artifacts" as the reproduction path.
- **Risk:** OpenLane configuration drift — pinning a specific `efabless/openlane:<tag>` may go stale. Mitigation: record the pinned tag in `data/semiconductor/openlane_demo/README.md` AND in `MANIFEST.yaml.flow_version`; flag stale-tag refresh as a follow-up issue rather than blocking #2509 closure.
- **Risk:** Scope creep into a "real" tapeout-style demo. Mitigation: forbidden-claim guardrail tests (`test_report_does_not_make_forbidden_claims`) keep the report scoped to literacy + reproducibility per the #2508 KB at lines 75 and 117.
- **Risk:** Job-keyword mapping drifts from the taxonomy. Mitigation: `test_report_links_to_taxonomy_role_families` enforces taxonomy linkage, and the report generator pulls keywords directly from `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` rather than hard-coding them.
- **Risk:** PDK choice (Sky130 vs GF180MCU) — both are open. Mitigation: pick Sky130A as primary (richer OpenLane tutorial coverage) and document GF180MCU as a follow-up alternate; the manifest's `pdk` field allows either without code changes.
- **Open question (for user during approval):** Should #2509 wait for KB-recommended execution order `#2508 → #2511 → #2510 → #2509 → #2512` (per `docs/reports/semiconductor-cad-fem-knowledge-base.md` line 153)? The issue is OPEN now, but the KB recommends #2509 land fourth. This plan can proceed but reviewer/user may prefer to defer execution until #2510 / #2511 land.
- **Open question (for user during approval):** Acceptable to commit a small (`< 2.5 MB`) binary `.gds` and `.def` file directly, or prefer Git LFS / external download with hash verification?

---

## Complexity: T3

T3 — multi-file new directory structure spanning `scripts/`, `tests/`, `data/`, and `docs/reports/`; introduces a new domain area (semiconductor EDA) to the repo; requires careful licensing / size management of vendored upstream artifacts; touches a multi-issue lane (#2507 umbrella, sibling closed #2508 + open #2510 / #2511 / #2512) and must remain consistent with their taxonomy/KB; documentation-first design pattern for tool-absent environments must be encoded in both runner and tests. Full TDD with custom guardrail tests (forbidden-claim regex, taxonomy-linkage assertion, replay-set size budget) and adversarial review required.
