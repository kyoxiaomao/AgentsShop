const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('deskant', {
  quitApp: () => ipcRenderer.send('app:quit'),
  getStatus: () => ipcRenderer.invoke('app:getStatus'),
  resetWindowPosition: () => ipcRenderer.invoke('window:resetPosition'),
  setIgnoreMouseEvents: (ignore) => ipcRenderer.invoke('window:setIgnoreMouseEvents', ignore),
})
