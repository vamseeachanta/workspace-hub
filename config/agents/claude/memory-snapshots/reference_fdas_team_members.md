---
name: reference_fdas_team_members
description: "client-a Appraisal Solutions (FDAS) LLC team roster — names, roles, bios from World Oil June 2026 Part-3 article"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5bc378d8-942f-43fa-b766-07bbf7940bc7
---

FDAS = **client-a Appraisal Solutions, LLC** — develops the Frontier Production System (FrPS) + patented Movable Wellbay™ dry-tree architecture for Lower Tertiary / ultra-deepwater (4,000–10,000 ft) Gulf of Mexico developments. Vamsee is a member (VP of Engineering). Team roster captured from World Oil June 2026 "Offshore Technology—Shilling—Part 3" (the 3rd of a 3-part series; co-authors: Shilling, White, Achanta, Hyatt, Ivers).

Source: https://read.nxtbook.com/gulf_energy_information/world_oil/june_2026/offshore_technology_shilling_part_3_frontier_deepwater_appraisal_solutions_llc.html

## Members

- **Roy Shilling** — President & founder. 40+ yrs deepwater dev at bp America (delivery mgr GoM HPHT floating systems/risers/topsides; key leader on bp Project 20K™ + Lower Tertiary team; later 20K work w/ Anadarko & Chevron). Eng/delivery mgr on Horn Mountain, Holstein, Mad Dog, Thunderhorse, Atlantis. Senior principal drilling engineer (jackups+floaters). During Macondo, patented first freestanding riser subsea containment system (installed 51 days, ran on Helix Producer I). 2018 US patents on the Movable Wellbay. BS ME Vanderbilt, MS Ocean Eng Texas A&M.
- **Chuck White** — EVP & co-founder. Naval architect (Univ. Michigan, 1975), MS ME Univ. Houston 1983. Fellow & past chairman of SNAME Texas. 20+ yrs at IOCs as PM & deepwater tech leader; since 2000 tech development + deepwater/natural-gas projects. Led large JIPs + API global task forces writing FPS & riser design RPs; co-chaired first probabilistic riser design code. Multiple US/international patents.
- **Vamsee Achanta** — VP of Engineering & owner of AceEngineer. Upstream engineer, offshore sector. 21 yrs experience, MS ME Texas A&M (2003). Project experience: facilities design incl. SURF, moorings, floaters. Specializes in data science + O&G asset lifecycle automations cradle-to-grave.
- **Paul Hyatt** — VP Drilling & Completions; managing director of TD Solutions Pty Ltd. Wells specialist all phases (exploration→full-field dev). 44 yrs global: offshore, deepwater, arctic, remote heli-rig exploration, HTHP completions, extended-reach, decommissioning. BS Petroleum Eng (honors) UT Austin; SPE life member.
- **Terrance N. Ivers** — Founding chairman. Started at Brown & Root/KBR (27 yrs; retired 2004 as KBR officer & VP Global Offshore Engineering). COO Alliance Wood Group Eng (2004–07); president Amec Paragon (2007–11); CEO Siemens Oil&Gas Compression & Solutions BU (2011–13); EVP SNC-Lavalin Resources/Environment/Water (2013–15); exec president Bilfinger North America (2016–20). BS ME Univ. Houston 1980; registered PE in Texas.

## Part-3 article capture (2026-06-27, MERGED llm-wiki-fdas PR #84, squash `928bb9a`)

Captured the published World Oil June 2026 Part-3 article (FrPS / Movable Wellbay™) into `llm-wiki-fdas` via Claude-in-Chrome `get_page_text`:
- `sources/articles/2026-06_lt-performance-part3-frps.txt` — full published text + provenance header + bios
- `sources/public-data-register.md` — registered `FDAS-WO-2026-06` (public tier; the new 2026 series = `FDAS-WO-2026-04`/`-05`/`-06` = Part 1/2/3, distinct from the 2022 BMT trilogy)
- `docs/2026-06-27_frps-technical-claims-part3.md` — all FrPS technical claims by concept layer + numeric quick-ref (1.45× buoyancy, +5%, 90/15/75-ft joints, 56/18/16-in foam, 600 kg/m³, ≤8 ft air-cans, 7-in→9.625-in tubing, TLP ~5,000-ft limit, >30% reserves vs wet-tree/20yr per BMT 2022)

Cleared the repo's `verify-gate` (record comment + `verified` label); human merged (agent self-merge denied — see [[feedback_agent_can_verify_but_not_self_merge_pr]]).

Related: [[project_chuck_udw_well_access_article_backing]], [[project_fdas_public_tier_dashboard_hse]], [[project_field_development_playbook_epic]]
