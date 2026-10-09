# Local CI Owner Install

This runner is for private repositories whose GitHub Actions checks cannot run while the billing lock is active. It runs as an unprivileged `ghrunner` user on `ace-linux-1`, posts commit statuses, and leaves installation under owner control.

## One-Time Owner Steps

1. Create the unprivileged account:

```bash
sudo adduser --disabled-password ghrunner
```

2. Create a fine-grained GitHub token for `vamseeachanta` with access only to:

- `llm-wiki-acma`
- `deckhand`
- `achantas-data`
- `llm-wiki-fdas`
- `aceengineer-admin`
- `llm-wiki-baez`

Grant repository permissions:

- Commit statuses: write
- Contents: read
- Pull requests: read

3. Authenticate `gh` as `ghrunner`:

```bash
sudo -iu ghrunner
gh auth login --with-token
```

Paste the fine-grained token on stdin when prompted.

4. Ensure the configured repositories already exist as normal checkouts for `ghrunner`. The runner creates only throwaway `git worktree` directories from those checkouts; it does not clone repositories:

```bash
mkdir -p ~/ws/vamseeachanta
# Place existing checkouts at ~/ws/vamseeachanta/<repo>, or edit repos.yaml path entries.
```

5. Run the owner check script:

```bash
~/ws/workspace-hub/scripts/ci/local-ci/install-local-ci.sh
```

6. To install the timer manually, copy the unit files into the user systemd directory and enable them:

```bash
mkdir -p ~/.config/systemd/user
cp ~/ws/workspace-hub/scripts/ci/local-ci/local-ci.service ~/.config/systemd/user/
cp ~/ws/workspace-hub/scripts/ci/local-ci/local-ci.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now local-ci.timer
```

The PR does not perform these steps, register runners, install cron, or change repository settings.

## Manual Run

```bash
~/ws/workspace-hub/scripts/ci/local-ci/local-ci.py --config ~/ws/workspace-hub/scripts/ci/local-ci/repos.yaml
```

By default, the last 50 log lines are posted in an updated PR comment. Set `LOCAL_CI_GIST=1` only after adding an approved gist transport.
