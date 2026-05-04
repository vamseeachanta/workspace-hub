---
name: orcaflex-static-debug-quick-checks
description: 'Sub-skill of orcaflex-static-debug: Quick Checks (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Quick Checks (+3)

## Quick Checks


- [ ] Water depth is correct
- [ ] All lines have valid line types
- [ ] End connections are properly defined
- [ ] Vessel/buoy initial positions are reasonable
- [ ] No objects at exactly the same position
- [ ] Waves are disabled for pure statics


## Line Checks


- [ ] Line lengths exceed minimum span
- [ ] Segment lengths are appropriate
- [ ] Line type properties are valid (EA, mass, diameter)
- [ ] End connections reference existing objects
- [ ] Anchor depths match water depth


## Vessel/Buoy Checks


- [ ] Displacement and draft are correct
- [ ] COG position is realistic
- [ ] RAO data is loaded (if applicable)
- [ ] Connection points are valid


## Environment Checks


- [ ] Current profile is reasonable
- [ ] Water depth matches model
- [ ] Seabed elevation is correct
