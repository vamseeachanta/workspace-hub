# Client Conversion Pipeline

> Turn repo engineering capability into paying ACE Engineer clients.

**Target:** $120K/yr retainer revenue from offshore engineering consulting.
**Owner:** ACE Engineer -- 23yr P.E., marine/offshore/structural.
**Status:** Pipeline design -- April 2026.

---

## 1. Capability Inventory -- Repo Assets as Value Propositions

The workspace-hub ecosystem contains production-grade engineering infrastructure that maps directly to billable services.

### Service Lines

| Repo Capability | Client-Facing Service | Target Rate | Demo Asset |
|---|---|---|---|
| OrcaFlex modeling + parametric sweeps | Marine dynamic analysis (mooring, riser, installation) | $200-400/hr | Demo 1 (freespan), Demo 3 (mudmat), Demo 5 (jumper) |
| Wall thickness / multi-code comparison | Pipeline engineering design verification | $200-300/hr | Demo 2 (72 cases, 3 codes -- DONE) |
| FEA + cathodic protection | Structural integrity and corrosion assessments | $250-400/hr | Case studies from digitalmodel/ |
| API 579 Fitness-for-Service | Remaining life assessment, repair-or-replace decisions | $300-500/hr | Methodology docs |
| Python automation + parametric analysis | Digital twin / calculation automation consulting | $150-250/hr | Overnight engineering demo GIFs |
| DNV/ISO/NORSOK compliance | Standards compliance review and gap analysis | $200-350/hr | Code reference databases |
| VIV assessment | Vortex-induced vibration screening and analysis | $250-400/hr | Demo 1 (freespan), VIV notebook |

### Differentiator: "Overnight Engineering"

The parametric demo reports are the core sales asset. A single demo shows:
- Volume: "108 cases screened overnight" triggers "this would take my team 2 weeks"
- Rigor: real code clause refs, safety factors, material data -- senior engineers will spot-check
- Automation: not a one-off spreadsheet but a repeatable, auditable pipeline
- Insight: FAIL cases show value ("you would have caught this overnight")

### Content Assets Ready or In Progress

| Asset | Status | Location |
|---|---|---|
| 4 methodology docs (publication-ready) | DONE | docs/methodology/published/ |
| Wall thickness demo report (72 cases) | DONE | digitalmodel/examples/demos/gtm/ |
| GTMReportBuilder template | DONE | digitalmodel/examples/demos/gtm/report_template.py |
| 7 input databases (vessels, pipes, structures) | DONE | digitalmodel/examples/demos/gtm/data/ |
| Knowledge-to-website pipeline design | DONE | docs/methodology/knowledge-to-website-pipeline.md |
| 729 engineering skills | Structured | .claude/skills/ |
| 51+ wiki pages (marine, naval arch) | Raw markdown | knowledge/wikis/ |
| Freespan demo (Demo 1, ~680 cases) | Open | #1930 |
| Mudmat demo (Demo 3, 180 cases) | Open | #1931 |
| Jumper demo (Demo 5) | Open | #1874 |
| Pipelay demo (Demo 4) | Open | #1873 |
| Screencast GIFs (5x) | Blocked | #1809 |

---

## 2. Pipeline Stages -- Prospect to Retainer

### Stage Definitions

```
PROSPECT --> QUALIFY --> PROPOSE --> CLOSE --> RETAIN
```

#### Stage 0: PROSPECT -- Identify and capture leads

**Criteria:** Name + company + engineering need identified.

