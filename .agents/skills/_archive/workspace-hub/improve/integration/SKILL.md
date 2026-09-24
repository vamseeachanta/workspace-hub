---
name: improve-integration
description: 'Sub-skill of improve: Integration.'
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Integration

## Integration


- **Consumes** `/reflect` output from `.claude/state/patterns/`
- **Consumes** `/insights` output from session reports
- **Complements** session hooks (`capture-corrections.sh` produces signals)
- **Does NOT duplicate**: `/reflect` analyzes git history, `/improve` acts on signals
