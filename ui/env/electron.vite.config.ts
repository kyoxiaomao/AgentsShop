import { defineConfig } from 'electron-vite'
import path from 'node:path'

const desktopRoot = path.resolve(__dirname, '..', 'desktop')
const outRoot = path.resolve(__dirname, '.electron-vite')

export default defineConfig({
  main: {
    build: {
      rollupOptions: {
        input: path.join(desktopRoot, 'main', 'index.ts')
      },
      outDir: path.join(outRoot, 'main')
    }
  },
  preload: {
    build: {
      rollupOptions: {
        input: path.join(desktopRoot, 'preload', 'index.ts')
      },
      outDir: path.join(outRoot, 'preload')
    }
  },
  renderer: {
    root: path.join(__dirname, 'renderer'),
    base: './',
    publicDir: path.join(desktopRoot, 'main', 'public'),
    css: {
      postcss: path.join(__dirname, 'postcss.config.cjs')
    },
    server: {
      fs: {
        allow: [desktopRoot, __dirname]
      }
    },
    build: {
      rollupOptions: {
        input: path.join(__dirname, 'renderer', 'index.html')
      },
      outDir: path.join(outRoot, 'renderer')
    }
  }
})
