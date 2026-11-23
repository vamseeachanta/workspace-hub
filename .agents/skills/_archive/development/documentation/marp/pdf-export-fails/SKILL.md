---
name: marp-pdf-export-fails
description: 'Sub-skill of marp: PDF Export Fails (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# PDF Export Fails (+3)

## PDF Export Fails


```bash
# Specify Chrome path
marp slides.md -o slides.pdf --chrome-path /usr/bin/chromium-browser

# Use Chrome arguments for headless environments
marp slides.md -o slides.pdf \
  --chrome-arg=--no-sandbox \
  --chrome-arg=--disable-setuid-sandbox
```


## Images Not Loading


```bash
# Enable local file access
marp slides.md -o slides.pdf --allow-local-files

# Use relative paths from markdown file location
![](./images/photo.png)
```


## Custom Theme Not Applied


```bash
# Specify theme file path
marp slides.md --theme ./themes/custom.css -o slides.html

# Ensure theme has correct header comment
# /* @theme custom-theme */
```


## Debug Mode


```bash
marp slides.md -o slides.pdf --debug
marp --version
```
