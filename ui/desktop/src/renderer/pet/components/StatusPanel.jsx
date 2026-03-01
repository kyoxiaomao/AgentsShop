import { useEffect, useState } from 'react'

// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function StatusPanel({ open, onClose }) {
  const [data, setData] = useState(null)

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
    <div
      className="
        fixed inset-0
        grid place-items-center
        bg-black/30
        pointer-events-auto
      "
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.()
      }}
    >
      <div
        className="
          w-[360px] max-w-[calc(100vw-32px)]
          rounded-xl
          bg-slate-900/80 border border-white/10
          backdrop-blur-xl
          p-3
          text-white/90
        "
      >
        <div className="flex items-center justify-between mb-2">
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
        <pre
          className="
            m-0 p-2.5
            rounded-xl
            bg-white/5
            max-h-[260px] overflow-auto
            text-xs leading-relaxed
            text-white/80
          "
        >
          {JSON.stringify(data ?? {}, null, 2)}
        </pre>
      </div>
    </div>
  )
}
