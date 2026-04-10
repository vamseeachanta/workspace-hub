# LinkedIn Content Calendar --- Month 1

Generated: 2026-04-10 | GH: #2099

## Posting Strategy

- **Frequency**: 3 posts/week (Monday, Wednesday, Friday)
- **Best times**: 7-8am CST (before work), 12-1pm CST (lunch scroll)
- **Format mix**: Technical insight (40%), Demo showcase (40%), Engagement/question (20%)
- **Hashtags**: #SubseaEngineering #OffshorePipeline #MarineOperations #DNV #OrcaFlex #EngineeringAutomation
- **Tone**: Senior engineer sharing lessons from the field. No marketing jargon. Specific numbers, real trade-offs, named standards.

---

## Week 1: Establish Credibility

### Post 1 (Monday) --- Demo Showcase: Wall Thickness

**Hook**:
3 design codes. 72 combinations. Under 2 seconds.

**Body**:
Your team probably spends a week comparing DNV-ST-F101, API RP 1111, and PD 8010-2 for one pipe size. Maybe two weeks if the client wants the comparison documented.

I built a parametric screening tool that runs the entire comparison overnight --- every pipe size in your catalog, every design pressure, every corrosion allowance. 72 cases in the demo, but it scales to thousands.

The interesting finding: API RP 1111 governs for thin-wall deepwater lines where hydrostatic collapse dominates. DNV-ST-F101 governs for shallow water where the system test pressure requirement bites. PD 8010-2 sits in between for most cases but becomes the governing code for sour service with high corrosion allowances.

Every result is traceable from input assumptions through to utilisation ratio. No black box. Same formulas your engineers use.

**CTA**: Drop a comment with a pipe size and water depth --- I will tell you which code governs and why.

**Image**: Demo 2 GIF --- lifecycle utilisation chart showing three codes side by side, colour-coded by governing condition
**Hashtags**: #PipelineDesign #WallThickness #DNV #APIRP1111 #OffshorePipeline #SubseaEngineering
**References**: Demo 2, DNV-ST-F101, API RP 1111, PD 8010-2

---

### Post 2 (Wednesday) --- Technical Insight: Splash Zone

**Hook**:
Splash zone slamming governs for 200te+ structures. Your DAF assumption is probably wrong.

**Body**:
I screened 180 deepwater installation cases last month --- structure mass, sling configuration, vessel crane capacity, significant wave height. The pattern was clear.

Below 150te, the dynamic amplification factor (DAF) from crane tip motion drives the design. Standard stuff. But above 200te, slamming loads during splash zone transit dominate. The DNV-RP-H103 slamming formulation gives loads 2-3x higher than what most installation contractors estimate from experience.

The problem: many feasibility studies use a blanket DAF of 2.0 and call it conservative. For heavy structures, that is not conservative --- it misses the slamming peak entirely. The actual governing load comes from the combination of slam coefficient, lowering velocity, and exposed area at the waterline.

This matters because it changes which vessel you need. A crane capacity that looks adequate on paper fails the slamming check.

**CTA**: What is the heaviest structure you have installed through splash zone? I am curious how the slamming check compared to your DAF estimate.

**Image**: Demo 3 hero chart --- go/no-go heatmap (Hs vs. structure weight), red zone expanding above 200te
**Hashtags**: #DeepwaterInstallation #SubseaEngineering #DNVRPH103 #MarineOperations #HeavyLift #SplashZone
**References**: Demo 3, DNV-RP-H103, DNV-ST-N001

---

### Post 3 (Friday) --- Engagement: Engineering Automation

**Hook**:
"We ran it in OrcaFlex" is not the same as "we understand the result."

**Body**:
Unpopular opinion: the bottleneck in offshore engineering is not computation time. It is engineering judgment applied to results.

I have seen teams run 500 OrcaFlex cases and then spend three weeks staring at output files trying to figure out which ones matter. The problem is not the software. The problem is that nobody designed the parametric sweep to answer a specific question.

