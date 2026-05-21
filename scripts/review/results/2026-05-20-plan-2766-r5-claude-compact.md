The Write tool for local filesystem is not available in this environment — I only have Gmail, Calendar, and Drive MCP tools. I'll deliver the review as text output; the orchestrator can commit the artifact.

---

`★ Insight ─────────────────────────────────────`
R5 is the most structurally complete revision to date. The historical-provenance schema, placement-rule table, and host-scoped readiness integration are now genuinely specified. What remains are three cross-section contradictions that would produce divergent implementations without further resolution.
`─────────────────────────────────────────────────`

---

## Verdict
**MAJOR**

## Retrieval adequacy
**adequate**

---

## Findings

- **MAJOR** — **`Files to Change` directly contradicts AC, Registry Semantics, and pseudocode on `data_access_profile.repos`.** The "Files to Change" table says: *"update `telegram_hermes.data_access_profile.repos` to include all required repos **and classified runtime non-tier-1 repos only**."* The Registry Semantics section, the pseudocode assertion (`assert data_access_profile.repos == required`), and the AC all say `data_access_profile.repos` must equal *exactly the required tier-1 set* — explicitly excluding all non-tier-1 repos. An implementer following the Files to Change row would produce a wrong and wider `data_access_profile`, undermining the OGManufacturing removal and the entire tier-1 runtime-access contract.

- **MAJOR** — **`assert machine.hostname == "ace-linux-1"` references a field absent from the proposed registry YAML schema.** The pseudocode requires `machine.hostname`, but the proposed YAML structure shown under `machines.dev-primary` does not include a `hostname` field — and the existing registry fields listed in Resource Intelligence (`workspace_root`, `tier1_repo_root`, `repo_layout`, `repos`, `telegram_hermes`) confirm it is not currently present. Without adding `hostname: ace-linux-1` to the YAML schema *and* the `Files to Change` row, the checker will raise an `AttributeError`/`KeyError` at startup. The plan does not specify this addition.

- **MAJOR** — **`overall_status` recompute after host mutation is underspecified.** The pseudocode closes with *"recompute overall_status from host_entry.status after mutation"* but provides no algorithm. `overall_status` is presumably an aggregation across all host entries; if the existing readiness script computes it internally (not as a callable function), the implementer cannot simply call it after mutating one host entry. The plan neither cites the existing function signature nor defines the aggregation rule (e.g., worst-case across hosts). An implementer must resolve this independently, creating divergence risk.

- **MINOR** — **Pseudocode double-sets host status in two overlapping blocks.** Block 1 sets `host_entry["status"] = "fail"` when `repo_placement.blockers` is non-empty. Block 2 re-evaluates `if host_entry["failures"]:` and sets `status = "fail"` again. For the warnings-only path, Block 2 correctly handles `host_entry["warnings"]`, but the two-block structure creates a non-obvious execution order. The first block mutates then falls through into the second block unconditionally, producing status overwrite redundancy. A single combined block would be unambiguous.

- **MINOR** — **`historical_absence_policy` in `placement_rules` appears unused.** The YAML defines both `historical_absence_policy: warning` and `historical_state_changed_since_prior_comment_policy: warning`. The pseudocode only references `historical_state_changed_since_prior_comment` warnings. `historical_absence_policy` is never cited in the pseudocode flow. Either it is dead configuration or it covers a case (historical entry is absent but *prior_claim* was not `sibling=git`) that goes undescribed. This ambiguity will produce unused-key drift in the checker's policy table.

- **MINOR** — **`infra dir contains .git` check is ambiguous in scope.** The pseudocode states: *"if infra dir contains .git file/dir, warn/error per unknown_sibling_git_policy."* It is unclear whether this checks for `agent-worktrees/.git` directly (top-level gitlink on the infra dir itself) or for `.git` files within *subdirectories* of `agent-worktrees` (individual worktree gitlinks). Agent worktrees by design contain per-worktree `.git` files. If the check recurses into subdirectories, it will fire spuriously on legitimate worktrees. The live probe found `agent-worktrees` as non-git, but its contents are unexamined.

- **MINOR** — **`test_checker_is_readonly` does not name the monkeypatched surfaces.** The test specification says "monkeypatch around subprocess/path mutation helpers" but does not identify which function names or modules will be patched (e.g., `subprocess.run`, `subprocess.Popen`, `os.rename`, `shutil.move`, `pathlib.Path.unlink`). Without this, the test spec is ambiguous to implement — a reviewer cannot determine whether the read-only guarantee covers all mutation paths or only the obvious ones.

- **MINOR** — **`test_html_report_sections_and_data_attributes` does not specify fixture type.** The test must "parse HTML structurally, not only grep substrings." But the plan does not state whether this test runs the checker against a synthetic fixture tree (deterministic) or against live `/mnt/local-analysis` state (non-deterministic due to dirty/ahead counts). Given dirty counts will change as #2766 implementation proceeds, a live-data HTML test is fragile. The plan says "All filesystem and git inputs below are synthetic fixtures unless explicitly stated" — but this test is not explicitly clarified.

- **MINOR** — **Python `assert` used for user input validation is unsafe under `-O`.** `assert args.machine == "dev-primary"` and `assert baseline.version == 1` would be silently skipped when Python runs with `-O`/`-OO` optimization flags (e.g., in some CI environments). User-input and schema validation should use explicit `if ... raise ValueError(...)` or `argparse` choices constraint, not assert statements. This is a correctness risk in optimized environments.

---

## Blockers

1. **Fix `Files to Change` `data_access_profile.repos` description.** Change *"include all required repos and classified runtime non-tier-1 repos only"* to *"set to exactly the required tier-1 set: workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold; remove OGManufacturing and all non-tier-1 repos."* This eliminates the implementer-visible contradiction with AC, Registry Semantics, and pseudocode.

2. **Add `hostname: ace-linux-1` to the proposed `machines.dev-primary` YAML block** and include its addition in the `Files to Change` modify row for `registry.yaml`. Without it, `assert machine.hostname == "ace-linux-1"` fails at runtime.

3. **Define the `overall_status` recompute algorithm explicitly.** Either cite the existing readiness script function that aggregates host statuses (with line reference) and confirm it is callable after external mutation, or reproduce the algorithm inline: *"overall_status = worst(host.status for host in hosts.values()) using the ordering pass < warn < fail."* Without this, the pseudocode terminus is unimplementable without reading and re-engineering the existing script.
