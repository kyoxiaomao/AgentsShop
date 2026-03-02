import { useEffect, useRef, useState } from 'react'
import MenuPanel from './MenuPanel'
// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function ControlButton({
  speed,
  onSpeedChange,
  onInteractionLockChange,
  petVisible,
  onPetVisibleChange,
}) {
  const [open, setOpen] = useState(false)
  const [appVisible, setAppVisible] = useState(false)
  const [statusVisible, setStatusVisible] = useState(false)
  const wrapRef = useRef(null)

  useEffect(() => {
    onInteractionLockChange?.(open)
  }, [open, onInteractionLockChange])

  useEffect(() => {
    const onDocMouseDown = (e) => {
      if (!wrapRef.current) return
      if (wrapRef.current.contains(e.target)) return
      setOpen(false)
    }
    document.addEventListener('mousedown', onDocMouseDown)
    return () => document.removeEventListener('mousedown', onDocMouseDown)
  }, [])

  useEffect(() => {
    const offOpened = electronApi?.pet?.onStatusWindowOpened?.(() => {
      setStatusVisible(true)
    })
    const offClosed = electronApi?.pet?.onStatusWindowClosed?.(() => {
      setStatusVisible(false)
    })
    return () => {
      offOpened?.()
      offClosed?.()
    }
  }, [])

  return (
    <div
      ref={wrapRef}
      data-interactive="control"
      className="absolute right-5 bottom-[70px] w-14 h-14 pointer-events-auto group"
    >
      <MenuPanel
        open={open}
        onShowStatus={() => {
          if (statusVisible) {
            electronApi?.pet?.closeStatusWindow?.()
            setStatusVisible(false)
          } else {
            electronApi?.pet?.openStatusWindow?.()
            setStatusVisible(true)
          }
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
        statusVisible={statusVisible}
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
    </div>
  )
}
