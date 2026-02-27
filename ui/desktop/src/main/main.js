const { app, BrowserWindow, ipcMain, Menu, Tray, screen } = require('electron')
const path = require('node:path')

let mainWindow = null
let tray = null

function getWorkArea() {
  const primary = screen.getPrimaryDisplay()
  return primary.workArea
}

function getDefaultWindowBounds() {
  const workArea = getWorkArea()
  return {
    x: workArea.x,
    y: workArea.y,
    width: workArea.width,
    height: workArea.height,
  }
}

function getTrayIconPath() {
  return path.join(app.getAppPath(), 'public', 'assets', 'ant-idle.png')
}

function createTray() {
  const iconPath = getTrayIconPath()
  tray = new Tray(iconPath)
  tray.setToolTip('Deskant')

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示/隐藏',
      click: () => {
        if (!mainWindow) return
        if (mainWindow.isVisible()) mainWindow.hide()
        else mainWindow.show()
      },
    },
    { type: 'separator' },
    { label: '退出', click: () => app.quit() },
  ])
  tray.setContextMenu(contextMenu)

  tray.on('double-click', () => {
    if (!mainWindow) return
    mainWindow.show()
  })
}

function loadRenderer(win) {
  const devServerUrl = process.env.VITE_DEV_SERVER_URL
  if (devServerUrl) {
    win.loadURL(devServerUrl)
    return
  }

  const indexHtml = path.join(app.getAppPath(), 'dist', 'renderer', 'index.html')
  win.loadFile(indexHtml)
}

function createMainWindow() {
  const bounds = getDefaultWindowBounds()

  mainWindow = new BrowserWindow({
    ...bounds,
    frame: false,
    transparent: true,
    resizable: false,
    maximizable: false,
    minimizable: false,
    hasShadow: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })
  mainWindow.setIgnoreMouseEvents(true, { forward: true })
  loadRenderer(mainWindow)

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function registerIpc() {
  ipcMain.on('app:quit', () => app.quit())

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

  ipcMain.handle('window:resetPosition', () => {
    if (!mainWindow) return null
    const bounds = getDefaultWindowBounds()
    mainWindow.setBounds(bounds, false)
    return { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height }
  })

  ipcMain.handle('window:setIgnoreMouseEvents', (_e, ignore) => {
    if (!mainWindow) return null
    const value = Boolean(ignore)
    if (value) mainWindow.setIgnoreMouseEvents(true, { forward: true })
    else mainWindow.setIgnoreMouseEvents(false)
    return value
  })
}

app.whenReady().then(() => {
  createMainWindow()
  createTray()
  registerIpc()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
