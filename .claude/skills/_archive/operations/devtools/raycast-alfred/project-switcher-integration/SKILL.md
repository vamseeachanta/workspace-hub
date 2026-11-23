---
name: raycast-alfred-project-switcher-integration
description: 'Sub-skill of raycast-alfred: Project Switcher Integration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Project Switcher Integration

## Project Switcher Integration


```tsx
// src/project-switcher.tsx
// ABOUTME: Unified project switcher
// ABOUTME: Integrates with multiple project sources

import {
  ActionPanel,
  Action,
  List,
  Icon,
  LocalStorage,
  getPreferenceValues,
} from "@raycast/api";
import { useState, useEffect } from "react";
import { exec } from "child_process";
import { promisify } from "util";
import fs from "fs";
import path from "path";

const execAsync = promisify(exec);

interface Preferences {
  projectDirs: string;
  githubEnabled: boolean;
  gitlabEnabled: boolean;
}

interface Project {
  name: string;
  path: string;
  source: "local" | "github" | "gitlab";
  url?: string;
  lastAccessed?: number;
}

export default function Command() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const preferences = getPreferenceValues<Preferences>();

  useEffect(() => {
    loadAllProjects();
  }, []);

  async function loadAllProjects() {
    const allProjects: Project[] = [];

    // Load local projects
    const dirs = preferences.projectDirs.split(",").map((d) => d.trim());
    for (const dir of dirs) {
      const expandedDir = dir.replace("~", process.env.HOME || "");
      if (fs.existsSync(expandedDir)) {
        const entries = fs.readdirSync(expandedDir, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith(".")) {
            allProjects.push({
              name: entry.name,
              path: path.join(expandedDir, entry.name),
              source: "local",
            });
          }
        }
      }
    }

    // Load access times
    const accessJson = await LocalStorage.getItem<string>("project-access");
    const accessTimes = accessJson ? JSON.parse(accessJson) : {};

    allProjects.forEach((p) => {
      p.lastAccessed = accessTimes[p.path] || 0;
    });

    // Sort by last accessed
    allProjects.sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0));

    setProjects(allProjects);
    setIsLoading(false);
  }

  async function openProject(project: Project, app: string) {
    const cmd =
      app === "code"
        ? `code "${project.path}"`
        : app === "terminal"
        ? `open -a Terminal "${project.path}"`
        : `open "${project.path}"`;

    await execAsync(cmd);

    // Update access time
    const accessJson = await LocalStorage.getItem<string>("project-access");
    const accessTimes = accessJson ? JSON.parse(accessJson) : {};
    accessTimes[project.path] = Date.now();
    await LocalStorage.setItem("project-access", JSON.stringify(accessTimes));
  }

  const sourceIcons = {
    local: Icon.Folder,
    github: Icon.Globe,
    gitlab: Icon.Globe,
  };

  return (
    <List isLoading={isLoading} searchBarPlaceholder="Search projects...">
      {projects.map((project) => (
        <List.Item
          key={project.path}
          title={project.name}
          subtitle={project.path}
          icon={sourceIcons[project.source]}
          accessories={[
            project.lastAccessed
              ? { text: new Date(project.lastAccessed).toLocaleDateString() }
              : {},
          ]}
          actions={
            <ActionPanel>
              <Action
                title="Open in VS Code"
                icon={Icon.Code}
                onAction={() => openProject(project, "code")}
              />
              <Action
                title="Open in Terminal"
                icon={Icon.Terminal}
                onAction={() => openProject(project, "terminal")}
              />
              <Action
                title="Open in Finder"
                icon={Icon.Finder}
                onAction={() => openProject(project, "finder")}
              />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```
