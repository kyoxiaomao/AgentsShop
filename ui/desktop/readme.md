# AgentShop Desktop

基于 Electron + React + Phaser 3 + TailwindCSS 的桌面应用，集成桌宠、Agent 控制台和管理后台。

## 功能概览

### 桌宠模式
- **透明覆盖层**：全屏工作区透明窗口，默认鼠标穿透
- **Phaser 游戏引擎**：驱动桌宠动画与交互
- **智能交互接管**：鼠标移入桌宠或控制面板时自动接管输入
- **控制中心**：速度调节、重置位置、状态面板、打开控制台

### 应用窗口
- **Agent 控制台**：与 AI Agent 进行对话交互
- **管理后台**：Agent 配置、访问权限、运行日志、告策略（需管理员权限）
- **权限控制**：基于角色的视图切换

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Electron 主进程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐              ┌─────────────────┐      │
│   │   petWindow     │              │   appWindow     │      │
│   │   (桌宠窗口)     │   IPC 通信   │   (应用窗口)     │      │
│   │   透明/置顶/穿透  │ ←─────────→ │   普通窗口      │      │
│   └─────────────────┘              └─────────────────┘      │
│          │                                │                 │
│          ▼                                ▼                 │
│   ┌─────────────────┐              ┌─────────────────┐      │
│   │  pet/index.html │              │  app/index.html │      │
│   │  (桌宠渲染进程)  │              │  (应用渲染进程)  │      │
│   └─────────────────┘              └─────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
ui/desktop/
├── package.json
├── vite.config.mjs              # 多入口构建配置
├── tailwind.config.js           # TailwindCSS 配置
├── postcss.config.js
├── index.html                   # 桌宠入口
├── app.html                     # 应用窗口入口
│
├── public/
│   └── assets/                  # 桌宠资源
│
└── src/
    ├── main/                    # Electron 主进程
    │   ├── main.js              # 多窗口管理
    │   └── preload.js           # 预加载脚本
    │
    └── renderer/
        ├── pet/                 # 桌宠模块
        │   ├── main.jsx
        │   ├── App.jsx
        │   ├── index.css
        │   ├── game/            # Phaser 游戏引擎
        │   │   ├── PhaserGame.jsx
        │   │   ├── EventBus.js
        │   │   └── scenes/
        │   │       └── MainScene.js
        │   └── components/      # 桌宠 UI 组件
        │       ├── ControlButton.jsx
        │       ├── MenuPanel.jsx
        │       └── StatusPanel.jsx
        │
        └── app/                 # 应用窗口模块
            ├── main.jsx
            ├── App.jsx
            ├── index.css
            ├── store/           # Redux 状态管理
            │   ├── index.js
            │   ├── authSlice.js
            │   └── chatSlice.js
            ├── pages/           # 页面组件
            │   ├── AgentPage.jsx
            │   └── AdminPage.jsx
            └── components/      # 业务组件
                ├── Layout.jsx
                ├── Header.jsx
                └── Sidebar.jsx
```

## 开发指南

### 安装依赖

```powershell
cd ui/desktop
npm install
```

### 启动开发环境

```powershell
# 同时启动桌宠和应用窗口
npm run dev

# 仅启动桌宠窗口
npm run dev:pet

# 仅启动应用窗口
npm run dev:app
```

### 构建打包

```powershell
npm run build   # 构建渲染层
npm run dist    # 打包应用
```

## 窗口交互

| 操作 | 桌宠窗口 | 应用窗口 |
|------|----------|----------|
| 启动应用 | ✅ 自动打开 | ❌ 不打开 |
| 点击桌宠菜单"打开控制台" | - | ✅ 打开/聚焦 |
| 关闭应用窗口 | - | ✅ 隐藏（不退出） |
| 托盘"退出" | ✅ 销毁 | ✅ 销毁 |

## 技术栈

- **Electron** - 跨平台桌面应用框架
- **React 18** - UI 框架
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **Phaser 3** - 游戏引擎
- **Redux Toolkit** - 状态管理
- **React Router** - 路由管理
- **React Markdown** - Markdown 渲染
