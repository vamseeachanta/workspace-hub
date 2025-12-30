---
name: algorithmic-art
description: Create generative art using p5.js with seeded randomness and interactive exploration. Use for computational aesthetics, parametric design, particle systems, noise fields, and procedural generation.
---

# Algorithmic Art Skill

## Overview

Create generative art using p5.js with seeded randomness and interactive exploration. Beauty emerges from algorithmic execution rather than static composition.

## Two-Phase Process

### Phase 1: Algorithmic Philosophy

Develop a computational aesthetic manifesto (4-6 paragraphs) articulating:

- How art emerges through algorithmic processes
- The role of noise fields and randomness
- Particle behaviors and interactions
- Parametric variation and control
- The relationship between order and chaos

**Key Emphasis:**
"Master-level implementation... algorithms appear as though they took countless hours to develop... craftsmanship is paramount."

### Phase 2: p5.js Implementation

Express the philosophy through code, creating:
- Self-contained interactive HTML
- Parameter controls for exploration
- Seed navigation for reproducibility
- Deterministic randomness

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

## Template Structure

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
  <style>
    body {
      margin: 0;
      display: flex;
      font-family: 'Poppins', sans-serif;
      background: #faf9f5;
    }
    #sidebar {
      width: 300px;
      padding: 20px;
      background: #f5f4f0;
      height: 100vh;
      overflow-y: auto;
    }
    #canvas-container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .control-group { margin-bottom: 20px; }
    label { display: block; margin-bottom: 5px; font-weight: 600; }
    input[type="range"] { width: 100%; }
    button { padding: 10px 20px; margin: 5px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>Seed Navigation</h2>
    <div class="control-group">
      <button onclick="prevSeed()">Previous</button>
      <button onclick="nextSeed()">Next</button>
      <button onclick="randomizeSeed()">Random</button>
    </div>
    <div class="control-group">
      <label>Seed: <span id="seedDisplay">0</span></label>
      <input type="number" id="seedInput" onchange="jumpToSeed()">
    </div>
    <h2>Parameters</h2>
    <div class="control-group">
      <label>Complexity: <span id="complexityValue">50</span></label>
      <input type="range" id="complexity" min="10" max="200" value="50" oninput="updateParam()">
    </div>
    <h2>Actions</h2>
    <button onclick="generate()">Regenerate</button>
    <button onclick="downloadArt()">Download</button>
  </div>
  <div id="canvas-container"></div>
  <script>
    let currentSeed = 0;
    let params = { complexity: 50 };

    function setup() {
      let canvas = createCanvas(800, 800);
      canvas.parent('canvas-container');
      generate();
    }

    function generate() {
      randomSeed(currentSeed);
      noiseSeed(currentSeed);
      document.getElementById('seedDisplay').textContent = currentSeed;
      background(10, 10, 20);
      // YOUR ALGORITHM HERE
    }

    function prevSeed() { currentSeed = max(0, currentSeed - 1); generate(); }
    function nextSeed() { currentSeed++; generate(); }
    function randomizeSeed() { currentSeed = floor(random(10000)); generate(); }
    function jumpToSeed() { currentSeed = int(document.getElementById('seedInput').value); generate(); }
    function updateParam() { params.complexity = int(document.getElementById('complexity').value); generate(); }
    function downloadArt() { saveCanvas('algorithmic_art_' + currentSeed, 'png'); }
  </script>
</body>
</html>
```

## Algorithm Patterns

### Noise Fields
```javascript
loadPixels();
for (let x = 0; x < width; x++) {
  for (let y = 0; y < height; y++) {
    let n = noise(x * 0.01, y * 0.01);
    let idx = (x + y * width) * 4;
    pixels[idx] = pixels[idx+1] = pixels[idx+2] = n * 255;
    pixels[idx + 3] = 255;
  }
}
updatePixels();
```

### Particle Systems
```javascript
let particles = [];
for (let i = 0; i < 500; i++) {
  particles.push({ x: random(width), y: random(height), vx: 0, vy: 0 });
}

function draw() {
  background(10, 10, 20, 20);
  for (let p of particles) {
    let angle = noise(p.x * 0.01, p.y * 0.01) * TWO_PI * 2;
    p.vx = cos(angle) * 2;
    p.vy = sin(angle) * 2;
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > width) p.x = random(width);
    if (p.y < 0 || p.y > height) p.y = random(height);
    stroke(255, 100); point(p.x, p.y);
  }
}
```

### Recursive Structures
```javascript
function fractalTree(x, y, len, angle, depth) {
  if (depth === 0 || len < 2) return;
  let x2 = x + cos(angle) * len;
  let y2 = y + sin(angle) * len;
  stroke(255, 255 - depth * 20);
  strokeWeight(depth * 0.5);
  line(x, y, x2, y2);
  let spread = random(0.3, 0.6);
  fractalTree(x2, y2, len * 0.7, angle - spread, depth - 1);
  fractalTree(x2, y2, len * 0.7, angle + spread, depth - 1);
}
```

## Philosophy-Driven Implementation

The algorithm flows from the philosophy, not from a menu of options.

- **Emergence**: Focus on particle interactions and self-organization
- **Mathematical beauty**: Golden ratio, Fibonacci, geometric precision
- **Controlled chaos**: Combine noise fields with rule-based systems

---

## Version History

- **1.0.0** (2024-10-15): Initial release with p5.js templates, seeded randomness, noise fields, particle systems, recursive structures
