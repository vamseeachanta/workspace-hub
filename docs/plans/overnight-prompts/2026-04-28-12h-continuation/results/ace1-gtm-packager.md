# Lane C2 — GTM packager result (2026-04-28 → 2026-04-29)

> **Run window.** Start 2026-04-28 21:49:46 local. Stop target
> 2026-04-29 09:49:46 local. ace-linux-1, Claude provider.
>
> **Mode.** GTM / docs only. No code changes; no GitHub mutations.
> Output is content for the user to review and authorize.
>
> **Outputs.** Three files written, two new + this result file:
>
> - `docs/gtm/outreach-candidate-briefs-2026-04-28.md` — 10-candidate
>   evidence-bounded brief, 8-field per candidate.
> - `docs/gtm/overnight-client-ready-material-2026-04-28.md` — capability
>   blurbs, per-demo claim envelopes, three send-ready outreach scripts,
>   pre-send check, gap list, evidence-boundary library.
> - `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md`
>   — this file.
>
> **Cross-lane discipline.** No edits to other lanes' files. No GitHub
> mutations. No client-confidential corpora referenced by name (Woodfibre
> #2544 + SESA #2541 are gated by ACMA / project-owner clearance and were
> deliberately excluded from the GTM material per the lane's
> "preserve engineering evidence boundaries" rule).

---

## §1 — What was done

The lane converted shipped repo evidence — five demo HTML reports
(1,292 cases), capability summary, scope notes, knowledge corpus, and
the prospect-intake adapter scaffold — into engineering-bounded
client-ready material across two new files. The work loop in the lane
prompt was followed step-by-step:

1. **Read.** `docs/gtm/` and the most recent overnight-results
   directories
   (`2026-04-28-elements-wave/results/`,
   `2026-04-28-night-both-machines/results/`).
2. **Extract.** 10 candidates produced — 8 with shipped proof paths, 2
   marked as pipeline-narrative-only (no proof yet, kept in the brief
   to prevent future lanes from accidentally elevating them).
3. **Per-candidate.** 8-field structure: buyer problem, ACE
   proof/evidence, can-say-now, cannot-claim-yet, missing proof, next
   repo issue/action, draft outreach angle, confidence rating.
4. **Snippets.** 3 send-ready outbound emails (pipeline manager,
   heavy-lift CSV / installation contractor, LNG terminal lead).
5. **Demo follow-ups.** 3 follow-up asks calibrated to the demo the
   prospect just opened — every ask extends an existing artifact rather
   than promising new capability.
6. **Priority push list.** §3 below — ranked by time-to-revenue and gap
   size.

---

## §2 — Candidate index

