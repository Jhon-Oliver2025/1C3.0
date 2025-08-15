import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Detectar se está em produção ou desenvolvimento
  const isProduction = mode === 'production';
  
  // Configurar target da API baseado no ambiente
  const apiTarget = isProduction 
    ? 'https://1crypten.space'  // HTTPS em produção
    : 'http://127.0.0.1:5000';  // HTTP em desenvolvimento local

  return {
    plugins: [react()],
    
    // Otimizações para produção
    build: {
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: isProduction, // Remove console.log em produção
          drop_debugger: isProduction,
          pure_funcs: isProduction ? ['console.log', 'console.info'] : []
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            styled: ['styled-components']
          }
        }
      },
      chunkSizeWarningLimit: 1000,
      assetsInlineLimit: 4096 // Inline assets menores que 4kb
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 3000,
      host: true,
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
      target: 'es2015',
      minify: 'esbuild',
      sourcemap: false,
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom']
          }
        }
      }
    }
  };
})