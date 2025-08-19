# 🎬 Troubleshooting - Vídeos das Aulas Despertar Crypto

## 📋 Problema Identificado
Os vídeos das aulas do curso Despertar Crypto não estão carregando em produção.

## 🔍 Diagnóstico Realizado

### ✅ Arquivos Verificados
- [x] Arquivos de vídeo existem em `front/src/assets/vdc/` (v1.mp4 até v8.mp4)
- [x] Imports corretos no componente AulaPage.tsx
- [x] VideoMap configurado corretamente

### 🛠️ Correções Aplicadas

#### 1. **Configuração do Vite (vite.config.ts)**
```typescript
// Antes
assetsInlineLimit: 4096,

// Depois
assetsInlineLimit: 0, // Não inlinear assets para evitar problemas com vídeos

// Adicionado
assetFileNames: (assetInfo) => {
  // Manter estrutura de pastas para vídeos
  if (assetInfo.name && assetInfo.name.endsWith('.mp4')) {
    return 'assets/videos/[name]-[hash][extname]';
  }
  return 'assets/[name]-[hash][extname]';
}
```

#### 2. **Configuração do Nginx (nginx.conf)**
```nginx
# Configuração específica para arquivos de vídeo
location ~* \.(mp4|webm|ogg|avi|mov)$ {
    expires 30d;
    add_header Cache-Control "public";
    add_header Accept-Ranges bytes;
    
    # Permitir range requests para streaming
    location ~* \.(mp4)$ {
        mp4;
        mp4_buffer_size 1m;
        mp4_max_buffer_size 5m;
    }
}
```

#### 3. **Melhor Tratamento de Erros (AulaPage.tsx)**
```typescript
// Adicionado logs de debug e tratamento de erro
onError={(e) => {
  console.error('Erro ao carregar vídeo:', e.target.error);
  console.log('Tentando carregar:', currentLesson ? videoMap[currentLesson.id] : v1);
}}
onLoadStart={() => {
  console.log('Iniciando carregamento do vídeo:', currentLesson ? videoMap[currentLesson.id] : v1);
}}
```

## 🚀 Passos para Deploy

### 1. **Rebuild do Frontend**
```bash
cd front
npm run build
```

### 2. **Rebuild do Container Docker**
```bash
# Parar containers
docker-compose down

# Rebuild sem cache
docker-compose build --no-cache frontend

# Subir novamente
docker-compose up -d
```

### 3. **Verificar Logs**
```bash
# Logs do frontend
docker-compose logs frontend

# Logs do nginx
docker-compose logs nginx
```

## 🔧 Debug em Produção

### 1. **Script de Diagnóstico**
Use o arquivo `debug_video_loading.js` no console do navegador:

```javascript
// Copie e cole no console do navegador na página das aulas
// O script está em: debug_video_loading.js
```

### 2. **Verificações Manuais**

#### Verificar se os arquivos estão sendo servidos:
```bash
# Acessar container
docker exec -it <container_frontend> sh

# Verificar arquivos buildados
ls -la /usr/share/nginx/html/assets/
ls -la /usr/share/nginx/html/assets/videos/
```

#### Testar URLs diretamente:
```
https://seudominio.com/assets/videos/v1-[hash].mp4
https://seudominio.com/assets/videos/v2-[hash].mp4
```

### 3. **Logs do Navegador**
Abra o DevTools (F12) e verifique:
- **Console**: Erros de carregamento
- **Network**: Status das requisições dos vídeos
- **Sources**: Se os arquivos estão disponíveis

## 🎯 Possíveis Causas Restantes

### 1. **Problema de MIME Type**
```nginx
# Adicionar ao nginx.conf se necessário
location ~* \.mp4$ {
    add_header Content-Type video/mp4;
}
```

### 2. **Problema de CORS**
```nginx
# Adicionar headers CORS se necessário
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
```

### 3. **Problema de Tamanho de Arquivo**
```nginx
# Aumentar limite se necessário
client_max_body_size 100M;
```

### 4. **Problema de CDN/Proxy**
Se usando CDN (Cloudflare, etc.), verificar:
- Cache settings
- File size limits
- MIME type handling

## 📞 Próximos Passos

1. **Aplicar as correções** (já feito)
2. **Rebuild e deploy**
3. **Testar em produção**
4. **Usar script de debug** se ainda houver problemas
5. **Verificar logs** do servidor

## 🆘 Se o Problema Persistir

### Alternativa 1: Hospedar Vídeos Externamente
```typescript
// Usar URLs externas (YouTube, Vimeo, S3, etc.)
const videoMap: { [key: string]: string } = {
  '1': 'https://external-cdn.com/v1.mp4',
  '2': 'https://external-cdn.com/v2.mp4',
  // ...
};
```

### Alternativa 2: Streaming Adaptativo
```typescript
// Implementar HLS ou DASH
import Hls from 'hls.js';

// Usar .m3u8 files para streaming
```

### Alternativa 3: Lazy Loading
```typescript
// Carregar vídeos sob demanda
const [videoSrc, setVideoSrc] = useState<string | null>(null);

useEffect(() => {
  if (currentLesson) {
    import(`../../assets/vdc/v${currentLesson.id}.mp4`)
      .then(module => setVideoSrc(module.default));
  }
}, [currentLesson]);
```

---

**📝 Nota**: Todas as correções foram aplicadas. Execute o rebuild e teste em produção.