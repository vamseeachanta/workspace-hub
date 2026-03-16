---
name: raycast-alfred-common-issues
description: 'Sub-skill of raycast-alfred: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Raycast extension not loading**
```bash
# Clear Raycast cache
rm -rf ~/Library/Caches/com.raycast.macos

# Rebuild extension
cd your-extension
npm run build

# Check for errors
npm run lint
```

**Issue: Alfred workflow not executing**
```bash
# Check script permissions
chmod +x workflow-script.sh

# Test script manually
./workflow-script.sh "test query"

# Check Alfred debug log
# Alfred Preferences > Workflows > Click workflow > Debug
```

**Issue: AppleScript permissions**
```applescript
-- Grant accessibility permissions
-- System Preferences > Security & Privacy > Privacy > Accessibility

-- Test permissions
tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
end tell
```


## Debug Commands


```bash
# Test Raycast script command
./script.sh "test argument"

# Test Alfred Python script
python3 workflow.py "test query" | jq

# Check Alfred workflow variables
echo $alfred_workflow_data

# Monitor Raycast logs
log stream --predicate 'subsystem == "com.raycast.macos"'
```
