import React from 'react'

type Props = {
  onClick: () => void
}

const ExitButton = React.forwardRef<HTMLButtonElement, Props>(
  ({ onClick }, ref) => {
    return (
      <div className="group pointer-events-auto fixed bottom-6 right-6">
        <button
          ref={ref}
          type="button"
          onClick={onClick}
          className="relative flex h-12 w-12 items-center justify-center rounded-full border border-white/20 bg-white/10 backdrop-blur transition hover:bg-white/20"
          aria-label="退出"
        >
          <img src="/electron-vite.svg" className="h-7 w-7" />
          <div className="pointer-events-none absolute bottom-1/2 right-full mr-3 translate-y-1/2 whitespace-nowrap rounded bg-black/70 px-2 py-1 text-xs text-white opacity-0 transition group-hover:opacity-100">
            退出
          </div>
        </button>
      </div>
    )
  }
)

ExitButton.displayName = 'ExitButton'

export default ExitButton