A good parametric study starts with: "What decision does this analysis support?" If the answer is "which vessel can install this structure," then every parameter in the sweep maps to a vessel capability. If the answer is "which pipe sizes are lay-feasible," then every parameter maps to a lay corridor.

The automation is not the hard part. Framing the right question is.

**CTA**: What is the most cases you have ever run for a single analysis? And did the client actually use all of them?

**Image**: Text post, no image (engagement posts perform well as text-only on LinkedIn)
**Hashtags**: #EngineeringAutomation #OrcaFlex #OffshorePipeline #SubseaEngineering #ParametricDesign
**References**: General methodology, compound engineering approach

---

## Week 2: Showcase Depth

### Post 4 (Monday) --- Demo Showcase: Freespan VIV

**Hook**:
680 freespan cases. The allowable span map your pipeline route survey actually needs.

**Body**:
Pipeline route surveys identify spans. Engineers assess each one. For a 100km deepwater pipeline, you might have 200+ spans to screen against DNV-RP-F105.

The traditional approach: build an OrcaFlex model for every span, run modal analysis, check onset velocity. Takes 2-3 weeks for a competent engineer. Or longer if the pipe-soil interaction assumptions keep changing (they will).

I built a screening tool that runs 680 cases across the full parameter space --- span length, pipe OD, current velocity, soil stiffness. The output is an allowable span envelope: for each pipe size, here is the maximum span length at each current velocity that passes VIV onset screening.

The insight that saved one project a month of detailed analysis: 85% of surveyed spans fell well inside the allowable envelope. Only 32 spans needed detailed FEA. That is 32 OrcaFlex models instead of 200+.

**CTA**: If you work pipeline route engineering, what percentage of your surveyed spans typically need detailed VIV analysis? Curious if 15-20% matches your experience.

**Image**: Demo 1 GIF --- allowable span envelope with green/red pass/fail bands, surveyed spans overlaid as points
**Hashtags**: #PipelineDesign #VIV #FreeSpan #DNVRPF105 #SubseaEngineering #OffshorePipeline
**References**: Demo 1, DNV-RP-F105, DNV-RP-C205

---

### Post 5 (Wednesday) --- Technical Insight: Fatigue Curve Selection

**Hook**:
221 S-N curves across 17 standards. Picking the wrong one changes your fatigue life by 10x.

**Body**:
I compiled every published S-N curve I could find --- DNV-RP-C203, BS 7608, API RP 2A, AWS D1.1, the lot. 221 curves, 17 standards bodies.

Here is what surprised me: for the same weld detail category, the predicted fatigue life can vary by an order of magnitude depending on which standard you use. A DNV Class D curve and a BS 7608 Class D curve look similar on paper but diverge significantly in the high-cycle regime (>10^7 cycles).

This matters for subsea pipelines where the loading is low-amplitude but high-cycle (wave and current). The slope change in the bi-linear S-N curve is where the action is, and each standard handles it differently.

Most engineers default to whatever standard the project specification calls out. But if you are doing concept screening, you should check sensitivity to curve selection before committing. A design that passes on DNV-RP-C203 D-curve may fail on the equivalent BS 7608 curve, or vice versa.

**CTA**: Which S-N curve standard does your company default to, and have you ever cross-checked against another?

**Image**: Chart showing 4-5 S-N curves from different standards for the same weld class, annotated with divergence region
**Hashtags**: #FatigueAnalysis #SNcurve #DNVRPC203 #WeldedJoints #SubseaEngineering #StructuralIntegrity
**References**: S-N library (221 curves), DNV-RP-C203, BS 7608, API RP 2A

---

### Post 6 (Friday) --- Demo Showcase: Pipelay Catenary

**Hook**:
Your pipe catalog has 40 line items. Only 12 are lay-feasible for that water depth. Here is how to find them in an hour.

**Body**:
S-lay feasibility is not just about tensioner capacity. It is about the interaction between pipe stiffness, water depth, stinger setting, and allowable strain at the sagbend.

