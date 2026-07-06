> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-06
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_add_lessons_routes_to_docs_lessons.md

---
name: feedback_add_lessons_routes_to_docs_lessons
description: "\"add lessons: <url>\" requests → source-attributed markdown notes under workspace-hub docs/lessons/"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 10d3e147-935c-4f1a-bd41-cd62beac98ae
---

When the user says **"add lessons: \<url\>"** (or pastes article/LinkedIn URLs to capture as lessons), fetch each source and write a source-attributed markdown note under `workspace-hub/docs/lessons/`. Do NOT route these to `knowledge/wikis/`.

**Why:** 2026-06-22 the user chose `docs/lessons/` markdown notes over the `knowledge/wikis/` corpus and over `.claude/memory/*-lessons.md`. These captures are **named-author practitioner/reference material** (LinkedIn posts, blog Q&A guides), not vendor-licensed standards — so `codes-standards-data-routing` does NOT force them into the private llm-wiki, and the wiki's frontmatter/provenance ceremony is unwanted overhead for raw captures. The existing `.claude/memory/*-lessons.md` files are a different genre (tool-API gotchas: orcawave/aqwa).

**How to apply:**
1. Fetch each URL (WebFetch). One note per source.
2. Filename: `docs/lessons/YYYY-MM-DD-<slug>.md`.
3. Body header: source URL, author, domain, capture date, type (practitioner methodology / reference), then distilled bullets, then a "Why it matters here" tie-in to the user's work (BSEE reservoir, digitalmodel marine, etc.).
4. Keep `docs/lessons/README.md` index table updated (Date | Note | Domain).
5. Commit on a feature branch off `main`, push, open PR — do not commit to `main`. Docs-only ⇒ pre-push gate fails on UNRELATED tier-1 issues (assetutilities test fails, digitalmodel ruff baseline) and is irrelevant; bypass with the hook's audited `GIT_PRE_PUSH_SKIP=1` (logs to `logs/hooks/pre-push-bypass.jsonl`), not `--no-verify`. See [[feedback_prepush_no_verify_allowed_on_feature_branch]].

First instance: PR #3228 (3 notes — Campillo geomodeling, Schlömilch marine-analysis-timing, naval-arch interview fundamentals).
