import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import type { UserConfig } from 'vite';

export default defineConfig(({ mode }: { mode: string }): UserConfig => {
  // Carrega as variáveis de ambiente do arquivo .env
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          // Proxy para o backend na porta 5000
          target: 'http://localhost:5000',
          changeOrigin: true,
          rewrite: (path: string) => path.replace(/^\/api/, '')
        },
        '/webhook': {
          // Proxy para o n8n na porta padrão 5678
          target: env.N8N_WEBHOOK_URL || 'http://localhost:5678',
          changeOrigin: true
        }
      }
    },
    build: {
      // Configurações para melhor compatibilidade no Docker
      target: 'es2015',
      minify: 'esbuild' as const,
      sourcemap: false
    }
  };
});