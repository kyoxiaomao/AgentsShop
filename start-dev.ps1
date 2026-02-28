Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$webIndex = Join-Path $root "ui\web\index"

Push-Location $webIndex
try {
  npm run dev:all
} finally {
  Pop-Location
}
