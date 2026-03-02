const { app, BrowserWindow, ipcMain, Menu, Tray, screen, shell } = require('electron')
const fs = require('node:fs')
const path = require('node:path')

// 窗口实例
let petWindow = null
let appWindow = null
let tray = null

// ==================== 工具函数 ====================

function getFullScreenBounds() {
  const primary = screen.getPrimaryDisplay()
  return primary.bounds // 使用完整屏幕尺寸，包括任务栏区域
}

const PET_WINDOW_Y_OFFSET = 25
const PET_WINDOW_FIXED_WIDTH = 1920
const PET_WINDOW_FIXED_HEIGHT = 1080
const PET_WINDOW_BOTTOM_EXTRA = 50

function getPetWindowBounds() {
  const bounds = getFullScreenBounds()
  return {
    x: bounds.x,
    y: bounds.y - PET_WINDOW_Y_OFFSET,
    width: PET_WINDOW_FIXED_WIDTH,
    height: PET_WINDOW_FIXED_HEIGHT + PET_WINDOW_BOTTOM_EXTRA,
  }
}

function getWorkArea() {
  const primary = screen.getPrimaryDisplay()
  return primary.workArea
}

function getTrayIconPath() {
  return path.join(app.getAppPath(), 'public', 'assets', 'ant-idle.png')
}

function isDev() {
  return process.env.NODE_ENV === 'development' || !app.isPackaged
}

function getDevServerUrl() {
  return 'http://localhost:5173'
}

function getLogFilePath() {
  const logDir = path.resolve(app.getAppPath(), '..', 'logs')
  fs.mkdirSync(logDir, { recursive: true })
  return path.join(logDir, 'debug.jsonl')
}

function clearDebugLog() {
  try {
    fs.writeFileSync(getLogFilePath(), '')
  } catch {}
}

function logEvent(event, data = {}) {
  try {
    const payload = {
      ts: new Date().toISOString(),
      pid: process.pid,
      ppid: process.ppid,
      event,
      data,
    }
    fs.appendFileSync(getLogFilePath(), `${JSON.stringify(payload)}\n`)
  } catch {}
}

function attachWindowLogs(win, name) {
  if (!win) return
  const id = win.id
  win.on('ready-to-show', () => logEvent('window:ready-to-show', { name, id }))
  win.on('show', () => logEvent('window:show', { name, id }))
  win.on('hide', () => logEvent('window:hide', { name, id }))
  win.on('close', () => logEvent('window:close', { name, id }))
  win.on('closed', () => logEvent('window:closed', { name, id }))
  win.on('unresponsive', () => logEvent('window:unresponsive', { name, id }))
  win.on('responsive', () => logEvent('window:responsive', { name, id }))
  win.webContents?.on('render-process-gone', (_e, details) => {
    logEvent('window:render-process-gone', { name, id, details })
  })
  win.webContents?.on('did-fail-load', (_e, errorCode, errorDescription, validatedURL) => {
    logEvent('window:did-fail-load', { name, id, errorCode, errorDescription, validatedURL })
  })
}

// ==================== 窗口加载 ====================

function loadRenderer(win, entry) {
  if (isDev()) {
    // 开发模式：加载 Vite 开发服务器
    const url = `${getDevServerUrl()}/${entry}.html`
    win.loadURL(url)
    return
  }

  // 生产模式：加载打包后的文件
  const indexHtml = path.join(app.getAppPath(), 'dist', entry, 'index.html')
  win.loadFile(indexHtml)
}

// ==================== 桌宠窗口 ====================

function createPetWindow() {
  if (petWindow && !petWindow.isDestroyed()) {
    petWindow.show()
    return petWindow
  }

  const bounds = getFullScreenBounds()

  petWindow = new BrowserWindow({
    frame: false,
    transparent: true,
    resizable: false,
    maximizable: false,
    minimizable: false,
    fullscreen: true,
    fullscreenable: true,
    hasShadow: false,
    focusable: true,// false不可聚焦,系统标题栏不会显示
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    show: false, // 先不显示
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  logEvent('window:create', { name: 'pet', id: petWindow.id })
  attachWindowLogs(petWindow, 'pet')
  petWindow.setAlwaysOnTop(true, 'screen-saver')
  petWindow.setBounds({
    x: bounds.x,
    y: bounds.y - PET_WINDOW_Y_OFFSET,
    width: bounds.width,
    height: bounds.height + PET_WINDOW_Y_OFFSET,
  }, false)
  petWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })
  petWindow.setIgnoreMouseEvents(true, { forward: true })
  
  // 窗口准备好后再显示
  petWindow.once('ready-to-show', () => {
    petWindow.show()
  })
  
  loadRenderer(petWindow, 'index')

  petWindow.on('closed', () => {
    logEvent('window:ref-cleared', { name: 'pet', id: petWindow?.id ?? null })
    petWindow = null
  })

  return petWindow
}

function showPetWindow() {
  if (petWindow && !petWindow.isDestroyed()) {
    petWindow.show()
  }
}

function hidePetWindow() {
  if (petWindow && !petWindow.isDestroyed()) {
    petWindow.hide()
  }
}

// ==================== 应用窗口 ====================

