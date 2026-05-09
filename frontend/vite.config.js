import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for Heritage Explorer frontend
// Configured with React plugin for JSX support
export default defineConfig({
  plugins: [react()],
})