**Sources and tools:**
- Expert networks (GLG, AlphaSights, Guidepoint) -- inbound consultation requests (#1994)
- Rigzone / job board scanning -- cron-based job market scanner (#1993, #1670, #1671)
- 1,281 ACE contacts database -- existing contacts needing follow-up
- aceengineer.com inbound -- contact form submissions from published content
- LinkedIn -- engineering manager outreach
- Industry conferences and technical papers

**Automation in place:**
- 3x Gmail triage (automated email classification and routing)
- Job market scanner cron (daily sweep of energy postings)
- Competitor analysis cron (aceengineer-website-update skill)

**Actions:**
- Register on all 3 expert networks immediately (2 hours, $300-600/hr potential)
- Apply to Rigzone postings matching OrcaFlex/mooring/riser/FEA profiles
- Begin systematic follow-up campaign from 1,281 contacts (batches of 50)

#### Stage 1: QUALIFY -- Confirm fit and budget

**Criteria:** Engineering scope confirmed + budget authority identified + timeline known.

**Qualifying questions:**
1. What engineering analysis do you need? (maps to service lines above)
2. What software/codes are you using? (confirms tool compatibility)
3. What is the project timeline? (determines retainer vs project pricing)
4. Who approves the purchase order? (budget authority)
5. Have you done this work in-house before? (pain point identification)

**Tools:**
- Account research skill (.claude/skills/business/sales/account-research/)
- Draft outreach skill (.claude/skills/business/sales/draft-outreach/)
- LinkedIn company research for org size, recent projects

**Disqualification signals:**
- No budget (startup without funding)
- Need full-time hire, not consultant
- Scope outside marine/offshore/structural domain
- Tire-kickers requesting free work

#### Stage 2: PROPOSE -- Deliver tailored pitch

**Criteria:** Written proposal or demo report sent, addressing specific client need.

**Proposal components:**
1. Parametric demo report showing relevant analysis (select from Demo 1-5)
2. Methodology document showing engineering rigor
3. P.E. credentials and 23-year experience summary
4. Scope of work with deliverable list
5. Pricing: retainer ($10K/month) or project-based (hourly x estimated hours)
6. LIVE MODE teaser: "In production, connect to your VMMS/IMMS for real-time go/no-go"

**Content matching by prospect type:**

| Prospect Type | Lead With | Support With |
|---|---|---|
| Engineering manager at 10-50 person firm | Parametric demo report (volume + rigor) | Methodology docs, P.E. credentials |
| Technical lead evaluating tools | Calculation walkthrough, code comparisons | Wiki knowledge base, skill inventory |
| Procurement / contracts | Case studies, P.E. stamp, insurance | Rate card, retainer terms |
| Expert network (GLG etc.) | Domain expertise, hourly availability | LinkedIn profile, publication list |

#### Stage 3: CLOSE -- Secure agreement

**Criteria:** Signed SOW or retainer agreement + first invoice sent.

**Close tactics:**
- Trial engagement: "Let me run your first analysis at reduced rate"
- Urgency: "This parametric sweep can be ready by Monday"
- Risk reversal: "If the deliverable doesn't meet your technical standard, no charge"
- Retainer pitch: "$10K/month for on-call engineering support vs $50K/month for a full-time hire"

**Administrative:**
- SOW template (scope, timeline, deliverables, pricing, payment terms)
- P.E. stamp availability for deliverables requiring licensed review
- Professional liability insurance confirmation
- Invoicing via ACE Engineer C-corp

#### Stage 4: RETAIN -- Expand and renew

**Criteria:** Repeat engagement or retainer renewal.

**Retention tactics:**
- Monthly engineering insights report (automated from repo knowledge)
- Proactive analysis: "I noticed your region had a mooring failure -- here's a screening"
- Scope expansion: start with one service line, cross-sell adjacent capabilities
- Annual retainer review with demonstrated value summary

---

## 3. Content Strategy -- Which Content Drives Which Client Segment

### Audience-Content Matrix

| Audience | Content Type | Channel | Conversion Goal |
|---|---|---|---|
| Engineering managers (10-50 person firms) | Parametric demo reports | Email outreach, LinkedIn | Schedule technical call |
| Technical leads / principal engineers | Methodology docs, wiki knowledge base | aceengineer.com SEO, expert networks | Request specific analysis |
| Procurement / contracts | Case studies, credentials page | Direct email, RFP responses | Issue PO |
| Industry peers / referral sources | Technical blog posts, conference papers | LinkedIn, industry forums | Referral introduction |
| Expert network platforms | Domain expertise profile | GLG/AlphaSights/Guidepoint | Accept consultation |

### Content Production Priority

1. **Parametric demo reports** (highest conversion potential)
   - Demo 2 (wall thickness) -- DONE, use immediately for outreach
   - Demo 3 (mudmat/lifting) -- next priority, showcases vessel comparison
   - Demo 5 (jumper) -- complements Demo 3 with subsea scope
   - Demo 1 (freespan) -- broadest applicability, highest case count

2. **aceengineer.com service pages** (SEO + credibility)
   - Convert top 50 engineering skills to service descriptions (#2022 pipeline)
   - Publish 4 methodology docs (done, awaiting deployment)
   - Add case studies from digitalmodel/ completed analyses

3. **Outreach collateral** (direct sales)
   - Email templates for each prospect type (draft-outreach skill)
   - One-pager PDF: "ACE Engineering Capabilities" (derived from skill inventory)
   - LinkedIn articles adapted from methodology docs

---

## 4. Outreach Channels

### Channel Priority (ordered by time-to-revenue)

| Priority | Channel | Expected Timeline | Revenue Model | Effort |
|---|---|---|---|---|
| 1 | Expert networks (GLG, AlphaSights, Guidepoint) | Days | $300-600/hr per consultation | 2 hrs setup (#1994) |
| 2 | Rigzone / job board applications | Weeks | Contract rates ($150-400/hr) | 4 hrs/week (#1993) |
| 3 | Direct email to 1,281 contacts | Weeks-months | Retainer ($10K/month target) | Batches of 50 |
| 4 | aceengineer.com inbound (SEO) | Months | Mixed (project + retainer) | Content pipeline (#2022) |
| 5 | LinkedIn outreach to engineering managers | Weeks-months | Retainer or project | 2 hrs/week |
| 6 | Industry conferences / technical papers | Months | Retainer + reputation | Variable |

### Expert Network Strategy (#1994)

Fastest path to revenue. Register on all three platforms:
- **GLG**: Largest network, highest volume of consultation requests
- **AlphaSights**: Strong in energy sector, good hourly rates
- **Guidepoint**: Growing platform, less competition per query

Profile emphasis: OrcaFlex/mooring/riser/FEA, offshore installation, pipeline engineering, DNV/API/ISO codes. 23 years P.E. experience is a strong differentiator on these platforms.

### Contact Database Campaign

1,281 existing contacts. Segment and sequence:

| Segment | Count (est.) | Approach | Attach |
|---|---|---|---|
| Former colleagues at offshore firms | ~200 | Personal reconnect + capability update | Demo 2 report |
| Industry contacts (conferences, projects) | ~500 | "What ACE is doing now" + relevant demo | Methodology doc |
| Cold contacts (scraped, purchased) | ~500 | Value-first email (engineering insight) | Blog post link |
| Recruiters / staffing firms | ~80 | Availability + rate card | Credentials one-pager |

---

## 5. Metrics -- Tracking Pipeline Health

### Funnel Metrics

| Metric | Definition | Target (90-day) | Measurement |
|---|---|---|---|
| Prospects identified | New names entering pipeline | 200+ | Contact DB + CRM |
| Qualification rate | % of prospects that qualify | 15-20% | Manual tracking |
| Proposal sent rate | % of qualified leads receiving proposal | 50%+ | Email tracking |
| Close rate | % of proposals that close | 20-30% | Invoice records |
| Average deal size | Revenue per closed engagement | $5K-15K | Accounting |
| Time to close | Days from first contact to signed SOW | < 30 days | Pipeline tracking |

### Channel Metrics

| Channel | Metric | Target |
|---|---|---|
| Expert networks | Consultations completed / month | 5+ |
| Expert networks | Revenue / month | $3K-6K |
| Job boards | Applications submitted / week | 5+ |
| Contact database | Personalized emails sent | 50 in first 30 days |
| Contact database | Response rate | > 10% |
| aceengineer.com | Monthly unique visitors | Track baseline |
| aceengineer.com | Contact form submissions / month | 2+ |
| Demo reports | Reports sent to prospects | 10+ in first 60 days |

### Revenue Targets

| Timeframe | Monthly Revenue Target | Cumulative | Source Mix |
|---|---|---|---|
| Month 1 | $3K | $3K | Expert networks (80%), job board (20%) |
| Month 2 | $5K | $8K | Expert networks (50%), first project (50%) |
| Month 3 | $10K | $18K | Retainer (40%), expert networks (30%), projects (30%) |
| Month 6 | $15K | $63K | Retainer (60%), projects (30%), expert networks (10%) |
| Month 12 | $20K+ | $150K+ | Retainer (70%), projects (25%), expert networks (5%) |

---

## 6. 90-Day Action Plan

### Week 1-2: Immediate Revenue (TIER 0)

- [ ] Register on GLG, AlphaSights, Guidepoint with optimized profiles (#1994)
- [ ] Complete 2-3 expert network consultations
- [ ] Apply to 5+ Rigzone postings matching OrcaFlex/mooring/FEA (#1993)
- [ ] Send Demo 2 (wall thickness) report to 10 warm contacts from database
- [ ] Deploy 4 methodology docs to aceengineer.com (#2030)

### Week 3-4: Demo Materials (TIER 1)

- [ ] Complete Demo 3 (mudmat lifting, 180 cases) (#1931)
- [ ] Complete cache infrastructure (#1831, #1832)
- [ ] Begin Demo 5 (jumper model) (#1874)
- [ ] Send 20 personalized follow-ups from contact database (batch 1)
- [ ] Create "ACE Engineering Capabilities" one-pager PDF

### Week 5-6: Outreach Infrastructure (TIER 2)

- [ ] Complete Demo 1 (freespan, ~680 cases) (#1930)
- [ ] Set up aceengineer.com email triage workflow (#1971)
- [ ] Send 20 more follow-ups (batch 2)
- [ ] Publish first 10 service pages on aceengineer.com (#2022)
- [ ] Record first screencast GIF for outreach

### Week 7-8: Scaled Outreach (TIER 3)

- [ ] Complete Demo 4 (shallow water pipelay) (#1873)
- [ ] Record all 5 demo GIFs (#1809)
- [ ] Launch email outreach to vessel contractors (20+ targets) (#1669)
- [ ] Publish 25+ service pages on aceengineer.com
- [ ] Develop chatbot persona and pitch template (#191)

### Week 9-10: Pipeline Expansion (TIER 4)

- [ ] Begin Field Development Pipeline Engineering skill (#1834)
- [ ] Begin On-bottom Stability module (#1835)
- [ ] Send remaining contact database follow-ups (batch 3)
- [ ] Assess and optimize channel performance

### Week 11-12: Optimization

- [ ] Review metrics against targets above
- [ ] Double down on highest-converting channel
- [ ] Refine demo reports based on prospect feedback
- [ ] Prepare retainer proposal template for qualified prospects
- [ ] Set Month 4-6 priorities based on pipeline health

---

## 7. Critical Path to First Paying Client

The fastest route, based on existing assets:

```
TODAY
  |
  v
Register expert networks (#1994)      -- 2 hours
  |                                       Revenue starts in days ($300-600/hr)
  v
Send Demo 2 to 10 warm contacts       -- 2 hours
  |                                       Pipeline starts filling
  v
Apply to Rigzone postings (#1993)      -- 4 hours
  |                                       Contract pipeline
  v
Deploy methodology docs (#2030)        -- 1 hour (already done)
  |                                       SEO credibility
  v
Build Demo 3 (#1931)                   -- 1-2 days
  |                                       Broader service demo
  v
Email outreach batch 1 (50 contacts)   -- 4 hours
  |                                       Retainer pipeline
  v
FIRST CLIENT ENGAGEMENT                -- Target: within 30 days
```

---

## Related Issues

- #1994 -- Expert network registration (TIER 0)
- #1993 -- Rigzone job pipeline (TIER 0)
- #2030 -- Methodology docs publication (DONE)
- #2022 -- Knowledge-to-website pipeline (parallel)
- #1931 -- Demo 3: mudmat lifting analysis
- #1930 -- Demo 1: freespan VIV screening
- #1874 -- Demo 5: rigid jumper
- #1873 -- Demo 4: shallow water pipelay
- #1809 -- Screencast GIFs
- #1831, #1832 -- Cache infrastructure for demos
- #1669 -- Vessel contractor email outreach
- #191 -- Chatbot persona and pitch template
- #108 -- ACE-GTM parent strategy stream
