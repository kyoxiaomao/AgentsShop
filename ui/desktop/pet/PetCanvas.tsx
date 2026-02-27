import { useEffect, useRef } from 'react'
import Phaser from 'phaser'

class PetScene extends Phaser.Scene {
  private pet?: Phaser.GameObjects.Image
  private vx = 180
  private marginBottom = 10

  preload() {
    this.load.image('pet', '/1.png')
  }

  create() {
    const { width, height } = this.scale.gameSize
    const pet = this.add.image(width * 0.5, height - this.marginBottom, 'pet')
    pet.setOrigin(0.5, 1)

    const maxH = 280
    const scale = Math.min(1, maxH / pet.height)
    pet.setScale(scale)
    pet.setFlipX(this.vx < 0)

    this.pet = pet

    this.scale.on('resize', (gameSize: Phaser.Structs.Size) => {
      if (!this.pet) return
      this.pet.setY(gameSize.height - this.marginBottom)
      this.pet.setX(
        Phaser.Math.Clamp(
          this.pet.x,
          this.pet.displayWidth / 2,
          gameSize.width - this.pet.displayWidth / 2
        )
      )
    })
  }

  update(_time: number, delta: number) {
    if (!this.pet) return
    const { width } = this.scale.gameSize
    const half = this.pet.displayWidth / 2

    this.pet.x += (this.vx * delta) / 1000

    if (this.pet.x <= half) {
      this.pet.x = half
      this.vx = Math.abs(this.vx)
      this.pet.setFlipX(false)
    } else if (this.pet.x >= width - half) {
      this.pet.x = width - half
      this.vx = -Math.abs(this.vx)
      this.pet.setFlipX(true)
    }
  }
}

export default function PetCanvas() {
  const hostRef = useRef<HTMLDivElement | null>(null)
  const gameRef = useRef<Phaser.Game | null>(null)

  useEffect(() => {
    if (!hostRef.current) return
    if (gameRef.current) return

    const game = new Phaser.Game({
      type: Phaser.AUTO,
      parent: hostRef.current,
      transparent: true,
      backgroundColor: 'rgba(0,0,0,0)',
      scene: PetScene,
      scale: {
        mode: Phaser.Scale.RESIZE,
        width: window.innerWidth,
        height: window.innerHeight
      }
    })

    gameRef.current = game

    return () => {
      gameRef.current?.destroy(true)
      gameRef.current = null
    }
  }, [])

  return <div ref={hostRef} className="pointer-events-none h-full w-full" />
}

