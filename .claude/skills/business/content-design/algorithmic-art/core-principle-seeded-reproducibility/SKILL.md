---
name: algorithmic-art-core-principle-seeded-reproducibility
description: 'Sub-skill of algorithmic-art: Core Principle: Seeded Reproducibility.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Core Principle: Seeded Reproducibility

## Core Principle: Seeded Reproducibility


Same seed ALWAYS produces identical output:

```javascript
function setup() {
  createCanvas(800, 800);
  randomSeed(currentSeed);
  noiseSeed(currentSeed);
  generate();
}

function generate() {
  background(10);
  // Your algorithm here
  // Same seed = same result
}
```
