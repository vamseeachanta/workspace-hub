---
name: marp-integration-with-npm-project
description: 'Sub-skill of marp: Integration with npm Project (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with npm Project (+1)

## Integration with npm Project


```json
// package.json
{
  "scripts": {
    "start": "marp -s ./slides",
    "watch": "marp -w ./slides -o ./dist",
    "build": "marp ./slides --output ./dist",
    "build:pdf": "marp ./slides -o ./dist --pdf"
  },
  "devDependencies": {
    "@marp-team/marp-cli": "^3.0.0"
  }
}
```


## Integration with Makefile


```makefile
SLIDES_DIR = slides
OUTPUT_DIR = dist

.PHONY: html pdf clean serve

html:
	marp $(SLIDES_DIR)/*.md --output $(OUTPUT_DIR)

pdf:
	marp $(SLIDES_DIR)/*.md --output $(OUTPUT_DIR) --pdf --allow-local-files

clean:
	rm -rf $(OUTPUT_DIR)

serve:
	marp -s $(SLIDES_DIR)
```
