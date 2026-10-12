---
name: algorithmic-art
description: Create generative art using p5.js with seeded randomness and interactive
  exploration. Use for computational aesthetics, parametric design, particle systems,
  noise fields, and procedural generation.
type: reference
version: 2.0.0
category: business
last_updated: 2026-01-02
related_skills:
- canvas-design
- frontend-design
- web-artifacts-builder
capabilities: []
requires: []
tags: []
---

# Algorithmic Art

## Overview

Create generative art using p5.js with seeded randomness and interactive exploration. Beauty emerges from algorithmic execution rather than static composition.

## When to Use

- Creating generative art with reproducible randomness
- Building interactive visual explorations
- Implementing particle systems and flow fields
- Designing parametric compositions
- Procedural pattern generation
- Art that rewards exploration through seed navigation

## Quick Start

1. **Write algorithmic philosophy** (how art emerges from code)
2. **Set up p5.js template** with seed controls
3. **Implement core algorithm** (noise, particles, recursion)
4. **Add parameter controls** for exploration
5. **Enable seed navigation** for reproducibility

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
</head>
<body>
<script>
let seed = 0;

function setup() {
  createCanvas(800, 800);
  generate();
}

function generate() {
  randomSeed(seed);
  noiseSeed(seed);
  background(10);

*See sub-skills for full details.*

## Related Skills

- [canvas-design](../canvas-design/SKILL.md) - Static visual art
- [frontend-design](../frontend-design/SKILL.md) - Web interface design
- [web-artifacts-builder](../../builders/web-artifacts-builder/SKILL.md) - Self-contained HTML apps

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with p5.js templates, seeded randomness, noise fields, particle systems, recursive structures

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Phase 1: Algorithmic Philosophy (+1)](phase-1-algorithmic-philosophy/SKILL.md)
- [Core Principle: Seeded Reproducibility](core-principle-seeded-reproducibility/SKILL.md)
- [Template Structure](template-structure/SKILL.md)
- [Noise Fields (+2)](noise-fields/SKILL.md)
- [Philosophy-Driven Implementation](philosophy-driven-implementation/SKILL.md)
