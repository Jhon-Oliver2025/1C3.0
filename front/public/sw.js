/**
 * Service Worker para 1Crypten PWA
 * Implementa cache strategies e funcionalidade offline
 */

const CACHE_NAME = '1crypten-v1.0.0';
const STATIC_CACHE = '1crypten-static-v1.0.0';
const DYNAMIC_CACHE = '1crypten-dynamic-v1.0.0';
const API_CACHE = '1crypten-api-v1.0.0';

// Recursos estáticos para cache
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/assets/terra.png',
  '/assets/logo2.png'
];

// URLs da API para cache
const API_URLS = [
  '/api/status',
  '/api/signals/public'
];

// URLs que devem sempre buscar da rede
const NETWORK_FIRST_URLS = [
  '/api/signals',
  '/api/auth',
  '/api/trading'
];

/**
 * Evento de instalação do Service Worker
 * Faz o cache inicial dos recursos estáticos
 */
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Instalando...');
  
  event.waitUntil(
    Promise.all([
      // Cache de recursos estáticos
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Service Worker: Fazendo cache dos recursos estáticos');
        return cache.addAll(STATIC_ASSETS.map(url => {
          return new Request(url, { cache: 'reload' });
        }));
      }),
      
      // Pular waiting para ativar imediatamente
      self.skipWaiting()
    ])
  );
});

/**
 * Evento de ativação do Service Worker
 * Limpa caches antigos e assume controle
 */
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Ativando...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('🗑️ Service Worker: Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Assumir controle de todas as abas
      self.clients.claim()
    ])
  );
});

/**
 * Intercepta todas as requisições de rede
 * Implementa diferentes estratégias de cache
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorar requisições não-HTTP
  if (!request.url.startsWith('http')) {
    return;
  }
  
  // Estratégia para recursos estáticos (Cache First)
  if (isStaticAsset(request.url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }
  
  // Estratégia para API crítica (Network First)
  if (isNetworkFirstUrl(request.url)) {
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }
  
  // Estratégia para API de sinais (Stale While Revalidate)
  if (isApiUrl(request.url)) {
    event.respondWith(staleWhileRevalidate(request, API_CACHE));
    return;
  }
  
  // Estratégia padrão para outros recursos (Network First)
  event.respondWith(networkFirst(request, DYNAMIC_CACHE));
});

/**
 * Estratégia Cache First
 * Busca no cache primeiro, depois na rede
 */
async function cacheFirst(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('📦 Cache Hit:', request.url);
      return cachedResponse;
    }
    
    console.log('🌐 Cache Miss, buscando na rede:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Erro em cacheFirst:', error);
    return getOfflineFallback(request);
  }
}

/**
 * Estratégia Network First
 * Busca na rede primeiro, depois no cache
 */
async function networkFirst(request, cacheName) {
  try {
    console.log('🌐 Network First:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📦 Network falhou, tentando cache:', request.url);
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return getOfflineFallback(request);
  }
}

/**
 * Estratégia Stale While Revalidate
 * Retorna do cache e atualiza em background
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Buscar na rede em background
  const networkPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    console.log('🌐 Network falhou para:', request.url);
  });
  
  // Retornar cache imediatamente se disponível
  if (cachedResponse) {
    console.log('📦 Stale cache retornado:', request.url);
    return cachedResponse;
  }
  
  // Se não há cache, aguardar rede
  console.log('🌐 Aguardando rede (sem cache):', request.url);
  return networkPromise;
}

/**
 * Retorna fallback offline apropriado
 */
function getOfflineFallback(request) {
  if (request.destination === 'document') {
    return caches.match('/index.html');
  }
  
  if (request.url.includes('/api/')) {
    return new Response(
      JSON.stringify({
        success: false,
        error: 'Sem conexão com a internet',
        offline: true,
        cached: false
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
  
  return new Response('Recurso não disponível offline', {
    status: 503,
    statusText: 'Service Unavailable'
  });
}

/**
 * Verifica se é um recurso estático
 */
function isStaticAsset(url) {
  return STATIC_ASSETS.some(asset => url.includes(asset)) ||
         url.includes('/static/') ||
         url.includes('/assets/') ||
         url.includes('/icons/') ||
         url.includes('.css') ||
         url.includes('.js') ||
         url.includes('.png') ||
         url.includes('.jpg') ||
         url.includes('.svg');
}

/**
 * Verifica se é uma URL de API
 */
function isApiUrl(url) {
  return url.includes('/api/');
}

/**
 * Verifica se deve usar Network First
 */
function isNetworkFirstUrl(url) {
  return NETWORK_FIRST_URLS.some(pattern => url.includes(pattern));
}

/**
 * Listener para mensagens do cliente
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    clearAllCaches().then(() => {
      event.ports[0].postMessage({ success: true });
    });
  }
});

/**
 * Limpa todos os caches
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  return Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
}

/**
 * Listener para notificações push
 */
self.addEventListener('push', (event) => {
  console.log('📱 Push notification recebida:', event);
  
  const options = {
    body: 'Novos sinais de trading disponíveis!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/dashboard'
    },
    actions: [
      {
        action: 'view',
        title: 'Ver Sinais',
        icon: '/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Fechar'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.data = { ...options.data, ...data };
  }
  
  event.waitUntil(
    self.registration.showNotification('1Crypten', options)
  );
});

/**
 * Listener para cliques em notificações
 */
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notificação clicada:', event);
  
  event.notification.close();
  
  if (event.action === 'view' || !event.action) {
    const url = event.notification.data?.url || '/dashboard';
    
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Verificar se já há uma aba aberta
        for (const client of clientList) {
          if (client.url.includes(url) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Abrir nova aba se necessário
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
    );
  }
});

console.log('🚀 Service Worker 1Crypten carregado!');