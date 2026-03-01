import { Link, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'

export default function Header() {
  const location = useLocation()
  const { role, username } = useSelector((state) => state.auth)

  return (
    <header className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-dark-900/80 backdrop-blur-sm">
      <div className="flex items-center gap-6">
        <div className="text-lg font-semibold text-white">AgentShop</div>
        <nav className="flex items-center gap-4 text-sm">
          <Link
            to="/"
            className={`transition ${
              location.pathname === '/'
                ? 'text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            控制台
          </Link>
          {role === 'admin' && (
            <Link
              to="/admin"
              className={`transition ${
                location.pathname === '/admin'
                  ? 'text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              管理后台
            </Link>
          )}
        </nav>
      </div>

      <div className="flex items-center gap-4">
        {username && (
          <span className="text-sm text-slate-400">{username}</span>
        )}
      </div>
    </header>
  )
}
