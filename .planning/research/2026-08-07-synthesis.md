# Weekly Research Synthesis — 2026-08-07

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| GSD Framework archived 2026-06-26; upstream repo now read-only | High | Create GitHub issue: audit hard dependencies, decide vendor-vs-migrate | Pending |
| uv 0.12.0/0.12.1 hardens workspace lock-group validation | High | Promote to PROJECT.md (Phase 7 prerequisite) + create issue for adoption | Pending |
| Pydantic-settings CVE-2026-58203 (symlink LFR, CVSS 5.3) | High | Create GitHub issue: grep all `uv.lock`, upgrade to 2.14.2+ | Pending |
| SACS/Sesam/Flexcom cloud+subscription consolidation | High | Promote to PROJECT.md (GTM positioning: pre-cloud screening) | Pending |
| Floating wind + mooring/cable coupling now industry-standard | High | Create GitHub issue: Phase 999.2 floating-platform hydrostatic module | Pending |
| Anthropic Agent SDK multi-agent orchestration (May 6, 2026) | Medium | Create GitHub issue: sketch Phase 7 orchestration design option | Pending |
| Claude Code v2.1.221 OpenTelemetry (`message.uuid`, `tool_source`) | Medium | Monitor — adopt into cross-review harness at v1.1 | Pending |
| MCP 2026-07-28 stateless spec shift | Medium | Monitor — audit Gmail/Calendar/Drive MCP tools for session assumptions | Pending |
| Codex CLI v0.143–v0.144 daemon workflows + credit tracking | Medium | Monitor — verify quota-pool integration with `agent-quota-latest.json` | Pending |
| Desktop tool pricing (~$13k/yr) now industry baseline | Medium | Monitor — validate consultation-pricing decision still holds | Pending |
| Pydantic AI CVE-2026-25580 (SSRF) | Low | Monitor — one-time grep, close if absent | Pending |
| Python 3.13 typing deprecations (`typing.List`→native) | Low | Ignore for v1.1 — defer audit to v1.2 planning | Pending |
| OrcaFlex v11.5 modeless UI + pre-bend modeling | Low | Monitor — pre-bend may seed a fabrication-tolerance mini-module | Pending |
| Open-source FEA/OpenFAST maturation | Low | Monitor — revisit as research-partnership angle in Q4 | Pending |

## Top 3 Insights for PROJECT.md

1. **GSD framework is archived (2026-06-26) — the ROADMAP.md phase-transition workflow (`/gsd:transition`, `/gsd:complete-milestone`) now depends on an unmaintained, read-only upstream.** This isn't a "nice to fix later" item: PROJECT.md's own "Evolution" section names these commands as the mechanism for updating itself. If any hook, CI step, or auto-sync flow invokes GSD CLI directly (not yet confirmed), Phase 7 and beyond are at risk. Promote to PROJECT.md Constraints/Key Decisions once the dependency audit lands, recording the vendor-vs-Open-GSD-migration decision.

2. **uv 0.12.1+'s workspace lock-group validation should be an explicit precondition of Phase 7 (Solver Verification Gate)**, not a background upgrade. Phase 7 exists to prove OrcFxAPI + remote execution + module-boundary separation are trustworthy; a lock-validation blind spot (silent success on a nonexistent dependency group) undermines exactly the kind of infra confidence Phase 7 is meant to establish. This is a rare case where a routine ecosystem-tooling bump has direct causal relevance to a named roadmap phase — worth a line in PROJECT.md's Phase 7 context, not just a changelog note.

3. **Competitor cloud-compute consolidation (SACS Cloud, Sesam Cloud, Flexcom+OpenFAST) reframes v1.1's positioning from "alternative to commercial solvers" to "pre-cloud screening gate."** This is a genuine strategic insight, not just a market note: aceengineer.com's lightweight Python calculators become *more* valuable, not less, as competitors gate expensive analysis behind cloud subscriptions — clients need a cheap, transparent way to decide whether a design warrants that spend. Worth codifying in PROJECT.md's Current Milestone or a new Key Decision row ("Position digitalmodel as pre-cloud screening layer, not solver replacement").

