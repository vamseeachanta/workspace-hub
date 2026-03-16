---
name: raycast-alfred-3-alfred-workflows-applescript
description: 'Sub-skill of raycast-alfred: 3. Alfred Workflows - AppleScript.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Alfred Workflows - AppleScript

## 3. Alfred Workflows - AppleScript


```applescript
-- workflow-launcher.applescript
-- ABOUTME: Launch applications with Alfred
-- ABOUTME: AppleScript for application control

on alfred_script(q)
    set appName to q

    if appName is "" then
        return "No application specified"
    end if

    try
        tell application appName
            activate
        end tell
        return "Launched " & appName
    on error errMsg
        return "Error: " & errMsg
    end try
end alfred_script
```

```applescript
-- window-manager.applescript
-- ABOUTME: Window positioning and management
-- ABOUTME: Move and resize windows with Alfred

on alfred_script(q)
    -- Parse command: "left", "right", "top", "bottom", "maximize", "center"
    set position to q

    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell

    tell application "Finder"
        set screenBounds to bounds of window of desktop
        set screenWidth to item 3 of screenBounds
        set screenHeight to item 4 of screenBounds
    end tell

    -- Menu bar offset
    set menuBarHeight to 25

    tell application frontApp
        if position is "left" then
            set bounds of front window to {0, menuBarHeight, screenWidth / 2, screenHeight}
        else if position is "right" then
            set bounds of front window to {screenWidth / 2, menuBarHeight, screenWidth, screenHeight}
        else if position is "top" then
            set bounds of front window to {0, menuBarHeight, screenWidth, screenHeight / 2}
        else if position is "bottom" then
            set bounds of front window to {0, screenHeight / 2, screenWidth, screenHeight}
        else if position is "maximize" then
            set bounds of front window to {0, menuBarHeight, screenWidth, screenHeight}
        else if position is "center" then
            set winWidth to 1200
            set winHeight to 800
            set xPos to (screenWidth - winWidth) / 2
            set yPos to ((screenHeight - winHeight) / 2) + menuBarHeight
            set bounds of front window to {xPos, yPos, xPos + winWidth, yPos + winHeight}
        end if
    end tell

    return "Moved " & frontApp & " to " & position
end alfred_script
```

```applescript
-- clipboard-cleaner.applescript
-- ABOUTME: Clean and transform clipboard content
-- ABOUTME: Remove formatting, convert text

on alfred_script(q)
    -- Get clipboard content
    set clipContent to the clipboard

    if q is "plain" then
        -- Convert to plain text
        set the clipboard to clipContent as text
        return "Converted to plain text"

    else if q is "trim" then
        -- Trim whitespace
        set trimmed to do shell script "echo " & quoted form of clipContent & " | xargs"
        set the clipboard to trimmed
        return "Trimmed whitespace"

    else if q is "lower" then
        -- Convert to lowercase
        set lowered to do shell script "echo " & quoted form of clipContent & " | tr '[:upper:]' '[:lower:]'"
        set the clipboard to lowered
        return "Converted to lowercase"

    else if q is "upper" then
        -- Convert to uppercase
        set uppered to do shell script "echo " & quoted form of clipContent & " | tr '[:lower:]' '[:upper:]'"
        set the clipboard to uppered
        return "Converted to uppercase"

    else if q is "slug" then
        -- Convert to URL slug
        set slugged to do shell script "echo " & quoted form of clipContent & " | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'"
        set the clipboard to slugged
        return "Converted to slug: " & slugged

    end if

    return "Unknown command: " & q
end alfred_script
```
