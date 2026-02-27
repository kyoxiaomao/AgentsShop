import { ipcRenderer, contextBridge } from 'electron'
import type { MenuResult } from '@agentsshop/ui-shared'

contextBridge.exposeInMainWorld('desktopApi', {
  openMenu: () => ipcRenderer.invoke('menu:open'),
  setMouseInteractive: (isInteractive: boolean) => ipcRenderer.send('mouse:interactive', isInteractive),
  onMenuResult: (listener: (payload: MenuResult) => void) => {
    const handler = (_event: unknown, payload: MenuResult) => listener(payload)
    ipcRenderer.on('menu:result', handler)
    return () => ipcRenderer.off('menu:result', handler)
  }
})
