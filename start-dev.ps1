# 启动前先结束可能残留的 electron/AgentShop 进程
& "$PSScriptRoot\kill-electron.ps1"
Write-Host "[start-dev] Cleaned old Electron processes"
& "$PSScriptRoot\clean-runtime-data.ps1"
Write-Host "[start-dev] Runtime data cleaned by clean-runtime-data.ps1"

$serverHost = "127.0.0.1"
$serverPort = 8000
$serverRunning = $false
try {
  $client = New-Object System.Net.Sockets.TcpClient
  $connectAsync = $client.BeginConnect($serverHost, $serverPort, $null, $null)
  $serverRunning = $connectAsync.AsyncWaitHandle.WaitOne(300)
  if ($serverRunning) {
    $null = $client.EndConnect($connectAsync)
  }
  $client.Close()
} catch {
  $serverRunning = $false
}

if (-not $serverRunning) {
  Write-Host "[start-dev] Server not detected, starting datacenter.server"
  $pythonExe = "$PSScriptRoot\.venv\Scripts\python.exe"
  if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
  }
  Start-Process -FilePath $pythonExe -ArgumentList "-m", "datacenter.server" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden | Out-Null
  $serverReady = $false
  for ($i = 0; $i -lt 20; $i++) {
    try {
      $probeClient = New-Object System.Net.Sockets.TcpClient
      $probeAsync = $probeClient.BeginConnect($serverHost, $serverPort, $null, $null)
      $ready = $probeAsync.AsyncWaitHandle.WaitOne(300)
      if ($ready) {
        $null = $probeClient.EndConnect($probeAsync)
        $probeClient.Close()
        $serverReady = $true
        break
      }
      $probeClient.Close()
    } catch {}
    Start-Sleep -Milliseconds 200
  }
  if ($serverReady) {
    Write-Host "[start-dev] Server is up: $serverHost`:$serverPort"
  } else {
    Write-Host "[start-dev] Server is still starting, continue to frontend startup"
  }
} else {
  Write-Host "[start-dev] Server already running: $serverHost`:$serverPort"
}

Push-Location "$PSScriptRoot\ui\desktop"
$viteProcess = $null
try {
  Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
  $desktopPath = (Join-Path $PSScriptRoot "ui\desktop")
  $electronUserData = (Join-Path $PSScriptRoot "ui\.electron-user-data")
  $viteCmd = (Join-Path $desktopPath "node_modules\.bin\vite.cmd")
  $waitOnCmd = (Join-Path $desktopPath "node_modules\.bin\wait-on.cmd")
  $electronCmd = (Join-Path $desktopPath "node_modules\.bin\electron.cmd")
  if (-not (Test-Path $electronUserData)) {
    New-Item -Path $electronUserData -ItemType Directory | Out-Null
  }
  Write-Host "[start-dev] Starting Vite and Electron"
  $viteProcess = Start-Process -FilePath $viteCmd -WorkingDirectory $desktopPath -PassThru
  Write-Host "[start-dev] Vite process started (PID: $($viteProcess.Id))"
  & $waitOnCmd "http://localhost:5173"
  Write-Host "[start-dev] Vite is ready, launching Electron..."
  & $electronCmd "." "--user-data-dir=$electronUserData"
} finally {
  if ($viteProcess -and -not $viteProcess.HasExited) {
    Stop-Process -Id $viteProcess.Id -Force -ErrorAction SilentlyContinue
  }
  Pop-Location
}
