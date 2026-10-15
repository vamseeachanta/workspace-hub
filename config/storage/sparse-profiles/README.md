# Sparse checkout profiles

Profiles are explicit choices for jobs that need only part of a repository.
`job_checkout.sh --profile <name>` reads `<repository>-<name>.txt` here.
Each nonempty, non-comment line names one repository-relative directory.
Cone mode also checks out root files; do not add glob patterns or file names.

`digitalmodel-code.txt` includes `src`, `tests`, `scripts`, `config`, `data`,
`assets`, `examples`, and `.github`. It omits `docs/`. A job editing `docs/`
must not use the code profile. Jobs needing other omitted content must also
choose a full checkout or an appropriate separately defined profile.

A sparse profile never makes an NTFS or FUSE destination acceptable. The
location guard and free-space floor apply before any checkout is created.
