# 检查并结束 electron / AgentShop 相关进程
# 用于启动 dev 前清理残留进程，避免旧窗口配置被复用

$names = @('electron', 'AgentShop')
function Stop-ProcById($procId, $reason) {
  if (-not $procId) { return }
  $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
  if (-not $p) { return }
  Write-Host "Killing $($p.ProcessName) (PID: $procId) by $reason..."
  Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
}

foreach ($name in $names) {
  $procs = Get-Process -Name $name -ErrorAction SilentlyContinue
  if ($procs) {
    foreach ($p in $procs) {
      Stop-ProcById $p.Id "name"
    }
  }
}

$ports = @(5173, 8000)
foreach ($port in $ports) {
  $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
  if (-not $listeners) { continue }
  $ownedProcessIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $ownedProcessIds) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $proc) { continue }
    $procName = ($proc.ProcessName | ForEach-Object { $_.ToLowerInvariant() })
    $wmi = Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue
    $cmd = "$($wmi.CommandLine)"
    $path = "$($wmi.ExecutablePath)"
    $isAgentShopOwned = $cmd -like "*AgentsShop*" -or $path -like "*AgentsShop*"
    $isExpectedDevProc = @("node", "python", "electron", "agentshop") -contains $procName
    if ($isAgentShopOwned -or $isExpectedDevProc) {
      Stop-ProcById $procId "port:$port"
    }
  }
}
