# Phase E — Agent Routing Intelligence

**Date**: 2026-04-02
**Issue**: #1720
**Data Period**: 2026-03-02 to 2026-04-02 (31 days)
**Corpus**: 153,884 Claude tool calls, 13,554 Hermes tool calls, 410 Codex files, 219 Gemini files

---

## 1. Per-Agent Domain Affinity

### Claude (73,646 post-hook calls across 24 sessions)

| Rank | Repo / Directory     | Calls  | % of Total |
|------|----------------------|--------|------------|
| 1    | workspace-hub        | 70,303 | 95.5%      |
| 2    | digitalmodel         | 1,900  | 2.6%       |
| 3    | assetutilities       | 535    | 0.7%       |
| 4    | worldenergydata      | 201    | 0.3%       |
| 5    | aceengineer-admin    | 87     | 0.1%       |
| 6    | assethold            | 38     | 0.1%       |
| 7    | OGManufacturing      | 32     | <0.1%      |
| 8    | doris                | 28     | <0.1%      |

**Top directories touched** (file path analysis):

| Directory            | File Accesses | Interpretation                  |
|----------------------|---------------|----------------------------------|
| .claude/             | 15,002        | Ecosystem infrastructure (skills, commands, hooks) |
| scripts/             | 7,291         | Automation, orchestration, CI    |
| digitalmodel/        | 1,319         | OrcaFlex/OrcaWave engineering code |
| specs/               | 799           | WRK specifications               |
| tests/               | 619           | Test suites                      |
| assetutilities/      | 301           | Shared utility library           |
| config/              | 229           | Agent/routing configuration      |
| worldenergydata/     | 205           | Energy data repo                 |
| data/                | 180           | Data files and indexes           |
| docs/                | 118           | Documentation                    |

**Finding**: Claude is overwhelmingly focused on workspace-hub (95.5%), functioning as the central orchestrator. Its secondary domain is digitalmodel (engineering code). The .claude/ directory dominates file access, indicating heavy investment in ecosystem infrastructure rather than pure code.

### Hermes (13,554 post-hook calls across 2 sessions)

| Rank | Directory            | File Accesses | % of File I/O |
|------|----------------------|---------------|---------------|
| 1    | digitalmodel/        | 1,083         | 25.2%         |
| 2    | scripts/             | 879           | 20.4%         |
| 3    | docs/                | 594           | 13.8%         |
| 4    | .claude/             | 383           | 8.9%          |
| 5    | tests/               | 199           | 4.6%          |
| 6    | config/              | 132           | 3.1%          |
| 7    | data/                | 112           | 2.6%          |
| 8    | .planning/           | 98            | 2.3%          |
| 9    | logs/                | 70            | 1.6%          |
| 10   | aceengineer-strategy | 63            | 1.5%          |

**Models used**: claude-opus-4-6 (90.4%), gpt-5.4 (9.6%)

**Finding**: Hermes has a significantly different domain affinity profile than Claude. It works heavily on digitalmodel (25.2% vs Claude's 2.6%) and docs (13.8% vs Claude's <1%). Hermes acts more as a research/analysis agent focused on engineering content rather than ecosystem infrastructure.

### Codex (410 files, 88 WRK review logs)

**Activity profile**: Primarily review-focused.
- WRK review logs: 88 files (21.5% of all files)
- Unknown-tagged review logs: 321 files (78.3%)
- Session logs: 1 file (0.2%)

**Repos referenced in reviews**: workspace-hub (6 references found in WRK JSON)

**Finding**: Codex is almost exclusively a cross-review agent. Its WRK file count (88) plus unknown reviews (321) = 409 review-related files out of 410 total. No evidence of direct implementation work.

### Gemini (219 files, 59 WRK review logs)

**Activity profile**: Review-focused with slightly lower volume.
- WRK review logs: 59 files (26.9%)
- Unknown-tagged review logs: 160 files (73.1%)
- Session logs: 0 files

**Finding**: Gemini mirrors Codex as a review agent but at ~53% of Codex's volume. This aligns with the routing config designating it as a secondary reviewer activated on triggers.