## Cross-Domain Connections

- **GSD archival (ai-tooling) ↔ Anthropic Agent SDK orchestration (ai-tooling) ↔ Phase 7 (roadmap):** one orchestration dependency is dying (GSD, phase/milestone tracking) while a new first-class one is emerging (Anthropic's May 6 multi-agent primitive, well-suited to the T3 Claude→Codex→Agy cross-review pattern). Worth evaluating both transitions together rather than serially — Phase 7 design work is a natural point to decide whether to lean into the new Anthropic primitive while also settling the GSD question, instead of patching GSD now and re-architecting again in v1.2.
- **uv 0.12.1 lock validation (python-ecosystem) ↔ Phase 7 Solver Verification Gate (roadmap):** the security/tooling research and the roadmap are talking about the same infrastructure trust boundary from two different angles — dependency-lock integrity and remote-execution verification are both "can we trust what's running on licensed-win-1."
- **Pydantic-settings CVE (python-ecosystem) ↔ Phase 7 remote execution (roadmap):** if any config/secrets loading on licensed-win-1 (SSH-triggered remote Claude Code execution) uses pydantic-settings in the vulnerable range, the symlink-traversal CVE is specifically dangerous in a remote-execution context — worth including in the Phase 7 smoke-test checklist, not just a generic dependency audit.
- **Competitive cloud-compute shift (competitor-market) ↔ v1.1 OrcaWave Automation (roadmap):** the "design-phase pre-analysis" reframing directly validates the current milestone's batch-report-generation and sensitivity-analysis-tooling targets — these are exactly the "screen before you pay for cloud solver hours" features competitors' cloud pricing makes more valuable, not less.
- **Floating wind convergence (competitor-market) ↔ Phase 999.2 Wind Energy backlog (roadmap):** all three competitor findings point the same direction — the backlog item's WRK rubric score (1/4, currently low-priority) understates urgency now that floating wind is the industry's primary growth vector; this is a case where external market signal should influence internal backlog prioritization.

## Detailed Action Items

- [ ] Promote: GSD archival dependency risk → PROJECT.md Constraints (pending audit outcome) + ROADMAP.md Phase 7 context note
- [ ] Promote: uv 0.12.1+ lock validation as Phase 7 precondition → PROJECT.md Phase 7 / ROADMAP.md Requirements
- [ ] Promote: "pre-cloud screening" positioning → PROJECT.md Key Decisions
- [ ] Issue: `workspace-hub#TBD` — "GSD archival impact assessment: audit hard dependencies, decide vendor vs. Open GSD migration" (URGENT, blocks Phase 7 if confirmed)
- [ ] Issue: `workspace-hub#TBD` — "uv 0.12.1+ adoption across all repos + CI `--locked` enforcement" (pre-Phase-7)
- [ ] Issue: `workspace-hub#TBD` — "Audit Tier-1 repos for pydantic-settings CVE-2026-58203 exposure" (this week; check licensed-win-1 config path specifically)
- [ ] Issue: `digitalmodel#TBD` — "Floating platform hydrostatic module — promote Phase 999.2 backlog item given market convergence"
- [ ] Issue: `aceengineer-website#TBD` — "Design-phase positioning refresh: pre-cloud screening messaging tier"
- [ ] Issue: `workspace-hub#TBD` — "Sketch Phase 7 orchestration using Anthropic Agent SDK vs. manual Agent dispatch — decide by adoption or defer to v1.1"
- [ ] Monitor: MCP stateless spec migration path for Gmail/Calendar/Drive tool implementations
- [ ] Monitor: Codex CLI credit-tracking integration vs. `config/ai-tools/agent-quota-latest.json`
- [ ] Monitor: OrcaFlex release notes for pre-bend-driven fabrication-tolerance module opportunity
- [ ] Monitor: Pydantic AI grep result (expected: not-in-use, close if confirmed)
