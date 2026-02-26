import { useEffect, useRef } from 'react'
import Phaser from 'phaser'

export function PhaserPet() {
  const hostRef = useRef<HTMLDivElement | null>(null)
  const gameRef = useRef<Phaser.Game | null>(null)

  useEffect(() => {
    if (!hostRef.current) return

    class PetScene extends Phaser.Scene {
      private pet?: Phaser.GameObjects.Container
      private tween?: Phaser.Tweens.Tween

      create() {
        const body = this.add.circle(0, 0, 18, 0x7aa2ff, 0.95)
        const face = this.add.triangle(20, 0, 0, -8, 0, 8, 12, 0, 0x0b1020, 0.9)
        this.pet = this.add.container(0, 0, [body, face])
        this.pet.setPosition(30, this.scale.height / 2)

        this.startMove()

        this.scale.on('resize', () => {
          this.pet?.setY(this.scale.height / 2)
          this.startMove()
        })
      }

      private startMove() {
        if (!this.pet) return
        this.tween?.stop()

        const left = 30
        const right = Math.max(left, this.scale.width - 30)

        this.pet.setX(left)
        this.tween = this.tweens.add({
          targets: this.pet,
          x: right,
          duration: 2400,
          ease: 'Sine.easeInOut',
          yoyo: true,
          repeat: -1
        })
      }
    }

    const game = new Phaser.Game({
      type: Phaser.CANVAS,
      parent: hostRef.current,
      transparent: true,
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH
      },
      scene: [PetScene]
    })

    gameRef.current = game

    return () => {
      gameRef.current?.destroy(true)
      gameRef.current = null
    }
  }, [])

  return <div ref={hostRef} style={{ width: '100%', height: '100%' }} />
}

