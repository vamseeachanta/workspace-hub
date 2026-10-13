---
name: slack-gif-creator
description: Create custom animated GIFs for Slack reactions and celebrations. Use
  for team milestones, custom emoji reactions, inside jokes, and workplace fun.
type: reference
version: 2.0.0
category: business
last_updated: 2026-01-02
related_skills:
- internal-comms
- canvas-design
- algorithmic-art
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Slack Gif Creator

## Overview

Create custom animated GIFs for Slack workspaces, including celebration GIFs, reaction GIFs, and custom emoji animations. These add personality and fun to team communications.

## When to Use

- Celebrating team wins and milestones
- Creating custom emoji reactions
- Building "Ship it!" or "LGTM" animations
- Designing status indicators
- Adding personality to team channels
- Inside jokes and team culture building

## Quick Start

1. **Choose GIF type** (celebration, reaction, status)
2. **Select method** (PIL/Pillow for simple, moviepy for video)
3. **Create frames** with animation loop
4. **Optimize for Slack** (128x128px emoji, <200KB)
5. **Upload to workspace**

```python
from PIL import Image, ImageDraw, ImageFont

def create_shipped_gif(output_path):
    frames = []
    size = (128, 128)

    for i in range(10):
        img = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Pulsing effect
        scale = 0.8 + 0.2 * abs(i - 5) / 5
        font_size = int(20 * scale)

        draw.text((20, 50), "SHIPPED!", fill=(255, 100, 100))
        frames.append(img)

    frames[0].save(output_path, save_all=True, append_images=frames[1:],
                   duration=100, loop=0, transparency=0, disposal=2)

create_shipped_gif("shipped.gif")
```

## GIF Types

### 1. Celebration GIFs

- Team wins
- Project completions
- Work anniversaries
- Promotions
- Goal achievements
### 2. Reaction GIFs

- Approval/thumbs up variations
- "Ship it!"
- "LGTM" (Looks Good To Me)
- "Deploying..."
- Custom team expressions
### 3. Status GIFs

- "In a meeting"
- "Deep work mode"
- "Coffee break"
- "Reviewing PR"

## Creation Methods

### Method 1: Python with Pillow (Simple Animations)

```python
from PIL import Image, ImageDraw, ImageFont
import os

def create_text_gif(text, output_path, frames=10, size=(128, 128)):
    """
    Create simple animated text GIF.

    Args:
        text: Text to animate

*See sub-skills for full details.*
### Method 2: Python with moviepy (Video-to-GIF)

```python
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

def video_to_slack_gif(video_path, output_path, start=0, duration=3, text=None):
    """
    Convert video clip to Slack-optimized GIF.

    Args:
        video_path: Source video file

*See sub-skills for full details.*
### Method 3: Frame-by-Frame Animation

```python
from PIL import Image, ImageDraw
import math

def create_spinner_gif(output_path, size=64, frames=12):
    """Create loading spinner GIF."""
    images = []

    for frame in range(frames):
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))

*See sub-skills for full details.*

## Slack-Specific Optimization

### Size Requirements

| Use Case | Max Size | Recommended |
|----------|----------|-------------|
| Custom emoji | 128x128 px | 64x64 px |
| Message GIF | 500 KB | Under 200 KB |
| Profile image | 512x512 px | 256x256 px |
### Optimization Script

```python
from PIL import Image
import subprocess

def optimize_for_slack(input_path, output_path, max_size_kb=200):
    """
    Optimize GIF for Slack file size limits.

    Args:
        input_path: Source GIF

*See sub-skills for full details.*

## Related Skills

- [internal-comms](../internal-comms/SKILL.md) - Team communications
- [canvas-design](../../content-design/canvas-design/SKILL.md) - Static visual art
- [algorithmic-art](../../content-design/algorithmic-art/SKILL.md) - Generative animations

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with PIL/Pillow, moviepy methods, Slack optimization, celebration GIF templates

## Sub-Skills

- [Design Guidelines (+2)](design-guidelines/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)
