

## 激活虚拟环境
.\.venv\Scripts\Activate.ps1    


## pip更新
python -m pip install --upgrade pip

## 换源
pip install agentscope -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install agentscope-runtime -i https://pypi.tuna.tsinghua.edu.cn/simple

cd d:\AgentsShop\ui\env
npm run dev:desktop
cd d:\AgentsShop\ui\web\index
npm run dev:all

cd d:\AgentsShop
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1

- 主页： npm run dev:index （自动打开 / ）npm run dev:all
- 管理端： npm run dev:admin （自动打开
