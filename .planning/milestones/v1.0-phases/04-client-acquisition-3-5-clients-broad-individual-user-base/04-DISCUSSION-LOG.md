# Phase 4: Client Acquisition — 3-5 Clients + Broad Individual User Base - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 04-client-acquisition-3-5-clients-broad-individual-user-base
**Areas discussed:** Acquisition channels, Self-service vs consultation, Onboarding flow, Feedback & CRM

---

## Acquisition Channels

### Enterprise Outreach Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Direct network | Leverage existing industry contacts and LinkedIn connections — personal outreach | ✓ |
| Content-led inbound | Double down on SEO + blog + calculator traffic → contact form conversions | |
| Conference presence | OTC, Subsea Tieback, SPE events — booth or presentations | |
| LinkedIn campaigns | Targeted LinkedIn ads or systematic outreach sequences | |

**User's choice:** Direct network
**Notes:** Lowest cost, highest conversion for first 3-5 clients.

### Individual Engineer Growth

| Option | Description | Selected |
|--------|-------------|----------|
| SEO + open calculators | Keep calculators free and ungated, scale with content | ✓ |
| Community building | Discord, forum, or LinkedIn group around offshore/subsea topics | |
| Newsletter/email list | Add email capture to build mailing list | |

**User's choice:** SEO + open calculators
**Notes:** Already working — scale it with more content.

### Outreach Automation

| Option | Description | Selected |
|--------|-------------|----------|
| Manual only | No CRM or automation tooling this phase | ✓ |
| Lightweight CRM | Simple tracking spreadsheet or free CRM | |
| Email sequences | Automated follow-up emails for site leads | |

**User's choice:** Manual only
**Notes:** Focus energy on conversations, not tools.

### Content Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Case study focus | 2-3 detailed case studies showing real problems solved with digitalmodel | ✓ |
| Calculator expansion | 2-3 more calculators to broaden SEO surface | |
| Technical whitepapers | In-depth technical papers as downloadable PDFs | |
| You decide | Claude picks best content strategy | |

**User's choice:** Case study focus
**Notes:** Best enterprise sales tools, paired with calculator demos.

---

## Self-service vs Consultation

### User Accounts

| Option | Description | Selected |
|--------|-------------|----------|
| No auth this phase | Keep calculators fully open, no login | ✓ |
| Lightweight auth | Optional accounts for saving calculation history | |
| Full auth + gating | Gate advanced calculators behind login | |

**User's choice:** No auth this phase
**Notes:** Auth adds complexity with uncertain payoff at 3-5 client scale.

### Payment Model

| Option | Description | Selected |
|--------|-------------|----------|
| Invoice-based | Manual invoicing after consultation | ✓ |
| Stripe checkout | Self-service payment links for defined packages | |
| Proposal + PO flow | Formal proposal, purchase order, net-30 terms | |

**User's choice:** Invoice-based
**Notes:** Standard for small consultancy-to-consultancy work. No payment infrastructure needed.

### Client Definition for UAT

| Option | Description | Selected |
|--------|-------------|----------|
| Paid invoice or signed pilot | Concrete, verifiable | ✓ |
| Committed engagement | Agreed scope and timeline, even without payment | |
| Any revenue | Any payment received for engineering services | |

**User's choice:** Paid invoice or signed pilot
**Notes:** Concrete, verifiable definition.

### Service Offerings

| Option | Description | Selected |
|--------|-------------|----------|
| Custom analysis reports | Full standard-compliant analysis using digitalmodel as engine | ✓ |
| Software licensing | License access to digitalmodel as Python library or API | |
| Consulting + automation | Broader consulting scope — OrcaFlex, FEA, data pipelines | |
| You decide | Claude picks based on capabilities | |

**User's choice:** Custom analysis reports
**Notes:** Calculators demonstrate capability, reports are the product.

---

## Onboarding Flow

### Enterprise Prospect Journey

