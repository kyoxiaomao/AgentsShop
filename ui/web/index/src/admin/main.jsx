import React from 'react'
import { createRoot } from 'react-dom/client'
import AdminApp from './AdminApp.jsx'
import '../index.css'

const root = document.getElementById('root')
createRoot(root).render(
  <React.StrictMode>
    <AdminApp />
  </React.StrictMode>,
)
