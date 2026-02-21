# Plan: /mnt/ace/ Document Organisation & ABS Standards Acquisition

## Context

The user organised `/mnt/ace/` (4.6 TB technical archive) to be friendly for both AI agents and humans.
During that work, Codex produced a 10-step "drastic relocation" migration checklist that would move all
legacy project roots (`2H/`, `0_mrv/`, `Production/`, `umbilical/`) into a new
`docs/clients/{client}/projects/{project}/` hierarchy.  17 projects in `2H/` already have
`README_MIGRATED.md` pointers and are hard to find in their new locations.

Two additional gaps surfaced:
1. ABS Guidance Notes for Cathodic Protection (GN Ships Dec 2017, GN Offshore Structures Dec 2018) are
   absent from `/mnt/ace/O&G-Standards/` — existing ABS files are mislabelled under `BSI/`.
2. The migrated 2H projects are not intuitively discoverable; the Codex plan would worsen this if
   applied wholesale.

**Goal**: Capture three scoped work items, then plan their execution in priority order.

---

## Work Items to Create (via `/work`)

### WRK-277 — Audit & govern the /mnt/ace/ Codex relocation plan
**Priority**: HIGH  **Complexity**: Medium  **Route**: B (plan + cross-review)

**Problem**: Codex generated a migration checklist that proposes moving ALL legacy roots.
17 projects already partially migrated; the remaining ~200+ are untouched.  No human
approval gate was in place before the plan was drafted.

**Scope**:
- Read `/mnt/ace/docs/_templates/MIGRATION_CHECKLIST.md` and the GOVERNANCE.md
- Inventory what has already moved (17 × `README_MIGRATED.md` in `2H/`)
- Assess whether the full migration is desired, deferred, or cancelled
- Define a human-approval gate before any further files are relocated
- Produce a decision record: proceed / pause / cancel with rationale

**Acceptance**:
- Decision record committed to `/mnt/ace/docs/REORGANISATION_DECISION.md`
- No further files moved until decision record is in place
- Existing `README_MIGRATED.md` pointers verified as accurate

**Blocks**: WRK-279

---

### WRK-278 — ABS standards acquisition: create folder + download CP Guidance Notes
**Priority**: HIGH  **Complexity**: Simple  **Route**: A
**Unblocks**: WRK-269 (CP standards research)

**Problem**:
- No `ABS/` folder in `/mnt/ace/O&G-Standards/`; existing ABS PDFs are mislabelled under `BSI/`
- ABS GN Ships (Dec 2017) is only in `acma-projects/`
- ABS GN Offshore Structures (Dec 2018) is only at eagle.org (public download)
- Other ABS Guidance Notes and Rules relevant to CP and offshore structures are undiscovered

**Scope**:
1. Create `/mnt/ace/O&G-Standards/ABS/` with sub-folders:
   `Guidance-Notes/`, `Rules/`, `Notices/`
2. Move existing ABS PDFs from `BSI/` into `ABS/` with correct names
3. Copy ABS GN Ships PDF from `acma-projects/admin/` → `ABS/Guidance-Notes/`
4. Download from eagle.org (public, free):
   - ABS Guidance Notes for Cathodic Protection of Ships (Dec 2017) — if not already present
   - ABS Guidance Notes for Offshore Structures Cathodic Protection (Dec 2018)
   - Any other freely available ABS GN / Rules related to CP, offshore, and subsea
5. Index all acquired files in `/mnt/ace/O&G-Standards/ABS/INDEX.md`
6. Update `/mnt/ace/docs/DISCIPLINE_INDEX.md` to reflect ABS coverage

**Acceptance**:
- `ABS/` folder exists with ≥2 CP Guidance Notes (Ships 2017, Offshore 2018)
- INDEX.md lists every file with: title, edition/date, document number, file name
- No ABS files remain under `BSI/`
- WRK-269 CP standards research can reference these files

---

### WRK-279 — Fix 2H legacy project discoverability (navigation layer)
**Priority**: MEDIUM  **Complexity**: Simple  **Route**: A
**Blocked by**: WRK-277 (decision on migration must come first)

**Problem**: 17 projects migrated from `2H/` to `docs/clients/unknown/projects/` are hard to
find.  Original project names (e.g., "31098 - Grupo-R Piklis-1DL") do not map intuitively to
standardised slugs.  Remaining `2H/` projects have no navigation to their new locations.

**Scope**:
1. Build `/mnt/ace/2H/MIGRATION_MAP.md` — table of:
   original `2H/` folder name → new path → project description (1 line)
2. Verify each `README_MIGRATED.md` points to an existing target path; fix broken links
3. Add a `2H/INDEX.md` listing all 17 migrated projects with direct links plus the un-migrated
   projects still in-place
4. Ensure the `docs/clients/unknown/projects/` counterparts each have a `README.md` with the
   original `2H/` folder name visible in the first line

**Acceptance**:
- `2H/MIGRATION_MAP.md` exists and covers all 17 migrated projects
- All `README_MIGRATED.md` links verified live
- `2H/INDEX.md` created
- Human can find any legacy 2H project within 2 lookups

---

## Execution Order

```
WRK-277  (audit decision — no files move until done)
    └── WRK-278  (ABS download — independent, can run in parallel)
    └── WRK-279  (navigation fix — after WRK-277 decision)
```

WRK-278 is independent and can start immediately (no dependency on reorganisation decision).

---

## Implementation Steps

1. Run `/work` to capture the three items above into the work queue (WRK-277, WRK-278, WRK-279)
2. Set WRK-279 `blocked_by: WRK-277` in the work queue
3. Set WRK-278 as `unblocks: WRK-269` in the notes
4. Begin WRK-277: read MIGRATION_CHECKLIST.md + GOVERNANCE.md, produce REORGANISATION_DECISION.md
5. Begin WRK-278 in parallel: create ABS folder, move misplaced docs, download from eagle.org
6. After WRK-277 complete: begin WRK-279 navigation layer

---

## Verification

- `ls /mnt/ace/O&G-Standards/ABS/` shows GN Ships 2017 and GN Offshore Structures 2018
- `cat /mnt/ace/O&G-Standards/ABS/INDEX.md` lists all acquired files
- `cat /mnt/ace/docs/REORGANISATION_DECISION.md` exists with a clear decision
- `cat /mnt/ace/2H/MIGRATION_MAP.md` maps all 17 migrated projects
- `grep "ABS" /mnt/ace/docs/DISCIPLINE_INDEX.md` returns CP-relevant entries
- WRK-269 CP standards research can proceed without sourcing ABS docs from acma-projects
