param(
    [ValidateSet("public", "private")]
    [string]$Visibility = "public"
)

$Repo = "prateek-wahane/personal-medical-assistant-vapi"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Install it from https://cli.github.com/"
    exit 1
}

$insideRepo = git rev-parse --is-inside-work-tree 2>$null
if (-not $insideRepo) {
    git init
}

git add .
try {
    git commit -m "Initial commit: Personal Medical Assistant with Vapi" | Out-Null
} catch {
}

git branch -M main

gh repo create $Repo --$Visibility --source=. --remote=origin --push
Write-Host "Repository created and pushed: https://github.com/$Repo"
