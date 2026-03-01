const { contextBridge, ipcRenderer } = require('electron')

// 桌宠窗口 API
const petApi = {
  quitApp: () => ipcRenderer.send('app:quit'),
  getStatus: () => ipcRenderer.invoke('app:getStatus'),
  resetWindowPosition: () => ipcRenderer.invoke('pet:resetPosition'),
  setIgnoreMouseEvents: (ignore) => ipcRenderer.invoke('pet:setIgnoreMouseEvents', ignore),
  openAppWindow: () => ipcRenderer.send('pet:openApp'),
  show: () => ipcRenderer.send('pet:show'),
  hide: () => ipcRenderer.send('pet:hide'),
}

// 应用窗口 API
const appApi = {
  quitApp: () => ipcRenderer.send('app:quit'),
  getStatus: () => ipcRenderer.invoke('app:getStatus'),
  show: () => ipcRenderer.send('app:show'),
  hide: () => ipcRenderer.send('app:hide'),
  openExternal: (url) => ipcRenderer.send('shell:openExternal', url),
}

// 根据当前页面暴露不同的 API
contextBridge.exposeInMainWorld('electronApi', {
  // 通用 API
  quitApp: () => ipcRenderer.send('app:quit'),
  getStatus: () => ipcRenderer.invoke('app:getStatus'),

  // 桌宠专用
  pet: {
    resetWindowPosition: () => ipcRenderer.invoke('pet:resetPosition'),
    setIgnoreMouseEvents: (ignore) => ipcRenderer.invoke('pet:setIgnoreMouseEvents', ignore),
    openAppWindow: () => ipcRenderer.send('pet:openApp'),
    show: () => ipcRenderer.send('pet:show'),
    hide: () => ipcRenderer.send('pet:hide'),
  },

  // 应用窗口专用
  app: {
    show: () => ipcRenderer.send('app:show'),
    hide: () => ipcRenderer.send('app:hide'),
    openExternal: (url) => ipcRenderer.send('shell:openExternal', url),
  },
})
