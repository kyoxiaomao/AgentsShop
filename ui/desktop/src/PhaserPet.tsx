import { useEffect, useRef } from 'react'
import Phaser from 'phaser'

export function PhaserPet() {
  const hostRef = useRef<HTMLDivElement | null>(null)
  const gameRef = useRef<Phaser.Game | null>(null)

  useEffect(() => {
    if (!hostRef.current) return

    class PetScene extends Phaser.Scene {
      private pet?: Phaser.GameObjects.Image
      private jitterTween?: Phaser.Tweens.Tween
      private isHovering = false
      private direction = 1
      private speed = 120

      preload() {
        this.load.image('dragon', '/1.png')
      }

      create() {
        this.pet = this.add.image(0, 0, 'dragon').setOrigin(0.5, 1)
        this.resizePet()
        this.pet.setX(this.getBounds().left)
        this.pet.setFlipX(false)

        this.pet.setInteractive()
        this.pet.on('pointerover', () => {
          this.isHovering = true
          this.startJitter()
        })
        this.pet.on('pointerout', () => {
          this.isHovering = false
          this.stopJitter()
        })

        this.scale.on('resize', () => {
          this.resizePet()
        })
      }

      update(_time: number, delta: number) {
        if (!this.pet) return
        if (this.isHovering) return

        const { left, right } = this.getBounds()
        let nextX = this.pet.x + this.direction * this.speed * (delta / 1000)

        if (nextX >= right) {
          nextX = right
          this.direction = -1
          this.pet.setFlipX(true)
        } else if (nextX <= left) {
          nextX = left
          this.direction = 1
          this.pet.setFlipX(false)
        }

        this.pet.setX(nextX)
      }

      private resizePet() {
        if (!this.pet) return
        const marginBottom = 8
        const targetHeight = Math.max(80, Math.min(200, this.scale.height - marginBottom))
        const scale = targetHeight / this.pet.height
        this.pet.setScale(scale)
        this.pet.setY(this.scale.height - marginBottom)
        this.pet.setX(Phaser.Math.Clamp(this.pet.x || this.getBounds().left, this.getBounds().left, this.getBounds().right))
      }

      private getBounds() {
        const padding = 16
        const half = this.pet ? this.pet.displayWidth / 2 : 0
        const left = padding + half
        const right = Math.max(left, this.scale.width - padding - half)
        return { left, right }
      }

      private startJitter() {
        if (!this.pet) return
        this.jitterTween?.stop()
        this.pet.setAngle(0)
        this.jitterTween = this.tweens.add({
          targets: this.pet,
          angle: { from: -3, to: 3 },
          duration: 80,
          yoyo: true,
          repeat: -1,
          ease: 'Sine.easeInOut',
        })
      }

      private stopJitter() {
        if (!this.pet) return
        this.jitterTween?.stop()
        this.jitterTween = undefined
        this.pet.setAngle(0)
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
