$root = $PSScriptRoot

$logFiles = @(
  (Join-Path $root "ui\logs\ui_debug.jsonl"),
  (Join-Path $root "datacenter\logs\server_debug.jsonl")
)

foreach ($file in $logFiles) {
  if (Test-Path $file) {
    Clear-Content $file
    Write-Host "[clean] cleared $file"
  }
}

$msgDir = Join-Path $root "datacenter\service\message\msgdata"
if (Test-Path $msgDir) {
  Get-ChildItem -Path $msgDir -File -Filter "*.jsonl" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "[clean] removed $($_.FullName)"
  }
}

$rootLogs = Join-Path $root "logs"
if (Test-Path $rootLogs) {
  Remove-Item $rootLogs -Recurse -Force
  Write-Host "[clean] removed $rootLogs"
}
