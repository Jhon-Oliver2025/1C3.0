import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Detectar se está em produção ou desenvolvimento
  const isProduction = mode === 'production';
  
  // Configurar target da API baseado no ambiente
  const apiTarget = isProduction 
    ? 'https://1crypten.space'  // HTTPS em produção
    : 'http://localhost:5000';  // HTTP em desenvolvimento local
  
  console.log(`🔧 Vite Mode: ${mode}`);
  console.log(`🎯 API Target: ${apiTarget}`);
  console.log(`🔍 Is Production: ${isProduction}`);

  return {
    optimizeDeps: {
      include: ['react', 'react-dom'],
      exclude: ['@rollup/rollup-linux-x64-musl']
    },
    esbuild: {
      target: 'es2020'
    },
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
          secure: isProduction, // true em produção para HTTPS
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
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name]-cb9db726.[hash].js`,
          chunkFileNames: `assets/[name]-cb9db726.[hash].js`,
          assetFileNames: (assetInfo) => {
            // Manter nome original para vídeos na pasta public
            if (assetInfo.name && assetInfo.name.endsWith('.mp4')) {
              return '[name][extname]';
            }
            return 'assets/[name]-cb9db726.[hash].[ext]';
          }
        }
      }
    }
  };
})