I screened 60 combinations for a recent project --- pipe OD/WT, water depth, applied tension, stinger departure angle. The tension-curvature envelope tells you immediately which pipe sizes work and which ones require either a different lay method or a different vessel.

The non-obvious result: increasing wall thickness does not always help. For certain OD/WT ratios in 1,500m+ water depth, the added weight increases the catenary tension faster than the added stiffness reduces the sagbend strain. There is an optimal WT window, and it is narrower than most people assume.

This is the kind of insight that comes from sweeping the full parameter space instead of checking one pipe size at a time.

**CTA**: Pipelay engineers --- what is the deepest S-lay you have worked on? I am collecting data points on where the practical limit sits these days.

**Image**: Demo 4 GIF --- tension-curvature envelope plot with pass/fail regions per pipe size
**Hashtags**: #Pipelay #SLay #OffshorePipeline #SubseaEngineering #DNV #CatenaryAnalysis
**References**: Demo 4, DNV-ST-F101 Section 5, API RP 1111

---

## Week 3: Build Authority

### Post 7 (Monday) --- Technical Insight: Jumper VIV

**Hook**:
8" rigid jumper VIV pass rate: 33%. Standard pipe at the same size: 13%. Geometry matters more than mass.

**Body**:
I ran 300 parametric cases for rigid jumper installation --- varying jumper geometry, spool length, rigging configuration, and sea state. The VIV screening results were not what I expected.

Standard pipe sections have a predictable vortex shedding response. But rigid jumpers with their M-shaped or Z-shaped geometry create wake interference between the legs. The result: some configurations suppress VIV that would otherwise occur on a straight pipe, while others amplify it.

The 33% vs. 13% pass rate comes down to the effective aspect ratio of the exposed leg. Jumpers with short horizontal runs and long vertical legs behave closer to a single riser and respond better to standard VIV suppression. Jumpers with long horizontal spans act like a pair of coupled cylinders.

What this means for installation planning: do not use a generic VIV screening criterion for jumper lowering. The geometry-specific check is not harder to run, but it gives a completely different answer.

**CTA**: Have you seen VIV issues during rigid jumper installation? Curious whether anyone has field measurements to compare against the analytical predictions.

**Image**: Demo 5 chart --- VIV pass rate comparison by jumper geometry type, bar chart with pipe baseline
**Hashtags**: #RigidJumper #VIV #SubseaInstallation #MarineOperations #DNVRPH103 #SubseaEngineering
**References**: Demo 5, DNV-RP-H103, DNV-OS-F101

---

### Post 8 (Wednesday) --- Engagement: Standards Proliferation

**Hook**:
There are now 14 DNV standards that reference pipeline wall thickness. In 2005 there were 4.

**Body**:
I keep a database of offshore engineering standards mapped to calculation methods. The growth over the past 20 years is striking.

Wall thickness alone is referenced in DNV-ST-F101, DNV-OS-F101 (legacy), API RP 1111, PD 8010-1, PD 8010-2, ISO 13623, ASME B31.4, ASME B31.8, CSA Z662, AS 2885, and several more. Each one has slightly different safety factors, slightly different load combinations, slightly different corrosion treatment.

The intent is good --- more guidance for more situations. The reality is that young engineers spend more time navigating the standards maze than applying engineering judgment. I have seen projects where the code comparison study (which code to use?) takes longer than the actual wall thickness calculation.

This is exactly the problem parametric screening solves. Instead of debating which code gives the "right" answer, run all of them and show the client where they agree and where they diverge.

**CTA**: What is the most standards you have had to cross-reference for a single calculation? I think my record is 6 for a sour service pipeline in the North Sea.

**Image**: Text post with a table graphic showing the standards count growth by decade
**Hashtags**: #DNV #PipelineDesign #EngineeringStandards #OffshorePipeline #SubseaEngineering #API
**References**: Standards database, Demo 2 multi-code comparison

---

### Post 9 (Friday) --- Demo Showcase: Cathodic Protection

