

# Weekly Research Synthesis — 2026-03-29

## Top 3 Insights for PROJECT.md

1. **DNV-RP-C203 2024 S-N curves require digitalmodel fatigue module update** — The spectral fatigue module shipped in Phase 1 (plan 01-04) references 2016-era S-N curves. The 2024 edition introduces revised curves for seawater with cathodic protection and an updated notch model. This directly affects fatigue life outputs for clients. A benchmarked update is the highest-priority technical debt item.

2. **pandas 3.0 Copy-on-Write breaks chained assignment across tier-1 packages** — `worldenergydata` (Phase 2, just verified), `assetutilities`, and `digitalmodel` all rely on pandas. Copy-on-Write is now the only mode, string columns default to `str` dtype (PyArrow backend), and `SettingWithCopyWarning` is gone. This affects the Parquet output pipelines shipped in Phase 2 and calculation DataFrames in digitalmodel. A compatibility audit before the next `uv lock` refresh is critical.

3. **GSD-2 autonomous milestone execution aligns with Phase 5 nightly research** — GSD-2's TypeScript rewrite adds crash recovery, cost tracking, and autonomous milestone execution. Phase 5 (nightly research automation) is currently unplanned — GSD-2's process model could replace a custom cron + Agent SDK approach, reducing build-vs-buy effort significantly.

## Cross-Domain Connections

- **PyYAML CVE-2026-24009 ↔ digitalmodel YAML manifests** — Phase 1 shipped Pydantic-based YAML manifest schemas. While the CVE targets `docling-core`, any `yaml.load()` call without `SafeLoader` is vulnerable. This Python ecosystem security finding directly impacts the engineering standards traceability system.
- **uv 0.11.0 TLS change ↔ all 24 repos ↔ Windows license-locked machines** — The certificate verification switch to `rustls-platform-verifier` could break `uv sync` on `licensed-win-1` and `licensed-win-2` which may use corporate/self-signed certs. This Python tooling change has infrastructure-wide blast radius.
- **ASME B31.4-2025 edition ↔ digitalmodel wall thickness module ↔ aceengineer.com calculator** — The new standard edition may change coefficients in the wall thickness module (Phase 1, plan 01-03), which flows through to the live ASME B31.4 calculator on aceengineer.com (Phase 3). A single standard update affects both the library and the website.
- **MCP Tasks primitive ↔ worldenergydata staleness monitoring** — The call-now/fetch-later pattern from MCP v1.27 could replace the cron-based staleness checks built in Phase 2, connecting AI tooling advances to data pipeline architecture.
- **Agent SDK rename ↔ Phase 5 nightly researchers** — If Phase 5 builds on the Agent SDK programmatically, the breaking rename (`ClaudeCodeOptions` → `ClaudeAgentOptions`, default system prompt removed, filesystem settings no longer auto-loaded) must be accounted for in the design.
- **Gemini CLI free-tier ended ↔ multi-provider cross-review workflow** — The project's tech stack explicitly lists "Claude Code, Codex CLI, Gemini CLI — multi-provider with cross-review." Gemini Pro free access ended March 25, potentially breaking one leg of the review triad.

## Action Items

### Promote to PROJECT.md
- [ ] **Promote:** Add DNV-RP-C203 2024 and ASME B31.4-2025 as tracked standard editions under Engineering Domains, noting existing modules need update
- [ ] **Promote:** Add ISO 19901-4:2025 (geotechnical, CPT-based pile design) as a future calculation module candidate
- [ ] **Promote:** Note GSD-2 as candidate architecture for Phase 5 nightly automation under Workflow section

### GitHub Issues to Create
- [ ] **Issue:** `digitalmodel` — Update spectral fatigue module to DNV-RP-C203 2024 S-N curves (benchmark 2016 vs 2024 impact)
- [ ] **Issue:** `digitalmodel` — Verify ASME B31.4-2025 wall thickness clauses against current implementation
- [ ] **Issue:** `digitalmodel` — Audit YAML traceability manifests for superseded DNV OS-C103/C105/C106 identifiers
- [ ] **Issue:** `workspace-hub` — Audit tier-1 repos for pandas 3.0 compatibility (chained assignment, `.dtype == object`, string column assumptions)
- [ ] **Issue:** `workspace-hub` — Audit tier-1 repos for NumPy 2.4 expired deprecations (`np.sum(generator)`, array-to-scalar)
- [ ] **Issue:** `workspace-hub` — Audit all `yaml.load()` calls for `SafeLoader` usage (PyYAML security hygiene)
- [ ] **Issue:** `workspace-hub` — Test uv 0.11.0 TLS certificate verification on all 4 machines (especially Windows workstations)
- [ ] **Issue:** `workspace-hub` — Verify Gemini CLI paid subscription for continued cross-review workflow
- [ ] **Issue:** `workspace-hub` — Evaluate GSD-2 for Phase 5 nightly research automation

### Monitor Next Week
- [ ] **Monitor:** ASME B31.4-2025 — specific clause/coefficient changes not yet publicly enumerated; watch for detailed comparison documents
- [ ] **Monitor:** GSD-2 stability — at 32K stars and actively evolving; wait for v2.1+ before committing to migration
- [ ] **Monitor:** MCP v1.27 Tasks primitive adoption — evaluate when first production implementations appear for long-running workflows
- [ ] **Monitor:** uv 0.11.x patch releases — TLS change may get refinements based on community feedback

---

**Impact ranking of all findings:**

| Finding | Impact | Rationale |
|---------|--------|-----------|
| DNV-RP-C203 2024 S-N curves | **High** | Directly affects shipped fatigue module accuracy |
| pandas 3.0 breaking changes | **High** | Affects 3 tier-1 packages, breaks working code silently |
| ASME B31.4-2025 | **High** | Affects shipped wall thickness module + live calculator |
| uv 0.11.0 TLS change | **High** | Could break `uv sync` across all 24 repos on all machines |
| PyYAML safe loading audit | **High** | Security — RCE vector if any `yaml.load()` uses unsafe loader |
| NumPy 2.4 expired deprecations | **Medium** | TypeErrors in calculation code, but grep-and-fix is mechanical |
| DNV July 2025 structural standards | **Medium** | Manifest metadata update, no calculation logic affected |
| ISO 19901-4:2025 | **Medium** | Future module candidate, not immediate code impact |
| GSD-2 evaluation for Phase 5 | **Medium** | Strategic architecture decision, not urgent |
| Agent SDK rename | **Medium** | Only relevant when Phase 5 implementation begins |
| Gemini CLI paid tier | **Medium** | Cross-review workflow degraded if not addressed |
| MCP Tasks primitive | **Low** | Exploratory — no immediate implementation needed |
| ABS Offshore Rules consolidation | **Low** | Website copy only, no calculation impact |
| Claude Code voice mode | **Low** | Quality-of-life, no project impact |
| pytest-cov / coverage.py updates | **Low** | Opportunistic upgrade, no breaking changes |