---

## 2. Per-Agent Tool Profile

### Claude Tool Distribution

| Tool               | Calls  | % of Total | Category       |
|--------------------|--------|------------|----------------|
| Bash               | 40,093 | 54.4%      | Execution      |
| Read               | 13,811 | 18.8%      | Research       |
| Edit               | 6,724  | 9.1%       | Implementation |
| Write              | 6,436  | 8.7%       | Implementation |
| Grep               | 1,758  | 2.4%       | Research       |
| Agent              | 730    | 1.0%       | Delegation     |
| ToolSearch          | 681    | 0.9%       | Research       |
| TaskUpdate          | 541    | 0.7%       | Delegation     |
| WebSearch           | 519    | 0.7%       | Research       |
| Glob               | 392    | 0.5%       | Research       |
| TaskOutput          | 323    | 0.4%       | Delegation     |
| Skill              | 309    | 0.4%       | Infrastructure |
| TaskCreate          | 280    | 0.4%       | Delegation     |
| StructuredOutput    | 257    | 0.3%       | Output         |
| WebFetch            | 221    | 0.3%       | Research       |
| Browser (MCP)       | 298    | 0.4%       | Research       |
| EnterPlanMode       | 83     | 0.1%       | Planning       |

**Claude profile summary**:
- Execution: 54.4% (Bash-dominant — uses shell for builds, git, tests, orchestration)
- Research: 23.6% (Read + Grep + Glob + Web + Browser)
- Implementation: 17.8% (Edit + Write)
- Delegation: 2.5% (Agent + Task* tools)
- Planning: 0.1%

**Verdict**: Claude is an execution-heavy orchestrator that reads and explores extensively before writing. Its R/W ratio of 1.57:1 confirms a "understand first, then act" pattern.

### Hermes Tool Distribution

| Hermes Tool     | Calls | % of Total | Category       |
|-----------------|-------|------------|----------------|
| terminal        | 6,691 | 49.4%      | Execution      |
| read_file       | 2,044 | 15.1%      | Research       |
| search_files    | 1,410 | 10.4%      | Research       |
| write_file      | 724   | 5.3%       | Implementation |
| todo            | 692   | 5.1%       | Planning       |
| execute_code    | 558   | 4.1%       | Execution      |
| patch           | 555   | 4.1%       | Implementation |
| skill_view      | 169   | 1.2%       | Infrastructure |
| memory          | 169   | 1.2%       | Infrastructure |
| skill_manage    | 124   | 0.9%       | Infrastructure |
| delegate_task   | 102   | 0.8%       | Delegation     |
| process         | 102   | 0.8%       | Execution      |
| session_search  | 90    | 0.7%       | Research       |
| skills_list     | 86    | 0.6%       | Infrastructure |
| clarify         | 20    | 0.1%       | Interaction    |
| cronjob         | 7     | 0.1%       | Automation     |

**Hermes profile summary**:
- Execution: 54.3% (terminal + execute_code + process)
- Research: 26.2% (read_file + search_files + session_search)
- Implementation: 9.4% (write_file + patch)
- Infrastructure: 3.9% (skill_view + skill_manage + skills_list + memory)
- Planning: 5.1% (todo)
- Delegation: 0.8% (delegate_task)

**Hermes unique trait**: High skill engagement — 379 skill-related calls per session avg. This is dramatically higher than Claude's skill tool usage (309 total across all sessions). Hermes leverages the skill system ~18x more intensively per session.

### Codex Activity Profile

| Metric                     | Value |
|----------------------------|-------|
| Total files produced       | 410   |
| WRK review verdicts        | 88    |
| Review files (all types)   | 409   |
| Direct sessions            | 1     |
| Files with APPROVE mention | 169   |
| Files with REVISION mention| 315   |
| Avg issues per review      | 5.6   |

**Codex is 99.8% review activity**. Its single session log suggests minimal direct coding work through the orchestrator pipeline.

### Gemini Activity Profile

| Metric                     | Value |
|----------------------------|-------|
| Total files produced       | 219   |
| WRK review verdicts        | 59    |
| Review files (all types)   | 219   |
| Direct sessions            | 0     |
| Files with APPROVE mention | 124   |
| Files with REVISION mention| 130   |

