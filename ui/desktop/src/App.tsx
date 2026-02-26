import { useEffect, useState } from 'react'
import { PhaserPet } from './PhaserPet'

function App() {
  const [lastAction, setLastAction] = useState<string>('')

  useEffect(() => {
    const off = window.desktopApi.onMenuResult((payload) => {
      const suffix = payload.value === undefined ? '' : `: ${JSON.stringify(payload.value)}`
      setLastAction(`${payload.action}${suffix}`)
    })
    return () => off()
  }, [])

  return (
    <div className="relative flex h-full w-full items-center gap-2 p-2">
      <button
        className="h-9 rounded-xl border border-white/15 bg-white/10 px-3 text-sm font-semibold text-white/90 backdrop-blur hover:bg-white/15"
        type="button"
        onClick={() => window.desktopApi.openMenu()}
      >
        IPC
      </button>
      <div className="h-full min-w-0 flex-1 overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur">
        <PhaserPet />
      </div>
      {lastAction ? (
        <div className="absolute bottom-2 right-2 rounded-2xl border border-white/10 bg-white/10 px-3 py-1 text-xs text-white/85 backdrop-blur">
          {lastAction}
        </div>
      ) : null}
    </div>
  )
}

export default App
