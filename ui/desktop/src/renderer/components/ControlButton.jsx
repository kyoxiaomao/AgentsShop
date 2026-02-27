import { useEffect, useRef, useState } from 'react'
import styled from 'styled-components'
import MenuPanel from './MenuPanel'
import StatusPanel from './StatusPanel'
import { electronApi } from '../env'

const Wrap = styled.div`
  position: absolute;
  right: 20px;
  bottom: 20px;
  width: 56px;
  height: 56px;
  pointer-events: auto;
`

const Button = styled.button`
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: rgba(30, 30, 30, 0.62);
  backdrop-filter: blur(8px);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: transform 150ms linear;

  ${Wrap}:hover & {
    transform: rotate(20deg);
  }
`

const Icon = styled.div`
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(255, 200, 0, 0.9), rgba(255, 120, 0, 0.9));
  transform: rotate(12deg);
`

export default function ControlButton({
  speed,
  onSpeedChange,
  onReset,
  onInteractionLockChange,
}) {
  const [open, setOpen] = useState(false)
  const [statusOpen, setStatusOpen] = useState(false)
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
    <Wrap ref={wrapRef} data-interactive="control">
      <MenuPanel
        open={open}
        onShowStatus={() => {
          setStatusOpen(true)
          setOpen(false)
        }}
        onReset={() => {
          onReset?.()
          electronApi?.resetWindowPosition?.()
          setOpen(false)
        }}
        onQuit={() => {
          setOpen(false)
          electronApi?.quitApp?.()
        }}
        speed={speed}
        onSpeedChange={onSpeedChange}
      />
      <Button
        type="button"
        aria-label="控制中心"
        onClick={() => setOpen((v) => !v)}
      >
        <Icon />
      </Button>
      <StatusPanel open={statusOpen} onClose={() => setStatusOpen(false)} />
    </Wrap>
  )
}
