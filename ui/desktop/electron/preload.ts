import { ipcRenderer, contextBridge } from 'electron'

type MenuResult = { action: string; value?: unknown }

contextBridge.exposeInMainWorld('desktopApi', {
  openMenu: () => ipcRenderer.invoke('menu:open'),
  onMenuResult: (listener: (payload: MenuResult) => void) => {
    const handler = (_event: unknown, payload: MenuResult) => listener(payload)
    ipcRenderer.on('menu:result', handler)
    return () => ipcRenderer.off('menu:result', handler)
  }
})
