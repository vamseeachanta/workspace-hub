# Weekly Research Synthesis — 2026-08-28

Five research passes this week (2026-08-22 skill-design, 2026-08-24 standards, 2026-08-25 python-ecosystem, 2026-08-26 ai-tooling, 2026-08-27 competitor-market). No `gh`/Bash tool in this session — issue creation below is **recommended titles only**, same caveat as last week.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Phase 999.2 has absorbed 5+ weeks of scope (ABS cables, Flexcom slug, DNV-ST-0359, MIM notation) with 0/4 WRK score and no plan | High | Create GitHub issue: force Phase 999.2 design sketch + WRK re-score NOW — this is week 3+ of the same unaddressed finding | Pending |
| ISO 19902 SHM + DNV MIM notation + Anthropic Outcomes rubric independently converge on one JSON schema decision for v1.1 reports | High | Promote to PROJECT.md — single v1.1 report-schema design decision (reserve factors, fatigue %, quality score) | Pending |
| Claude Code v2.1.245 (Aug 25) — glibc 2.40+ startup-crash fix + `/usage` loop introspection | High | Create GitHub issue: upgrade dev-primary before Phase 7 implementation (15 min) | Pending |
| DNV-ST-N001 marine ops standard revised (400+ comments, 5-yr cycle) | Medium | Promote to PROJECT.md — v1.1 installation-verification checklist section | Pending |
| GSD v1.42.1 skill-surface budgeting (`--profile=core`) | Medium | Create GitHub issue: scope Phase 7 solver lanes to core-profile skills | Pending |
| Anthropic SDK Dreaming (reflective pass) + Outcomes (rubric grading) | Medium-High | Promote to PROJECT.md — Phase 7 solver-verification architecture sketch | Pending |
| MCP remote servers now standard HTTP + load-balancer compatible | Medium | Promote to PROJECT.md — Phase 7 MCP tunnel design note (no custom transport needed) | Pending |
| uv 0.12.0 pre-release-fallback default change | Low-Medium | Create GitHub issue: 30-min CI audit for explicit `--pre` overrides | Pending |
| Three consecutive unconfirmed carryover-issue batches (08-14→08-21, 08-21→08-28) | Medium (process risk) | Create GitHub issue: reconcile all pending `workspace-hub#TBD`/`digitalmodel#TBD` titles from 3 weeks in one filing pass | Pending |
| Agent Plugins 1.0 vendor-neutral skill packaging | Low-Medium | Monitor — quarterly adoption check, Oct 2026 | Pending |
| Python 3.15 feature freeze (frozendict, UTF-8 default), release Oct 1 | Low | Monitor — v1.2 roadmap documentation only | Pending |
| Competitor landscape (Sesam/SACS/OrcaFlex/Flexcom/ANSYS) — confirmation pass, no new entrants | Low | Ignore/monitor — validates current v1.1/999.2 positioning | Pending |
| Coverage.py 7.15.4, pytest 9.0.3 stable | Low | No action | Pending |
| LDP/Agent Cards delegation contracts, SkillsBench behavior validation | Low-Medium | Monitor — sketch during Phase 999.4 design only | Pending |

## Top 3 Insights for PROJECT.md

1. **Phase 999.2 scope creep has crossed from "worth flagging" to "actively costing you design integrity" — this is the third consecutive week the same finding has been logged without a plan existing.** The 08-21 synthesis flagged it, 08-24 standards research flagged it again ("the right moment to force the design sketch... before a fourth week adds another finding"), and this week's competitor-market report explicitly confirms "the backlog-creep risk remains... competitive landscape isn't the blocker — the design sketch is." PROJECT.md's own constraint is "plan before acting"; a `0/4`-WRK backlog phase that has now silently accumulated ABS cables, Flexcom slug flow, DNV-ST-0359, and MIM notation across five weeks is the exact failure mode that constraint exists to prevent. This is no longer a "promote to PROJECT.md" item — it needs to be forced this week, independent of any further research.

2. **Three independent domains (standards, ai-tooling, skill-design) have converged on the same single decision: v1.1's OrcaWave JSON output needs a continuous-quality schema, not a binary pass/fail.** ISO 19902 SHM integration + DNV's new MIM mooring-notation (standards, 08-24) both expect continuous state data (reserve factors, fatigue accumulation); Anthropic's Outcomes rubric (ai-tooling, 08-26) formalizes rubric-based grading as the 2026 pattern; and skill-design's SkillsBench (08-22) validates *behavior*, not just output correctness. Three unrelated research threads landing on one schema decision in the same two-week window is a strong signal to write the schema once — reserve factors, fatigue %, corrosion indices, and a 1–5 quality score — rather than three separate "monitor" line items drifting toward three separate half-implementations.

