export const electronApi = (() => {
  if (typeof window !== 'undefined' && window.deskant) return window.deskant
  return null
})()

