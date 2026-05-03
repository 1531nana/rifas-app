$ErrorActionPreference = "Stop"

$issues = Get-ChildItem -Path "issues" -Filter "*.md" | Sort-Object Name | ForEach-Object {
  "## $($_.Name)`n" + (Get-Content $_.FullName -Raw)
}

$commits = ""
try {
  $commits = git log --oneline -5
} catch {
  $commits = "No git history yet."
}

$prompt = Get-Content "ralph/prompt.md" -Raw
$body = @"
$prompt

# Open issues
$($issues -join "`n`n---`n`n")

# Last commits
$commits
"@

Write-Host "Prompt preparado para Claude Code. Copia el contenido siguiente si no tienes claude en PATH:"
Write-Host $body

if (Get-Command claude -ErrorAction SilentlyContinue) {
  $body | claude --permission-mode acceptEdits
}
