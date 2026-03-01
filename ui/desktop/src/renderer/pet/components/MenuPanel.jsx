export default function MenuPanel({
  open,
  onShowStatus,
  onToggleApp,
  onTogglePet,
  appVisible,
  petVisible,
  onReset,
  onQuit,
  speed,
  onSpeedChange,
}) {
  if (!open) return null

  return (
    <div
      data-interactive="menu"
      className="
        absolute right-0 bottom-16
        w-[200px] p-2.5
        rounded-xl
        bg-slate-900/70 backdrop-blur-md
        flex flex-col gap-2
      "
    >
      <button
        type="button"
        onClick={onToggleApp}
        className="
          w-full py-2.5 px-3
          rounded-[10px]
          border border-white/10
          bg-white/5
          text-white/90 text-left text-sm
          cursor-pointer
          hover:bg-white/10 transition-colors
        "
      >
        {appVisible ? '隐藏应用' : '打开应用'}
      </button>
      <button
        type="button"
        onClick={onTogglePet}
        className="
          w-full py-2.5 px-3
          rounded-[10px]
          border border-white/10
          bg-white/5
          text-white/90 text-left text-sm
          cursor-pointer
          hover:bg-white/10 transition-colors
        "
      >
        {petVisible ? '隐藏桌宠' : '打开桌宠'}
      </button>
      <button
        type="button"
        onClick={onShowStatus}
        className="
          w-full py-2.5 px-3
          rounded-[10px]
          border border-white/10
          bg-white/5
          text-white/90 text-left text-sm
          cursor-pointer
          hover:bg-white/10 transition-colors
        "
      >
        状态面板
      </button>
      <div className="flex items-center justify-between gap-2.5">
        <span className="text-white/80 text-xs">速度</span>
        <input
          type="range"
          min={40}
          max={260}
          value={speed}
          onChange={(e) => onSpeedChange?.(Number(e.target.value))}
          className="w-[120px] accent-amber-500"
        />
      </div>
      <button
        type="button"
        onClick={onReset}
        className="
          w-full py-2.5 px-3
          rounded-[10px]
          border border-white/10
          bg-white/5
          text-white/90 text-left text-sm
          cursor-pointer
          hover:bg-white/10 transition-colors
        "
      >
        重置位置
      </button>
      <button
        type="button"
        onClick={onQuit}
        className="
          w-full py-2.5 px-3
          rounded-[10px]
          border border-white/10
          bg-white/5
          text-white/90 text-left text-sm
          cursor-pointer
          hover:bg-white/10 transition-colors
        "
      >
        退出应用
      </button>
    </div>
  )
}