**Hook**:
Your anode sled was designed for 25-year life. But the current density assumption came from a 1990 JIP. Time to re-check.

**Body**:
Cathodic protection design per DNV-RP-B401 is straightforward in principle: calculate current demand, size anodes, check design life. In practice, the result is extremely sensitive to the assumed current density and coating breakdown factor.

I run CP screening for pipeline and subsea structures with parametric variation on the two inputs that matter most: current density (which depends on temperature, depth, and seawater resistivity) and coating breakdown (which depends on coating system and service history).

The pattern I see repeatedly: designs from 10-15 years ago used mean current density values from JIP data that predates modern deepwater experience. Actual field measurements from surveys show higher current demand in deepwater, especially below 1,500m where temperature profiles differ from the shallow-water data the original JIP was based on.

Running a quick parametric check with updated current density data can tell you whether your remaining anode life is 15 years or 5 years. That changes your integrity management plan significantly.

**CTA**: Pipeline integrity engineers --- have you seen CP surveys that diverged significantly from the original design predictions? What drove the difference?

**Image**: CP demo output --- anode life sensitivity chart (life vs. current density, parametric on coating breakdown)
**Hashtags**: #CathodicProtection #DNVRPB401 #PipelineIntegrity #SubseaEngineering #CorrosionProtection #NACE
**References**: CP demo, DNV-RP-B401, NACE SP0169

---

## Week 4: Convert Interest

### Post 10 (Monday) --- Technical Insight: Overnight Engineering

**Hook**:
Monday morning: your client changes the pipe size. Monday evening: you have 680 updated freespan results. That is the real value.

**Body**:
The first parametric run is impressive. The second run is where the business case lives.

Traditional engineering: client changes one input assumption, engineer re-does 3 weeks of analysis. Consulting firm bills another $20K-40K. Client hesitates to explore alternatives because each iteration costs real money.

Parametric screening: client changes one input, engineer updates the config file, re-runs overnight. The incremental cost is effectively zero. The client gets to explore 5 alternatives instead of 1, and the final design is better for it.

I have had clients change their pipe catalog three times during FEED. Each time, the updated wall thickness comparison, freespan screening, and pipelay feasibility study was delivered within 24 hours. The total cost of those three re-runs was less than what a single manual re-analysis would have cost.

This is not about being cheaper. It is about letting the engineering drive the design decisions instead of the budget constraining how many options get studied.

**CTA**: What is the most design iterations you have gone through on a single project? And did the budget allow proper re-analysis each time, or did you end up hand-waving?

**Image**: Workflow diagram: input change --> config update --> overnight run --> morning delivery
**Hashtags**: #EngineeringAutomation #OffshorePipeline #SubseaEngineering #FEED #ParametricDesign #DigitalEngineering
**References**: General methodology, Demos 1-5

---

### Post 11 (Wednesday) --- Demo Showcase: Full Pipeline

**Hook**:
1,292 cases. 5 disciplines. One pipeline route. Everything your FEED team needs before the detailed design kick-off.

**Body**:
Here is what a full parametric screening package looks like for a deepwater pipeline:

Wall thickness: 72 cases across 3 codes, every pipe size in the catalog. Result: 4 candidate pipe sizes that satisfy all three codes for the design conditions.

Freespan/VIV: 680 cases for those 4 pipe sizes across the expected span and current range. Result: allowable span envelope that tells the route engineer exactly where the critical zones are.

Installation feasibility: 180 cases for vessel screening. Result: 3 of 5 candidate vessels can handle the structure weights. The other 2 fail on slamming, not crane capacity.

Pipelay: 60 cases for the 4 candidate pipe sizes. Result: 2 pipe sizes are S-lay feasible at the target water depth. The other 2 need J-lay or a different vessel.

Jumper: 300 cases covering the tie-in geometry range. Result: VIV pass rate depends strongly on jumper configuration, which narrows the spool design early.

Total time: 48 hours from inputs to delivered report. Total cases: 1,292.

