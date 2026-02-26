import { app, BrowserWindow, Menu, ipcMain } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    width: 520,
    height: 240,
    transparent: true,
    frame: false,
    hasShadow: false,
    alwaysOnTop: true,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  ipcMain.removeHandler('menu:open')
  ipcMain.handle('menu:open', async () => {
    if (!win) return

    const isTop = win.isAlwaysOnTop()
    const isVisible = win.isVisible()

    const menu = Menu.buildFromTemplate([
      {
        label: isTop ? '取消置顶' : '置顶',
        click: () => {
          if (!win) return
          const next = !win.isAlwaysOnTop()
          win.setAlwaysOnTop(next)
          win.webContents.send('menu:result', { action: 'alwaysOnTop', value: next })
        }
      },
      {
        label: isVisible ? '隐藏' : '显示',
        click: () => {
          if (!win) return
          const nextVisible = !win.isVisible()
          if (nextVisible) win.show()
          else win.hide()
          win.webContents.send('menu:result', { action: 'visible', value: nextVisible })
        }
      },
      {
        type: 'separator'
      },
      {
        label: '退出',
        click: () => {
          win?.webContents.send('menu:result', { action: 'quit' })
          app.quit()
        }
      }
    ])

    menu.popup({ window: win })
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(createWindow)
