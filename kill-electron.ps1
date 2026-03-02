# 检查并结束 electron / AgentShop 相关进程
# 用于启动 dev 前清理残留进程，避免旧窗口配置被复用

$names = @('electron', 'AgentShop')
foreach ($name in $names) {
  $procs = Get-Process -Name $name -ErrorAction SilentlyContinue
  if ($procs) {
    foreach ($p in $procs) {
      Write-Host "Killing $name (PID: $($p.Id))..."
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
