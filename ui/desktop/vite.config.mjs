import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { resolve } from 'node:path'

export default defineConfig({
  base: './',
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(process.cwd(), 'src/renderer'),
      '@pet': resolve(process.cwd(), 'src/renderer/pet'),
      '@app': resolve(process.cwd(), 'src/renderer/app'),
      '@shared': resolve(process.cwd(), 'src/renderer/shared'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        pet: resolve(__dirname, 'index.html'),
        app: resolve(__dirname, 'app.html'),
      },
      output: {
        entryFileNames: (chunkInfo) => {
          return chunkInfo.name === 'pet' ? 'pet/index.js' : 'app/index.js'
        },
        chunkFileNames: '[name]/[hash].js',
        assetFileNames: '[name]/[hash].[ext]',
      },
    },
  },
  server: {
    port: 5173,
  },
})
