import { useEffect, useState } from 'react'
import { PhaserPet } from './PhaserPet'

function App() {
  const [lastAction, setLastAction] = useState<string>('')
  const [isIpcHover, setIsIpcHover] = useState(false)

  useEffect(() => {
    const off = window.desktopApi.onMenuResult((payload) => {
      const suffix = payload.value === undefined ? '' : `: ${JSON.stringify(payload.value)}`
      setLastAction(`${payload.action}${suffix}`)
    })
    return () => off()
  }, [])

  return (
    <div className="relative h-full w-full bg-transparent">
      <div className="absolute inset-x-0 bottom-0 h-full">
        <PhaserPet />
      </div>

      <div
        className="pointer-events-auto absolute right-4 top-1/2 -translate-y-1/2"
        onMouseEnter={() => {
          setIsIpcHover(true)
          window.desktopApi.setMouseInteractive(true)
        }}
        onMouseLeave={() => {
          setIsIpcHover(false)
          window.desktopApi.setMouseInteractive(false)
        }}
      >
        <button
          className="grid h-12 w-12 cursor-pointer place-items-center rounded-full bg-white/0"
          type="button"
          onClick={() => window.desktopApi.openMenu()}
        >
          <img
            className="h-10 w-10"
            src={isIpcHover ? '/electron-vite.animate.svg' : '/electron-vite.svg'}
            alt="IPC"
          />
        </button>
        {lastAction ? (
          <div className="mt-2 max-w-56 rounded-xl border border-white/10 bg-black/20 px-2 py-1 text-[10px] text-white/85 backdrop-blur">
            {lastAction}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default App
