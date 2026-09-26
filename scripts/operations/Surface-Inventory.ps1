<#
Surface-Inventory.ps1 — read-only work-surface inventory for a Windows fleet host.

The Windows boxes (ace-win-1 / ace-win-2) have no remote-exec channel, so this
must be run ON the box. It only READS — it never moves or deletes anything.

Usage (PowerShell, on ace-win-1 or ace-win-2):
    .\Surface-Inventory.ps1 -Surface C:\Users\<you>\work | Tee-Object surface-inventory.txt

Then paste the output back into the session so the same adjudication can run.
#>
param(
    [Parameter(Mandatory = $true)][string]$Surface
)

if (-not (Test-Path $Surface)) { "SURFACE_MISSING $Surface"; exit 0 }
Set-Location $Surface

"### HOST $env:COMPUTERNAME"
"### SURFACE $Surface"

"### FILESYSTEM"
Get-PSDrive -PSProvider FileSystem |
    Where-Object { $_.Used -ne $null } |
    ForEach-Object {
        "{0}: used={1:N1}GB free={2:N1}GB" -f $_.Name, ($_.Used / 1GB), ($_.Free / 1GB)
    }

"### LOOSE_FILES_TOPLEVEL"
Get-ChildItem -File | Sort-Object LastWriteTime |
    ForEach-Object { "{0,12}  {1:yyyy-MM-dd}  {2}" -f $_.Length, $_.LastWriteTime, $_.Name }

"### DIRECTORIES"
foreach ($d in Get-ChildItem -Directory) {
    $n = $d.Name
    $gitPath = Join-Path $d.FullName ".git"
    if (Test-Path $gitPath) {
        $kind   = if (Test-Path $gitPath -PathType Leaf) { "WORKTREE" } else { "CLONE" }
        $br     = (git -C $n rev-parse --abbrev-ref HEAD 2>$null)
        $origin = (git -C $n remote get-url origin 2>$null) -replace '.*[/:]', '' -replace '\.git$', ''
        $dirty  = @(git -C $n status --porcelain 2>$null).Count
        $ahead  = (git -C $n rev-list --count '@{u}..HEAD' 2>$null); if (-not $ahead) { $ahead = "NO_UPSTREAM" }
        $behind = (git -C $n rev-list --count 'HEAD..@{u}' 2>$null); if (-not $behind) { $behind = "NO_UPSTREAM" }
        $stash  = @(git -C $n stash list 2>$null).Count
        $notmain= @(git -C $n log --oneline origin/main..HEAD 2>$null).Count
        $untrk  = @(git -C $n ls-files --others --exclude-standard 2>$null).Count
        $last   = (git -C $n log -1 --format=%cs 2>$null)
        "DIR $n kind=$kind origin=$origin branch=$br dirty=$dirty ahead=$ahead behind=$behind stash=$stash not_on_main=$notmain untracked_files=$untrk last_commit=$last"
    }
    else {
        $cnt = @(Get-ChildItem -LiteralPath $d.FullName -Force -ErrorAction SilentlyContinue).Count
        $sz  = (Get-ChildItem -LiteralPath $d.FullName -Recurse -File -ErrorAction SilentlyContinue |
                Measure-Object Length -Sum).Sum
        $newest = (Get-ChildItem -LiteralPath $d.FullName -Recurse -File -ErrorAction SilentlyContinue |
                   Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        "DIR $n kind=PLAIN entries=$cnt size_gb={0:N2} newest_file={1:yyyy-MM-dd}" -f (($sz, 0 -ne $null)[0] / 1GB), $newest
    }
}

"### REGISTERED_WORKTREES"
foreach ($d in Get-ChildItem -Directory) {
    if (Test-Path (Join-Path $d.FullName ".git") -PathType Container) {
        git -C $d.Name worktree list 2>$null | Select-Object -Skip 1 |
            ForEach-Object { "$($d.Name) -> $_" }
    }
}

"### END"
