# Session handover prompt — hull curvature screening, parametric forms, drawing-to-digital-twin (for a Codex agent)

Date: 2026-10-01. Previous orchestrator: Claude (session ws-34) on the dev-primary Windows workstation. Owner: the repository owner (vamseeachanta). You are continuing a chain of bounded implementation lanes. Read this whole prompt, then verify the live state with the commands in section 1 before doing anything; everything below is a snapshot and may have moved.

## 0. Operating rules (do not relax)

- Repos: `vamseeachanta/digitalmodel` (PUBLIC), `vamseeachanta/workspace-hub` (PUBLIC), `vamseeachanta/llm-wiki` (PRIVATE, generic knowledge wiki). Never write client names, vessel names, drawing numbers, host names or private paths into a public repo, an issue, a PR body or a commit message. Client drawings and models live only in the client wiki sibling and are never copied out.
- Every task maps to a GitHub issue. Each phase needs its own plan comment on the issue and the owner's explicit approval before implementation; `status:plan-approved` is applied only by the owner. Never self-approve.
- Merges are owner-run. Verify a PR is green and `mergeStateStatus == CLEAN`, then hand the owner the exact `gh pr merge <N> --squash --delete-branch --repo <owner/repo>` command. Do not merge, do not force-push. A rebased branch is pushed under a NEW name and the old remote branch deleted normally.
- Work in an isolated `git clone --no-hardlinks` per task under `C:\ws\codex-<repo>-<slug>` (set `git config core.longpaths true` for llm-wiki). Environment per clone: `uv venv --python 3.11 .venv` then `UV_NO_SOURCES=true uv pip install -e ".[test,curvature]"` (add `ezdxf` for drawing work). Never `uv sync` (sibling path deps fail). Run tests with `.venv/Scripts/python.exe -m pytest ... -p no:randomly`.
- Evidence rules: every physics or calculation result names its comparator class (closed-form, measured, cross-solver, conservation, archived-run, none); corrections are named in place, never silently amended; a mechanism is a hypothesis until read from the tool's source or output.
- Lint: new files black (24.x) and ruff clean; existing non-clean files keep their surrounding style. Modules under 400 lines, functions under 50.
- Commit style: conventional subject with `(#issue)`, body states what and why, trailer `Co-Authored-By: Codex <noreply@openai.com>`.

## 1. Verify live state first

```
gh pr list --repo vamseeachanta/digitalmodel --state open --search "hull_library OR 2241 OR 2253 OR 2272"
gh pr view 2255 --repo vamseeachanta/digitalmodel --json state,mergeStateStatus
gh pr view 2273 --repo vamseeachanta/digitalmodel --json state,mergeStateStatus
gh issue view 2170 --repo vamseeachanta/digitalmodel --comments | tail -60
gh issue view 2241 --repo vamseeachanta/digitalmodel --comments | tail -80
gh issue view 2272 --repo vamseeachanta/digitalmodel --comments | tail -60
git -C C:\ws\digitalmodel fetch --prune origin && git -C C:\ws\digitalmodel ls-remote --heads origin "codex/*"
nltest /sc_query:<your-domain>      (no logon server = your sandbox cannot start; stop and report)
```

## 2. What is landed on digitalmodel main (as of 2026-09-29)

