
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
.\kill-electron

## 测试案例
python -m unittest tests\test_ui_like_chat_sera.py -v