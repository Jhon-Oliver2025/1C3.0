import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Carrega as variáveis de ambiente do arquivo .env
  // O terceiro argumento '' garante que todas as variáveis (não apenas as com prefixo VITE_) sejam carregadas
  const env = loadEnv(mode, process.cwd(), '');

  // --- Adicione estes logs para depuração ---
  console.log('--- Vite Config: Variáveis de Ambiente Carregadas ---');
  console.log('Modo:', mode);
  console.log('Diretório de Trabalho:', process.cwd());
  console.log('VITE_EVO_AI_AGENT_BASE_URL:', env.VITE_EVO_AI_AGENT_BASE_URL);
  console.log('VITE_EVO_AI_API_KEY:', env.VITE_EVO_AI_API_KEY);
  console.log('----------------------------------------------------');
  // ------------------------------------------

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          // Usa a variável de ambiente carregada para o target
          target: env.VITE_EVO_AI_AGENT_BASE_URL || 'https://api-evoai.evoapicloud.com',
          changeOrigin: true,
          // O rewrite deve remover o '/api' para que a URL base da API seja usada
          rewrite: (path) => path.replace(/^\/api/, ''),
          headers: {
            // Usa a variável de ambiente carregada para o header x-api-key
            'x-api-key': env.VITE_EVO_AI_API_KEY
          }
        }
      }
    },
    define: {
      // Isso expõe as variáveis de ambiente para o código do seu frontend (import.meta.env)
      // AVISO: Expor todo o process.env pode ser um risco de segurança.
      // Para produção, considere expor apenas as variáveis necessárias explicitamente.
      'process.env': env
    }
  };
});