- HullProd curvature screening adapter `hull_library/curvature_screen.py` (optional extra `[curvature]`, `hullprod` also in the `test` extra), catalog and sweep signatures, diffraction quality gate (reliability POOR blocks, monohull saddle > 0.35 warns), PCHIP station lofting in `mesh_generator.py` (#2193, #2223).
- Native BRep route `hull_library/hull_surface_brep.py` (OCP B-spline, STEP, `screen_step`, `representation="both"`) (#2227).
- Parametric monohull form generator `hull_library/parametric_form.py` (#2242, Phase 1 of #2191).
- Inventory screening script and signature table `scripts/hull_library/screen_inventory.py`, `docs/domains/hull_library/curvature-signature-{catalog.yaml,table.md}`.
- Docs: `docs/domains/hull_library/{curvature-screening,parametric-form,hullprod-curvature-screening-evaluation}.md`, plans under `docs/plans/2026-09-2*`.

## 3. Open PRs and the stacked chain (land in this order)

| Order | PR / branch | Content | State at snapshot |
|---|---|---|---|
| 1 | digitalmodel #2255 (`codex/2241-end-closure-main`) | #2241 item 1: exact end closure with finite entrance/run angles in `parametric_form.py` + `parametric_form_ends.py`; two mesh acceptance tests held as strict xfail | OPEN, CLEAN, owner to merge |
| 2 | branch `codex/2253-quad-triangulation` (no PR yet; based on the OLD end-closure tip `aab87647`) | #2253: `panel_mesh_to_trimesh(quad_split="shortest")` default, provenance field, inventory re-baselined with dated corrections | pushed |
| 3 | branch `codex/2241-winding` (no PR yet; based on `b0213e57`, the 2253 tip) | #2241 item 6: adjacency-BFS panel orientation in `HullMeshGenerator._orient_normals_outward`; generated Wigley mesh I_D 6.62 vs 6.60 reference; signature acceptance un-xfailed, end-cap share kept xfail (28.8 %, threshold was mis-specified); the #2253 broken-winding test rewritten to assert consistent winding | pushed |
| 4 | digitalmodel #2273 (`codex/2272-a1-dxf-lines-reader`, based on main) | #2272 phase A1: DXF body-plan reader `line_generator/dxf_lines_reader.py` + `dxf_entities.py`, CLI `scripts/hull_library/dxf_to_profile.py`, extra `drawings=[ezdxf]`; round trips Wigley 0.018 %, transom 0.48 %, box exact | OPEN, CLEAN, independent of the chain |
| 5 | workspace-hub #3930 | `docs/roadmaps/drawing-to-digital-twin-roadmap.md` | OPEN (docs) |
| 6 | llm-wiki #923 | three LinkedIn source pages (ShipReality ShipHULL, Li AI-FEA, Friedl tidal mooring) with index/log entries | OPEN (docs) |

Chain procedure after the owner merges #2255: in a clone, `git rebase --onto origin/main aab87647 codex/2253-quad-triangulation`, run the suite, push as `codex/2253-quad-triangulation-main`, open the PR from the saved body (see section 6), delete the old remote branch. After that merges: `git rebase --onto origin/main b0213e57 codex/2241-winding`, same steps, push as `codex/2241-winding-main`. Expected full-suite counts with the whole chain: 625 passed, 42 skipped, 3 xfailed (`tests/hydrodynamics/hull_library` + `tests/hydrodynamics/diffraction/test_quality_gates.py`).

## 4. Open issues and what each needs next

- #2170 (epic, HullProd adoption): all decisions D1–D8 approved on 2026-09-25 (workspace-hub decision page, PR #3889 merged). Only reporting remains.
- #2241 (Phase 2 of parametric forms): item 1 and item 6 implemented (chain above). Remaining items, each needing an owner-approved plan: 2 BRep validity on rounded-Cb and transom forms (statuses `geometric_singularity_nonintegrable` / `quadrature_unconverged`), 3 semi-sub and spar generators (crease-dominated caveat, screen per primitive), 4 moonpools/cutouts, 5 optimisation loop.
- #2253: implemented on the chain; close when branch 2 merges.
- #2272 (epic, drawing-to-digital-twin): A1 in #2273. Next: the OWNER converts the six DWG lines plans in `docs/domains/freecad/src/hulls` to DXF (ODA File Converter) and the reader is run on them; then plans for A2 (view segmentation, title block, scale and dimension recognition on DXF/vector PDF) and B1 (assembled structural model from midship section + frame table; geometry-derived section modulus vs `hull_girder_strength`; export to the Nastran chain).
- Known weak spots to keep honest: the mesh end-cap share on generated forms is 28.8 % (the reference itself is 28.6 %); BRep of a coarse 5-station profile is fit-sensitive; HullProd imports CAD in millimetres (`screen_step` converts lref internally).

## 5. Blockers and environment facts

- Codex sandbox lanes require a reachable domain controller (ACL setup); on 2026-09-30 `nltest` reported no logon servers and lanes could not start. Check before launching; if blocked, stop and report rather than retry.
- The classifier on the Claude side denied force-push and merges; those remain owner actions.
- Local residue to delete after the corresponding PRs merge (owner may need `takeown /f <dir> /r /d y` first because the sandbox owns `.pytest_cache`): `C:\ws\codex-digitalmodel-{2191,2241,tri,wind,a1}`, `C:\ws\codex-llm-wiki-friedl`, worktrees `C:\ws\wt-llm-wiki-sources`, `C:\ws\wt-workspace-hub-roadmap`.
- Memory pressure on the workstation has killed background watchers before; do not run long polling loops.

## 6. Saved artefacts

PR bodies written by the previous lanes are in the Claude session scratchpad and are also mirrored in each branch's last commit messages and the issue comments; when opening the chain PRs, regenerate the body from the issue comments (#2253 comment of 2026-09-27; #2241 item-6 comment of 2026-09-27) plus an "orchestrator verification" section with your own rerun counts. Plans are committed verbatim under `docs/plans/2026-09-2*-issue-*.md`.

## 7. Immediate next actions, in order

1. Run section 1; report the live state to the owner in one short message.
2. If #2255 is merged: do chain step 2 (rebase, test, new-name push, PR). If not: hand the owner the merge command and wait.
3. If #2273 is merged and the owner has produced DXF files for the six lines plans: write per-drawing YAML configs (layer names, units, station x) and run `scripts/hull_library/dxf_to_profile.py` on each, reporting read reports, hydrostatics and signatures; file results under `docs/domains/hull_library/` without drawing numbers in prose.
4. Draft the plan for #2241 item 2 or #2272 A2 (owner picks) as an issue comment; do not implement until approved.