| # | Candidate | Proof status | Can-ship today? | Confidence |
|---|---|---|---|---|
| 1 | Pipeline freespan / VIV (Demo 1, 680 cases) | **Shipped** — `demo_01_freespan_report.html` | Yes | High |
| 2 | Multi-code wall thickness (Demo 2, 72 cases) | **Shipped** — `demo_02_wall_thickness_report.html` | Yes | High |
| 3 | Deepwater mudmat install (Demo 3, 180 cases) | **Shipped** — `demo_03_mudmat_installation_report.html` | Yes | High (screening) / Medium (vessel-specific) |
| 4 | Shallow-water S-lay (Demo 4, 60 cases) | **Shipped** — `demo_04_shallow_pipelay_report.html` | Yes | High |
| 5 | Deepwater rigid jumper install (Demo 5, 300 cases) | **Shipped** — `demo_05_jumper_installation_report.html` | Yes | High |
| 6 | LNG marine-terminal berth-operability framing | Scope note + 40-entry knowledge corpus shipped; **2-pager not yet built** | Partial — capability blurbs OK; 2-pager needed before Snippet 3.3 ships | Medium-High |
| 7 | FOWT mooring / installation / bankability | Scope note shipped; orcaflex/orcawave modules shipped; **worked example not yet built** | Partial — capability blurbs OK; OC4-DeepCwind worked example needed | Medium-High |
| 8 | Methodology + multi-AI cross-review | 4 published-ready docs shipped; **not yet on aceengineer.com** | Yes (PDF attach); link-form blocked on #2030 | High (rigor) / Medium (outreach efficacy) |
| 9 | Prospect-data 48-hr custom-demo pipeline (#2346) | Scaffold + adapter + 13 tests shipped; `run_demo` stubbed; deliveries log empty | **No — pipeline narrative only** until first DELIVERED row | High (design) / Low (outreach use today) |
| 10 | Semiconductor CAD / FEM lane (#2507/#2509/#2510) | Plans only; no shipped artifact | **No — internal narrative only** | N/A for outreach |

---

## §3 — Priority-ranked GTM push list (morning action queue)

The list below is ordered by **shippable-impact-per-hour**. Read top
to bottom: each item names the action, the artifact it touches, the
boundary, and the next step on success.

### Tier A — Send-ready material (zero new artifacts required)

**A1. Pipeline-integrity outreach to warm contacts (Snippet 3.1).**
- *Action.* Identify 5–10 pipeline-integrity managers from the 1,281
  contact database (`docs/gtm/client-conversion-pipeline.md` §4).
  Personalize Snippet 3.1, attach Demo 1 + Demo 2 HTML reports +
  `prospect-template.yaml`.
- *Boundary.* Snippet already carries the screening-only disclaimer.
  Do **not** mention CFD VIV time-domain or ECA / sour-service in the
  body; offer them only as scoped follow-on if the prospect asks.
- *Next on response.* Send Follow-up 1 from
  `outreach-candidate-briefs-2026-04-28.md` §2.2.
- *Why first.* Demo 1 + Demo 2 are the most rigorous shipped artifacts
  (Demo 2 uses the live `digitalmodel` library; Demo 1 covers 680 cases)
  and have the cleanest evidence boundary.

**A2. Heavy-lift CSV / installation-contractor outreach (Snippet 3.2).**
- *Action.* Send Snippet 3.2 to vessel installation contractor list per
  #1669. Attach Demo 3 + Demo 5 HTML reports + capability summary PDF.
- *Boundary.* Class-typical-vessel disclaimer must be visible. If a
  prospect asks for vessel-specific recommendations without sending
  RAOs, fall back to the qualifying questions in Follow-up 2.
- *Next on response.* Send Follow-up 2.
- *Why second.* Demo 3 + Demo 5 cover the highest day-rate-leverage
  conversation (CSV utilization, jumper tie-in alignment), and the
  outreach list (#1669) already exists.

**A3. Expert-network application reinforcement.**
- *Action.* Use the per-demo capsules in
  `overnight-client-ready-material-2026-04-28.md` §2 to update GLG /
  AlphaSights / Guidepoint profile copy (#1994). The "1,292 cases
  overnight" headline is the strongest expert-network differentiator.
- *Boundary.* Do not list Candidate 9 (#2346) in the profile until it
  has a DELIVERED row. Do not list Candidate 10 (semiconductor) at all.
- *Why third.* Expert networks are the fastest path to revenue per the
  conversion pipeline; the new capsule format makes profile copy
  defensible per consultation.

### Tier B — Small-lift artifacts that unlock new outreach paths

**B1. Publish the 4 methodology docs to aceengineer.com (#2030).**
- *Action.* Deploy `docs/methodology/published/*.md` (or the HTML
  companions at `docs/gtm/website-pages/`) to aceengineer.com.
- *Effect.* Promotes Candidate 8 from "PDF attachment" to "linked
  authoritative URL". Strongest lever for engineering-manager outreach
  because the methodology language passes a senior reviewer's
  spot-check.
- *Boundary.* Verify the 4 HTML pages contain no internal-only links
  before deploy.
- *Issue.* #2030.

**B2. Add Demo 2 "Standards Compliance Note" 2-pager (companion to
Candidate 2).**
- *Action.* Cherry-pick 3 representative cases from Demo 2's 72 and
  produce a 2-page PDF that procurement reviewers can carry into spec
  meetings.
- *Effect.* Converts Candidate 2 from "engineer-tier artifact" into a
  procurement-tier artifact. High lift in expert-network consultations
  where the buyer is a procurement lead, not a senior engineer.
- *Lift.* Small — the calc engine and HTML are shipped; this is a
  formatting + selection job.
- *Issue.* Open follow-up to #2422.

**B3. Add a screencast GIF for Demo 1 or Demo 2 (#1809).**
- *Action.* Record a 30-second GIF of one demo HTML page being scrolled
  + interacted with. The first GIF is the highest-marginal-value (any
  prospect with Gmail preview gets the hook before opening attachments).
- *Effect.* Shortens prospect eval time from "I'll click later" to "I
  get it in 30 s".
- *Issue.* #1809.

### Tier C — Medium-lift artifacts that unlock new buyer segments

**C1. Public-source berth-operability decision frame 2-pager
(Candidate 6 missing-proof).**
- *Action.* Synthesize the NWS LNG long-period-swell mechanism from
  `knowledge/seeds/mooring-failures-lng-terminals.yaml` (40 entries)
  into a 2-page POV piece. No client data, no project-specific data —
  only public Woodside articles and SIGTTO context.
- *Effect.* Unblocks Snippet 3.3 (LNG terminal lead). Without this
  artifact, Snippet 3.3 cannot ship.
- *Boundary.* Stay strictly in the public-source corpus. Do **not**
  reference Woodfibre, SESA, or any ACMA-corpus content.
- *Issue.* Open new issue with this scope; cross-link
  `lng-berth-operability-framing.md` and the seed YAML.

**C2. OC4-DeepCwind FOWT mooring screening worked example (Candidate 7
missing-proof).**
- *Action.* Run a single mooring screening pass against the public OC4
  semi-sub geometry; produce a 1-pager output showing where assumptions
  need a coupled follow-up vs. where the screening result stands alone.
- *Effect.* Unblocks FOWT bankability outreach. Bankability reviewers
  need a worked example, not a scope note.
- *Lift.* Medium — single OrcaFlex run, 1-pager output, public-source
  geometry.
- *Issue.* Open new issue, cross-link `fowt-engineering-scope.md` and
  `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py`.

### Tier D — Pipeline lifts (not for morning outreach)

**D1. Drive #2346 to first DELIVERED row.**
- *Action.* Following the `IMPLEMENTATION-STATUS.md` "Not done" list:
  finish `materialize_demo_inputs` for demo_03; wire `run_demo`
  subprocess dispatch; ship `branded_report.py`; run one end-to-end
  pass against the canonical Seven Borealis intake; append a row to
  `docs/gtm/deliveries-log.md`.
- *Effect.* Promotes Candidate 9 from "pipeline narrative" to **lead
  outreach asset**. Once shipped, Candidate 9's outreach line ("send a
  YAML by Tuesday EOD, branded report Thursday EOD") becomes the
  highest-conversion message ACE has.
- *Issue.* #2346 (already `status:plan-approved` + `status:working` +
  `agent:codex`).
- *Why D, not B.* This is a multi-step engineering lift owned by Codex;
  not a content task. Tracking only.

**D2. Wire the GTM unified smoke runner (#2345).**
- *Action.* Add the 5 demos to a shared smoke-test runner so silent
  demo rot is caught before the next outreach push.
- *Effect.* Prevents an embarrassment risk where outreach attaches a
  stale or broken demo HTML.
- *Issue.* #2345.

**D3. Mooring demo (Demo 6) for station-keeping outreach (#2115).**
- *Action.* Add a sixth GTM demo focused on mooring / station-keeping —
  the gap that #2115 identifies in the demo suite. Highest-utility
  buyer segment is FPSO operators and floating-platform owners.
- *Effect.* Adds a sixth shipped artifact to the demo suite; opens a
  new outreach lane for mooring-line-replacement / re-tensioning
  conversations.
- *Issue.* #2115.

---

## §4 — What was deliberately NOT done (engineering-evidence discipline)

This lane respected a strict evidence boundary. The following were all
*intentionally excluded* from the outreach material despite being
visible in the repo:

1. **Woodfibre LNG (#2544) and SESA (#2541) corpora.** Both are
   ACMA-clearance-gated, metadata-only, and explicitly out-of-scope for
   any GTM material. Per the prior lane's `terminal-4-woodfibre.md`:
   "every confidentiality call is left for ACMA / project-owner
   review."
2. **Semiconductor lanes (#2507, #2509, #2510).** Plans only — no proof
   path. Listed as Candidate 10 with "PLAN-ONLY" warning, not
   integrated into snippets.
3. **Doc-intel MCP / embeddings work (#2400 / #2402 / #2404).**
   In-flight engineering — not yet a buyer-ready capability. No buyer
   asks "do you have an embeddings index"; they ask "do you have a
   methodology." Buyer-facing: covered by Candidate 8 (methodology),
   not by direct doc-intel mention.
4. **Mooring failure animations (#2043 / #2350).** Status-uncertain;
   not safe to cite in send-ready material until #2350 verifies render
   outputs.
5. **Manim animation pipeline (#2035 / #2037 / #2038).** Open;
   not yet shipped.
6. **Specific named-client claims.** Every snippet uses "your portfolio /
   your team / your candidate" framing — never a specific client by
   name unless that client is in a public-source citation.

---

## §5 — Verification (post-write)

| Check | Result |
|---|---|
| `docs/gtm/outreach-candidate-briefs-2026-04-28.md` exists, non-empty | yes |
| `docs/gtm/overnight-client-ready-material-2026-04-28.md` exists, non-empty | yes |
| This result file exists, non-empty | yes (this file) |
| No edits to other lanes' result files (`ace1-control-reconciler.md`, `ace1-plan-review-hardener.md`) | confirmed (only own result file written) |
| No edits to `/mnt/ace/**` or any ACMA-corpus paths | confirmed (no /mnt/ace access) |
| No GitHub mutations (no `gh issue comment`, no label changes) | confirmed (only `gh issue view` reads were used) |
| No `status:plan-approved` self-label hint in any output | confirmed |
| Each shipped-artifact reference cross-checked against actual file path | yes — five demo HTML files at `digitalmodel/examples/demos/gtm/output/*.html` confirmed via `ls -la` (sizes: 118 KB / 85 KB / 72 KB / 85 KB / 66 KB) |
| Snippet 3.3 marked "do not send until 2-pager exists" | yes — see §3 of `overnight-client-ready-material-2026-04-28.md` and Tier C1 above |

---

## §6 — Open questions for the user / control surface

Surfaced for review; not auto-resolved by this lane.

1. **Does the user want Snippets 3.1 / 3.2 sent to the contact database,
   or kept as drafts?** They are send-ready content, but the lane has
   no authority to send. Recommend the user reads §4 of the
   client-ready material file (the pre-send check) before authorizing.
2. **#2030 deploy authorization.** The 4 methodology docs are
   publication-ready and have been so for 13+ days. If the user wants
   the highest-leverage Tier-B move, this is it — but it requires the
   user to authorize the aceengineer-website deploy.
3. **Should Candidate 9 (#2346) outreach language be drafted now and
   suppressed, or held until first DELIVERED row?** Lane chose
   "drafted with HOLD label" so the content is ready when the gate
   lifts. User can override.
4. **Berth-operability 2-pager scope.** Should it be (a) a
   public-source-only POV piece that can ship immediately, or (b) wait
   for one terminal-project worked example with proper clearance? Lane
   recommends (a) as the morning's Tier-C1 lift.

---

## §7 — Status / next action

- Lane C2 result is **complete** as of the timestamp on this file.
- All three required outputs exist. The candidate brief is the deepest
  artifact (10 candidates × 8 fields); the client-ready material is
  the morning-ready packet; this result file is the priority push.
- **Recommended next action for the control surface:** read §3 (the
  priority push list) and authorize Tier-A1 / A2 / A3 actions, in that
  order. Tier-B and Tier-C are unlock lifts for subsequent outreach
  waves.
- **No blockers from this lane.** No GitHub mutations attempted, no
  cross-lane writes, no engineering-evidence overruns.

---

## §8 — Appendix — files written by this lane

```
docs/gtm/outreach-candidate-briefs-2026-04-28.md
docs/gtm/overnight-client-ready-material-2026-04-28.md
docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md
```

No other files were written or edited.

---

## §9 — Pass-2 update (2026-04-28 22:1x local)

After completing the first pass, the lane ran a validation pass against
shipped artifacts to spot-check claims. Findings:

### What pass 2 confirmed

- All five demo HTML reports exist at the cited paths and sizes (118 / 85
  / 72 / 85 / 66 KB).
- Case counts match — Demo 1 ~680 (subtitle in script line:
  `f"~{total_cases} parametric cases across 3 pipe sizes and rigid jumpers"`),
  Demo 2 72, Demo 3 180 (subtitle: `"2 vessels x 6 depths x 3 mudmats x
  5 sea states"`), Demo 4 60, Demo 5 300.
- The `prospect-template.yaml`, `prospect-schema.json`, and three
  canonical vessel YAMLs all exist with the disclaimer + citation
  blocks.

### What pass 2 found (engineering-evidence defects in existing files)

Four defects were discovered in *existing* GTM files. The lane is **not
authorized to fix them in place** (they are outside this lane's allowed
write list), but they are flagged in §3 of
`docs/gtm/outreach-candidate-briefs-2026-04-28.md` and §7 of
`docs/gtm/overnight-client-ready-material-2026-04-28.md` with severity,
blocked Tier, and drop-in corrections.

| ID | File | Severity | Blocks |
|---|---|---|---|
| **D1** | `docs/gtm/expert-network-profiles.md` — bio claims 5 demos including "mooring system sensitivity" + "cathodic protection sizing"; neither exists | **HIGH** | **Tier-A3 expert-network refresh** — do not paste this bio into GLG / AlphaSights / Guidepoint until corrected |
| D2 | `docs/gtm/linkedin-content-calendar.md` Week-1 Post-1 — "Under 2 seconds" runtime claim, unvalidated | Medium | LinkedIn Week-1 Monday post |
| D3 | `docs/gtm/website-pages/capability-summary.html` — relative font path breaks when attached standalone | Low | Standalone HTML attach pattern (PDF version unaffected) |
| D4 | Demo 1 pass-rate semantics — `PASS + INLINE_ONLY` combined; outreach must not say "all pass" | Low | Snippet A wording tightening |

### Tier-A3 reorder

The original Tier-A3 ranked expert-network profile refresh as the third
morning action. **Pass 2 changes this:** Tier-A3 is now **blocked on the
D1 fix** to `docs/gtm/expert-network-profiles.md`. Recommended new
ordering:

1. **Tier-A1** (pipeline integrity outreach) — unchanged.
2. **Tier-A2** (heavy-lift CSV outreach) — unchanged.
3. **D1 fix** to `expert-network-profiles.md` — drop-in correction is in
   the briefs file §3.D1. Quick to apply.
4. **Tier-A3** (expert-network profile refresh) — runs after D1 lands.
5. **Tier-B / C / D** — unchanged.

### Why this matters

The defect profile is exactly the kind of GTM drift that would harm the
ACE brand if surfaced during a paid expert-network consultation: a
buyer asking "show me the mooring sensitivity demo you mentioned in
your bio" hits empty, and the lost trust is hard to recover. This is
the high-leverage save for the morning.

---

## §10 — Pass-2 verification

| Check | Result |
|---|---|
| Pass-2 edits limited to the three allowed files | yes — `outreach-candidate-briefs-2026-04-28.md`, `overnight-client-ready-material-2026-04-28.md`, this file |
| `expert-network-profiles.md` NOT modified by this lane | confirmed — defect flagged for user, not auto-fixed |
| `linkedin-content-calendar.md` NOT modified by this lane | confirmed — defect flagged |
| `website-pages/capability-summary.html` NOT modified by this lane | confirmed — defect flagged |
| Drop-in correction text for D1 provided in the briefs file | yes — see §3.D1 |
| Pass-2 file size delta within 30% of pass 1 | yes (briefs +85 lines, client-ready +25 lines, this result +60 lines — all proportional refinements) |

---

---

## §11 — Pass-3 update (2026-04-28 22:1x local)

### What pass 3 added

Pass 3 converted the three highest-leverage `missing-proof` items into
**ready-to-paste drop-in templates** in
`docs/gtm/outreach-candidate-briefs-2026-04-28.md` §4. Total lift to
unblock three new outreach lanes is ~6 hours of focused user work
tomorrow morning.

| Template | Briefs §  | Buyer segment unlocked | Author lift |
|---|---|---|---|
| §4.1 — Corrected expert-network bio (D1 fix, drop-in 198 words) | §4.1 | Expert networks (GLG / AlphaSights / Guidepoint) | 5 min (paste) |
| §4.2 — Berth-operability decision frame 2-pager outline | §4.2 | LNG terminal / FSRU operations leads | 2 h (write-up) |
| §4.3 — OC4-DeepCwind FOWT mooring screening 1-pager outline | §4.3 | Floating-wind developers + bankability reviewers | 4 h (1 OrcaFlex run + write-up) |

### Why this matters

The original priority push list ranked tasks by *do-this-first* order.
Pass-3 templates change the marginal cost of each Tier-B / Tier-C lift
— the user does not start from a blank canvas. The expert-network bio
fix is the highest leverage in the queue: it unblocks Tier-A3 entirely
with a single paste action.

### What pass 3 did NOT do

- Did not run the OrcaFlex screening for the OC4-DeepCwind worked
  example. Numerical fields in §4.3 §3 are placeholders awaiting the
  actual run during morning execution.
- Did not author the live methodology-doc HTML for #2030 (still
  awaits user-authorized aceengineer.com deploy).
- Did not draft the public-source-only Day-7 / 14 / 21 / 30 dashboard
  per #2351 — out of scope for this lane.

### Pass-3 verification

| Check | Result |
|---|---|
| Pass-3 edits limited to the three allowed files | yes — only `outreach-candidate-briefs-2026-04-28.md` was edited (template additions only) |
| No drift in the existing pass-1 / pass-2 content | confirmed — all additions are new sections, no rewrites of prior content |
| Public-source-only constraint maintained for §4.2 and §4.3 | yes — §4.2 cites only public Woodside articles + SIGTTO context + the public knowledge corpus; §4.3 cites only public OC4-DeepCwind reference geometry |
| `expert-network-profiles.md` still NOT modified | confirmed — D1 fix is provided as drop-in only |

### Final state at 22:14 local (~24 minutes into the 12h window)

| File | Lines | Sections |
|---|---|---|
| `docs/gtm/outreach-candidate-briefs-2026-04-28.md` | ~890 | 10 candidates, 3 snippets, 3 follow-ups, 4 defects, 3 drop-in templates |
| `docs/gtm/overnight-client-ready-material-2026-04-28.md` | ~370 | 7 capability blurbs, 5 demo capsules, 3 send-ready scripts, pre-send check, gaps table, defects table |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md` | ~440 | run summary, 10-candidate index, priority push list, defects, pass-2 update, pass-3 update |

The lane work product is at a defensible stop point. Subsequent passes
risk over-elaborating without new evidence — ACE GTM material gains
*depth* with new shipped artifacts (#2030 deploy, #2346 first
delivery, #1809 GIFs, #2422 detail pages), not from more lane re-runs
on the same evidence base.

The lane will continue to monitor for any new evidence that lands in
the result tree and will refresh the briefs file if and only if a
material change to the shipped artifact base appears (e.g. a new demo
ships, a methodology doc deploys, a deliveries-log row lands).

---

*End of lane C2 result.*
