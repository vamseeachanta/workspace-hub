# Weekly Research Synthesis — 2026-08-14

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| GSD archival risk RESOLVED — [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) v1.42.3 live, stable, 7.5K+ stars | High | Promote to PROJECT.md/ROADMAP.md (close out last week's URGENT item); update repo references from `gsd-build` to `open-gsd/gsd-core` | Pending |
| DNV July 2026 edition — FL(Y) design-fatigue-life notation + revised FMS fatigue design factors | High | Create GitHub issue: `digitalmodel` — audit spectral fatigue module against DNV 2026 FL(Y)/FMS guidance | Pending |
| Floating offshore wind convergence complete — Flexcom+OpenFAST, SACS 2026 R1, Sesam Veracity, FLOATBench all shipping coupled aero-hydro-servo-elastic capability in 2026 | High | Create GitHub issue: promote ROADMAP.md Phase 999.2 from backlog (WRK 1/4) to v1.2 execution queue (WRK 3/4) | Pending |
| Anthropic Agent SDK multi-agent orchestration production-stable (Aug 2026) + Claude Code self-hosted environments (Team/Enterprise) | High | Create GitHub issue: Phase 7 design decision — orchestration workspace vs. manual Agent dispatch, self-hosted Claude Code on licensed-win-1 feasibility check | Pending |
| NORSOK M-501 R7 (coatings) + M-503 (cathodic protection current density) 2026 refresh | Medium | Create GitHub issue: `digitalmodel` CP module audit against NORSOK M-503 2026 guidance | Pending |
| API 579-1/ASME FFS-1 Part 16 (FRP equipment assessment) under active development for 2026 finalization | Medium | Monitor — note in Phase 999.2 backlog context; no action until Part 16 finalizes | Pending |
| Pydantic AI second SSRF, CVE-2026-54249 (UploadedFile handling, distinct from prior CVE-2026-25580) | Medium | Create GitHub issue: one-time grep across repos, close if absent (expected: not in use) | Pending |
| Skill-composition bottleneck at ecosystem scale (280K+ public skills, no coordination standard) + skill-coverage evaluation metric | Medium | Monitor — no action for v1.1; revisit for Phase 999.4 autoresearch design | Pending |
| ISO 19902 digital/SHM integration now industry practice | Low-Medium | Monitor — note as v1.2 report-format enhancement (structured JSON output) | Pending |
| Coverage.py 7.13.5 AI-driven gap suggestions + async support | Low-Medium | Monitor — adopt opportunistically at v1.1 coverage audit | Pending |
| Claude Code Opus 5 now default (replacing Opus 4.8); spend-limit tracking with reset-time visibility | Low-Medium | Create GitHub issue: reconcile `model-routing.md` + `agent-quota-latest.json` with Opus 5 default | Pending |
| pytest 9.0.3 subtests, PEP 794 namespace clarification, pyproject.toml ecosystem stability | Low | Ignore/monitor — no action needed | Pending |
| MCP 2000+ servers, Linux Foundation governance, stateless spec finalized | Low | Monitor — quarterly conformance check on Gmail/Calendar/Drive MCP tools | Pending |
| Competitor pricing stable (SACS Cloud ~$13.3K/yr, Sesam Veracity) — validates consultation-pricing decision | Low | Monitor — validate with next client outreach cycle | Pending |
| Helica (flexible pipe/umbilical) mature, no 2026 updates; steel/elastomer only, no FRP yet | Low | Monitor — revisit only if API 579-1 Part 16 ships | Pending |

## Top 3 Insights for PROJECT.md

1. **Promote Phase 999.2 (Wind Energy Vision) from backlog to v1.2 execution queue.** Three independent research passes (2026-08-06, 08-10, 08-13) converge on the same signal: every major competitor (Bentley/SACS, DNV/Sesam, Wood Group/Flexcom) shipped production-grade floating-wind aero-hydro-servo-elastic coupling in 2026, and the FLOATBench dataset gives a ready-made fatigue benchmark. This isn't speculative market-watching — it's three vendors independently confirming the same demand signal in the same quarter. The backlog item's own WRK rubric score (1/4) is now stale; it understates a validated market opportunity. Also strengthens v1.1's "pre-cloud screening" positioning (from the 2026-08-07 synthesis) — digitalmodel's lightweight calculators become the qualification gate before clients pay for Flexcom/Sesam/SACS cloud hours.

2. **GSD archival blocker is resolved — close the loop and move forward with Phase 7 planning.** Last week's synthesis flagged this as the #1 risk to the ROADMAP.md phase-transition workflow. `open-gsd/gsd-core` v1.42.3 is live, active, and Codex-integrated. This is worth a PROJECT.md/ROADMAP.md note not because the fix is complex, but because it removes a documented open risk — the record should reflect resolution, not linger as an unresolved threat.

3. **Anthropic's Agent SDK orchestration primitive (production-stable Aug 2026) directly matches workspace-hub's existing T3 cross-review pattern (Claude→Codex→Agy) and should shape Phase 7's design, not be retrofitted after.** Combined with Claude Code's new self-hosted environments (Team/Enterprise), there's a real design choice for Phase 7's solver-verification gate: adopt the formal orchestration workspace (shared filesystem, persistent event log, role-based dispatch) instead of manual SSH dispatch + Agent-tool stitching. This is a "decide once, build correctly" moment — Phase 7 hasn't started implementation yet, so this is architecture, not migration debt.

## Cross-Domain Connections

- **Floating wind convergence (competitor-market, 08-06/08-13) ↔ DNV FL(Y)/FMS fatigue notations (standards, 08-10) ↔ Phase 999.2 (roadmap):** the same underlying trend — floating wind fatigue is now a first-class, standardized, benchmarked engineering problem (DNV notation + FLOATBench dataset + four vendors' coupled solvers) — appears from three independent angles in one week. When multiple domains converge on the same conclusion without cross-referencing each other, that's a stronger signal than any single report alone.
- **GSD resolution (ai-tooling, 08-12) ↔ Anthropic orchestration production-stability (ai-tooling, 08-08 + 08-12) ↔ Phase 7 (roadmap):** both of last week's Phase-7-blocking/shaping ai-tooling risks resolved or matured in the same week, which means Phase 7 design work is now unblocked on two fronts simultaneously (tooling dependency + orchestration architecture) — worth doing the Phase 7 design sketch now rather than waiting, since the inputs won't get more settled.
- **Pydantic AI's second SSRF, CVE-2026-54249 (python-ecosystem, 08-11) ↔ prior CVE-2026-25580 (from 08-07 synthesis):** two SSRFs in the same framework in one month is a pattern, not a one-off — worth recording as a standing caution (a framework class to CVE-audit on adoption, not after) rather than two separate one-time greps.
- **NORSOK M-503 / API 579-1 Part 16 (standards, 08-10) ↔ Helica's steel/elastomer-only scope (competitor-market, 08-13):** the composite/FRP fitness-for-service gap identified in standards research is corroborated by the competitor research finding that DNV's own Helica module hasn't extended to FRP yet — meaning no competitor currently covers this niche either, which is worth noting as a potential differentiation window rather than just a monitoring item.

## Detailed Action Items

- [ ] Promote: GSD migration resolution → PROJECT.md Constraints (remove GSD-archival risk note) + ROADMAP.md Phase 7 context (unblocked)
- [ ] Promote: Floating wind competitive convergence → ROADMAP.md Phase 999.2 (rewrite WRK rubric 1/4 → 3/4, move toward v1.2 execution queue)
- [ ] Promote: DNV FL(Y)/FMS + NORSOK M-503 2026 guidance → PROJECT.md Phase 7 smoke-test checklist ("cite correct standards edition")
- [ ] Issue: `digitalmodel#TBD` — "Audit spectral fatigue module against DNV July 2026 FL(Y)/FMS notations"
- [ ] Issue: `digitalmodel#TBD` — "Cathodic protection module audit vs. NORSOK M-503 (2026) current density guidance"
- [ ] Issue: `workspace-hub#TBD` — "Migrate GSD references gsd-build → open-gsd/gsd-core, pin v1.42.3+"
- [ ] Issue: `workspace-hub#TBD` — "Phase 7 design decision: Anthropic orchestration workspace vs. manual Agent dispatch + self-hosted Claude Code feasibility on licensed-win-1"
- [ ] Issue: `workspace-hub#TBD` — "Promote Phase 999.2 backlog — floating wind hydrostatic/fatigue modules (FLOATBench + 4-vendor market validation)"
- [ ] Issue: `workspace-hub#TBD` — "Grep all repos for Pydantic AI CVE-2026-54249 exposure (expected: not in use, close if confirmed)"
- [ ] Issue: `workspace-hub#TBD` — "Reconcile model-routing.md + agent-quota-latest.json with Claude Code Opus 5 default"
- [ ] Monitor: API 579-1 Part 16 (FRP) finalization status — quarterly check, tie to Phase 999.2 scope expansion
- [ ] Monitor: Coverage.py 7.13.5 AI-gap-suggestion signal quality before adopting into completeness gate
- [ ] Monitor: MCP Gmail/Calendar/Drive tool conformance to 2026-07-28 stateless spec

**Note on last week's carryover:** several 2026-08-07 action items (`workspace-hub#TBD` pydantic-settings CVE audit, uv 0.12.1 adoption, Anthropic SDK orchestration sketch) don't yet show as created issues in the material reviewed — worth confirming whether they were filed before adding this week's new batch, to avoid duplicate issue creation.
