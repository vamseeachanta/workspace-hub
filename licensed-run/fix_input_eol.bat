@echo off
REM Renormalize the acma run input to LF so its sha256 matches the producer's LF
REM hash (licensed-run gate 9). PR #35 pinned *.yml to eol=lf; a plain pull does
REM not rewrite an already-checked-out file, so re-materialize the working copy.
REM Only this ONE file changes. Does NOT touch the .sim or the agent.
REM Result (eol + SHA256) -> runtime\input_sha.log for inspection.
setlocal
set "ACMA=C:\ws\llm-wiki-acma"
set "RELWIN=cases\orcaflex-strength-post\input.yml"
set "RELGIT=cases/orcaflex-strength-post/input.yml"
set "OUT=C:\ws\workspace-hub\licensed-run\runtime\input_sha.log"
cd /d "%ACMA%"
echo === fix_input_eol %date% %time% === > "%OUT%"
echo --- git pull --rebase --autostash (lands PR #35 .gitattributes) --- >> "%OUT%"
git pull --rebase --autostash >> "%OUT%" 2>&1
git config core.autocrlf false
del "%RELWIN%"
git checkout -- "%RELGIT%"
echo --- git ls-files --eol (expect i/lf w/lf) --- >> "%OUT%"
git ls-files --eol "%RELGIT%" >> "%OUT%" 2>&1
echo --- CertUtil SHA256 (must = 6fc6e7920344084fc6b55d66c4f9e93e53951e1113ae76a92792aa9acd389565) --- >> "%OUT%"
CertUtil -hashfile "%RELWIN%" SHA256 >> "%OUT%" 2>&1
echo --- done --- >> "%OUT%"
endlocal
