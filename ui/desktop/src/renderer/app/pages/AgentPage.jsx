import { useEffect, useRef, useState, useMemo } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { setMessages, addMessage, setSending, updateLastMessage } from '../store/chatSlice'

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

const markdownComponents = {
  p: ({ children }) => <p className="whitespace-pre-wrap leading-6">{children}</p>,
  ul: ({ children }) => <ul className="list-disc space-y-1 pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal space-y-1 pl-5">{children}</ol>,
  li: ({ children }) => <li className="leading-6">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-slate-700 pl-3 text-slate-300">
      {children}
    </blockquote>
  ),
  strong: ({ children }) => <strong className="font-semibold text-slate-100">{children}</strong>,
  code: ({ inline, children }) =>
    inline ? (
      <code className="rounded bg-slate-800/80 px-1 py-0.5 text-xs text-slate-100">
        {children}
      </code>
    ) : (
      <code className="block whitespace-pre-wrap">{children}</code>
    ),
  pre: ({ children }) => (
    <pre className="overflow-auto rounded-lg border border-slate-800 bg-dark-950/80 p-3 text-xs text-slate-200">
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="overflow-auto">
      <table className="w-full border-collapse text-left text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-slate-800 bg-dark-900/70 px-3 py-2 font-semibold text-slate-100">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-slate-800 px-3 py-2 align-top text-slate-200">
      {children}
    </td>
  ),
  a: ({ children, href }) => (
    <a className="text-indigo-300 underline decoration-slate-500" href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  ),
}

const fallbackAgents = [
  { id: 'seraAgent', name: 'seraAgent', cn_name: '塞瑞', enabled: true },
]

function normalizeContent(value) {
  if (typeof value === 'string') return value
  if (value === null || value === undefined) return ''
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  return String(value)
}

function resolveWsUrl() {
  if (typeof window === 'undefined') return 'ws://127.0.0.1:8000/ws'
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const hostname = window.location.hostname || '127.0.0.1'
  return `${protocol}://${hostname}:8000/ws`
}

