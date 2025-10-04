import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use a fallback for GitHub Actions where import.meta.env may not be defined
const base = process.env.VITE_BASE || '/'

export default defineConfig({
  plugins: [react()],
  base
})