**Gemini is 100% review activity** in the orchestrator logs. No direct implementation sessions recorded.

---

## 3. Per-Agent Task Complexity

### Claude Session Complexity

| Metric                          | Value    |
|----------------------------------|----------|
| Total sessions                   | 24       |
| Total tool calls (post-hook)     | 73,646   |
| Avg tool calls per session       | 3,068.6  |
| Largest session                  | 8,278    |
| Smallest session                 | 135      |
| Top 5 sessions (calls)          | 8,278 / 7,811 / 6,787 / 5,778 / 5,551 |
| Sessions with >5000 calls       | 7 (29%)  |
| Sessions with delegation (>0)    | 24 (100%)|

**Session-level profiles** (avg across 24 sessions):
- Read: 26.0%
- Write: 18.0%
- Exec: 52.7%
- Delegation: 3.4%
- R/W ratio: 1.57

**Session classification**:
- Research-heavy (read >40%): 0/24 sessions
- Implementation-heavy (write >25%): 3/24 sessions (12.5%)
- Exec-heavy (exec >60%): 4/24 sessions (16.7%)

**Finding**: Claude sessions are consistently large and execution-heavy. Even "small" sessions (135 calls) still involve delegation. The lack of any research-heavy sessions is notable — Claude always mixes research with execution rather than doing pure research passes.

### Hermes Session Complexity

| Metric                          | Value    |
|----------------------------------|----------|
| Total sessions                   | 2        |
| Total tool calls                 | 13,554   |
| Avg tool calls per session       | 6,777.0  |
| Session sizes                    | 7,046 / 6,508 |
| Delegation calls                 | 102      |
| Avg skill calls per session      | 189.5    |

**Session-level profiles** (avg across 2 sessions):
- Read: 27.8%
- Write: 16.9%
- Exec: 54.6%
- Delegation: 0.8%

**Finding**: Hermes sessions are 2.2x larger than Claude sessions on average (6,777 vs 3,069). This suggests Hermes handles more sustained, complex workloads per session. Its higher read percentage (27.8% vs 26.0%) and lower write percentage (16.9% vs 18.0%) suggest a more research-oriented posture.

### Codex/Gemini Task Complexity

These agents operate as reviewers, so complexity is measured differently:

| Metric                       | Codex | Gemini |
|------------------------------|-------|--------|
| Total reviews                | 409   | 219    |
| WRK items reviewed           | 88    | 59     |
| Avg issues found per review  | 5.6   | N/A    |
| Reviews with APPROVE         | 169   | 124    |
| Reviews with REVISION        | 315   | 130    |

**Finding**: Codex is 1.87x more active than Gemini as a reviewer. Codex is also significantly more critical — 76.8% of its files mention revision/changes vs 59.4% for Gemini. Codex finds an average of 5.6 issues per review, suggesting thorough analysis.

---

## 4. Cross-Review Verdict Analysis

### Codex Verdicts (from 88 WRK logs + 321 review logs)

| Verdict                | Count | %      |
|------------------------|-------|--------|
| APPROVE                | 35    | 38.5%  |
| MINOR                  | 24    | 26.4%  |
| REVISE / REVISION      | 12    | 13.2%  |
| changes-requested      | 11    | 12.1%  |
| MAJOR                  | 6     | 6.6%   |
| Request changes        | 2     | 2.2%   |
| Other                  | 1     | 1.1%   |

**Codex issue severity distribution**:

| Severity      | Count |
|---------------|-------|
| MEDIUM        | 23    |
| UNCLASSIFIED  | 23    |
| MAJOR         | 2     |
| LOW           | 2     |

### Gemini Verdicts (from 59 WRK logs)

| Verdict   | Count | %      |
|-----------|-------|--------|
| APPROVE   | 48    | 81.4%  |
| MINOR     | 5     | 8.5%   |
| MAJOR     | 1     | 1.7%   |
| Unparsed  | 5     | 8.5%   |

### Cross-Reviewer Agreement

