import { useEffect, useRef } from 'react'
import ExitButton from './ExitButton'
import PetCanvas from './PetCanvas'

export default function PetApp() {
  const exitButtonRef = useRef<HTMLButtonElement | null>(null)
  const lastIgnoreRef = useRef<boolean>(true)

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      const btn = exitButtonRef.current
      if (!btn || !window.pet) return

      const r = btn.getBoundingClientRect()
      const inRect =
        e.clientX >= r.left &&
        e.clientX <= r.right &&
        e.clientY >= r.top &&
        e.clientY <= r.bottom

      const nextIgnore = !inRect
      if (nextIgnore === lastIgnoreRef.current) return
      lastIgnoreRef.current = nextIgnore
      window.pet.setMouseIgnore(nextIgnore)
    }

    window.addEventListener('mousemove', onMouseMove)
    return () => window.removeEventListener('mousemove', onMouseMove)
  }, [])

  return (
    <div className="relative h-full w-full">
      <PetCanvas />
      <ExitButton ref={exitButtonRef} onClick={() => window.pet.quit()} />
    </div>
  )
}

