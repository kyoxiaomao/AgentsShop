import { useEffect, useMemo, useRef, useState } from 'react'

const fallbackAgents = [
  { id: 'seraAgent', name: 'seraAgent', cn_name: '塞瑞', enabled: true },
]

const statusLabels = {
  busy: '忙碌',
  idle: '空闲',
  offline: '离线',
}

const statusStyles = {
  busy: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  idle: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  offline: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
}

export default function App() {
  const [agents, setAgents] = useState(fallbackAgents)
  const [statusMap, setStatusMap] = useState({})
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const streamIdRef = useRef(null)
  const reportDebug = (event, data = {}) => {
    fetch('/api/debug', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event,
        data,
      }),
    }).catch(() => {})
  }
  const normalizeContent = (value) => {
    if (typeof value === 'string') {
      return value
    }
    if (value === null || value === undefined) {
      return ''
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  useEffect(() => {
    reportDebug('frontend_ready', { url: window.location.href })
    fetch('/api/agents')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data?.agents) && data.agents.length > 0) {
          setAgents(data.agents)
        }
        if (data?.status && typeof data.status === 'object') {
          setStatusMap(data.status)
        }
        reportDebug('frontend_agents_loaded', {
          agentCount: Array.isArray(data?.agents) ? data.agents.length : 0,
        })
      })
      .catch((error) => {
        reportDebug('frontend_agents_error', { message: String(error) })
      })
  }, [])

  const viewAgents = useMemo(() => {
    return agents.map((agent) => {
      const status = statusMap?.[agent.id]?.status ?? 'offline'
      return {
        id: agent.id,
        name: agent.cn_name || agent.name || agent.id,
        rawName: agent.name || agent.id,
        status,
      }
    })
  }, [agents, statusMap])

  const activeAgent = viewAgents[0] ?? {
    id: 'unknown',
    name: '未知 Agent',
    rawName: 'unknown',
    status: 'offline',
  }

  useEffect(() => {
    const agentId = activeAgent.rawName || activeAgent.id
    if (!agentId || agentId === 'unknown') {
      return
    }
    fetch(`/api/messages?agent_id=${encodeURIComponent(agentId)}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data?.messages)) {
          setMessages(data.messages)
        }
        reportDebug('frontend_messages_loaded', {
          agentId,
          count: Array.isArray(data?.messages) ? data.messages.length : 0,
        })
      })
      .catch((error) => {
        reportDebug('frontend_messages_error', {
          agentId,
          message: String(error),
        })
      })
  }, [activeAgent.id, activeAgent.rawName])

  useEffect(() => {
    const handleError = (event) => {
      reportDebug('frontend_runtime_error', {
        message: event?.message,
        filename: event?.filename,
        lineno: event?.lineno,
        colno: event?.colno,
      })
    }
    const handleRejection = (event) => {
      reportDebug('frontend_unhandled_rejection', {
        reason: String(event?.reason),
      })
    }
    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleRejection)
    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleRejection)
    }
  }, [])

  const handleSend = async () => {
    const content = input.trim()
    if (!content || sending) {
      return
    }
    const agentId = activeAgent.rawName || activeAgent.id
    setInput('')
    setSending(true)
    const tempId = `assist-${Date.now()}`
    streamIdRef.current = tempId
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: normalizeContent(content), ts: new Date().toISOString() },
      { role: 'assistant', content: '', ts: new Date().toISOString(), id: tempId },
    ])
    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          content,
        }),
      })
      if (!res.body) {
        throw new Error('empty_stream')
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) {
          break
        }
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''
        for (const part of parts) {
          const line = part
            .split('\n')
            .map((item) => item.trim())
            .find((item) => item.startsWith('data:'))
          if (!line) {
            continue
          }
          const jsonText = line.replace(/^data:\s*/, '')
          if (!jsonText) {
            continue
          }
          let payload
          try {
            payload = JSON.parse(jsonText)
          } catch {
            continue
          }
          if (payload.type === 'delta') {
            setMessages((prev) =>
              prev.map((item) =>
                item.id === streamIdRef.current
                  ? { ...item, content: `${item.content}${payload.content || ''}` }
                  : item,
              ),
            )
          } else if (payload.type === 'done') {
            if (Array.isArray(payload?.messages)) {
              setMessages(payload.messages)
            }
            reportDebug('frontend_chat_done', {
              agentId,
              messages: Array.isArray(payload?.messages) ? payload.messages.length : 0,
            })
          } else if (payload.type === 'error') {
            reportDebug('frontend_chat_error', {
              agentId,
              message: String(payload.message),
            })
          }
        }
      }
    } catch (error) {
      reportDebug('frontend_chat_error', {
        agentId,
        message: String(error),
      })
    } finally {
      setSending(false)
      streamIdRef.current = null
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="text-lg font-semibold">Agent 控制台</div>
          <nav className="flex items-center gap-6 text-sm text-slate-300">
            <a className="transition hover:text-white" href="#">
              主页
            </a>
            <a className="transition hover:text-white" href="#">
              次页1
            </a>
            <a className="transition hover:text-white" href="#">
              次页2
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-[280px_1fr] gap-6 px-6 py-6">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="mb-3 text-sm font-semibold text-slate-200">
            Agent 列表
          </div>
          <div className="space-y-3">
            {viewAgents.map((agent) => (
              <div
                key={agent.id}
                className="flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-3"
              >
                <div className="flex items-center gap-3">
                  <div className="grid h-10 w-10 place-items-center rounded-full bg-slate-700 text-sm font-semibold text-slate-100">
                    {agent.name.slice(0, 1)}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{agent.name}</div>
                    <div
                      className={`mt-1 inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${statusStyles[agent.status]}`}
                    >
                      {statusLabels[agent.status] ?? statusLabels.offline}
                    </div>
                  </div>
                </div>
                <button className="rounded-full border border-slate-800 px-3 py-1 text-xs text-slate-300 transition hover:border-slate-600 hover:text-white">
                  查看
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-semibold">{activeAgent.name}</div>
              <div
                className={`mt-1 inline-flex items-center rounded-full border px-3 py-1 text-xs ${statusStyles[activeAgent.status]}`}
              >
                {statusLabels[activeAgent.status] ?? statusLabels.offline}
              </div>
            </div>
            <div className="text-xs text-slate-400">最近对话</div>
          </div>

          <div className="flex-1 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300">
            <div className="space-y-3">
              {messages.length === 0 ? (
                <div className="rounded-xl bg-slate-900/70 px-3 py-2">
                  暂无对话，发送一条消息开始交流。
                </div>
              ) : (
                messages.map((item, index) => (
                  <div
                    key={`${item.ts ?? 'msg'}-${index}`}
                    className={`rounded-xl px-3 py-2 ${
                      item.role === 'user'
                        ? 'bg-slate-800/70 text-right text-slate-200'
                        : 'bg-slate-900/70'
                    }`}
                  >
                    {normalizeContent(item.content)}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              className="h-11 flex-1 rounded-xl border border-slate-800 bg-slate-950/60 px-4 text-sm text-slate-100 outline-none ring-0 transition focus:border-slate-500"
              placeholder="请输入信息"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  handleSend()
                }
              }}
            />
            <button
              className="h-11 rounded-xl bg-indigo-500 px-5 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-indigo-500/60"
              type="button"
              onClick={handleSend}
              disabled={sending || !input.trim()}
            >
              发送
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
