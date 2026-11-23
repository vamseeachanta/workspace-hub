---
name: obsidian-file-operations
description: 'Sub-skill of obsidian: File Operations.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# File Operations

## File Operations


<% tp.file.rename("New Name") %>
<% tp.file.move("Folder/Subfolder") %>
```

**Advanced Templater Template:**
```markdown
<%*
// Prompt for project details
const projectName = await tp.system.prompt("Project Name");
const priority = await tp.system.suggester(
  ["High", "Medium", "Low"],
  ["high", "medium", "low"],
  false,
  "Select Priority"
);
const dueDate = await tp.system.prompt("Due Date (YYYY-MM-DD)",
  tp.date.now("YYYY-MM-DD", 30));

// Rename file
await tp.file.rename(projectName);

// Move to Projects folder
await tp.file.move(`Projects/${projectName}`);
-%>
---

*See sub-skills for full details.*
