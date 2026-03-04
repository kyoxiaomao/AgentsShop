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
    this.isDragging = false
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
    this.input.setDraggable(this.ant)

    // Events
    this.ant.on('pointerover', () => {
      this.isHovering = true
      this.ant.setTexture('ant-idle')
      this.ant.displayWidth = this.baseAntWidth * 1.2
      this.ant.displayHeight = this.baseAntHeight * 1.2
      EventBus.emit('set-interaction-lock', true)
      EventBus.emit('request-ignore', { value: false, source: 'ant:pointerover' })
    })

    this.ant.on('pointerout', () => {
      this.isHovering = false
      this.ant.setTexture('ant-walk')
      this.ant.displayWidth = this.baseAntWidth
      this.ant.displayHeight = this.baseAntHeight
      EventBus.emit('set-interaction-lock', false)
      EventBus.emit('request-ignore', { value: true, source: 'ant:pointerout' })
    })

    this.input.on('dragstart', (_pointer, gameObject) => {
      if (gameObject !== this.ant) return
      this.isDragging = true
      this.ant.setTexture('ant-idle')
      EventBus.emit('set-interaction-lock', true)
      EventBus.emit('request-ignore', { value: false, source: 'ant:dragstart' })
    })

    this.input.on('drag', (_pointer, gameObject, dragX, dragY) => {
      if (gameObject !== this.ant) return
      const { width, height } = this.scale
      const halfWidth = this.ant.displayWidth / 2
      const minX = halfWidth
      const maxX = width - halfWidth
      const minY = this.ant.displayHeight
      const maxY = height
      this.ant.x = Math.min(Math.max(dragX, minX), maxX)
      this.ant.y = Math.min(Math.max(dragY, minY), maxY)
    })

    this.input.on('dragend', (_pointer, gameObject) => {
      if (gameObject !== this.ant) return
      this.isDragging = false
      this.ant.setTexture('ant-walk')
      EventBus.emit('set-interaction-lock', false)
      EventBus.emit('request-ignore', { value: true, source: 'ant:dragend' })
    })

    // Listen to React updates
    EventBus.on('update-settings', (settings) => {
      if (settings.speed !== undefined) {
        this.speed = settings.speed
      }
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
      EventBus.off('toggle-pet-visible', handlePetVisible)
    })
  }

  update(time, delta) {
    if (!this.ant || !this.ant.visible) return
    const pointer = this.input?.activePointer
    const isPointerOverAnt = Boolean(pointer && this.ant.getBounds().contains(pointer.x, pointer.y))
    if (this.isHovering || this.isDragging || isPointerOverAnt) return

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
}