| Metric                              | Value |
|--------------------------------------|-------|
| WRK items reviewed by both           | 14    |
| WRK items Codex-only                 | 5     |
| WRK items Gemini-only                | 2     |
| Shared WRK items                     | WRK-624, WRK-658, WRK-691, WRK-1007, WRK-1017, WRK-1020, WRK-1075, WRK-1081, WRK-1105, WRK-1141, WRK-1142, WRK-1295, WRK-1381, WRK-9995 |

**Verdict format inconsistency note**: Both agents use varied verdict labels (APPROVE vs approve, REVISE vs REVISION NEEDED vs changes-requested vs Request changes). This makes automated agreement calculation unreliable. Recommendation: standardize verdict enum in review scripts.

### Key Cross-Review Findings

1. **Gemini is significantly more lenient**: 81.4% APPROVE rate vs Codex's 38.5%
2. **Codex is the harder gate**: Only 38.5% clean approvals, with 6.6% MAJOR verdicts
3. **Codex provides more actionable feedback**: Avg 5.6 issues per review with severity classification
4. **Gemini's sparse severity data**: No structured issue_severities parsed from Gemini logs, suggesting simpler review format
5. **Verdict format inconsistency**: At least 7 different verdict strings across agents — needs standardization

---

## 5. Routing Recommendations

Based on observed behavior patterns vs current routing-config.yaml:

| Task Type               | Recommended Agent | Confidence | Reason |
|--------------------------|-------------------|------------|--------|
| High-context synthesis   | Claude            | HIGH       | 95.5% of work is in workspace-hub; handles 3,069 calls/session avg; exclusively does cross-module work |
| Bounded implementation   | Claude + Codex review | HIGH   | Claude does 17.8% implementation; Codex provides 5.6-issue review gate |
| Cross-review             | Codex (primary)   | HIGH       | 1.87x more active than Gemini; 38.5% vs 81.4% approve rate = harder gate; finds MEDIUM/MAJOR issues |
| Documentation            | Hermes            | MEDIUM     | 13.8% of Hermes file access is docs/ (vs <1% for Claude); strong research posture |
| Data analysis            | Hermes            | MEDIUM     | High skill engagement (189.5 skill calls/session); 25.2% digitalmodel access; execute_code capability |
| Skill creation/mgmt      | Hermes            | HIGH       | 379 skill-related calls/session vs Claude's 309 total; explicitly uses skill_manage (124 calls) |
| Research & exploration   | Claude or Hermes  | MEDIUM     | Claude R/W ratio 1.57:1; Hermes read% 27.8%; both research-heavy but Claude has web tools |
| Engineering code         | Claude + Hermes   | MEDIUM     | Claude: 1,900 digitalmodel calls; Hermes: 1,083 digitalmodel file accesses — complementary |
| Large-doc processing     | Gemini            | LOW        | Config says 1M context, but no evidence of this usage in logs — theoretical advantage only |

---

## 6. Capability Gaps

### Gap 1: Gemini Underutilization
- **Observed**: 219 review files total, 0 direct sessions, no structured issue data
- **Config claims**: "Research tasks and literature review", "Large-context analysis"
- **Gap**: Gemini is configured for research/large-doc work but used exclusively for reviews
- **Impact**: The $19.99/mo Gemini subscription is paying only for lenient reviews (81.4% approve)
- **Recommendation**: Route actual research tasks (doc extraction, literature gathering) to Gemini or consider consolidation

### Gap 2: Verdict Format Inconsistency
- **Observed**: 7+ different verdict strings across Codex/Gemini logs
- **Impact**: Cannot reliably compute agreement rates or trend verdict quality over time
- **Recommendation**: Enforce enum {APPROVE, MINOR, MAJOR, REJECT} in submit-to-codex.sh and submit-to-gemini.sh

### Gap 3: No Agent Handles Interactive/Real-Time Work
- **Observed**: Claude's browser MCP usage (298 calls) is minimal; Hermes has 9 browser calls
- **Gap**: Web-based testing, UI verification, and interactive debugging have no clear agent assignment
- **Recommendation**: Assign browser/interactive tasks to Claude (has MCP tools) or develop Hermes browser capability

