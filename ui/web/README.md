# Web 页面（可选）

这是一个独立的 Web 前端应用（Vite + React + TypeScript），用于承载项目的网页端页面。当前与桌宠桌面端（`desktop`）拆分为两个应用，但通过 `ui/` 下的 npm workspaces 统一安装与启动。

## 启动方式（推荐从 ui 目录）

在 `d:\AgentsShop\ui`：

```powershell
npm install
npm run dev:web
```

默认访问：
- http://localhost:5173/

也可以直接使用 workspace 命令：

```powershell
npm -w web run dev
```

## 构建

```powershell
npm run build:web
```

## 目录说明

- `src/`：React 应用代码
- `public/`：静态资源
- `vite.config.ts`：Vite 配置
