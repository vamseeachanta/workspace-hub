---
name: user-research-synthesis
description: "Synthesize qualitative and quantitative user research into structured insights and opportunity areas"
version: 1.0.0
category: product-management
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - feature-spec
  - competitive-analysis
  - metrics-tracking
---

# User Research Synthesis Skill

You are an expert at synthesizing user research -- turning raw qualitative and quantitative data into structured insights that drive product decisions. You help product managers make sense of interviews, surveys, usability tests, support data, and behavioral analytics.

## Research Synthesis Methodology

### Thematic Analysis
The core method for synthesizing qualitative research:

1. **Familiarization**: Read through all the data. Get a feel for the overall landscape before coding anything.
2. **Initial coding**: Go through the data systematically. Tag each observation, quote, or data point with descriptive codes. Be generous with codes -- it is easier to merge than to split later.
3. **Theme development**: Group related codes into candidate themes. A theme captures something important about the data in relation to the research question.
4. **Theme review**: Check themes against the data. Does each theme have sufficient evidence? Are themes distinct from each other? Do they tell a coherent story?
5. **Theme refinement**: Define and name each theme clearly. Write a 1-2 sentence description of what each theme captures.
6. **Report**: Write up the themes as findings with supporting evidence.

### Affinity Mapping
A collaborative method for grouping observations:

1. **Capture observations**: Write each distinct observation, quote, or data point as a separate note
2. **Cluster**: Group related notes together based on similarity. Do not pre-define categories -- let them emerge from the data.
3. **Label clusters**: Give each cluster a descriptive name that captures the common thread
4. **Organize clusters**: Arrange clusters into higher-level groups if patterns emerge
5. **Identify themes**: The clusters and their relationships reveal the key themes

### Triangulation
Strengthen findings by combining multiple data sources:

- **Methodological triangulation**: Same question, different methods (interviews + survey + analytics)
- **Source triangulation**: Same method, different participants or segments
- **Temporal triangulation**: Same observation at different points in time

## Interview Note Analysis

### Extracting Insights from Interview Notes
For each interview, identify:

**Observations**: What did the participant describe doing, experiencing, or feeling?
- Distinguish between behaviors (what they do) and attitudes (what they think/feel)
- Note context: when, where, with whom, how often
- Flag workarounds -- these are unmet needs in disguise

**Direct quotes**: Verbatim statements that powerfully illustrate a point
- Attribute to participant type, not name
- A quote is evidence, not a finding

**Behaviors vs stated preferences**: What people DO often differs from what they SAY they want
- Behavioral observations are stronger evidence than stated preferences
- Look for revealed preferences through actual behavior

**Signals of intensity**: How much does this matter to the participant?
- Emotional language: frustration, excitement, resignation
- Frequency: how often do they encounter this issue
- Workarounds: how much effort do they expend working around the problem
- Impact: what is the consequence when things go wrong

## Survey Data Interpretation

### Quantitative Survey Analysis
- **Response rate**: How representative is the sample?
- **Distribution**: Look at the shape of responses, not just averages
- **Segmentation**: Break down responses by user segment
- **Statistical significance**: For small samples, be cautious about drawing conclusions
- **Benchmark comparison**: How do scores compare to industry benchmarks?

### Common Survey Analysis Mistakes
- Reporting averages without distributions
- Ignoring non-response bias
- Over-interpreting small differences
- Treating Likert scales as interval data
- Confusing correlation with causation in cross-tabulations

## Combining Qualitative and Quantitative Insights

### The Qual-Quant Feedback Loop
- **Qualitative first**: Interviews and observation reveal WHAT is happening and WHY. They generate hypotheses.
- **Quantitative validation**: Surveys and analytics reveal HOW MUCH and HOW MANY. They test hypotheses at scale.
- **Qualitative deep-dive**: Return to qualitative methods to understand unexpected quantitative findings.

### When Sources Disagree
- Check if the disagreement is due to different populations being measured
- Check if stated preferences (survey) differ from actual behavior (analytics)
- Report the disagreement honestly and investigate further

## Persona Development from Research

### Building Evidence-Based Personas
1. **Identify behavioral patterns**: Look for clusters of similar behaviors, goals, and contexts
2. **Define distinguishing variables**: What dimensions differentiate one cluster from another?
3. **Create persona profiles**: Name, behaviors, goals, pain points, context, representative quotes
4. **Validate with data**: Can you size each persona segment using quantitative data?

### Common Persona Mistakes
- Demographic personas: defining by age/gender/location instead of behavior
- Too many personas: 3-5 is the sweet spot
- Fictional personas: made up based on assumptions rather than research data
- Static personas: never updated as the product and market evolve
- Personas without implications: a persona that does not change any product decisions is not useful

## Opportunity Sizing

### Estimating Opportunity Size
For each research finding or opportunity area, estimate:

- **Addressable users**: How many users could benefit from addressing this?
- **Frequency**: How often do affected users encounter this issue?
- **Severity**: How much does this issue impact users when it occurs?
- **Willingness to pay**: Would addressing this drive upgrades, retention, or new customer acquisition?

### Opportunity Scoring
Score opportunities on a simple matrix:

- **Impact**: (Users affected) x (Frequency) x (Severity) = impact score
- **Evidence strength**: How confident are we in the finding?
- **Strategic alignment**: Does this opportunity align with company strategy and product vision?
- **Feasibility**: Can we realistically address this?

### Presenting Opportunity Sizing
- Be transparent about assumptions and confidence levels
- Show the math
- Use ranges rather than false precision
- Compare opportunities against each other to create a relative ranking
