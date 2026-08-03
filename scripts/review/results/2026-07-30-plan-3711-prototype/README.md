# Verification prototype — plan for #3711

Committed alongside `docs/plans/2026-07-30-issue-3711-host-independent-identity-inventory.md` so a
reviewer can re-run the author's contract instead of reconstructing it. An earlier review in this
chain could not test the author's prototype because it was not committed, which tested the reviewer's
reading rather than the author's design.

These scripts are **read-only**. They write nothing into the repo, never invoke `crontab`,
`setup-cron.sh`, or `cron_apply.py --apply`, and monkeypatch only inside their own process.

Tracked past `.gitignore:577` (`scripts/review/results/`) with `git add -f` / `update-index
--cacheinfo`.

## Files

| File | What it measures |
|---|---|
| `proto_3711.py` | Sections A-D: today's host dependence; byte-identity of the artifact under the proposed lexical render; the portable symlink fixture (C1); the no-filesystem assertion (C2); the declared-root guard (C3); regeneration from git-index bytes (D). |
| `proto_ef.py` | Section E — the **headline** test: an injected fake macOS `/home`-firmlink resolver, on any host. Section F — `expanduser()`'s independent host dependence and the guard's verdict on `~` / `~user` roots. |
| `contents_check.py` | The proposed enforcement contents check, standalone: regenerate identity rows from a repo's **git index** with the lexical render and compare to the inventory blob in the same index. Exit 0 accept / 1 reject. |

## Running them

```bash
# on ace1
cd /mnt/local-analysis/workspace-hub
uv run --with pyyaml python scripts/review/results/2026-07-30-plan-3711-prototype/proto_3711.py \
    /mnt/local-analysis/workspace-hub /tmp/proto3711fx
uv run --with pyyaml python scripts/review/results/2026-07-30-plan-3711-prototype/proto_ef.py \
    /mnt/local-analysis/workspace-hub
uv run --with pyyaml python scripts/review/results/2026-07-30-plan-3711-prototype/contents_check.py \
    /mnt/local-analysis/workspace-hub

# on macOS — same commands with the mac checkout path
```

`proto_3711.py` takes `<repo-root> [<scratch-dir>]`; the scratch dir is created for the C1 symlink
fixture and may be deleted afterwards. The other two take `<repo-root>` only.

## Reproducing the poisoned-artifact demonstration (§5 / §11 of the verification log)

Do this in a throwaway clone. **Never** commit or push the regenerated inventory.

```bash
git clone -q --shared --no-checkout <repo> /tmp/poison-clone
git -C /tmp/poison-clone checkout -q main
cd /tmp/poison-clone
uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py     # run this ON macOS
git add docs/reports/issue-3475-command-identity-inventory.json

uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py ; echo "exit=$?"
# measured 2026-07-30 at 3fe934da9 -> exit=0   (the shipped checker ACCEPTS the poison)

uv run --with pyyaml python .../contents_check.py /tmp/poison-clone ; echo "exit=$?"
# measured -> exit=1, naming the three gpu-claw rows   (the proposed check REJECTS it)
```

## Expected output at `3fe934da9`

The full transcripts from both hosts are in
`scripts/review/results/2026-07-30-plan-3711-verification-log.md`. In one line each:

```
[A]  gpu-claw resolves faithfully on Linux, to /System/Volumes/Data/... on macOS
[B]  today: mac generation != committed; PROPOSED: byte-identical on BOTH hosts
[C1] today unfaithful on BOTH hosts (symlink fixture); PROPOSED faithful
[C2] today FAIL on BOTH hosts (touches the filesystem); PROPOSED PASS
[C3] today's registry passes the guard; '~' and non-normal roots are named and rejected
[D]  regeneration from index bytes matches the committed identities on BOTH hosts
[E]  today generated != baseline under the fake Darwin resolver on BOTH hosts; PROPOSED == baseline
[F]  '~' silently expands to the running user's home on BOTH hosts; '~user' raises an uncaught RuntimeError
```
