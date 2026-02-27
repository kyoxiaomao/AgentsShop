const modules = [
  { id: 'agent', name: 'Agent 配置模块' },
  { id: 'access', name: '访问权限' },
  { id: 'logs', name: '运行日志' },
  { id: 'alerts', name: '告警策略' },
]

export default function AdminApp() {
  const activeModule = modules[0]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="text-lg font-semibold">Admin 管理端</div>
          <div className="text-sm text-slate-400">Agent 管理控制台</div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-[260px_1fr] gap-6 px-6 py-6">
        <aside className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="mb-3 text-sm font-semibold text-slate-200">模块列表</div>
          <div className="space-y-2">
            {modules.map((item) => {
              const isActive = item.id === activeModule.id
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-sm transition ${
                    isActive
                      ? 'border-indigo-500/60 bg-indigo-500/10 text-white'
                      : 'border-slate-800 bg-slate-900/40 text-slate-300 hover:border-slate-600 hover:text-white'
                  }`}
                >
                  {item.name}
                  {isActive ? (
                    <span className="text-xs text-indigo-200">当前</span>
                  ) : null}
                </button>
              )
            })}
          </div>
        </aside>

        <section className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-semibold">{activeModule.name}</div>
              <div className="mt-1 text-xs text-slate-400">
                管理 Agent 的基础配置与运行策略
              </div>
            </div>
            <button className="rounded-xl border border-slate-700 px-4 py-2 text-xs text-slate-300 transition hover:border-slate-500 hover:text-white">
              保存配置
            </button>
          </div>

          <div className="grid gap-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300">
            <div className="grid gap-2">
              <div className="text-xs font-semibold text-slate-400">默认 Agent 名称</div>
              <input
                className="h-10 rounded-xl border border-slate-800 bg-slate-950/60 px-3 text-sm text-slate-100 outline-none transition focus:border-slate-500"
                defaultValue="Agent Alpha"
              />
            </div>
            <div className="grid gap-2">
              <div className="text-xs font-semibold text-slate-400">默认状态</div>
              <div className="flex gap-2">
                <button className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-200">
                  空闲
                </button>
                <button className="rounded-full border border-slate-800 px-3 py-1 text-xs text-slate-300">
                  忙碌
                </button>
              </div>
            </div>
            <div className="grid gap-2">
              <div className="text-xs font-semibold text-slate-400">最大并发任务数</div>
              <input
                className="h-10 rounded-xl border border-slate-800 bg-slate-950/60 px-3 text-sm text-slate-100 outline-none transition focus:border-slate-500"
                defaultValue="6"
              />
            </div>
            <div className="grid gap-2">
              <div className="text-xs font-semibold text-slate-400">运行模式</div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-2 text-xs text-slate-300">
                当前为安全模式（限制高危操作）
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