3. **The tooling substrate for Phase 7 is now fully current and requires zero further research — the only remaining work is mechanical (upgrade, configure, execute).** Across the last three weeks, ai-tooling research has repeatedly confirmed "no blocking changes to Phase 7" while quietly stacking up concrete, actionable version bumps (Claude Code v2.1.234 → v2.1.245, GSD v1.8.0 → v1.42.1, MCP roadmap clarity, uv 0.12.0). Python-ecosystem and competitor-market are both pure confirmation passes this week with zero new actions. Continuing to run all five weekly domains at full depth is now yielding diminishing returns relative to just executing Phase 7 — worth deciding whether next week trims to 2-3 domains (standards + skill-design, where real scope changes are still landing) rather than five.

## Cross-Domain Connections

- **Standards (08-24 ISO 19902/MIM) ↔ ai-tooling (08-26 Outcomes rubric) ↔ skill-design (08-22 SkillsBench):** three unrelated domains all describe the same underlying shift — from binary pass/fail to continuous, standards-grounded quality scoring — landing on the same unimplemented Phase 7 report schema. Write it once; don't let three separate weekly synth entries turn into three partial implementations.
- **Competitor-market (08-27) ↔ standards (08-24):** competitor research explicitly de-risks the Phase 999.2 design-decision timing ("no competitive urgency... file the scope consolidation issue this week; competitive research isn't blocking it") while standards research is the domain actively *adding* the scope. Read together, they say: the facts needed to write the Phase 999.2 sketch are now all in hand — DNV-ST-0359 + MIM notation give the technical scope, and the market snapshot confirms there's no external time pressure forcing a rushed decision either way.
- **ai-tooling (08-26 MCP remote HTTP) ↔ python-ecosystem (quiet week):** MCP's maturation into standard load-balanced HTTP removes what would have been a custom-transport dependency for Phase 7's licensed-win-1 tunnel — a genuine simplification that reduces the surface python-ecosystem's CI audit (`--pre` flags) needs to worry about.
- **Process signal across all five weeks (08-14 → 08-28):** the "unconfirmed carryover" caveat has now appeared in at least two consecutive synthesis outputs (08-21, and implicitly this week) without a session that can actually run `gh issue create`. The fragmentation risk flagged for CVE audits last week applies equally here — each week assumes prior weeks' recommended issues got filed, and none of this session's research can verify that.

## Detailed Action Items

- [ ] Promote: v1.1 OrcaWave JSON schema (reserve factors, fatigue %, corrosion index, 1–5 Outcomes quality score) → PROJECT.md v1.1 definition-of-done, replacing three separate pending line items with one schema spec
- [ ] Promote: Phase 7 solver-verification architecture (Dreaming reflection checkpoint before execute) → PROJECT.md Phase 7 design
- [ ] Promote: DNV-ST-N001 installation-verification checklist section → PROJECT.md v1.1 report template
- [ ] Promote: MCP-as-standard-HTTP-load-balanced-service → PROJECT.md Phase 7 architecture note (removes custom-transport assumption)
- [ ] Issue: `workspace-hub#TBD` — "Phase 999.2 scope consolidation + WRK re-score — DNV-ST-0359 + MIM notation + ABS cables + Flexcom slug flow (week 3+, force this week)"
- [ ] Issue: `workspace-hub#TBD` — "Upgrade Claude Code to v2.1.245 on dev-primary before Phase 7 implementation (glibc fix + /usage introspection)"
- [ ] Issue: `workspace-hub#TBD` — "Enable GSD v1.42.1 skill-surface budgeting (--profile=core) for Phase 7 solver-verification lanes"
- [ ] Issue: `workspace-hub#TBD` — "uv 0.12.0 pre-release-fallback CI audit (30 min, grep for explicit --pre overrides)"
- [ ] Issue: `workspace-hub#TBD` — "Reconcile all pending workspace-hub#TBD/digitalmodel#TBD titles from 08-14 through 08-28 synthesis outputs in one filing pass"
- [ ] Issue: `digitalmodel#TBD` — "OrcaWave v1.1 report JSON schema — unify ISO 19902 SHM + DNV MIM + Outcomes rubric into one spec"
- [ ] Monitor: Agent Plugins 1.0 adoption — Oct 2026 quarterly check
- [ ] Monitor: Python 3.15 release (Oct 1, 2026) — v1.2 CI matrix planning
- [ ] Monitor: LDP/Agent Cards for Phase 999.4 routing design — sketch only when that phase starts
- [ ] **Carryover confirmation still needed:** verify whether any of the 08-21 or earlier weeks' recommended issues were filed — this is now the third week the same caveat applies with no `gh`-capable session having run.
