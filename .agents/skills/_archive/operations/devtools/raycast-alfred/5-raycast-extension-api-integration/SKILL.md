---
name: raycast-alfred-5-raycast-extension-api-integration
description: 'Sub-skill of raycast-alfred: 5. Raycast Extension - API Integration.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Raycast Extension - API Integration

## 5. Raycast Extension - API Integration


```tsx
// src/api-tester.tsx
// ABOUTME: API testing and debugging tool
// ABOUTME: Make HTTP requests from Raycast

import {
  ActionPanel,
  Action,
  Form,
  showToast,
  Toast,
  Clipboard,
  Detail,
  useNavigation,
} from "@raycast/api";
import { useState } from "react";
import fetch from "node-fetch";

interface RequestResult {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  body: string;
  time: number;
}

function ResultView({ result }: { result: RequestResult }) {
  const markdown = `
# Response

**Status:** ${result.status} ${result.statusText}
**Time:** ${result.time}ms
