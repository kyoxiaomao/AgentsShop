# 桌宠桌面端（Electron + React + Phaser）

这是桌宠客户端（桌面端）应用，特性：
- 透明置顶窗口
- 默认鼠标穿透（不遮挡底层应用）
- 鼠标移入交互区域时临时接管输入（便于点击按钮/悬停桌宠）
- Phaser 驱动桌宠渲染与动效
- 渲染进程与主进程通过 IPC 通信

## 启动方式（推荐从 ui 目录）

在 `d:\AgentsShop\ui`：

```powershell
npm install
npm run dev:desktop
```

桌面端开发时会启动 Vite 渲染服务：
- web 固定使用 5173，desktop 固定使用 5174。

也可以直接使用 workspace 命令：

```powershell
npm -w desktop run dev
```

## 关键目录

- `electron/`
  - `main.ts`：窗口创建、置顶/穿透策略、IPC 处理
  - `preload.ts`：安全 API 暴露（`window.desktopApi`）
- `src/`
  - `App.tsx`：UI 布局、IPC 按钮、交互接管逻辑
  - `PhaserPet.tsx`：桌宠渲染与动效（左右移动、悬停抖动）
- `public/`
  - `1.png`：桌宠角色图片
  - `electron-vite.svg`：按钮静态图标
  - `electron-vite.animate.svg`：按钮悬停旋转动效图标

## 交互说明

- 默认鼠标穿透：窗口不会拦截点击。
- 鼠标移入右侧按钮区域：
  - 光标显示手型
  - 图标从静态切换为旋转动效
  - 窗口临时变为可交互，允许点击触发 IPC 菜单
- 鼠标移到桌宠角色上：
  - 角色停止移动并播放抖动动效
  - 鼠标移开后恢复巡逻

## 共享协议

共享类型/协议统一放在 `shared`，用于减少 preload/renderer 的重复定义。
