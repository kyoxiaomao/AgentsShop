import { useEffect, useMemo, useRef, useState } from 'react'
import styled, { keyframes } from 'styled-components'

const ANT_WIDTH = 96
const ANT_HEIGHT = 96

const breathe = keyframes`
  0% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-2px) scale(1.02); }
  100% { transform: translateY(0) scale(1); }
`

const wiggle = keyframes`
  0% { transform: rotate(0deg); }
  20% { transform: rotate(-8deg); }
  40% { transform: rotate(10deg); }
  60% { transform: rotate(-6deg); }
  80% { transform: rotate(6deg); }
  100% { transform: rotate(0deg); }
`

const AntWrap = styled.div`
  position: absolute;
  left: ${(p) => p.$x}px;
  bottom: 12px;
  width: ${ANT_WIDTH}px;
  height: ${ANT_HEIGHT}px;
  transform: ${(p) =>
    `${p.$hover ? 'scale(1.2)' : 'scale(1)'} ${p.$dir < 0 ? 'scaleX(-1)' : ''}`};
  transform-origin: center bottom;
  transition: transform 120ms linear;
  pointer-events: auto;
  animation: ${(p) => (p.$hover ? breathe : 'none')} 1.4s ease-in-out infinite;
`

const AntImg = styled.img`
  width: 100%;
  height: 100%;
  image-rendering: auto;
  transform-origin: center bottom;
  animation: ${(p) => (p.$wiggle ? wiggle : 'none')} 520ms ease-in-out;
`

function nowMs() {
  return performance.now()
}

export default function Ant({ settings, resetSignal }) {
  const speed = settings?.speed ?? 120

  const [hover, setHover] = useState(false)
  const [x, setX] = useState(0)
  const [dir, setDir] = useState(1)
  const [wiggleOn, setWiggleOn] = useState(false)
  const directionRef = useRef(1)
  const lastTRef = useRef(nowMs())
  const rafRef = useRef(0)
  const wiggleTimerRef = useRef(0)

  const src = useMemo(() => {
    return './assets/ant-idle.png'
  }, [])

  useEffect(() => {
    setX(0)
    setDir(1)
    directionRef.current = 1
  }, [resetSignal])

  useEffect(() => {
    return () => window.clearTimeout(wiggleTimerRef.current)
  }, [])

  useEffect(() => {
    const tick = () => {
      const t = nowMs()
      const dt = Math.max(0, (t - lastTRef.current) / 1000)
      lastTRef.current = t

      if (!hover) {
        setX((prev) => {
          const stageWidth = window.innerWidth
          const maxX = Math.max(0, stageWidth - ANT_WIDTH)
          let next = prev + directionRef.current * speed * dt

          if (next <= 0) {
            next = 0
            if (directionRef.current !== 1) {
              directionRef.current = 1
              setDir(1)
            }
          } else if (next >= maxX) {
            next = maxX
            if (directionRef.current !== -1) {
              directionRef.current = -1
              setDir(-1)
            }
          }

          return next
        })
      }

      rafRef.current = window.requestAnimationFrame(tick)
    }

    lastTRef.current = nowMs()
    rafRef.current = window.requestAnimationFrame(tick)
    return () => window.cancelAnimationFrame(rafRef.current)
  }, [hover, speed])

  return (
    <AntWrap
      $x={x}
      $hover={hover}
      $dir={dir}
      data-interactive="pet"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={() => {
        setWiggleOn(false)
        window.clearTimeout(wiggleTimerRef.current)
        setWiggleOn(true)
        wiggleTimerRef.current = window.setTimeout(() => setWiggleOn(false), 560)
      }}
    >
      <AntImg
        src={src}
        alt="小蚁"
        draggable={false}
        $wiggle={wiggleOn}
        onError={(e) => {
          e.currentTarget.src = './assets/ant-idle.png'
        }}
      />
    </AntWrap>
  )
}
