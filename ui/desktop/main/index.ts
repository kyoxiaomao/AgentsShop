import path from 'node:path'
import { app, BrowserWindow, ipcMain, screen } from 'electron'

let mainWindow: BrowserWindow | null = null

const devDataRoot = path.join(app.getPath('temp'), 'agentshop-desktop')
app.setPath('userData', path.join(devDataRoot, 'user-data'))
app.setPath('cache', path.join(devDataRoot, 'cache'))
app.commandLine.appendSwitch('disk-cache-dir', path.join(devDataRoot, 'disk-cache'))
app.commandLine.appendSwitch('disable-gpu-shader-disk-cache')

function createWindow(): BrowserWindow {
  const display = screen.getPrimaryDisplay()
  const { x, y, width, height } = display.bounds
  const debug = process.env.PET_DEBUG === '1'

  const win = new BrowserWindow({
    x,
    y,
    width,
    height,
    transparent: true,
    frame: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: true,
    skipTaskbar: true,
    hasShadow: false,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  })

  win.setAlwaysOnTop(true, 'screen-saver')
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })
  if (debug) {
    win.setIgnoreMouseEvents(false)
    win.webContents.once('did-finish-load', () => {
      win.webContents.openDevTools({ mode: 'detach' })
    })
  } else {
    win.setIgnoreMouseEvents(true, { forward: true })
  }

  const url = process.env.ELECTRON_RENDERER_URL || process.env.VITE_DEV_SERVER_URL
  if (url) {
    win.loadURL(url)
  } else {
    win.loadFile(path.join(__dirname, '../renderer/index.html'))
  }

  return win
}

app.whenReady().then(() => {
  mainWindow = createWindow()

  ipcMain.handle('pet:quit', () => {
    app.quit()
  })

  ipcMain.handle('pet:set-ignore-mouse', (_event, ignore: boolean) => {
    if (!mainWindow) return
    if (ignore) mainWindow.setIgnoreMouseEvents(true, { forward: true })
    else mainWindow.setIgnoreMouseEvents(false)
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
