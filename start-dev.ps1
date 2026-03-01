Push-Location "$PSScriptRoot\ui\desktop"
$debugLogPath = "$PSScriptRoot\ui\logs\debug.jsonl"
if (Test-Path $debugLogPath) {
  Clear-Content $debugLogPath
}
try {
  Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
  npx concurrently -k "vite" "wait-on http://localhost:5173 && electron ."
} finally {
  Pop-Location
}
