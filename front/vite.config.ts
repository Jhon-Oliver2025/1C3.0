import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Detectar se está em produção ou desenvolvimento
  const isProduction = mode === 'production';
  
  // Forçar desenvolvimento local para evitar problemas
  const isDevelopment = mode === 'development' || !isProduction;
  
  // Configurar target da API baseado no ambiente
  const apiTarget = isDevelopment 
    ? 'http://localhost:5000'  // HTTP em desenvolvimento local
    : 'https://1crypten.space';  // HTTPS em produção
  
  console.log(`🔧 Vite Mode: ${mode}`);
  console.log(`🎯 API Target: ${apiTarget}`);
  console.log(`🔍 Is Development: ${isDevelopment}`);
  console.log(`🔍 Is Production: ${isProduction}`);

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 3000,
      host: true,
      fs: {
        allow: ['..', './src/assets']
      },
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: !isDevelopment, // false em desenvolvimento, true em produção
          ws: true,
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('proxy error', err);
            });
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('Enviando requisição para o alvo:', req.method, req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('Recebida resposta do alvo:', proxyRes.statusCode, req.url);
            });
          }
        }
      }
    },
    build: {
      target: 'es2015',
      minify: 'esbuild', // Usar sempre esbuild para evitar problemas com terser no Docker
      sourcemap: false,
      chunkSizeWarningLimit: 1000,
      assetsInlineLimit: 0, // Não inlinear assets para evitar problemas com vídeos
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            styled: ['styled-components'],
            router: ['react-router-dom']
          },
          assetFileNames: (assetInfo) => {
            // Manter estrutura de pastas para vídeos
            if (assetInfo.name && assetInfo.name.endsWith('.mp4')) {
              return 'assets/videos/[name]-[hash][extname]';
            }
            return 'assets/[name]-[hash][extname]';
          }
        }
      }
    }
  };
})