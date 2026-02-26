# 计划：引入 Tailwind CSS 并优化 UI 配色

## 背景
当前 `ui/web` 与 `ui/desktop` 的页面样式主要由手写 CSS（渐变 + 半透明卡片）组成，整体对比度偏低、信息层级不清晰，导致“观感丑”和可读性差。你希望改用更成熟的样式体系（Tailwind CSS）来提升配色与排版一致性。

## 目标
- 在 `ui/web` 与 `ui/desktop` 两个 Vite+React 工程中引入 Tailwind CSS。
- 用 Tailwind 的设计 token（颜色/间距/圆角/阴影/边框）重写当前页面的主要 UI 样式，形成更清晰的层级与更舒服的暗色主题。
- 保持现有交互不变：Web 的 agent 列表/对话/发送；Desktop 的透明窗口/IPC 菜单/Phaser 桌宠。

## 不做的事（本轮范围外）
- 不引入额外 UI 组件库（例如 shadcn、AntD 等），除非你明确要求。
- 不对接真实后端/agent 服务，仍使用 mock 数据。
- 不做复杂主题切换（仅提供更好的默认暗色主题；如需亮色/多主题可后续扩展）。

## 实施方案（高层）
### 1) 为 `ui/web` 引入 Tailwind
- 在 `ui/web` 安装 Tailwind 相关依赖（tailwindcss + postcss + autoprefixer）。
- 生成并配置 `tailwind.config.*` 与 `postcss.config.*`，设置扫描路径覆盖 `src/**/*.{ts,tsx}`。
- 在 `src/index.css` 引入 Tailwind 的 base/components/utilities，并保留必要的全局背景/字体设置。
- 将 `src/App.tsx` 的结构保留，逐块替换为 Tailwind class（导航/侧栏/状态徽章/消息气泡/输入区）。
- 删除或尽量清空不再需要的 `src/App.css` 样式（避免与 Tailwind 冲突），并保证构建与 lint 通过。

### 2) 为 `ui/desktop` 引入 Tailwind（透明窗口友好）
- 在 `ui/desktop` 安装 Tailwind 相关依赖并完成同样的 PostCSS/Tailwind 配置。
- 将 `src/index.css` 改为 Tailwind 入口，同时确保 `body/#root` 背景透明保持 Electron 透明窗口效果。
- 用 Tailwind 重写 `src/App.tsx` 布局：左侧 IPC 按钮 + 右侧桌宠容器（Phaser 画布容器），维持“从左到右”排列。
- 用 Tailwind 调整“玻璃拟态”观感：更合理的背景透明度、边框与模糊（backdrop-blur），提高文字对比度。

### 3) 统一一套更耐看的暗色主题策略
- 基础背景：更深的中性底色（避免强烈彩色渐变），局部用低饱和点缀色。
- 容器层级：卡片/面板/输入框使用一致的边框与透明度；hover/active 使用同一强调色。
- 文本层级：标题/正文/次要信息（placeholder、空态）使用不同 opacity 或 text-* 色阶。
- 状态色：忙碌/空闲使用固定的 warning/success 色阶与一致徽章样式。

## 具体改动清单（按工程）
### `ui/web`
- 新增：Tailwind 配置文件与 PostCSS 配置文件
- 修改：`src/index.css`（改为 Tailwind 入口 + 全局基础样式）
- 修改：`src/App.tsx`（className 全面迁移到 Tailwind）
- 修改/清理：`src/App.css`（移除旧样式，避免冲突）

### `ui/desktop`
- 新增：Tailwind 配置文件与 PostCSS 配置文件
- 修改：`src/index.css`（改为 Tailwind 入口，保持透明背景）
- 修改：`src/App.tsx`（className 全面迁移到 Tailwind）
- 修改/清理：`src/App.css`（移除旧样式，避免冲突）
- 不改：Electron 主进程透明窗口与 IPC 逻辑、Phaser 场景逻辑

## 验收标准
- `ui/web`：
  - 页面可读性明显提升（导航/列表/面板层级清晰）
  - 交互不回退：选角色、发送消息正常
  - `npm run build` 与 `npm run lint` 通过
- `ui/desktop`：
  - 透明窗口仍然透明，控件不被背景色覆盖
  - IPC 菜单仍可弹出且可回显操作结果
  - Phaser 桌宠仍可渲染与左右移动
  - `npm run build` 与 `npm run lint` 通过（build 以 bundle 为准）

## 风险与应对
- Tailwind 与旧 CSS 冲突：通过清空/移除 `App.css` 旧规则并统一使用 Tailwind class 解决。
- Electron 透明窗口被全局背景覆盖：在 `ui/desktop` 的全局样式中强制 `body/#root` 透明，并避免设置不透明背景色。