| Option | Description | Selected |
|--------|-------------|----------|
| Calculator → case study → contact | Natural funnel from demo to sales conversation | ✓ |
| Landing page → demo call | Dedicated enterprise landing page with 'Schedule a demo' | |
| Direct outreach → tailored demo | Send prospects a link to specific relevant calculator | |

**User's choice:** Calculator → case study → contact
**Notes:** Natural funnel leveraging existing assets.

### Individual User Experience

| Option | Description | Selected |
|--------|-------------|----------|
| Open access, no friction | All calculators free, no signup. Growth via GA4 metrics | ✓ |
| Optional email capture | Free calculators + optional 'Get results by email' | |
| Gated results | Run freely but detailed results require email | |

**User's choice:** Open access, no friction
**Notes:** Zero friction maximizes adoption.

### UAT Metric Redefinition

| Option | Description | Selected |
|--------|-------------|----------|
| Redefine as traffic/usage | Replace 'signups' with GA4 proxies (visitors, sessions, returns) | ✓ |
| Add optional signup | Lightweight account option just for metric tracking | |
| Contact form as proxy | Use form submissions + unique visitors as signal | |

**User's choice:** Redefine as traffic/usage
**Notes:** More honest metric for a no-auth site. GA4 already tracks all proxies.

### Site Changes

| Option | Description | Selected |
|--------|-------------|----------|
| Enhance existing pages | Stronger CTAs, case study links, improved contact form | ✓ |
| Add enterprise landing page | Dedicated /enterprise or /for-teams page | |
| Add services page | Detailed /services page with analysis report offerings | |

**User's choice:** Enhance existing pages
**Notes:** Better flow between existing pages rather than new pages.

---

## Feedback & CRM

### Prospect Pipeline Tracking

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Issues | Private repo/project board with stage labels | ✓ |
| Spreadsheet | Google Sheet or CSV for contact tracking | |
| Free CRM tool | HubSpot free tier or similar | |
| No tracking | Keep it in your head at 3-5 scale | |

**User's choice:** GitHub Issues
**Notes:** Consistent with existing GitHub-based task tracking.

### User Feedback Capture

| Option | Description | Selected |
|--------|-------------|----------|
| GA4 analytics + contact form | Analyze traffic, search terms, form requests | ✓ |
| Feedback widget | 'Was this useful?' widget on calculator pages | |
| Post-contact survey | Follow-up email asking what users were trying to accomplish | |

**User's choice:** GA4 analytics + contact form
**Notes:** No new infrastructure — read the data already being collected.

### Analytics Enhancements

| Option | Description | Selected |
|--------|-------------|----------|
| Enhanced GA4 events | More granular custom events on calculator interactions | ✓ |
| Heatmap tool | Hotjar or Microsoft Clarity for session recordings | |
| Keep current setup | Existing GA4 sufficient at current scale | |

**User's choice:** Enhanced GA4 events
**Notes:** Better signal from existing infrastructure.

### Feedback-to-Roadmap Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Manual review cycle | Periodic review of GA4 + contacts + conversations | ✓ |
| Automated reporting | Weekly automated GA4 reports or dashboard | |
| Client advisory input | Explicitly ask early clients what they'd pay for | |

**User's choice:** Manual review cycle
**Notes:** No automation — just a habit of reviewing data.

---

## Claude's Discretion

- Case study topic selection and structure
- GA4 event taxonomy for enhanced tracking
- CTA copy and placement
- Contact form project type selector options
- GitHub Issues label scheme for prospect tracking

## Deferred Ideas

- User accounts and authentication — revisit when scale demands it
- Stripe/payment infrastructure — revisit when invoicing becomes bottleneck
- Email newsletter/marketing — requires email capture, deferred
- Automated CRM — GitHub Issues sufficient at 3-5 scale
- Enterprise landing page — defer until social proof exists
- Services detail page — defer until offerings validated
- Heatmap tools — defer until traffic justifies
- Automated GA4 reporting — manual review sufficient
