import { useEffect, useRef, useState } from 'react'
import MenuPanel from './MenuPanel'
import StatusPanel from './StatusPanel'

// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function ControlButton({
  speed,
  onSpeedChange,
  onReset,
  onInteractionLockChange,
  petVisible,
  onPetVisibleChange,
}) {
  const [open, setOpen] = useState(false)
  const [statusOpen, setStatusOpen] = useState(false)
  const [appVisible, setAppVisible] = useState(false)
  const wrapRef = useRef(null)

  useEffect(() => {
    onInteractionLockChange?.(open || statusOpen)
  }, [open, statusOpen, onInteractionLockChange])

  useEffect(() => {
    const onDocMouseDown = (e) => {
      if (!wrapRef.current) return
      if (wrapRef.current.contains(e.target)) return
      setOpen(false)
    }
    document.addEventListener('mousedown', onDocMouseDown)
    return () => document.removeEventListener('mousedown', onDocMouseDown)
  }, [])

  return (
    <div
      ref={wrapRef}
      data-interactive="control"
      className="absolute right-5 bottom-5 w-14 h-14 pointer-events-auto group"
    >
      <MenuPanel
        open={open}
        onShowStatus={() => {
          setStatusOpen(true)
          setOpen(false)
        }}
        onToggleApp={() => {
          if (appVisible) {
            electronApi?.app?.hide?.()
            setAppVisible(false)
          } else {
            electronApi?.pet?.openAppWindow?.()
            setAppVisible(true)
          }
          setOpen(false)
        }}
        onTogglePet={() => {
          if (petVisible) {
            onPetVisibleChange?.(false)
          } else {
            onPetVisibleChange?.(true)
          }
          setOpen(false)
        }}
        appVisible={appVisible}
        petVisible={petVisible}
        onReset={() => {
          onReset?.()
          electronApi?.pet?.resetWindowPosition?.()
          setOpen(false)
        }}
        onQuit={() => {
          setOpen(false)
          electronApi?.quitApp?.()
        }}
        speed={speed}
        onSpeedChange={onSpeedChange}
      />
      <button
        type="button"
        aria-label="控制中心"
        onClick={() => setOpen((v) => !v)}
        className="
          w-14 h-14 rounded-full border-none
          bg-slate-800/60 backdrop-blur-md
          cursor-pointer grid place-items-center
          transition-transform duration-150
          group-hover:rotate-[20deg]
        "
      >
        <div
          className="
            w-[26px] h-[26px] rounded-md
            bg-gradient-to-br from-amber-400/90 to-orange-500/90
            rotate-[12deg]
          "
        />
      </button>
      <StatusPanel open={statusOpen} onClose={() => setStatusOpen(false)} />
    </div>
  )
}
