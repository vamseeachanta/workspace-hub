---
name: obsidian-common-issues
description: 'Sub-skill of obsidian: Common Issues (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Slow performance with large vault**
```markdown
Solutions:
1. Disable unused plugins
2. Reduce graph view nodes: Settings > Graph > Filters
3. Exclude folders from search: Settings > Files & Links > Excluded files
4. Use lazy loading for Dataview
5. Split into multiple vaults if > 10,000 notes
```

**Issue: Sync conflicts**
```markdown
Solutions:
1. Close Obsidian on all devices before syncing
2. Use .sync-conflict-* in .gitignore
3. For Git sync: pull before editing
4. For iCloud: wait for sync indicator
5. Use Obsidian Sync for best experience
```

**Issue: Broken links after moving notes**
```markdown
Solutions:
1. Use Obsidian's built-in move (F2 or right-click > Move)
2. Enable "Automatically update internal links"
3. Use Consistent Attachments and Links plugin
4. Run "Find and replace in all files" for bulk fixes
```

**Issue: Images not displaying**
```markdown
Solutions:
1. Check attachment folder setting
2. Use relative paths: ![[image.png]]
3. Verify file exists in vault
4. Check file extension (case-sensitive on Linux)
5. For external images: ensure URL is accessible
```

**Issue: Plugin conflicts**
```markdown
Solutions:
1. Disable all plugins, enable one by one
2. Check plugin compatibility in settings
3. Clear plugin cache: .obsidian/plugins/*/
4. Update all plugins to latest versions
5. Check plugin GitHub for known issues
```


## Plugin Recommendations


```markdown
