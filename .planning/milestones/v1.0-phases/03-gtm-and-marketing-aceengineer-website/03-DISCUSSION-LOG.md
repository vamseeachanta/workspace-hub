# Phase 3: GTM and marketing — aceengineer-website - Discussion Log (Assumptions Mode)

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-03-26
**Phase:** 03-gtm-and-marketing-aceengineer-website
**Mode:** assumptions
**Areas analyzed:** Calculation Demo Scope, Website Architecture, Pricing Model, SEO & Content Strategy

## Assumptions Presented

### Calculation Demo Scope
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Add 2-3 new calculators showcasing Phase 1 modules alongside 3 existing ones | Likely | `aceengineer-website/calculators/` has 3 live calculators; Phase 1 YAML manifests ready |

### Website Architecture
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Stay static Vercel with client-side JS calculators, no Python API | Likely | Site is static HTML/CSS/JS on Vercel. All calculators in-browser JS. No server infra exists. |

### Pricing Model
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Free calculators as lead-gen, consultation-based pricing, no payment infra | Likely | Zero payment/auth code. Site positions as consulting. Solo engineer. |

### SEO & Content Strategy
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Enhance existing SEO foundation with calculation-focused content | Confident | Schema.org, sitemap (30+ URLs), GA4, 15 blog posts, competitor analysis reports |

## Corrections Made

No corrections — all assumptions confirmed.

## External Research Flagged

- Vercel serverless Python support (if API backend chosen later)
- Competitor calculator landscape (what interactive tools others offer for free)
- Static form service alternatives to web3forms (for waitlist/signup flows)
- Domain authority baseline (current organic traffic metrics)

*These topics deferred — not needed for current assumption-confirmed decisions.*
