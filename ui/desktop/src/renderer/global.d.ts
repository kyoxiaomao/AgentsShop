export {}

declare global {
  interface Window {
    deskant?: {
      quitApp?: () => void
      getStatus?: () => Promise<any>
      resetWindowPosition?: () => Promise<{ x: number; y: number } | null>
      setIgnoreMouseEvents?: (ignore: boolean) => Promise<boolean | null>
    }
  }
}
