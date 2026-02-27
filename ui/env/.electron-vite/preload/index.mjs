import { contextBridge, ipcRenderer } from "electron";
contextBridge.exposeInMainWorld("pet", {
  quit: () => ipcRenderer.invoke("pet:quit"),
  setMouseIgnore: (ignore) => ipcRenderer.invoke("pet:set-ignore-mouse", ignore)
});
