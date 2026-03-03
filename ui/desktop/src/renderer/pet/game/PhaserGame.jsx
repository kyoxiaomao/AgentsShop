import { useEffect, useRef } from 'react'
import * as Phaser from 'phaser'
import { MainScene } from './scenes/MainScene'
import { EventBus } from './EventBus'

export default function PhaserGame({ settings, resetSignal, onInteractionLockChange, petVisible }) {
  const gameRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    const config = {
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: '100%',
      height: '100%',
      transparent: true,
      backgroundColor: 'rgba(0,0,0,0)',
      scene: [MainScene],
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { y: 0 },
        },
      },
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
    }

    gameRef.current = new Phaser.Game(config)

    const handleLock = (locked) => {
      onInteractionLockChange?.(locked)
    }

    EventBus.on('set-interaction-lock', handleLock)

    return () => {
      EventBus.off('set-interaction-lock', handleLock)
      if (gameRef.current) {
        gameRef.current.destroy(true)
        gameRef.current = null
      }
    }
  }, [])

  // Sync settings
  useEffect(() => {
    EventBus.emit('update-settings', settings)
  }, [settings])

  // Sync reset
  useEffect(() => {
    if (resetSignal > 0) {
      EventBus.emit('reset-position')
    }
  }, [resetSignal])

  useEffect(() => {
    if (petVisible === undefined) return
    EventBus.emit('toggle-pet-visible', petVisible)
  }, [petVisible])

  return (
    <div
      ref={containerRef}
      className="w-full h-full pointer-events-auto"
    />
  )
}
