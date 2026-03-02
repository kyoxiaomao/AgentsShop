import { Scene } from 'phaser'
import { EventBus } from '../EventBus'

export class MainScene extends Scene {
  constructor() {
    super('MainScene')

    // Ant state
    this.speed = 120
    this.ant = null
    this.direction = 1 // 1: right, -1: left
    this.isHovering = false
    this.isWiggling = false
    this.baseAntWidth = 96
    this.baseAntHeight = 96
  }

  preload() {
    this.load.setPath('assets')
    // Phaser 3 doesn't support GIF animation natively.
    // We load them as static textures for now.
    // Ideally, convert GIF to spritesheet for full animation.
    this.load.image('ant-idle', 'ant-idle.png')
    this.load.image('ant-walk', 'ant-idle.png')
  }

  create() {
    const { width, height } = this.scale

    // Create Ant Sprite
    // Start at bottom-left area. 上移 25 与 main.js 中 petWindow 的 y 偏移保持一致，避免被截断
    this.ant = this.add.sprite(0, height - 50, 'ant-walk')
    this.ant.setOrigin(0.5, 1) // Anchor at bottom center

    this.ant.displayWidth = this.baseAntWidth
    this.ant.displayHeight = this.baseAntHeight

    // Interactive
    this.ant.setInteractive({ useHandCursor: true, pixelPerfect: true })

    // Events
    this.ant.on('pointerover', () => {
      this.isHovering = true
      this.ant.setTexture('ant-idle')
      this.ant.displayWidth = this.baseAntWidth * 1.2
      this.ant.displayHeight = this.baseAntHeight * 1.2
      EventBus.emit('set-interaction-lock', true)
    })

    this.ant.on('pointerout', () => {
      this.isHovering = false
      this.ant.setTexture('ant-walk')
      this.ant.displayWidth = this.baseAntWidth
      this.ant.displayHeight = this.baseAntHeight
      EventBus.emit('set-interaction-lock', false)
    })

    this.ant.on('pointerdown', () => {
      this.wiggle()
    })

    // Listen to React updates
    EventBus.on('update-settings', (settings) => {
      if (settings.speed !== undefined) {
        this.speed = settings.speed
      }
    })

    EventBus.on('reset-position', () => {
      this.ant.x = 0
      this.direction = 1
      this.ant.setFlipX(false)
    })

    const handlePetVisible = (visible) => {
      if (!this.ant) return
      const nextVisible = Boolean(visible)
      this.ant.setVisible(nextVisible)
      this.ant.disableInteractive()
      if (nextVisible) {
        this.ant.setInteractive({ useHandCursor: true, pixelPerfect: true })
        return
      }
      this.isHovering = false
      this.ant.setTexture('ant-walk')
      this.ant.displayWidth = this.baseAntWidth
      this.ant.displayHeight = this.baseAntHeight
      EventBus.emit('set-interaction-lock', false)
    }
    EventBus.on('toggle-pet-visible', handlePetVisible)

    // Clean up listener on shutdown
    this.events.on('shutdown', () => {
      EventBus.off('update-settings')
      EventBus.off('reset-position')
      EventBus.off('toggle-pet-visible', handlePetVisible)
    })
  }

  update(time, delta) {
    if (!this.ant || !this.ant.visible) return
    if (this.isHovering) return // Stop moving when hovering

    const dt = delta / 1000 // seconds
    const { width } = this.scale

    // Move
    // Boundary check
    // We want the ant to stay within [0, width]
    // Taking width into account: [antWidth/2, width - antWidth/2]

    const halfWidth = this.ant.displayWidth / 2
    const minX = halfWidth
    const maxX = width - halfWidth

    let nextX = this.ant.x + this.direction * this.speed * dt

    if (nextX <= minX) {
      nextX = minX
      this.direction = 1
      this.ant.setFlipX(false)
    } else if (nextX >= maxX) {
      nextX = maxX
      this.direction = -1
      this.ant.setFlipX(true)
    }

    this.ant.x = nextX
  }

  wiggle() {
    if (this.isWiggling) return
    this.isWiggling = true

    // Simple wiggle tween
    this.tweens.add({
      targets: this.ant,
      angle: { from: -8, to: 8 },
      duration: 100,
      yoyo: true,
      repeat: 5,
      onComplete: () => {
        this.ant.angle = 0
        this.isWiggling = false
      },
    })
  }
}
