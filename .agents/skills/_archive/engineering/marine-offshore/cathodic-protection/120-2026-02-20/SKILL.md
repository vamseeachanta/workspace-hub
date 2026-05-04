---
name: cathodic-protection-120-2026-02-20
description: 'Sub-skill of cathodic-protection: [1.2.0] - 2026-02-20 (+2).'
version: 1.2.0
category: engineering
type: reference
scripts_exempt: true
---

# [1.2.0] - 2026-02-20 (+2)

## [1.2.0] - 2026-02-20


**Added:**
- `DNV_RP_B401_offshore` route: Offshore fixed platform SACP per DNV-RP-B401 (2021 edition)
- Covers jacket structures, gravity-based structures, and topsides steel
- Zones: submerged (temp-dependent), splash, atmospheric
- Coating categories I–III and bare per B401-2021 Sec.3.4.6
- Anode types: flush-mounted, stand-off, bracelet (Dwight formula, Sec.4.9)

## [1.1.0] - 2026-02-20


**Fixed:**
- Corrected Python examples to use real `CathodicProtection().router(cfg)` API
- Added working ABS GN Ships and DNV-RP-F103 cfg examples with verified key names
- Added DNV-RP-F103 to standards table and triggers

**Removed:**
- Non-existent class imports (AnodeDesign, PipelineCP, CoatingAnalysis, ICCPDesign, etc.)
- MCP tool integration section (not applicable to engineering calculations)

## [1.0.0] - 2026-01-07


**Added:**
- Initial version metadata and dependency management
