import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Porta padrão do Vite para evitar conflito
    strictPort: true // Impede que o Vite use outra porta se 5173 estiver ocupada
  }
})
