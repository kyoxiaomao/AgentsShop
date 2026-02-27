## 现状复盘（为什么根目录出现 package.json / package-lock / node_modules）

目前 workspaces 是放在仓库根目录的：[package.json](file:///d:/AgentsShop/package.json)。
因此 npm 会把**依赖安装与锁文件**放在根目录：
- `d:\AgentsShop\package.json`
- `d:\AgentsShop\package-lock.json`
- `d:\AgentsShop\node_modules`

这不是“多装了一份”的错误行为，而是 workspaces 的正常结果：**workspaces 的根在哪里，node_modules 就在哪里**。

另外，当前 `ui/web` 与 `ui/desktop` 目录里实际上**没有** `node_modules/`（你看到的“多出 3 份”更可能是之前单独在子目录执行过 install 的印象，或是 root node_modules 里包含 workspace 的依赖数量更大造成错觉）。

真正“额外变多”的主要来源是：
- Electron 运行时生成的 `ui/desktop/.electron-user-data/`（我们之前为了把 userData 放到项目里而显式设置了路径；一旦运行就会再次生成）
- workspaces 根放在仓库根目录，使得根目录出现 node 相关文件
- `.vercel/` 是 Vercel CLI 关联项目时生成的配置目录（当前仓库内没有引用它的内容）

---

## 目标

1) 把所有 node 相关“根级产物”迁移到 `ui/` 下，保证仓库根目录尽量保持 Python 项目的干净感：
   - 让 `ui/` 成为 workspaces 根
   - 最终仅保留一份 `ui/node_modules` 与一份 `ui/package-lock.json`
2) 彻底去掉 `ui/desktop/.electron-user-data` 这种运行时目录，避免污染仓库结构与热更新噪音。
3) 清理/删除无用目录（例如你不需要 Vercel 的情况下删除 `.vercel`）。

---

## 执行计划

### A. 将 workspaces 根从仓库根迁移到 ui/

1. 停止正在运行的 dev 进程（web/desktop），避免文件占用与端口冲突。
2. 在 `d:\AgentsShop\ui\package.json` 新建 workspaces 根配置：
   - `workspaces: ["web", "desktop", "shared"]`
   - 脚本迁移为：
     - `dev:web` => `npm -w web run dev`
     - `dev:desktop` => `npm -w desktop run dev`
     - 以及 build/lint 等
3. 删除仓库根目录的 node 根文件（迁移后不再需要）：
   - `d:\AgentsShop\package.json`
   - `d:\AgentsShop\package-lock.json`
   - `d:\AgentsShop\node_modules`
4. 在 `d:\AgentsShop\ui` 执行一次 `npm install`：
   - 生成 `d:\AgentsShop\ui\package-lock.json`
   - 生成 `d:\AgentsShop\ui\node_modules`
5. 校验 `ui/web`、`ui/desktop` 下不存在多余的 `node_modules`：
   - 若存在（曾经在子目录安装过），删除它们，保证只有 `ui/node_modules` 一份。

### B. 去掉 desktop 的 .electron-user-data 目录污染

1. 修改 `ui/desktop/electron/main.ts`：
   - 移除 `app.setPath('userData', path.join(APP_ROOT, '.electron-user-data'))`
   - 让 Electron 使用系统默认 userData 目录（AppData 下），避免在仓库内生成运行时缓存文件。
2. 删除已生成的 `ui/desktop/.electron-user-data/` 目录。
3. 评估 `ui/desktop/vite.config.ts` 的 watcher ignore：
   - 若 `.electron-user-data` 不再落在项目内，可移除忽略项（或保留也无害）。

### C. 清理根目录的 .vercel（可选）

1. 当前项目内未发现引用 `.vercel` 的配置或脚本。
2. 如果你不再使用 Vercel 部署本仓库：
   - 删除 `d:\AgentsShop\.vercel/`
   - 并在 `.gitignore` 中确保忽略 `.vercel/`（避免将来 Vercel CLI 再生成又被误提交）。

---

## 验证清单

1. `d:\AgentsShop\` 根目录不再存在 `package.json / package-lock.json / node_modules`（node 相关统一收敛到 `ui/`）。
2. `d:\AgentsShop\ui\` 存在且仅存在一份：
   - `ui/package.json`
   - `ui/package-lock.json`
   - `ui/node_modules`
3. `ui/web` 启动固定 `5173`，`ui/desktop` 启动固定 `5174`，两者互不抢占端口。
4. `ui/desktop` 运行后不再生成 `ui/desktop/.electron-user-data`。

