$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "GitHub CLI no esta instalado. Instala gh o crea las issues manualmente desde los archivos en issues/."
}

gh auth status | Out-Null

Get-ChildItem -Path "issues" -Filter "*.md" | Sort-Object Name | ForEach-Object {
  $content = Get-Content $_.FullName -Raw
  $title = ($content -split "`n" | Select-Object -First 1).TrimStart("#").Trim()
  $labelLine = ($content -split "`n" | Where-Object { $_ -like "Labels:*" } | Select-Object -First 1)
  $labels = @()

  if ($labelLine) {
    $labels = $labelLine.Replace("Labels:", "").Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
  }

  $args = @("issue", "create", "--title", $title, "--body-file", $_.FullName)
  foreach ($label in $labels) {
    $args += @("--label", $label)
  }

  Write-Host "Creando issue: $title"
  gh @args
}
