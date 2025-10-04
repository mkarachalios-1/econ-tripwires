import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Safely read VITE_BASE or default to '/'
const base = process.env.VITE_BASE || '/'

export default defineConfig({
  plugins: [react()],
  base,
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
