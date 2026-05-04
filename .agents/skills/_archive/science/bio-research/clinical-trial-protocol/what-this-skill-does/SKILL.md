---
name: clinical-trial-protocol-what-this-skill-does
description: 'Sub-skill of clinical-trial-protocol: What This Skill Does.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# What This Skill Does

## What This Skill Does


Starting with an intervention idea (device or drug), this orchestrated workflow offers two modes:

**Research Only Mode (Steps 0-1):**
0. **Initialize Intervention** - Collect device or drug information
1. **Research Similar Protocols** - Find similar trials, FDA guidance, and published protocols
   - **Deliverable:** Comprehensive research summary as formatted .md artifact

**Full Protocol Mode (Steps 0-5):**
0. **Initialize Intervention** - Collect device or drug information
1. **Research Similar Protocols** - Find similar trials, FDA guidance, and published protocols
2. **Protocol Foundation** - Generate protocol sections 1-6 (foundation, design, population)
3. **Protocol Intervention** - Generate protocol sections 7-8 (intervention details)
4. **Protocol Operations** - Generate protocol sections 9-12 (assessments, statistics, operations)
5. **Generate Protocol** - Create professional file ready for stakeholder review
