import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import PhaserGame from './game/PhaserGame'
import ControlButton from './components/ControlButton'

// 获取 Electron API
const electronApi = (() => {
  if (typeof window !== 'undefined' && window.electronApi) return window.electronApi
  return null
})()

export default function App() {
  const [speed, setSpeed] = useState(120)
  const [resetSignal, setResetSignal] = useState(0)
  const [interactionLock, setInteractionLock] = useState(false)
  const [phaserLock, setPhaserLock] = useState(false)
  const [petVisible, setPetVisible] = useState(true)
  const ignoreRef = useRef(true)
  const leaveTimerRef = useRef(0)
  const lastPosRef = useRef({ has: false, x: 0, y: 0 })

  const settings = useMemo(() => ({ speed }), [speed])

  const setIgnore = useCallback((value) => {
    if (!electronApi?.pet?.setIgnoreMouseEvents) return
    if (ignoreRef.current === value) return
    ignoreRef.current = value
    electronApi.pet.setIgnoreMouseEvents(value)
  }, [])

  useEffect(() => {
    setIgnore(true)
  }, [setIgnore])

  // Combined lock state: either React UI lock or Phaser Sprite lock
  const isLocked = interactionLock || phaserLock

  useEffect(() => {
    const onMove = (e) => {
      lastPosRef.current = { has: true, x: e.clientX, y: e.clientY }
      if (isLocked) return

      const el = document.elementFromPoint(e.clientX, e.clientY)
      const hit = el && typeof el.closest === 'function' ? el.closest('[data-interactive]') : null

      if (hit) {
        window.clearTimeout(leaveTimerRef.current)
        setIgnore(false)
        return
      }

      window.clearTimeout(leaveTimerRef.current)
      leaveTimerRef.current = window.setTimeout(() => setIgnore(true), 120)
    }

    window.addEventListener('mousemove', onMove, { passive: true })
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.clearTimeout(leaveTimerRef.current)
    }
  }, [isLocked, setIgnore])

  useEffect(() => {
    window.clearTimeout(leaveTimerRef.current)
    if (isLocked) {
      setIgnore(false)
      return
    }

    if (!lastPosRef.current.has) {
      setIgnore(true)
      return
    }

    const el = document.elementFromPoint(lastPosRef.current.x, lastPosRef.current.y)
    const hit = el && typeof el.closest === 'function' ? el.closest('[data-interactive]') : null
    setIgnore(!hit)
  }, [isLocked, setIgnore])

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
