---
name: slack-gif-creator-metrics
description: 'Sub-skill of slack-gif-creator: Metrics.'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Metrics

## Metrics


| Metric | Target | How to Measure |
|--------|--------|----------------|
| File Size (emoji) | < 128 KB | File properties |
| File Size (message) | < 200 KB | File properties |
| Dimensions (emoji) | 128x128 max | Image properties |
| Frame Rate | 10-15 FPS | frame_count / duration |
| Loop Smoothness | Seamless | Visual inspection |
