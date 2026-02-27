## 目标

将 `ui/desktop` 改造成桌宠客户端界面：
- IPC 按钮替换为 `public/electron-vite.animate.svg` 图片
- 左右移动的角色替换为 `public/1.png` 龙图片，角色位于屏幕底侧并左右移动
- 继续使用 IPC 通信（按钮触发主进程菜单/动作，渲染进程展示结果）
- 窗口整体透明，并实现“鼠标可穿透”（默认不拦截鼠标事件）

## 约束与假设

- 目标平台为 Windows，Electron 透明无边框置顶窗口作为桌面覆盖层。
- “鼠标可穿透”解释为：窗口默认忽略鼠标事件，但在按钮区域临时可交互（否则按钮无法点击）。
- 角色移动范围以窗口宽度为准；窗口将调整为屏幕宽度、较小高度，并贴合屏幕底部，满足“按钮在右侧、角色在底侧”的布局。

## 改动范围（文件）

- `d:\AgentsShop\ui\desktop\src\App.tsx`
- `d:\AgentsShop\ui\desktop\src\PhaserPet.tsx`
- `d:\AgentsShop\ui\desktop\src\index.css`（如需全局布局/指针事件策略）
- `d:\AgentsShop\ui\desktop\electron\preload.ts`
- `d:\AgentsShop\ui\desktop\electron\main.ts`
- `d:\AgentsShop\ui\desktop\vite.config.ts`（如需忽略 `.electron-user-data` 触发热更新）

## 实施步骤

### 1) 调整窗口为桌宠覆盖层（主进程）

- 在 `electron/main.ts`：
  - 使用 `screen` 获取主显示器工作区尺寸，将窗口设置为：
    - `width = workArea.width`
    - `height = 固定值（例如 220~300 之间）`
    - `x = workArea.x`
    - `y = workArea.y + workArea.height - height`
  - 保持 `transparent: true`、`frame: false`、`alwaysOnTop: true`。
  - 启用鼠标穿透：启动时调用 `win.setIgnoreMouseEvents(true, { forward: true })`。
  - 新增 IPC 通道用于切换交互模式：
    - `mouse:interactive`（boolean）=> 根据参数在主进程调用 `win.setIgnoreMouseEvents(...)`。

### 2) 暴露 IPC API 给渲染层（预加载）

- 在 `electron/preload.ts`：
  - 在现有 `desktopApi` 上新增方法：
    - `setMouseInteractive(isInteractive: boolean)`：通过 `ipcRenderer.send` 通知主进程切换鼠标穿透。
  - 保持现有 `openMenu` / `onMenuResult` 不变。

### 3) UI 布局与按钮替换（渲染层）

- 在 `src/App.tsx`：
  - 结构调整为“全屏底部条”的覆盖层布局：
    - 角色区域贴底（高度占窗口大部分）
    - IPC 按钮绝对定位在右侧（例如 `right: 16px`，垂直居中或略高于底部）
  - IPC 按钮内容替换为 SVG 图片：
    - 使用 `<img src="/electron-vite.animate.svg" />`（来自 `public`）
  - 按钮区域交互控制：
    - `onMouseEnter` => `window.desktopApi.setMouseInteractive(true)`
    - `onMouseLeave` => `window.desktopApi.setMouseInteractive(false)`
    - 点击按钮继续调用 `window.desktopApi.openMenu()`

### 4) 角色替换为龙图片并左右移动（Phaser）

- 在 `src/PhaserPet.tsx`：
  - Scene 中用 Phaser Loader 加载 `public/1.png`（key 如 `dragon`）。
  - 创建 `image/sprite`，设置 origin 为底部对齐（`0.5, 1`），Y 固定在 `scale.height - margin`。
  - 使用 tween 让其在 X 轴 `left -> right` 往返移动（yoyo + repeat -1），在 resize 时重新计算范围与 Y。
  - 保持 Phaser canvas 透明：`transparent: true`。

### 5) 热更新与文件写入噪音优化（可选但推荐）

- 若 `.electron-user-data` 导致 Vite 频繁 reload：
  - 在 `ui/desktop/vite.config.ts` 中将其加入 watcher ignore 列表，避免开发时抖动。

## 验证方式

- 本地启动 `ui/desktop`：
  - 窗口贴底、透明、置顶。
  - 鼠标在窗口大部分区域点击能穿透到桌面/下层应用。
  - 鼠标移入按钮区域后可点击按钮，触发 IPC 菜单，`lastAction` 正常更新；移出按钮区域恢复穿透。
  - 底部龙图片左右移动，缩放/窗口尺寸变化时仍贴底且运动范围正确。

