---
name: frontend-design
description: Create distinctive, production-grade web interfaces with high design
  quality. Use for components, pages, dashboards, and full applications that need
  to stand out from generic AI aesthetics.
type: reference
version: 2.0.0
category: business
last_updated: 2026-01-02
related_skills:
- theme-factory
- web-artifacts-builder
- canvas-design
capabilities: []
requires: []
tags: []
---

# Frontend Design

## Overview

This skill enables creation of distinctive, production-grade web interfaces that prioritize high design quality and avoid generic aesthetics. It applies to components, pages, dashboards, and full applications.

## When to Use

- Building custom UI components that need visual distinction
- Creating landing pages or marketing sites
- Designing dashboards and data visualization interfaces
- Full web applications requiring cohesive design systems
- Any interface that must avoid "generic AI" aesthetics

## Quick Start

1. **Establish design direction** before coding (purpose, tone, constraints)
2. **Select distinctive typography** (avoid Inter, Roboto, Arial defaults)
3. **Create intentional color palette** with clear primary/accent roles
4. **Add purposeful motion** for micro-interactions
5. **Break visual monotony** with asymmetry and grid variations

```css
/* Quick distinctive setup */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

:root {
  --primary: #1a1a2e;
  --accent: #e94560;
  --text: #eaeaea;
}

body {
  font-family: 'Space Grotesk', sans-serif;
  background: var(--primary);
  color: var(--text);
}
```

## Related Skills

- [theme-factory](../theme-factory/SKILL.md) - Pre-built color/font themes
- [web-artifacts-builder](../../builders/web-artifacts-builder/SKILL.md) - Self-contained HTML apps
- [canvas-design](../canvas-design/SKILL.md) - Visual art generation

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with typography, color, motion, spatial design patterns, component examples, Tailwind/React integration

## Sub-Skills

- [Before Coding: Design Direction](before-coding-design-direction/SKILL.md)
- [Typography (+3)](typography/SKILL.md)
- [Generic AI Aesthetics (+1)](generic-ai-aesthetics/SKILL.md)
- [Implementation Philosophy](implementation-philosophy/SKILL.md)
- [Cards with Character (+1)](cards-with-character/SKILL.md)
- [Tailwind CSS (Custom Config) (+1)](tailwind-css-custom-config/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Philosophy](philosophy/SKILL.md)
