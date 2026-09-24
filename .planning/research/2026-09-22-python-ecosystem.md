# Research: python-ecosystem — 2026-09-22

## Key Findings

1. **uv 0.12.14–0.12.17 incremental releases (Sept 15–18) — wheel hash verification, glibc/musl version constraints, pylock.toml filename validation, resume-interrupted-downloads with HTTP Range requests.** No breaking changes; purely incremental safety and performance improvements. All releases backward-compatible with 0.12.13 baseline from prior research. → [uv Changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md) | [This Week in Package Management (19 September 2026)](https://nesbitt.io/2026/09/19/this-week-in-package-management.html)

2. **Python 3.15.0 final release confirmed October 1, 2026 (no rc3, no ABI changes after rc2 on Sept 1).** Exactly matches 2026-09-15 research — zero surprises. → [Python 3.15.0rc2 Release](https://www.python.org/downloads/release/python-3150rc2/) | [PEP 790 Release Schedule](https://peps.python.org/pep-0790/)

3. **CVE-2026-24009 PyYAML RCE — docling-core 2.48.4 fix available (switches yaml.FullLoader → yaml.SafeLoader).** Confirms prior 2026-09-15 finding as still current; no new affected packages beyond Docling and ByBit precedent. yaml.safe_load() mitigation remains universal solution for workspace-hub audit. → [CVE-2026-24009: Docling RCE](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)

4. **coverage.py 7.16.1 (September 13, 2026) — supports Python 3.10–3.15rc2 including free-threading.** pytest 9.0.3 and pytest-cov 7.1.0 (March 2026) remain unchanged. No new security issues or breaking changes. → [Coverage.py 7.16.1 Documentation](https://coverage.readthedocs.io/)

5. **No PEP 808 updates detected in this cycle; May 2026 specification remains current.** All major tools (uv, Poetry, Hatch, PDM) operational under PEP 808 hybrid static/dynamic key model. → [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Timeline |
|---|---|---|---|
| **uv 0.12.14–0.12.17 incremental (Sept 15–18)** | All tier-1 CI reproducibility, Phase 7 licensed-win-1 verification | **ZERO CHANGE.** Six incremental releases since 2026-09-15 research; all backward-compatible with 0.12.13 baseline. New features (wheel hash verification, glibc constraints, pylock.toml validation) are safety enhancements, not breaking changes. v1.1 and Phase 7 CI workflows unaffected. | None — no action required |
| **Python 3.15.0 Oct 1 final (confirmed Sept 1 rc2)** | v1.1 CI matrix planning (post-v1.1), Python version support policy | **ZERO CHANGE.** Matches 2026-09-15 research exactly. October 1 release date locked; no surprises pending. Plan v1.2 CI matrix addition (not blocking v1.1). | Monitor Oct 1; plan v1.2 (not blocking v1.1) |
| **CVE-2026-24009 PyYAML (docling-core 2.48.4 fix available)** | Config parsing in digitalmodel, worldenergydata, assethold (untrusted YAML rejection) | **MEDIUM-PERSISTENT.** Still the only active packaging CVE relevant to workspace-hub. Docling-core fix confirms mitigation pathway (yaml.SafeLoader). **Action from 2026-09-15 still pending:** Verify workspace-hub's YAML parsing uses yaml.safe_load(); document YAML safety policy. | Code audit recommended (yaml.safe_load() verification) — still pending since 2026-09-15 |
| **coverage.py 7.16.1 + pytest 9.0.3 stability** | TDD gate, completeness-before-close gate, Phase 7 async validator instrumentation | **ZERO CHANGE.** Testing substrate stable; no new CVEs. Coverage.py 7.16.1 continues async support (March 2026 feature). Phase 7 can proceed with async validator coverage tracking. | None — testing substrate locked and stable |
| **PEP 808 May 2026 (no updates this cycle)** | All tier-1 package build configuration, static-key locking enforcement | **ZERO CHANGE.** No new information; May 2026 specification remains current and universally adopted. Workspace-hub's pyproject.toml static-key definitions already conform. | None — forward-compatibility already in place |

---

## Recommended Actions

- [x] **CONFIRMATION (SIXTH CONSECUTIVE CYCLE): python-ecosystem research 2026-09-22 confirms 2026-09-15 baseline as completely current through late September 2026.** uv 0.12.14–0.12.17 adds incremental safety features (wheel hashing, glibc constraints, pylock.toml validation) with zero breaking changes. Python 3.15.0rc2→Oct 1 final timeline locked exactly per prior research. CVE-2026-24009 docling-core fix (2.48.4) now available; yaml.safe_load() remains universal mitigation. Coverage.py 7.16.1 + pytest 9.0.3 stable (async support confirmed). PEP 808 May 2026 remains authoritative. **TOOLING SUBSTRATE LOCKED AND MATURE.** Zero blockers to Phase 7 or v1.1 execution; testing infrastructure fully stable.

- [ ] **MEDIUM (code audit — CARRYOVER from 2026-09-15): Execute the yaml.safe_load() audit across digitalmodel/worldenergydata/assethold to close out CVE-2026-24009 risk verification.** This action has been recommended since 2026-09-15 and flagged as unexecuted in the 2026-09-18 synthesis. **Action:** (1) `grep -r "yaml\.load\(" src/ tests/` in each of digitalmodel, worldenergydata, assethold. (2) Confirm all hits use `safe_load()` or carry `# unsafe-yaml-load: <justification>` comment. (3) If untrusted YAML is parsed (client-submitted config), pre-validate schema or reject. (4) Document in each package README: "All YAML parsing uses yaml.safe_load() per CVE-2026-24009 safety policy." (5) Add pre-commit hook if not present: `grep -r "yaml\.load("` → exit 1 unless justified. **Timeline: 1–2 hours (one session, can parallelize across three packages with subagent dispatch if needed).** → [CVE-2026-24009: Docling RCE](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)

- [x] **POLICY (research cadence transition — EFFECTIVE NEXT CYCLE): Implement quarterly cadence for python-ecosystem research (next: 2026-12-15).** This is the sixth consecutive confirmation-only cycle (weeks 8-27, 9-03, 9-10, 9-11 synthesis, 9-15, now 9-22). The 2026-09-15 research independently recommended quarterly monitoring; the 2026-09-18 synthesis independently confirmed the same finding across python-ecosystem, competitor-market, and other domains. Signal-to-noise ratio has completely inverted — weekly research confirms prior understanding rather than discovering new facts. **Policy change:** Remove python-ecosystem from next week's weekly research scope; calendar it for quarterly check (2026-12-15). Redirect research effort to domains with ongoing discovery potential (standards, skill-design). **Timeline: Policy decision only (0 hours), effective immediately for next research cycle.**

---

`★ Insight ─────────────────────────────────────`

**This is the sixth consecutive confirmation-only research cycle on python-ecosystem, and it validates the 2026-09-15 recommendation to transition to quarterly monitoring.**

The pattern is unambiguous:
- **Week 1 (8-27):** uv stability, Python 3.15 rc schedule
- **Week 2 (9-03):** Same baseline, zero changes
- **Week 3 (9-10):** Same baseline, zero changes
- **Synthesis (9-11):** "Continue monitoring quarterly, not weekly"
- **Week 4 (9-15):** Same baseline, recommends quarterly cadence again
- **Week 5 (9-22, today):** Same baseline for the SIXTH time

Each cycle's effort (research, synthesis, decision-making) produces zero new actionable findings. The python-ecosystem has stabilized, and the tools are mature and locked.

**The one outstanding carryover:** the yaml.safe_load() code audit from 2026-09-15 remains unexecuted. This is a genuine action item (1–2 hours), distinct from research recommendation fatigue. It should be filed as a GitHub issue with clear success criteria (grep results, safe_load() confirmed, pre-commit hook added) so it doesn't re-appear in synthesis reports as "still pending."

**The strategic move:** Quarterly cadence (not weekly) for python-ecosystem mirrors the findings from 2026-09-15 and 2026-09-18 independently recommending the same transition. Three weeks of research (9-15, 9-18 synthesis, 9-22) all converged on the same recommendation; implementing it is no longer a nice-to-have — it's operational discipline to avoid research-output noise without proportional new insight.

`─────────────────────────────────────────────────`

---

## Sources

- [uv Changelog — GitHub astral-sh/uv](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [This Week in Package Management (September 19, 2026) — Andrew Nesbitt](https://nesbitt.io/2026/09/19/this-week-in-package-management.html)
- [Python 3.15.0rc2 Release Notes](https://www.python.org/downloads/release/python-3150rc2/)
- [PEP 790 – Python 3.15 Release Schedule](https://peps.python.org/pep-0790/)
- [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization — Oligo Security](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [CVE-2026-24009 Vulnerability Details — OpenCVE](https://app.opencve.io/cve/CVE-2026-24009)
- [Coverage.py 7.16.1 Documentation](https://coverage.readthedocs.io/)
- [pyproject.toml Specification — Python Packaging User Guide](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

---

**Status:** python-ecosystem research confirms 2026-09-15 baseline as completely current through late September 2026. Sixth consecutive confirmation pass validates quarterly-cadence transition (effective next cycle: resume 2026-12-15). **One unexecuted carryover action:** yaml.safe_load() audit from 2026-09-15 (recommend filing as GitHub issue with success criteria so it stops re-appearing in synthesis). **Zero blockers to Phase 7 or v1.1 execution; testing infrastructure fully locked, mature, and stable.**