**CTA**: If this sounds useful for your next FEED, I will run a free screening with your actual project data. DM me or comment below.

**Image**: Composite image showing hero charts from all 5 demos arranged as a screening report cover page
**Hashtags**: #PipelineDesign #FEED #SubseaEngineering #OffshorePipeline #ParametricDesign #EngineeringAutomation
**References**: Demos 1-5, full screening package concept

---

### Post 12 (Friday) --- Engagement: Looking Ahead

**Hook**:
The offshore industry has a 30-year engineering workforce problem. Parametric tools are part of the solution --- but not the way you think.

**Body**:
The great crew change is real. Senior engineers are retiring faster than juniors are being trained. The knowledge gap is not in running software --- it is in knowing what to check, what to question, and what "reasonable" looks like for a given result.

Parametric screening tools do not replace that judgment. But they compress the learning cycle. A junior engineer who runs 72 wall thickness cases across 3 codes and then reviews every result against the governing criteria learns more in a day than they would in a month of single-case analysis.

The tool becomes a teaching environment. "Why does API govern here but DNV governs there?" becomes a concrete question with a concrete answer in the data, not an abstract discussion about safety philosophy.

I built these tools because I wanted to do better engineering faster. But the unexpected benefit is that they make it easier to train the next generation of engineers to think parametrically instead of point-by-point.

**CTA**: Senior engineers --- what is the one thing you wish junior engineers understood better about offshore design? Genuine question. I am collecting these to build better training workflows.

**Image**: Text post (engagement/reflection posts work best without images on LinkedIn)
**Hashtags**: #OffshoreEngineering #SubseaEngineering #EngineeringEducation #GreatCrewChange #KnowledgeTransfer #EngineeringAutomation
**References**: General methodology, workforce development angle

---

## Content Performance Tracking

| Post # | Date | Type | Topic | Impressions | Reactions | Comments | Shares |
|--------|------|------|-------|-------------|-----------|----------|--------|
| 1 | W1 Mon | Demo | Wall Thickness | | | | |
| 2 | W1 Wed | Technical | Splash Zone | | | | |
| 3 | W1 Fri | Engagement | Automation Philosophy | | | | |
| 4 | W2 Mon | Demo | Freespan VIV | | | | |
| 5 | W2 Wed | Technical | S-N Curves | | | | |
| 6 | W2 Fri | Demo | Pipelay Catenary | | | | |
| 7 | W3 Mon | Technical | Jumper VIV | | | | |
| 8 | W3 Wed | Engagement | Standards Proliferation | | | | |
| 9 | W3 Fri | Demo | Cathodic Protection | | | | |
| 10 | W4 Mon | Technical | Overnight Re-runs | | | | |
| 11 | W4 Wed | Demo | Full Pipeline Package | | | | |
| 12 | W4 Fri | Engagement | Workforce / Training | | | | |

## Engagement Rules

1. **Reply to every comment** within 4 hours. Technical questions get detailed answers. Agreement gets a "thanks" and a follow-up question.
2. **Tag relevant people** in demo posts if they have publicly discussed the topic (e.g., someone who posted about VIV screening).
3. **Cross-post demo GIFs** to relevant LinkedIn groups (SPE Digital Energy, Subsea Engineering Network).
4. **Never hard-sell**. Every post should be useful even if the reader never hires you. The CTA is always "engage with me" not "buy from me."
5. **Track what works**. If technical insight posts outperform demo showcases, shift the mix. If engagement posts generate more DMs, increase frequency.

## Month 2 Planning Triggers

- If W1-W2 demos get >50 reactions average: create video walkthroughs (2-3 min each)
- If engagement posts generate DMs: shift to 50% engagement / 30% demo / 20% technical
- If impressions plateau: test posting at noon CST instead of 7am
- If mooring/riser modules get demo packaging: add Demos 6-7 to the content rotation
- If a post goes viral (>500 reactions): immediately follow up with a deeper technical dive on the same topic
