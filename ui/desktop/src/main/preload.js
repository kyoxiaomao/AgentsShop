const { contextBridge, ipcRenderer } = require('electron')

// 根据当前页面暴露不同的 API
contextBridge.exposeInMainWorld('electronApi', {
  // 通用 API
  quitApp: () => ipcRenderer.send('app:quit'),
  getStatus: () => ipcRenderer.invoke('app:getStatus'),

  // 桌宠专用
  pet: {
    setIgnoreMouseEvents: (ignore) => ipcRenderer.invoke('pet:setIgnoreMouseEvents', ignore),
    openAppWindow: () => ipcRenderer.send('pet:openApp'),
    openStatusWindow: () => ipcRenderer.send('pet:openStatusWindow'),
    closeStatusWindow: () => ipcRenderer.send('pet:closeStatusWindow'),
    onStatusWindowOpened: (handler) => {
      const wrapped = (_event) => handler?.()
      ipcRenderer.on('pet:statusWindowOpened', wrapped)
      return () => ipcRenderer.removeListener('pet:statusWindowOpened', wrapped)
    },
    onStatusWindowClosed: (handler) => {
      const wrapped = (_event) => handler?.()
      ipcRenderer.on('pet:statusWindowClosed', wrapped)
      return () => ipcRenderer.removeListener('pet:statusWindowClosed', wrapped)
    },
    show: () => ipcRenderer.send('pet:show'),
    hide: () => ipcRenderer.send('pet:hide'),
  },

  // 应用窗口专用
  app: {
    show: () => ipcRenderer.send('app:show'),
    hide: () => ipcRenderer.send('app:hide'),
    onShow: (handler) => {
      const wrapped = (_event) => handler?.()
      ipcRenderer.on('app:shown', wrapped)
      return () => ipcRenderer.removeListener('app:shown', wrapped)
    },
    onHide: (handler) => {
      const wrapped = (_event) => handler?.()
      ipcRenderer.on('app:hidden', wrapped)
      return () => ipcRenderer.removeListener('app:hidden', wrapped)
    },
    openExternal: (url) => ipcRenderer.send('shell:openExternal', url),
  },
})
