# GTM blocker-removal continuation pattern

Use this reference when a GTM blocker-removal lane closes (for example, evidence-fill for a contractor matrix) and the user asks for the next logical step in the same stream.

## Pattern

1. **Verify and sync live repo state first**
   - Check `HEAD`, `origin/main`, and relevant issue states before choosing the next action.
   - If local `main` is behind `origin/main`, fast-forward before planning/executing the next gate.
   - If `git merge --ff-only origin/main` is blocked by untracked files that remote now tracks, compare local-vs-remote hashes with `sha256sum` + `git show origin/main:<path>`:
     - identical untracked files: remove local copies so the fast-forward can materialize tracked copies;
     - different untracked files: move them to `/tmp/...` backup before merging, then decide separately whether they matter.
   - Preserve unrelated local dirty files; do not mix them into the GTM stream.

2. **Do not jump directly to downstream send/collateral execution**
   - After an upstream blocker closes, the next step is usually to re-review/promote the upstream artifact gate, not execute the dependent send lane.
   - Example sequence: evidence-fill issue closes → re-review/promote contractor matrix issue → obtain user approval → only then harden brochure/send-tracker plan.

3. **Keep no-send boundaries explicit**
   - A brochure/send-tracker issue may produce collateral and tracker schemas, but it does not authorize outreach unless a separate approved send issue or explicit owner approval exists.
   - Public repo artifacts must not contain individual contact details.
   - Use official-domain evidence or explicit bounded language; do not invent third-party proof to make a row look ready.

4. **Promotion decision rule**
   - If fresh review has no unresolved MAJOR, move the upstream issue to `status:plan-review` and post a concise GitHub comment with artifacts, residual risks, and explicit approval request.
   - If review returns MAJOR/UNAVAILABLE that blocks policy, leave the issue blocked/draft and post the exact blocker instead of presenting it as approval-ready.

## Verification evidence to capture

- `gh issue view <upstream> --json state,labels,title,url`
- `gh issue view <downstream> --json state,labels,title,url`
- `git rev-parse --short HEAD origin/main`
- Review artifact paths under `scripts/review/results/`
- Any backup directory used for untracked-overwrite merge recovery
