# Weekly Research Synthesis — 2026-08-21

Five research passes this week (2026-08-15 skill-design, 2026-08-17 standards, 2026-08-18 python-ecosystem, 2026-08-19 ai-tooling, 2026-08-20 competitor-market — no 2026-08-16 report, weekend gap). No Bash/`gh` tool available in this session, so issue creation below is **recommended titles only** — filing requires a session with `gh` access.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| ABS Subsea Power Cables standard (Mar 2026, NEW) | High | Create GitHub issue: Phase 999.2 scope — ABS subsea cable criteria for mooring power/control | Pending |
| Flexcom v2026.1.1 commercial slug flow model (NEW) | High | Create GitHub issue: Phase 999.2 scope — slug flow assessment for subsea export risers | Pending |
| Claude Code v2.1.234 credential masking + session auto-continuation | High | Promote to PROJECT.md/Phase 7 design — required version + security checklist item | Pending |
| MCP private network tunnels + Agent SDK enterprise security (Aug 2026) | High | Promote to PROJECT.md — Phase 7 security architecture decision (resolves last week's open question) | Pending |
| GSD v1.8.0 Windows find.exe fix (Aug 17) | High | Create GitHub issue: verify/upgrade GSD on ace-win-1, licensed-win-1 before Phase 7 smoke tests | Pending |
| PyYAML CVE-2026-24009 (Docling RCE, NEW) | Medium-High (if present) | Create GitHub issue: one-time grep, bundle with 08-11 Pydantic AI CVE audit | Pending |
| ISO 19902 SHM JSON schema compatibility (confirms 08-10) | Medium | Promote to PROJECT.md — v1.1 OrcaWave report definition-of-done | Pending |
| Codex CLI v0.146/0.147 native MCP + Agent Plugins 1.0 support | Medium | Create GitHub issue: test Codex MCP tool access for cross-review harness | Pending |
| Competitor cloud-solver subscriptions (SACS 10x, Sesam Veracity, OrcaFlex tri-cloud) test consultation-pricing assumption | Medium | Promote to PROJECT.md — convert "Pending" pricing decision to active client-intake question | Pending |
| Skill descriptions as active routing rules, not passive docs | Medium | Create GitHub issue: audit 10-skill sample, produce exemplar rewrites | Pending |
| Anthropic Evaluations framework (20–50 task baseline) for skill/agent behavior | Medium | Create GitHub issue: Phase 7 eval suite — 25 tasks covering solver success/failure/constraint modes | Pending |
| MCP 2026-07-28 deprecations (Roots, Sampling, Logging; 12-mo window) | Medium | Create GitHub issue: audit `.claude/` MCP configs for deprecated API references | Pending |
| Coverage.py 7.15.4 (Python 3.15, free-threading) | Low-Medium | Monitor — defer to v1.1 optional coverage-tool refresh | Pending |
| DNV FL(Y)/FMS notations + OS-C103/105/106 restructure (validated) | Medium | No new action — already captured in 08-10/08-14 action items | Pending (carryover) |
| API 579-1/ASME FFS-1 Part 16 (FRP) — on track, no acceleration | Low | Monitor — quarterly check, Oct 2026 | Pending |
| Progressive disclosure three-layer topology now industry-formalized | Low | Document (not refactor) in `.claude/skills/README.md` | Pending |
| A2A protocol for multi-agent delegation integrity | Low | Monitor — sketch only if/when Phase 999.4 design starts | Pending |
| PEP 808 pyproject.toml static-key conformance | Low | Document reference in `coding-style.md` | Pending |
| Sesam/OpenFAST/ANSYS incremental advances — no disruptive new entrant | Low | Ignore/monitor — validates current v1.1/999.2 positioning, no change needed | Pending |

## Top 3 Insights for PROJECT.md

1. **Phase 7's security/execution architecture is now fully specified — capture it as the design basis, not another open question.** Last week flagged "orchestration workspace vs. manual dispatch" as an open Phase 7 decision. This week closes it with concrete, dated inputs: Claude Code v2.1.234 credential masking (Aug 13–17), GSD v1.8.0's Windows `find.exe` fix (Aug 17), and MCP private-tunnel support for internal-tool access (Aug 2026) together describe a complete secure path from dev-primary to licensed-win-1's OrcFxAPI solver. Promoting this to PROJECT.md turns three independent hardening releases into one design decision instead of three separate "monitor" items.

2. **Phase 999.2 (Wind Energy backlog) has now absorbed scope from three unconnected research weeks (08-10 floating-wind convergence, 08-17 ABS subsea cables, 08-20 Flexcom slug flow) with zero design sketch produced.** Each addition individually looked like a reasonable forward note; together they're requirements accumulating on a phase that's still `0/4` on its own WRK rubric and has no promoted plan. PROJECT.md's own constraint is "plan before acting" — a backlog phase silently growing its acceptance surface across weeks without a plan is the drift that constraint exists to prevent. Recommend forcing the WRK-rubric re-score this week rather than letting a fourth week add scope.

3. **The "Consultation-based pricing (no payment infra)" Key Decision has sat "— Pending" since v1.0 shipped (2026-03-30); this week is the first time research gave it a concrete, answerable test.** Three competitors (Bentley SACS Cloud, DNV Sesam Veracity, Orcina OrcaFlex tri-cloud) now gate 10x solver acceleration behind $1–5K/month subscriptions. That's not background market color — it's a direct A/B signal for whether clients want bundled expertise-plus-screening (current bet) or self-service cloud simplicity. Converting this from a passive PROJECT.md line to an explicit client-intake question in the next Phase 7 engagement finally resolves a five-month-old open decision with real data instead of another quarter of "pending."

## Cross-Domain Connections

- **AI-tooling (08-19) ↔ standards (08-17) ↔ python-ecosystem (08-18), all converging on Phase 7:** credential-safe execution, SHM-compatible JSON reporting, and stable coverage-gate infrastructure are three independent domains all landing readiness signals on the same single unimplemented plan (07-03). This is the strongest "stop researching, start building" signal of the week — Phase 7 has no remaining external blocker.
- **Standards (08-17 ABS cables) ↔ competitor-market (08-20 Flexcom slug flow):** both add scope to Phase 999.2's mooring/riser module from opposite directions (power/control cabling vs. production-flow physics) in the same week, without either referencing the other. Independent convergence on "Phase 999.2 needs more than hydrostatics" is a stronger signal than either alone — but see Insight #2: it's also the reason to force the design sketch now rather than let a fourth domain add another undocumented requirement next week.
- **Python-ecosystem (08-18 PyYAML/Docling CVE) ↔ carryover from 08-11 (Pydantic AI CVE-2026-54249):** two supply-chain CVE greps have now sat in separate weekly synthesis outputs without confirmed filing. Treat as one audit, not two — the fragmentation itself is the risk (each week's synthesis assumes the prior week's grep happened).
- **Skill-design (08-15 evaluations framework) ↔ ai-tooling (08-19 Codex MCP-native):** Anthropic's "Swiss Cheese" evaluation model and Codex's new native MCP tool access both land on the same target — Phase 7's solver-verification smoke tests. If Codex r2 reviews can now hit MCP tools directly, the eval-suite design (25 tasks, balanced pos/neg) should be written once and run identically across Claude and Codex, not authored per-provider.

## Detailed Action Items

- [ ] Promote: Phase 7 security architecture (Claude Code v2.1.234 + GSD v1.8.0 + MCP tunnels) → PROJECT.md Phase 7 context, replacing last week's open "orchestration vs. manual dispatch" question
- [ ] Promote: ISO 19902 SHM JSON schema → PROJECT.md v1.1 OrcaWave definition-of-done
- [ ] Promote: consultation-pricing validation test → PROJECT.md Key Decisions row (change "— Pending" to "Testing — client intake Q3 2026")
- [ ] Issue: `workspace-hub#TBD` — "Phase 999.2 WRK rubric re-score + design sketch (wind convergence + ABS cables + Flexcom slug flow now all pending on same backlog phase)"
- [ ] Issue: `workspace-hub#TBD` — "Bundle CVE grep: Pydantic AI CVE-2026-54249 (08-11) + PyYAML/Docling CVE-2026-24009 (08-18) across all repos, single audit pass"
- [ ] Issue: `workspace-hub#TBD` — "Upgrade Claude Code ≥v2.1.234 + verify GSD ≥v1.8.0 on ace-win-1/licensed-win-1 before Phase 7 implementation"
- [ ] Issue: `digitalmodel#TBD` — "OrcaWave report JSON schema — ISO 19902 SHM compatibility (v1.1 scope)"
- [ ] Issue: `workspace-hub#TBD` — "Codex MCP-native tool access test for T3 cross-review harness (Gmail/Calendar/Drive via v0.147.0+)"
- [ ] Issue: `workspace-hub#TBD` — "Skill description audit — 10-sample passive-vs-routing-rule rewrite"
- [ ] Issue: `workspace-hub#TBD` — "Phase 7 evaluation suite — 25 tasks, solver success/failure/constraint modes"
- [ ] Monitor: API 579-1 Part 16 (FRP) finalization — Oct 2026 check
- [ ] Monitor: GSD v1.8.0 stability soak period — Sept 2, 2026 check for regressions
- [ ] Monitor: MCP 2026-07-28 deprecated-API audit (Roots/Sampling/Logging) — expected none, 30-min check
- [ ] **Carryover confirmation needed:** verify whether last week's five `workspace-hub#TBD`/`digitalmodel#TBD` issues (GSD migration, Phase 7 orchestration decision, Phase 999.2 promotion, Opus 5 routing reconciliation, DNV/NORSOK audits) were actually filed — the pattern of unconfirmed carryovers is now two weeks running.
