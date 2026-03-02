import { useEffect, useState } from 'react'

// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function StatusPanel({ open, onClose }) {
  const [data, setData] = useState(null)
  const [activeTab, setActiveTab] = useState('system')

  useEffect(() => {
    if (!open) return
    let mounted = true
    Promise.resolve(electronApi?.getStatus?.())
      .then((res) => {
        if (!mounted) return
        setData(res ?? { error: '未连接到 Electron 主进程' })
      })
      .catch((e) => {
        if (!mounted) return
        setData({ error: String(e?.message ?? e) })
      })
    return () => {
      mounted = false
    }
  }, [open])

  if (!open) return null

  return (
    <div className="fixed inset-0 pointer-events-none">
      <div
        className="
          pointer-events-auto
          w-[680px] max-w-[calc(100vw-32px)]
          min-h-[420px]
          rounded-xl
          bg-slate-900/80 border border-white/10
          backdrop-blur-xl
          p-4
          text-white/90
          flex flex-col
        "
        style={{ margin: '24px auto 0' }}
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold">状态面板</span>
          <button
            type="button"
            onClick={onClose}
            className="
              border-none
              bg-white/10
              text-white/90
              rounded-[10px]
              px-2.5 py-1.5
              cursor-pointer
              text-sm
              hover:bg-white/20 transition-colors
            "
          >
            关闭
          </button>
        </div>
        <div className="flex items-center gap-2 border-b border-white/10 pb-2 mb-3 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab('system')}
            className={`px-3 py-1.5 rounded-full transition ${
              activeTab === 'system'
                ? 'bg-white/15 text-white'
                : 'text-white/70 hover:bg-white/10'
            }`}
          >
            系统调试
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('data')}
            className={`px-3 py-1.5 rounded-full transition ${
              activeTab === 'data'
                ? 'bg-white/15 text-white'
                : 'text-white/70 hover:bg-white/10'
            }`}
          >
            数据调试
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('ui')}
            className={`px-3 py-1.5 rounded-full transition ${
              activeTab === 'ui'
                ? 'bg-white/15 text-white'
                : 'text-white/70 hover:bg-white/10'
            }`}
          >
            UI 调试
          </button>
        </div>
        <div className="flex-1 min-h-0">
          {activeTab === 'system' && (
            <pre
              className="
                m-0 p-3
                rounded-xl
                bg-white/5
                h-full overflow-auto
                text-xs leading-relaxed
                text-white/80
              "
            >
              {JSON.stringify(data ?? {}, null, 2)}
            </pre>
          )}
          {activeTab === 'data' && (
            <div className="h-full rounded-xl bg-white/5 p-3 text-xs text-white/70">
              暂无数据调试内容
            </div>
          )}
          {activeTab === 'ui' && (
            <div className="h-full rounded-xl bg-white/5 p-3 text-xs text-white/70">
              暂无 UI 调试内容
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
