import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/missions': 'http://localhost:8000',
      '/shop': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/territories': 'http://localhost:8000',
      '/user_missions': 'http://localhost:8000',
      '/tma': 'http://localhost:8000',
      '/equipment': 'http://localhost:8000',
    }
  }
})