export default function AgentPage() {
  const dispatch = useDispatch()
  const { agents, statusMap, messages, sending } = useSelector((state) => state.chat)
  const [input, setInput] = useState('')
  const [inputMode, setInputMode] = useState('聊天')
  const [dotCount, setDotCount] = useState(1)
  const streamIdRef = useRef(null)

  // 获取当前活跃的 Agent
  const activeAgent = useMemo(() => {
    const viewAgents = agents.map((agent) => {
      const status = statusMap?.[agent.id]?.status ?? 'offline'
      return {
        id: agent.id,
        name: agent.cn_name || agent.name || agent.id,
        rawName: agent.name || agent.id,
        status,
      }
    })
    return viewAgents[0] ?? { id: 'unknown', name: '未知 Agent', rawName: 'unknown', status: 'offline' }
  }, [agents, statusMap])

  // 加载消息
  useEffect(() => {
    const agentId = activeAgent.rawName || activeAgent.id
    if (!agentId || agentId === 'unknown') return

    fetch(`/api/messages?agent_id=${encodeURIComponent(agentId)}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data?.messages)) {
          dispatch(setMessages(data.messages))
        }
      })
      .catch(() => {})
  }, [activeAgent.id, activeAgent.rawName, dispatch])

  // 加载动画
  useEffect(() => {
    if (!sending) return
    const timer = window.setInterval(() => {
      setDotCount((prev) => (prev >= 3 ? 1 : prev + 1))
    }, 500)
    return () => window.clearInterval(timer)
  }, [sending])

  const getDisplayName = (role) => {
    if (role === 'user') return '我'
    return activeAgent.name
  }

  const getAvatarLabel = (role) => {
    const name = getDisplayName(role)
    if (!name) return '·'
    return name.trim().slice(0, 1)
  }

  const handleSend = async () => {
    const content = input.trim()
    if (!content || sending) return

    const agentId = activeAgent.rawName || activeAgent.id
    setInput('')
    dispatch(setSending(true))

    const tempId = `assist-${Date.now()}`
    streamIdRef.current = tempId

    // 添加用户消息和空的助手消息
    dispatch(addMessage({ role: 'user', content: normalizeContent(content), ts: new Date().toISOString() }))
    dispatch(addMessage({ role: 'assistant', content: '', ts: new Date().toISOString(), id: tempId }))

    try {
      const wsUrl = resolveWsUrl()
      await new Promise((resolve, reject) => {
        let settled = false
        let assistantContent = ''
        const ws = new WebSocket(wsUrl)

        const settle = (error) => {
          if (settled) return
          settled = true
          if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
            ws.close()
          }
          if (error) reject(error)
          else resolve()
        }

        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              type: 'chat',
              agent_id: agentId,
              session_id: 'default',
              content,
              mode: inputMode,
            })
          )
        }

        ws.onmessage = (event) => {
          let payload
          try {
            payload = JSON.parse(event.data)
          } catch {
            return
          }
          if (payload.type === 'delta') {
            const text = normalizeContent(payload.content)
            assistantContent += text
            dispatch(updateLastMessage({ id: tempId, content: assistantContent }))
            return
          }
          if (payload.type === 'done') {
            if (Array.isArray(payload?.messages)) {
              dispatch(setMessages(payload.messages))
            }
            settle()
            return
          }
          if (payload.type === 'error') {
            settle(new Error(payload?.message || 'ws_error'))
          }
        }

        ws.onerror = () => {
          settle(new Error('ws_error'))
        }

        ws.onclose = () => {
          if (!settled) resolve()
        }
      })
    } catch (error) {
      console.error('Chat error:', error)
    } finally {
      dispatch(setSending(false))
      streamIdRef.current = null
      setDotCount(1)
    }
  }

  return (
    <div className="h-full flex flex-col gap-4">
      {/* 标题区域 */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">{activeAgent.name}</div>
          <div
            className={`mt-1 inline-flex items-center rounded-full border px-3 py-1 text-xs ${
              statusStyles[activeAgent.status]
            }`}
          >
            {statusLabels[activeAgent.status] ?? statusLabels.offline}
          </div>
        </div>
        <div className="text-xs text-slate-400">最近对话</div>
      </div>

      {/* 消息区域 */}
      <div className="flex-1 rounded-2xl border border-slate-800 bg-dark-950/60 p-4 text-sm text-slate-300 overflow-auto">
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="rounded-xl bg-dark-900/70 px-3 py-2">
              暂无对话，发送一条消息开始交流。
            </div>
          ) : (
            messages.map((item, index) => {
              const isUser = item.role === 'user'
              const name = getDisplayName(item.role)
              const isStreamingTarget = item.id && item.id === streamIdRef.current
              const showThinking = sending && isStreamingTarget && !normalizeContent(item.content)

              return (
                <div
                  key={`${item.ts ?? 'msg'}-${index}`}
                  className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse text-right' : ''}`}
                >
                  <div className="w-9 h-9 rounded-full bg-slate-700 grid place-items-center text-xs font-semibold text-slate-100">
                    {getAvatarLabel(item.role)}
                  </div>
                  <div className={`max-w-[75%] ${isUser ? 'items-end' : ''}`}>
                    <div className={`mb-1 text-xs text-slate-400 ${isUser ? 'text-right' : ''}`}>
                      {name}
                    </div>
                    <div
                      className={`rounded-xl px-3 py-2 ${
                        isUser ? 'bg-slate-800/70 text-slate-200' : 'bg-dark-900/70'
                      }`}
                    >
                      {showThinking ? (
                        <div className="text-slate-300">思考中{'.'.repeat(dotCount)}</div>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                          {normalizeContent(item.content)}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* 输入区域 */}
      <div className="flex items-center gap-3">
        <select
          className="h-11 rounded-xl border border-slate-800 bg-dark-950/60 px-3 text-sm text-slate-100 outline-none transition focus:border-slate-500"
          value={inputMode}
          onChange={(e) => setInputMode(e.target.value)}
        >
          <option value="聊天">聊天</option>
          <option value="任务">任务</option>
          <option value="工具">工具</option>
        </select>
        <input
          className="h-11 flex-1 rounded-xl border border-slate-800 bg-dark-950/60 px-4 text-sm text-slate-100 outline-none transition focus:border-slate-500"
          placeholder="请输入信息"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
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
    </div>
  )
}

