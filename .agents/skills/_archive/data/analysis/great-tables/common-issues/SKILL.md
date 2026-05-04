---
name: great-tables-common-issues
description: 'Sub-skill of great-tables: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Table not displaying in Jupyter**
```python
# Solution: Ensure rich display
from great_tables import GT
table = GT(df)
display(table)  # Or just: table
```

**Issue: HTML export looks different**
```python
# Solution: Include all styling
table.save("output.html")  # Includes CSS
```

**Issue: Image export not working**
```python
# Solution: Install webshot or use playwright
pip install webshot
# or
pip install playwright
playwright install chromium

table.save("output.png", web_driver="playwright")
```

**Issue: Slow with large DataFrames**
```python
# Solution: Limit rows
df_display = df.head(100)
table = GT(df_display)
```

**Issue: Special characters not rendering**
```python
# Solution: Use html() helper
from great_tables import html
cell_content = html("&euro; 100")  # Euro symbol
```
