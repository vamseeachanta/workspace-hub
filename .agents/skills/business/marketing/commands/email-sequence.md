---
name: email-sequence
type: command
plugin: marketing
source: https://github.com/anthropics/knowledge-work-plugins
---

# /email-sequence - Design Email Sequences

Design multi-email campaigns across various lifecycle stages with strategic planning, individual email creation, flow logic, and performance measurement.

## Usage

```
/email-sequence <sequence type> <goal> [audience]
```

## Inputs

1. **Sequence type**: onboarding, lead nurture, re-engagement, win-back, product launch, event follow-up, upgrade/upsell, educational drip
2. **Goal**: desired outcome for the sequence
3. **Audience**: target segment details
4. **Email count**: number of emails (or use template defaults)
5. **Timing**: interval preferences between emails
6. **Brand voice**: tone and style guidelines
7. **Context assets**: existing content, product details, offers

## Workflow

### 1. Strategic Planning

Before drafting:
- Define the narrative arc across the sequence
- Map the user journey
- Establish escalation logic
- Set success criteria

### 2. Email Design

Each email includes:
- Multiple subject line variations for testing
- Preview text
- Clear purpose statement
- Body copy with visual hierarchy
- Primary CTA
- Timing recommendation
- Segmentation conditions

### 3. Flow Architecture

- Branching based on engagement (opens, clicks)
- Exit conditions when conversions occur
- Re-entry rules
- Suppression guidelines to avoid duplicate messaging

### 4. Performance Tracking

Benchmark targets by sequence type:

| Sequence Type | Open Rate | Click Rate |
|---------------|-----------|------------|
| Onboarding | 50-70% | 10-20% |
| Lead nurture | 20-30% | 3-7% |
| Re-engagement | 15-25% | 2-5% |
| Win-back | 10-20% | 1-3% |

## Template Structures

| Type | Emails | Focus |
|------|--------|-------|
| Onboarding | 5-7 | Activation and value delivery |
| Lead nurture | 4-6 | Education and trust building |
| Re-engagement | 3-4 | Value reminder and incentive |
| Win-back | 3-5 | Last-chance offers |
| Product launch | 4-6 | Awareness and adoption |
| Event follow-up | 3-4 | Engagement and conversion |
| Upgrade/upsell | 3-5 | Feature discovery and value |
| Educational drip | 5-8 | Knowledge building |

## Follow-Up Options

- Set up A/B testing plan
- Configure in connected email marketing platform
- Build ongoing metric review cadence
- Refine based on initial performance data
