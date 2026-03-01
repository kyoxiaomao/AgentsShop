import { useEffect, useMemo } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { setAgents, setStatusMap, setActiveAgent } from '../store/chatSlice'

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

export default function Sidebar() {
  const dispatch = useDispatch()
  const { agents, statusMap, activeAgentId } = useSelector((state) => state.chat)

  useEffect(() => {
    // 加载 Agent 列表
    fetch('/api/agents')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data?.agents) && data.agents.length > 0) {
          dispatch(setAgents(data.agents))
        } else {
          dispatch(setAgents(fallbackAgents))
        }
        if (data?.status && typeof data.status === 'object') {
          dispatch(setStatusMap(data.status))
        }
      })
      .catch(() => {
        dispatch(setAgents(fallbackAgents))
      })
  }, [dispatch])

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

  const handleSelectAgent = (agent) => {
    dispatch(setActiveAgent(agent.id))
  }

  return (
    <aside className="w-[280px] border-r border-slate-800 bg-dark-900/60 p-4 overflow-auto">
      <div className="mb-3 text-sm font-semibold text-slate-200">
        Agent 列表
      </div>
      <div className="space-y-3">
        {viewAgents.map((agent) => (
          <div
            key={agent.id}
            onClick={() => handleSelectAgent(agent)}
            className={`
              flex items-center justify-between gap-3
              rounded-xl border p-3 cursor-pointer transition
              ${activeAgentId === agent.id
                ? 'border-indigo-500/60 bg-indigo-500/10'
                : 'border-slate-800 bg-dark-800/40 hover:border-slate-600'
              }
            `}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-700 grid place-items-center text-sm font-semibold">
                {agent.name.slice(0, 1)}
              </div>
              <div>
                <div className="text-sm font-medium">{agent.name}</div>
                <div
                  className={`mt-1 inline-flex items-center rounded-full border px-2 py-0.5 text-xs ${
                    statusStyles[agent.status]
                  }`}
                >
                  {statusLabels[agent.status] ?? statusLabels.offline}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