### Gap 4: Codex Has No Implementation Path
- **Observed**: 99.8% review activity, 1 session log
- **Config claims**: "Focused implementation tasks (Route A/B)", "Writing and expanding test suites"
- **Gap**: Codex is configured for implementation but used exclusively for reviews
- **Recommendation**: Either test Codex for bounded implementation tasks or update config to reflect review-only role

### Gap 5: Hermes Delegation Under-Leveraged
- **Observed**: 102 delegate_task calls (0.8% of activity)
- **Capability**: Hermes has sophisticated delegation (subagent spawning, parallel tasks)
- **Gap**: Very low delegation despite having the infrastructure
- **Recommendation**: Use Hermes as a delegation orchestrator for parallel workloads (overnight batch execution pattern)

### Gap 6: Session Size Variance
- **Observed**: Claude sessions range from 135 to 8,278 calls (61x variance)
- **Impact**: No session budgeting or complexity estimation before starting
- **Recommendation**: Implement pre-session complexity estimation to pick the right agent/model tier

---

## 7. Comparison with Existing Configuration

### routing-config.yaml Mismatches

| Config Setting                    | Config Says              | Observed Reality                      | Mismatch? |
|-----------------------------------|--------------------------|---------------------------------------|-----------|
| SIMPLE tier → primary: codex      | Codex handles simple     | Codex does 0 implementation tasks     | YES       |
| STANDARD tier → primary: codex    | Codex handles standard   | Codex does 0 implementation tasks     | YES       |
| COMPLEX tier → primary: claude    | Claude handles complex   | Confirmed — Claude handles 95.5%      | NO        |
| REASONING tier → primary: claude  | Claude handles reasoning | Confirmed                             | NO        |
| code_density → codex              | Codex is code-dense      | Codex only reviews, doesn't generate  | YES       |
| research_analysis → gemini        | Gemini researches        | Gemini only reviews                   | YES       |
| data_processing → gemini          | Gemini processes data    | Gemini only reviews                   | YES       |

### provider-capabilities.yaml Mismatches

| Provider | Claimed Capability                        | Observed | Status    |
|----------|------------------------------------------|----------|-----------|
| Claude   | Multi-file architecture                  | Yes      | CONFIRMED |
| Claude   | Orchestration and planning               | Yes      | CONFIRMED |
| Claude   | Code review and cross-review             | Partial  | Claude reviews but mostly orchestrates |
| Codex    | Single-file focused code changes         | No       | NOT OBSERVED — review only |
| Codex    | Algorithm implementation                 | No       | NOT OBSERVED |
| Codex    | Test writing and TDD                     | No       | NOT OBSERVED |
| Codex    | cross_review_hard_gate role              | Yes      | CONFIRMED  |
| Gemini   | Research and information gathering       | No       | NOT OBSERVED — review only |
| Gemini   | Data analysis and summarization          | No       | NOT OBSERVED |
| Gemini   | Large document processing                | No       | NOT OBSERVED |
| Gemini   | research_and_large_context role          | No       | NOT OBSERVED — review only |

### Summary of Mismatches

**5 of 11 claimed capabilities are NOT observed in the session corpus.** The routing config and provider capabilities files describe an idealized multi-agent architecture where each agent has distinct implementation roles. In practice:

1. **Claude does everything** — orchestration, implementation, research, delegation
2. **Codex reviews** — nothing else
3. **Gemini reviews** — nothing else, and more leniently than Codex
4. **Hermes** is not represented in routing-config.yaml at all, despite being the second most active agent (13,554 calls)

**Critical gap**: Hermes is completely absent from both routing-config.yaml and provider-capabilities.yaml, yet it is the second-highest-volume agent in the ecosystem. This is a significant configuration blindspot.

---

## Appendix: Raw Data Files

- Claude session profiles: `phase-e-data/claude-session-profiles.json`
- Hermes session profiles: `phase-e-data/hermes-session-profiles.json`
- Codex/Gemini review analysis: `phase-e-data/review-analysis.json`
