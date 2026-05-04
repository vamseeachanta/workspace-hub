---
name: algorithmic-art-noise-fields
description: 'Sub-skill of algorithmic-art: Noise Fields (+2).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Noise Fields (+2)

## Noise Fields


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

## Particle Systems


```javascript
let particles = [];
for (let i = 0; i < 500; i++) {
  particles.push({ x: random(width), y: random(height), vx: 0, vy: 0 });
}

function draw() {
  background(10, 10, 20, 20);
  for (let p of particles) {
    let angle = noise(p.x * 0.01, p.y * 0.01) * TWO_PI * 2;

*See sub-skills for full details.*

## Recursive Structures


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
