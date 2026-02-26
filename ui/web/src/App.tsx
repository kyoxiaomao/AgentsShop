import { useState } from 'react'

type AgentStatus = 'idle' | 'busy'

type Agent = {
  id: string
  name: string
  status: AgentStatus
}

type ChatRole = 'user' | 'agent'

type ChatMessage = {
  id: string
  role: ChatRole
  text: string
  createdAt: number
}

type PageKey = '主页' | '次页1' | '次页2'

const agentsSeed: Agent[] = [
  { id: 'sera', name: 'Sera', status: 'idle' },
  { id: 'archivist', name: 'Archivist', status: 'busy' },
  { id: 'builder', name: 'Builder', status: 'idle' }
]

function App() {
  const [page, setPage] = useState<PageKey>('主页')
  const [agents] = useState<Agent[]>(agentsSeed)
  const [selectedAgentId, setSelectedAgentId] = useState<string>(agentsSeed[0]?.id ?? '')
  const [draft, setDraft] = useState('')
  const [messagesByAgent, setMessagesByAgent] = useState<Record<string, ChatMessage[]>>(() => {
    const init: Record<string, ChatMessage[]> = {}
    for (const a of agentsSeed) init[a.id] = []
    return init
  })

  const selectedAgent = agents.find((a: Agent) => a.id === selectedAgentId) ?? agents[0]
  const selectedMessages = selectedAgent ? messagesByAgent[selectedAgent.id] ?? [] : []

  const sendMessage = () => {
    if (!selectedAgent) return
    const text = draft.trim()
    if (!text) return

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text,
      createdAt: Date.now()
    }

    const agentMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'agent',
      text: `收到：${text}`,
      createdAt: Date.now() + 1
    }

    setMessagesByAgent((prev: Record<string, ChatMessage[]>) => ({
      ...prev,
      [selectedAgent.id]: [...(prev[selectedAgent.id] ?? []), userMsg, agentMsg]
    }))
    setDraft('')
  }

  return (
    <div className="h-full w-full p-3">
      <div className="mx-auto flex h-full w-full max-w-6xl flex-col gap-3">
        <header className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-2 backdrop-blur">
        {(['主页', '次页1', '次页2'] as const).map((p) => (
          <button
            key={p}
            type="button"
            className={
              p === page
                ? 'h-8 rounded-lg border border-indigo-400/50 bg-indigo-500/20 px-3 text-sm font-medium text-white'
                : 'h-8 rounded-lg border border-white/10 bg-white/5 px-3 text-sm font-medium text-white/85 hover:bg-white/10'
            }
            onClick={() => setPage(p)}
          >
            {p}
          </button>
        ))}
        </header>

        {page !== '主页' ? (
          <main className="flex flex-1 items-center justify-center">
            <div className="rounded-xl border border-white/10 bg-white/5 px-5 py-4 text-white/80">
              {page}
            </div>
          </main>
        ) : (
          <main className="flex flex-1 gap-3 overflow-hidden">
            <aside className="w-72 shrink-0 overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur">
              <div className="border-b border-white/10 px-3 py-2 text-sm font-semibold text-white/90">
                Agents
              </div>
              <div className="flex h-full flex-col gap-2 overflow-auto p-2">
              {agents.map((a: Agent) => {
                const active = a.id === selectedAgentId
                return (
                  <button
                    key={a.id}
                    type="button"
                    className={
                      active
                        ? 'flex items-center justify-between gap-2 rounded-xl border border-indigo-400/50 bg-indigo-500/20 px-3 py-3 text-left'
                        : 'flex items-center justify-between gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-left hover:bg-white/10'
                    }
                    onClick={() => setSelectedAgentId(a.id)}
                  >
                    <span className="text-sm font-semibold text-white/95">{a.name}</span>
                    <span
                      className={
                        a.status === 'busy'
                          ? 'rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-0.5 text-xs text-amber-200'
                          : 'rounded-full border border-emerald-300/30 bg-emerald-300/10 px-2 py-0.5 text-xs text-emerald-200'
                      }
                    >
                      {a.status === 'busy' ? '忙碌' : '空闲'}
                    </span>
                  </button>
                )
              })}
              </div>
            </aside>

            <section className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur">
              <div className="flex h-12 items-center justify-between border-b border-white/10 px-3">
                <div className="text-sm font-bold text-white/95">{selectedAgent?.name ?? '-'}</div>
                <div
                  className={
                    selectedAgent?.status === 'busy'
                      ? 'rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-0.5 text-xs text-amber-200'
                      : 'rounded-full border border-emerald-300/30 bg-emerald-300/10 px-2 py-0.5 text-xs text-emerald-200'
                  }
                >
                  {selectedAgent?.status === 'busy' ? '忙碌' : '空闲'}
                </div>
              </div>

              <div className="flex flex-1 flex-col gap-2 overflow-auto p-3">
              {selectedMessages.length === 0 ? (
                <div className="text-sm text-white/60">开始与该角色对话</div>
              ) : (
                selectedMessages.map((m: ChatMessage) => (
                  <div
                    key={m.id}
                    className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
                  >
                    <div
                      className={
                        m.role === 'user'
                          ? 'max-w-[90%] rounded-xl border border-indigo-400/30 bg-indigo-500/15 px-3 py-2 text-sm text-white/90'
                          : 'max-w-[90%] rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/85'
                      }
                    >
                      {m.text}
                    </div>
                  </div>
                ))
              )}
              </div>

              <div className="flex gap-2 border-t border-white/10 p-3">
                <input
                  className="h-10 flex-1 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white/90 placeholder:text-white/35 focus:outline-none focus:ring-2 focus:ring-indigo-400/40"
                  value={draft}
                  placeholder="输入消息…"
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      sendMessage()
                    }
                  }}
                />
                <button
                  className="h-10 shrink-0 rounded-xl border border-indigo-400/50 bg-indigo-500/20 px-4 text-sm font-semibold text-white hover:bg-indigo-500/25"
                  type="button"
                  onClick={sendMessage}
                >
                  发送
                </button>
              </div>
            </section>
          </main>
        )}
      </div>
    </div>
  )
}

export default App
