import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';
  
  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: isProduction ? 'https://api.1crypten.space' : 'http://localhost:5000',
          changeOrigin: true,
          secure: isProduction
        }
      }
    },
    build: {
      target: 'es2015',
      minify: isProduction ? 'terser' : false,
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            icons: ['react-icons']
          }
        }
      },
      ...(isProduction && {
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true
          }
        }
      })
    },
    define: {
      'process.env.NODE_ENV': JSON.stringify(mode),
      'process.env.API_BASE_URL': JSON.stringify(
        isProduction ? 'https://api.1crypten.space' : 'http://localhost:5000'
      )
    }
  };
});