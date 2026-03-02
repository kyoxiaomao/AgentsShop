# 启动前先结束可能残留的 electron/AgentShop 进程
& "$PSScriptRoot\kill-electron.ps1"

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
