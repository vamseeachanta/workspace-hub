---
name: slack-gif-creator
description: Create custom animated GIFs for Slack reactions and celebrations. Use for team milestones, custom emoji reactions, inside jokes, and workplace fun.
---

# Slack GIF Creator Skill

## Overview

Create custom animated GIFs for Slack workspaces, including celebration GIFs, reaction GIFs, and custom emoji animations. These add personality and fun to team communications.

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
        output_path: Where to save the GIF
        frames: Number of animation frames
        size: GIF dimensions (width, height)
    """
    images = []

    for i in range(frames):
        # Create frame
        img = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Animation effect: pulse/scale
        scale = 0.8 + 0.2 * abs(i - frames//2) / (frames//2)
        font_size = int(24 * scale)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        # Draw with color variation
        hue_shift = int(255 * i / frames)
        color = (255, hue_shift, 100)
        draw.text((x, y), text, font=font, fill=color)

        images.append(img)

    # Save as GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=100,
        loop=0,
        transparency=0,
        disposal=2
    )

# Usage
create_text_gif("SHIPPED!", "shipped.gif")
create_text_gif("LGTM", "lgtm.gif")
```

### Method 2: Python with moviepy (Video-to-GIF)

```python
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

def video_to_slack_gif(video_path, output_path, start=0, duration=3, text=None):
    """
    Convert video clip to Slack-optimized GIF.

    Args:
        video_path: Source video file
        output_path: Output GIF path
        start: Start time in seconds
        duration: Duration in seconds
        text: Optional text overlay
    """
    # Load and trim video
    clip = VideoFileClip(video_path).subclip(start, start + duration)

    # Resize for Slack (max 128px for emoji, larger for messages)
    clip = clip.resize(height=128)

    # Add text overlay if provided
    if text:
        txt_clip = TextClip(
            text,
            fontsize=20,
            color='white',
            stroke_color='black',
            stroke_width=1,
            font='DejaVu-Sans-Bold'
        ).set_position('bottom').set_duration(clip.duration)

        clip = CompositeVideoClip([clip, txt_clip])

    # Optimize for file size
    clip.write_gif(
        output_path,
        fps=10,
        program='ffmpeg',
        opt='nq'  # Optimize quality
    )

# Usage
video_to_slack_gif("celebration.mp4", "party.gif", text="🎉 SHIPPED!")
```

### Method 3: Frame-by-Frame Animation

```python
from PIL import Image, ImageDraw
import math

def create_spinner_gif(output_path, size=64, frames=12):
    """Create loading spinner GIF."""
    images = []

    for frame in range(frames):
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        center = size // 2
        radius = size // 3

        for i in range(8):
            angle = (i / 8) * 2 * math.pi - math.pi / 2
            angle += (frame / frames) * 2 * math.pi

            x = center + int(radius * math.cos(angle))
            y = center + int(radius * math.sin(angle))

            # Fade based on position
            alpha = int(255 * (1 - i / 8))
            dot_radius = 4 - i // 3

            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=(100, 100, 255, alpha)
            )

        images.append(img)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=80,
        loop=0,
        transparency=0,
        disposal=2
    )

def create_confetti_gif(output_path, size=(128, 128), frames=20):
    """Create confetti celebration GIF."""
    import random

    # Generate confetti particles
    particles = []
    colors = [(255, 107, 107), (78, 205, 196), (255, 230, 109), (170, 111, 255)]

    for _ in range(30):
        particles.append({
            'x': random.randint(0, size[0]),
            'y': random.randint(-size[1], 0),
            'speed': random.uniform(3, 8),
            'color': random.choice(colors),
            'size': random.randint(3, 6),
            'wobble': random.uniform(0, math.pi * 2)
        })

    images = []

    for frame in range(frames):
        img = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        for p in particles:
            # Update position
            p['y'] += p['speed']
            p['wobble'] += 0.3
            x_offset = math.sin(p['wobble']) * 10

            # Reset if off screen
            if p['y'] > size[1]:
                p['y'] = -10
                p['x'] = random.randint(0, size[0])

            # Draw particle
            x = int(p['x'] + x_offset)
            y = int(p['y'])
            s = p['size']

            draw.rectangle([x, y, x + s, y + s], fill=p['color'])

        images.append(img)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=50,
        loop=0,
        transparency=0,
        disposal=2
    )

# Usage
create_spinner_gif("loading.gif")
create_confetti_gif("celebration.gif")
```

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
        output_path: Optimized output
        max_size_kb: Target max file size
    """
    # Use gifsicle for optimization
    subprocess.run([
        'gifsicle',
        '--optimize=3',
        '--colors', '64',
        '--lossy=80',
        '-o', output_path,
        input_path
    ])

    # Check size and reduce further if needed
    import os
    size_kb = os.path.getsize(output_path) / 1024

    if size_kb > max_size_kb:
        # Reduce colors further
        subprocess.run([
            'gifsicle',
            '--colors', '32',
            '--lossy=100',
            '-o', output_path,
            output_path
        ])

def resize_for_emoji(input_path, output_path, size=64):
    """Resize GIF for Slack emoji (maintaining animation)."""
    subprocess.run([
        'gifsicle',
        '--resize', f'{size}x{size}',
        '--optimize=3',
        '-o', output_path,
        input_path
    ])
```

## Common Celebration GIFs

### "Ship It" Animation

```python
def create_ship_it_gif(output_path):
    """Create 'Ship It!' celebration GIF with rocket."""
    from PIL import Image, ImageDraw, ImageFont

    frames = 15
    size = (128, 128)
    images = []

    for i in range(frames):
        img = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Background gradient effect
        progress = i / frames

        # Rocket emoji position (moving up)
        rocket_y = int(100 - (progress * 80))
        draw.text((50, rocket_y), "🚀", font=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 30) if os.path.exists("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf") else ImageFont.load_default())

        # "SHIPPED!" text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()

        draw.text((30, 100), "SHIPPED!", font=font, fill=(255, 100, 100))

        images.append(img)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=100,
        loop=0
    )
```

## Dependencies

```bash
# Required packages
pip install Pillow moviepy

# Optional for optimization
# macOS
brew install gifsicle

# Ubuntu/Debian
sudo apt-get install gifsicle

# For video conversion
pip install ffmpeg-python
```

## Best Practices

### Design Guidelines

1. **Keep it simple**: Slack GIFs are small, avoid complex details
2. **High contrast**: Ensure visibility in both light and dark mode
3. **Smooth loops**: End frame should transition to start frame
4. **Appropriate length**: 1-3 seconds for reactions, up to 5 for celebrations

### Technical Guidelines

1. **Frame rate**: 10-15 FPS is sufficient
2. **Colors**: Limit to 64-128 for smaller files
3. **Transparency**: Use for irregular shapes
4. **Disposal**: Use disposal=2 for transparency

### Content Guidelines

1. **Work-appropriate**: Keep it professional
2. **Inclusive**: Avoid content that could exclude
3. **On-brand**: Match company culture
4. **Clear meaning**: The GIF's purpose should be obvious

---

## Version History

- **1.0.0** (2024-10-15): Initial release with PIL/Pillow, moviepy methods, Slack optimization, celebration GIF templates
