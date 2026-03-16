---
name: raycast-alfred-2-raycast-typescript-extensions
description: 'Sub-skill of raycast-alfred: 2. Raycast TypeScript Extensions.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Raycast TypeScript Extensions

## 2. Raycast TypeScript Extensions


```tsx
// src/index.tsx
// ABOUTME: Raycast extension main command
// ABOUTME: Project launcher with favorites and recent

import {
  ActionPanel,
  Action,
  List,
  Icon,
  LocalStorage,
  showToast,
  Toast,
  getPreferenceValues,
} from "@raycast/api";
import { useState, useEffect } from "react";
import { exec } from "child_process";
import { promisify } from "util";
import fs from "fs";
import path from "path";

const execAsync = promisify(exec);

interface Preferences {
  projectsDir: string;
  editor: string;
}

interface Project {
  name: string;
  path: string;
  lastOpened?: number;
  isFavorite?: boolean;
}

export default function Command() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const preferences = getPreferenceValues<Preferences>();

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const projectsDir = preferences.projectsDir.replace("~", process.env.HOME || "");
      const dirs = fs.readdirSync(projectsDir, { withFileTypes: true });

      // Load favorites and recent from storage
      const favoritesJson = await LocalStorage.getItem<string>("favorites");
      const recentJson = await LocalStorage.getItem<string>("recent");

      const favorites = favoritesJson ? JSON.parse(favoritesJson) : [];
      const recent = recentJson ? JSON.parse(recentJson) : {};

      const projectList: Project[] = dirs
        .filter((dir) => dir.isDirectory() && !dir.name.startsWith("."))
        .map((dir) => ({
          name: dir.name,
          path: path.join(projectsDir, dir.name),
          lastOpened: recent[dir.name] || 0,
          isFavorite: favorites.includes(dir.name),
        }))
        .sort((a, b) => {
          // Favorites first, then by recent
          if (a.isFavorite && !b.isFavorite) return -1;
          if (!a.isFavorite && b.isFavorite) return 1;
          return (b.lastOpened || 0) - (a.lastOpened || 0);
        });

      setProjects(projectList);
    } catch (error) {
      showToast({
        style: Toast.Style.Failure,
        title: "Failed to load projects",
        message: String(error),
      });
    } finally {
      setIsLoading(false);
    }
  }

  async function openProject(project: Project) {
    try {
      const editor = preferences.editor || "code";
      await execAsync(`${editor} "${project.path}"`);

      // Update recent
      const recentJson = await LocalStorage.getItem<string>("recent");
      const recent = recentJson ? JSON.parse(recentJson) : {};
      recent[project.name] = Date.now();
      await LocalStorage.setItem("recent", JSON.stringify(recent));

      showToast({
        style: Toast.Style.Success,
        title: `Opened ${project.name}`,
      });
    } catch (error) {
      showToast({
        style: Toast.Style.Failure,
        title: "Failed to open project",
        message: String(error),
      });
    }
  }

  async function toggleFavorite(project: Project) {
    const favoritesJson = await LocalStorage.getItem<string>("favorites");
    const favorites = favoritesJson ? JSON.parse(favoritesJson) : [];

    if (project.isFavorite) {
      const index = favorites.indexOf(project.name);
      if (index > -1) favorites.splice(index, 1);
    } else {
      favorites.push(project.name);
    }

    await LocalStorage.setItem("favorites", JSON.stringify(favorites));
    await loadProjects();
  }

  return (
    <List isLoading={isLoading} searchBarPlaceholder="Search projects...">
      {projects.map((project) => (
        <List.Item
          key={project.path}
          title={project.name}
          subtitle={project.path}
          icon={project.isFavorite ? Icon.Star : Icon.Folder}
          accessories={[
            project.lastOpened
              ? { text: new Date(project.lastOpened).toLocaleDateString() }
              : {},
          ]}
          actions={
            <ActionPanel>
              <Action
                title="Open in Editor"
                icon={Icon.Code}
                onAction={() => openProject(project)}
              />
              <Action
                title="Open in Finder"
                icon={Icon.Finder}
                shortcut={{ modifiers: ["cmd"], key: "o" }}
                onAction={() => execAsync(`open "${project.path}"`)}
              />
              <Action
                title="Open in Terminal"
                icon={Icon.Terminal}
                shortcut={{ modifiers: ["cmd"], key: "t" }}
                onAction={() => execAsync(`open -a Terminal "${project.path}"`)}
              />
              <Action
                title={project.isFavorite ? "Remove from Favorites" : "Add to Favorites"}
                icon={project.isFavorite ? Icon.StarDisabled : Icon.Star}
                shortcut={{ modifiers: ["cmd"], key: "f" }}
                onAction={() => toggleFavorite(project)}
              />
              <Action.CopyToClipboard
                title="Copy Path"
                content={project.path}
                shortcut={{ modifiers: ["cmd", "shift"], key: "c" }}
              />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
```

```tsx
// src/search-github.tsx
// ABOUTME: GitHub repository search command
// ABOUTME: Search and open repositories

import {
  ActionPanel,
  Action,
  List,
  Icon,

*Content truncated — see parent skill for full reference.*
