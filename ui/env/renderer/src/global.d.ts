export {}

declare global {
  interface Window {
    pet: {
      quit: () => Promise<void>
      setMouseIgnore: (ignore: boolean) => Promise<void>
    }
  }
}

