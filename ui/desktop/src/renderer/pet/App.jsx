import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import PhaserGame from './game/PhaserGame'
import ControlButton from './components/ControlButton'
import StatusPanel from './components/StatusPanel'
import { EventBus } from './game/EventBus'

// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function App() {
  const view = useMemo(() => {
    if (typeof window === 'undefined') return 'pet'
    const params = new URLSearchParams(window.location.search)
    return params.get('view') || 'pet'
  }, [])
  const isStatusView = view === 'status'
  const [speed, setSpeed] = useState(120)
  const [resetSignal, setResetSignal] = useState(0)
  const [interactionLock, setInteractionLock] = useState(false)
  const [phaserLock, setPhaserLock] = useState(false)
  const [petVisible, setPetVisible] = useState(true)
  const ignoreRef = useRef(true)

  const settings = useMemo(() => ({ speed }), [speed])

  const setIgnore = useCallback((value) => {
    if (!electronApi?.pet?.setIgnoreMouseEvents) return
    if (ignoreRef.current === value) return
    ignoreRef.current = value
    electronApi.pet.setIgnoreMouseEvents(value)
  }, [])

  useEffect(() => {
    if (isStatusView) return
    setIgnore(true)
  }, [isStatusView, setIgnore])

  useEffect(() => {
    if (isStatusView) return
    const handleRequest = (payload) => {
      const value = Boolean(payload?.value)
      setIgnore(value)
    }
    EventBus.on('request-ignore', handleRequest)
    return () => {
      EventBus.off('request-ignore', handleRequest)
    }
  }, [isStatusView, setIgnore])

  // Combined lock state: either React UI lock or Phaser Sprite lock
  const isLocked = interactionLock || phaserLock

  useEffect(() => {
    if (isStatusView) return
    const onMove = (e) => {
      if (e.buttons > 0) return
      if (isLocked) return

      const el = document.elementFromPoint(e.clientX, e.clientY)
      const hit = el && typeof el.closest === 'function' ? el.closest('[data-interactive]') : null

      if (hit) {
        setIgnore(false)
        return
      }
      setIgnore(true)
    }

    window.addEventListener('mousemove', onMove, { passive: true })
    return () => {
      window.removeEventListener('mousemove', onMove)
    }
  }, [isLocked, isStatusView, setIgnore])

  useEffect(() => {
    if (isStatusView) return
    if (!isLocked) return
    setIgnore(false)
  }, [isLocked, isStatusView, setIgnore])

  if (isStatusView) {
    return (
      <div className="w-full h-full relative">
        <StatusPanel open />
      </div>
    )
  }

  return (
    <div className="w-full h-full relative">
      <PhaserGame
        settings={settings}
        resetSignal={resetSignal}
        onInteractionLockChange={setPhaserLock}
        petVisible={petVisible}
      />
      <ControlButton
        speed={speed}
        onSpeedChange={setSpeed}
        onReset={() => setResetSignal((x) => x + 1)}
        onInteractionLockChange={setInteractionLock}
        petVisible={petVisible}
        onPetVisibleChange={setPetVisible}
      />
    </div>
  )
}
