import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

const rootDir = process.cwd()

export default defineConfig({
  base: './',
  plugins: [react()],
  server: {
    open: true,
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(rootDir, 'index.html'),
        admin: path.resolve(rootDir, 'admin.html'),
      },
    },
  },
})
