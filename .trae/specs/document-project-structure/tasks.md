# Tasks
- [x] Task 1: 盘点仓库目录与关键入口
  - [x] 汇总顶层目录与职责（排除噪声目录）
  - [x] 标注关键入口文件与相互依赖关系（agents/datacenter/ui/models）
- [x] Task 2: 扩充根 README 的“项目结构与目录说明”
  - [x] 在适配器说明后追加目录树与模块说明（风格参考 README.MD#L1-36）
  - [x] 补充启动脚本与主要运行路径（如 start-dev.ps1、ui/web 的 dev:all）
- [x] Task 3: 自检 README 准确性与可读性
  - [x] 校验所有路径与目录树与仓库实际一致
  - [x] 确保不包含 `.venv/`、`node_modules/`、`__pycache__/` 的展开细节

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