function createAppWindow() {
  if (appWindow && !appWindow.isDestroyed()) {
    appWindow.show()
    appWindow.focus()
    return appWindow
  }

  const bounds = getFullScreenBounds()
  const width = Math.min(1280, bounds.width * 0.8)
  const height = Math.min(800, bounds.height * 0.8)
  const x = bounds.x + (bounds.width - width) / 2
  const y = bounds.y + (bounds.height - height) / 2

  appWindow = new BrowserWindow({
    x: Math.round(x),
    y: Math.round(y),
    title: 'AgentShop',
    width: Math.round(width),
    height: Math.round(height),
    frame: true,
    transparent: false,
    resizable: true,
    maximizable: true,
    minimizable: true,
    hasShadow: true,
    alwaysOnTop: false,
    skipTaskbar: false,
    backgroundColor: '#0f172a',
    autoHideMenuBar: true, // 隐藏菜单栏
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  logEvent('window:create', { name: 'app', id: appWindow.id })
  attachWindowLogs(appWindow, 'app')
  loadRenderer(appWindow, 'app')

  appWindow.on('close', (e) => {
    if (app.isQuitting) return
    logEvent('appWindow:close.prevented', { isQuitting: app.isQuitting })
    e.preventDefault()
    hideAppWindow()
  })

  appWindow.on('closed', () => {
    logEvent('window:ref-cleared', { name: 'app', id: appWindow?.id ?? null })
    appWindow = null
  })

  return appWindow
}

function showAppWindow() {
  if (appWindow && !appWindow.isDestroyed()) {
    appWindow.show()
    appWindow.focus()
  } else {
    createAppWindow()
  }
}

function hideAppWindow() {
  if (appWindow && !appWindow.isDestroyed()) {
    appWindow.hide()
  }
}

// ==================== 托盘 ====================

function createTray() {
  const iconPath = getTrayIconPath()
  tray = new Tray(iconPath)
  tray.setToolTip('AgentShop')

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示桌宠',
      click: () => showPetWindow(),
    },
    {
      label: '打开控制台',
      click: () => showAppWindow(),
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        logEvent('tray:quit')
        app.isQuitting = true
        logEvent('app:quit.requested', { source: 'tray' })
        app.quit()
      },
    },
  ])
  tray.setContextMenu(contextMenu)

  tray.on('double-click', () => {
    showAppWindow()
  })
}

// ==================== IPC 注册 ====================

function registerIpc() {
  // 应用控制
  ipcMain.on('app:quit', (e) => {
    app.isQuitting = true
    logEvent('ipc:app:quit', { senderId: e.sender?.id, url: e.sender?.getURL?.() })
    logEvent('app:quit.requested', { source: 'ipc:app:quit' })
    app.quit()
  })

  // 状态获取
  ipcMain.handle('app:getStatus', () => {
    return {
      platform: process.platform,
      arch: process.arch,
      electron: process.versions.electron,
      chrome: process.versions.chrome,
      node: process.versions.node,
      uptime: process.uptime(),
    }
  })

  // 桌宠窗口控制
  ipcMain.handle('pet:resetPosition', () => {
    if (!petWindow || petWindow.isDestroyed()) return null
    const bounds = getPetWindowBounds()
    petWindow.setBounds({
      x: bounds.x,
      y: bounds.y,
      width: bounds.width,
      height: bounds.height,
    }, false)
    return { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height }
  })

  ipcMain.handle('pet:setIgnoreMouseEvents', (_e, ignore) => {
    if (!petWindow || petWindow.isDestroyed()) return null
    const value = Boolean(ignore)
    if (value) petWindow.setIgnoreMouseEvents(true, { forward: true })
    else petWindow.setIgnoreMouseEvents(false)
    return value
  })

  ipcMain.on('pet:openApp', () => {
    logEvent('ipc:pet:openApp')
    showAppWindow()
  })

  ipcMain.on('pet:show', () => {
    logEvent('ipc:pet:show')
    showPetWindow()
  })

  ipcMain.on('pet:hide', () => {
    logEvent('ipc:pet:hide')
    hidePetWindow()
  })

  // 应用窗口控制
  ipcMain.on('app:show', () => {
    logEvent('ipc:app:show')
    showAppWindow()
  })

  ipcMain.on('app:hide', () => {
    logEvent('ipc:app:hide')
    hideAppWindow()
  })

  // 外部链接
  ipcMain.on('shell:openExternal', (_e, url) => {
    shell.openExternal(url)
  })
}

// ==================== 应用生命周期 ====================

app.whenReady().then(() => {
  clearDebugLog()
  logEvent('app:ready', { isDev: isDev() })
  // 创建桌宠窗口（常驻）
  createPetWindow()

  // 创建托盘
  createTray()

  // 注册 IPC
  registerIpc()

  app.on('activate', () => {
    logEvent('app:activate', { windowCount: BrowserWindow.getAllWindows().length })
    if (BrowserWindow.getAllWindows().length === 0) {
      createPetWindow()
    }
  })
})

app.on('window-all-closed', () => {
  logEvent('app:window-all-closed', { windowCount: BrowserWindow.getAllWindows().length })
  // macOS 除外，其他平台关闭所有窗口时退出
  if (process.platform !== 'darwin') {
    logEvent('app:quit.requested', { source: 'window-all-closed' })
    app.quit()
  }
})

app.on('before-quit', () => {
  app.isQuitting = true
  logEvent('app:before-quit', { isQuitting: app.isQuitting })
})

app.on('quit', (_event, exitCode) => {
  logEvent('app:quit', { exitCode })
})

process.on('beforeExit', (code) => {
  logEvent('process:beforeExit', { code })
})

process.on('exit', (code) => {
  logEvent('process:exit', { code })
})

process.on('uncaughtException', (error) => {
  logEvent('process:uncaughtException', { message: error?.message, stack: error?.stack })
})

process.on('unhandledRejection', (reason) => {
  logEvent('process:unhandledRejection', { reason: String(reason) })
})
