---
name: pandoc-9-lua-filters
description: 'Sub-skill of pandoc: 9. Lua Filters.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 9. Lua Filters

## 9. Lua Filters


```lua
-- filters/word-count.lua
-- Count words in document

local word_count = 0

function Str(el)
    word_count = word_count + 1
    return el
end

function Pandoc(doc)
    print("Word count: " .. word_count)
    return doc
end
```

```lua
-- filters/uppercase-headers.lua
-- Convert all headers to uppercase

function Header(el)
    return pandoc.walk_block(el, {
        Str = function(s)
            return pandoc.Str(string.upper(s.text))
        end
    })
end
```

```lua
-- filters/remove-links.lua
-- Remove all hyperlinks, keeping text

function Link(el)
    return el.content
end
```

```lua
-- filters/custom-blocks.lua
-- Convert custom div blocks to styled output

function Div(el)
    if el.classes:includes("warning") then
        -- For LaTeX output
        local latex_begin = pandoc.RawBlock('latex',
            '\\begin{tcolorbox}[colback=yellow!10,colframe=orange]')
        local latex_end = pandoc.RawBlock('latex', '\\end{tcolorbox}')

        table.insert(el.content, 1, latex_begin)
        table.insert(el.content, latex_end)
        return el.content
    end

    if el.classes:includes("info") then
        local latex_begin = pandoc.RawBlock('latex',
            '\\begin{tcolorbox}[colback=blue!5,colframe=blue!50]')
        local latex_end = pandoc.RawBlock('latex', '\\end{tcolorbox}')

        table.insert(el.content, 1, latex_begin)
        table.insert(el.content, latex_end)
        return el.content
    end
end
```

```lua
-- filters/include-files.lua
-- Include content from external files

function CodeBlock(el)
    if el.classes:includes("include") then
        local file = io.open(el.text, "r")
        if file then
            local content = file:read("*all")
            file:close()

            -- Get file extension for syntax highlighting
            local ext = el.text:match("%.(%w+)$")
            local lang = ext or ""

            return pandoc.CodeBlock(content, {class = lang})
        end
    end
end
```

```bash
# Use Lua filters
pandoc document.md -o document.pdf \
    --lua-filter=filters/uppercase-headers.lua \
    --lua-filter=filters/custom-blocks.lua

# Chain multiple filters
pandoc document.md -o document.pdf \
    --filter pandoc-crossref \
    --lua-filter=filters/custom-blocks.lua \
    --citeproc
```
