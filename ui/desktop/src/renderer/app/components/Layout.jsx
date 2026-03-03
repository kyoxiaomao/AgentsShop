import { useLocation } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

export default function Layout({ children }) {
  const location = useLocation()
  const isAdminRoute = location.pathname.startsWith('/admin')

  return (
    <div className="h-screen flex flex-col bg-dark-950 text-slate-100">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        {!isAdminRoute && <Sidebar />}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
