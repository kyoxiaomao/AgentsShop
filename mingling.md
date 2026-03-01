
## 激活虚拟环境
.\.venv\Scripts\Activate.ps1    


## pip更新
python -m pip install --upgrade pip

## 换源
pip install agentscope -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install agentscope-runtime -i https://pypi.tuna.tsinghua.edu.cn/simple


## ========================================
## AgentShop Desktop 启动命令
## ========================================

### 方式一：使用启动脚本（推荐）
# 在项目根目录下运行：
.\start-dev.ps1

### 方式二：手动启动
# 1. 进入 desktop 目录
cd D:/AgentsShop/ui/desktop

# 2. 清除环境变量并启动
Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npx concurrently -k "vite" "wait-on http://localhost:5173 && electron ."

### 方式三：分步启动
# 终端 1：启动 Vite
cd D:/AgentsShop/ui/desktop
npx vite

# 终端 2：启动 Electron（新开一个 PowerShell）
cd D:/AgentsShop/ui/desktop
Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
./node_modules/.bin/electron .
