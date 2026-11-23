# Local CI Owner Install

This runner is for private repositories whose GitHub Actions checks cannot run while the billing lock is active. It runs as an unprivileged `ghrunner` user on the Linux CI host, posts commit statuses, and leaves installation under owner control.

## One-Time Owner Steps

1. Create the unprivileged account:

```bash
sudo adduser --disabled-password ghrunner
sudo loginctl enable-linger ghrunner
```

2. Create a fine-grained GitHub token for `vamseeachanta` with access only to:

- `llm-wiki-acma`
- `achantas-data`
- `llm-wiki-fdas`
- `aceengineer-admin`
- `llm-wiki-baez`

Grant repository permissions:

- Commit statuses: write
- Contents: read
- Pull requests: read

Metadata read is implicit. Set `LOCAL_CI_COMMENT=1` only after granting pull requests write for PR comment updates.

3. Authenticate `gh` as `ghrunner`:

```bash
sudo -iu ghrunner
gh auth login --with-token
```

Paste the fine-grained token on stdin when prompted.

4. Ensure the configured repositories already exist as normal checkouts for `ghrunner`. The runner creates only throwaway `git worktree` directories from those checkouts; it does not clone repositories during a run. The `ghrunner` account needs its own `~/ws/workspace-hub` checkout plus one `~/ws/vamseeachanta/<repo>` checkout for each `repos.yaml` entry:

```bash
mkdir -p ~/ws/vamseeachanta
gh repo clone vamseeachanta/workspace-hub ~/ws/workspace-hub
for repo in llm-wiki-acma achantas-data llm-wiki-fdas aceengineer-admin llm-wiki-baez; do
  gh repo clone "vamseeachanta/${repo}" "${HOME}/ws/vamseeachanta/${repo}"
done
```

5. Run the owner check script:

```bash
~/ws/workspace-hub/scripts/ci/local-ci/install-local-ci.sh
```

6. To install the timer manually, copy the unit files into the user systemd directory and enable them:

```bash
sudo machinectl shell ghrunner@ /bin/bash -lc '
  mkdir -p ~/.config/systemd/user
  cp ~/ws/workspace-hub/scripts/ci/local-ci/local-ci.service ~/.config/systemd/user/
  cp ~/ws/workspace-hub/scripts/ci/local-ci/local-ci.timer ~/.config/systemd/user/
  systemctl --user daemon-reload
  systemctl --user enable --now local-ci.timer
'
```

If `machinectl` is unavailable, run the `systemctl --user` commands with `XDG_RUNTIME_DIR=/run/user/$(id -u ghrunner)` in the `ghrunner` session.

The PR does not perform these steps, register runners, install cron, or change repository settings.

## Manual Run

```bash
~/ws/workspace-hub/scripts/ci/local-ci/local-ci.py --config ~/ws/workspace-hub/scripts/ci/local-ci/repos.yaml
```

Logs are written under the configured state directory. PR comments are skipped by default; set `LOCAL_CI_COMMENT=1` only after granting pull requests write. Set `LOCAL_CI_GIST=1` only after adding an approved gist transport.

## Security Note

PR code runs as the unprivileged `ghrunner` account with a fresh job `HOME`. Keep `repos.yaml` limited to owner and agent repositories, and keep the token permissions minimal.
