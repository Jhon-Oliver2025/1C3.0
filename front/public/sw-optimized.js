/**
 * Service Worker Otimizado para Performance
 * Melhora significativamente a velocidade de carregamento do PWA
 */

const CACHE_NAME = '1crypten-v2.0';
const STATIC_CACHE = '1crypten-static-v2.0';
const DYNAMIC_CACHE = '1crypten-dynamic-v2.0';
const API_CACHE = '1crypten-api-v2.0';

// Recursos críticos para cache imediato
const CRITICAL_RESOURCES = [
  '/',
  '/login',
  '/dashboard',
  '/static/js/main.js',
  '/static/css/main.css',
  '/logo3.png',
  '/terra2.png',
  '/manifest.json'
];

// Recursos para cache em background
const BACKGROUND_RESOURCES = [
  '/btc-analysis',
  '/crm',
  '/sales-admin',
  '/suporte',
  '/app1crypten',
  '/vitrine-alunos'
];

// APIs que podem ser cacheadas temporariamente
const CACHEABLE_APIS = [
  '/api/market-status',
  '/api/auth/check-admin',
  '/api/cleanup-status'
];

/**
 * Instalação do Service Worker
 */
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Instalando versão otimizada...');
  
  event.waitUntil(
    Promise.all([
      // Cache crítico - deve ser instalado imediatamente
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Cacheando recursos críticos...');
        return cache.addAll(CRITICAL_RESOURCES.map(url => new Request(url, { cache: 'reload' })));
      }),
      
      // Cache em background - não bloqueia a instalação
      cacheBackgroundResources()
    ])
  );
  
  // Ativar imediatamente
  self.skipWaiting();
});

/**
 * Cache de recursos em background
 */
async function cacheBackgroundResources() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    console.log('🔄 Cacheando recursos em background...');
    
    // Cache recursos não críticos sem bloquear
    for (const url of BACKGROUND_RESOURCES) {
      try {
        await cache.add(new Request(url, { cache: 'reload' }));
      } catch (error) {
        console.warn(`⚠️ Falha ao cachear ${url}:`, error);
      }
    }
  } catch (error) {
    console.warn('⚠️ Erro no cache em background:', error);
  }
}

/**
 * Ativação do Service Worker
 */
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Ativando versão otimizada...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      cleanupOldCaches(),
      // Tomar controle imediatamente
      self.clients.claim()
    ])
  );
});

/**
 * Limpeza de caches antigos
 */
async function cleanupOldCaches() {
  const cacheNames = await caches.keys();
  const validCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
  
  const deletePromises = cacheNames
    .filter(cacheName => !validCaches.includes(cacheName))
    .map(cacheName => {
      console.log(`🗑️ Removendo cache antigo: ${cacheName}`);
      return caches.delete(cacheName);
    });
  
  await Promise.all(deletePromises);
}

/**
 * Interceptação de requisições
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégias diferentes por tipo de recurso
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
  } else if (url.pathname.startsWith('/static/')) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleNavigationRequest(request));
  }
});

/**
 * Estratégia para requisições de API
 */
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // APIs críticas como login não devem ser cacheadas
  if (url.pathname.includes('/auth/login') || 
      url.pathname.includes('/auth/logout') ||
      request.method !== 'GET') {
    return fetch(request);
  }
  
  // APIs que podem ser cacheadas temporariamente
  if (CACHEABLE_APIS.some(api => url.pathname.includes(api))) {
    return handleCacheableApi(request);
  }
  
  // Outras APIs - network first
  return networkFirst(request, API_CACHE);
}

/**
 * Estratégia para APIs cacheáveis
 */
async function handleCacheableApi(request) {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Se tem cache e é recente (5 minutos), usar cache
  if (cachedResponse) {
    const cacheDate = new Date(cachedResponse.headers.get('sw-cache-date') || 0);
    const now = new Date();
    const fiveMinutes = 5 * 60 * 1000;
    
    if (now - cacheDate < fiveMinutes) {
      console.log('📋 Usando cache de API:', request.url);
      return cachedResponse;
    }
  }
  
  // Buscar da rede e cachear
  try {
    const response = await fetch(request);
    if (response.ok) {
      const responseClone = response.clone();
      const headers = new Headers(responseClone.headers);
      headers.set('sw-cache-date', new Date().toISOString());
      
      const modifiedResponse = new Response(await responseClone.blob(), {
        status: responseClone.status,
        statusText: responseClone.statusText,
        headers: headers
      });
      
      cache.put(request, modifiedResponse);
    }
    return response;
  } catch (error) {
    // Se falhar, usar cache mesmo que antigo
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

/**
 * Estratégia para recursos estáticos
 */
async function handleStaticRequest(request) {
  // Cache first para recursos estáticos
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Se não está em cache, buscar e cachear
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.warn('⚠️ Falha ao carregar recurso estático:', request.url);
    return new Response('Recurso não disponível offline', { status: 503 });
  }
}

/**
 * Estratégia para navegação
 */
async function handleNavigationRequest(request) {
  // Para navegação, tentar rede primeiro, depois cache
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // Se falhar, tentar cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fallback para página offline ou index
    const fallback = await caches.match('/');
    return fallback || new Response('Página não disponível offline', {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

/**
 * Estratégia Network First
 */
async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

/**
 * Mensagens do cliente
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    clearAllCaches();
  }
});

/**
 * Limpar todos os caches
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('🗑️ Todos os caches foram limpos');
}

console.log('🚀 Service Worker Otimizado carregado e pronto!');