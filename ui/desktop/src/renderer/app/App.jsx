import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Layout from './components/Layout'
import AgentPage from './pages/AgentPage'
import AdminPage from './pages/AdminPage'

// 权限守卫组件
function ProtectedRoute({ children, requiredRole }) {
  const { role } = useSelector((state) => state.auth)

  if (requiredRole === 'admin' && role !== 'admin') {
    return <Navigate to="/" replace />
  }

  return children
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<AgentPage />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
