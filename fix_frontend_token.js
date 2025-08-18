/**
 * Script para identificar e corrigir problemas de token 'null' no frontend
 * Este script verifica localStorage e corrige tokens inválidos
 */

// Função para verificar e limpar tokens inválidos
function checkAndFixTokens() {
    console.log('🔍 Verificando tokens no localStorage...');
    
    // Lista de chaves de token que podem existir
    const tokenKeys = ['token', 'authToken', 'auth_token', 'access_token'];
    
    let foundIssues = false;
    
    tokenKeys.forEach(key => {
        const value = localStorage.getItem(key);
        
        if (value !== null) {
            console.log(`📋 Encontrado ${key}: ${value}`);
            
            // Verificar se o token é inválido
            if (value === 'null' || value === 'undefined' || value === '' || value.trim() === '') {
                console.log(`❌ Token inválido encontrado em '${key}': ${value}`);
                localStorage.removeItem(key);
                console.log(`🧹 Token inválido removido de '${key}'`);
                foundIssues = true;
            } else {
                console.log(`✅ Token válido em '${key}'`);
            }
        }
    });
    
    if (!foundIssues) {
        console.log('✅ Nenhum token inválido encontrado!');
    }
    
    return !foundIssues;
}

// Função para interceptar e corrigir requisições fetch
function setupFetchInterceptor() {
    console.log('🔧 Configurando interceptor de fetch...');
    
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        const [url, options = {}] = args;
        
        // Verificar se há header Authorization
        if (options.headers && options.headers.Authorization) {
            const authHeader = options.headers.Authorization;
            
            // Verificar se contém token 'null'
            if (authHeader === 'Bearer null' || authHeader === 'Bearer undefined' || authHeader === 'Bearer ') {
                console.warn(`⚠️ Interceptado token inválido para ${url}: ${authHeader}`);
                
                // Remover o header Authorization inválido
                delete options.headers.Authorization;
                console.log('🧹 Header Authorization inválido removido');
            }
        }
        
        return originalFetch.apply(this, [url, options]);
    };
    
    console.log('✅ Interceptor de fetch configurado!');
}

// Função para monitorar mudanças no localStorage
function setupStorageMonitor() {
    console.log('👀 Configurando monitor de localStorage...');
    
    const originalSetItem = localStorage.setItem;
    
    localStorage.setItem = function(key, value) {
        // Verificar se está tentando salvar um token inválido
        if ((key.includes('token') || key.includes('Token')) && 
            (value === 'null' || value === 'undefined' || value === '')) {
            console.warn(`⚠️ Tentativa de salvar token inválido bloqueada: ${key} = ${value}`);
            return; // Não salvar
        }
        
        return originalSetItem.apply(this, arguments);
    };
    
    console.log('✅ Monitor de localStorage configurado!');
}

// Função principal
function initTokenFix() {
    console.log('🚀 Iniciando correção de tokens...');
    console.log('=' * 50);
    
    // 1. Verificar e limpar tokens existentes
    checkAndFixTokens();
    
    // 2. Configurar interceptor de fetch
    setupFetchInterceptor();
    
    // 3. Configurar monitor de localStorage
    setupStorageMonitor();
    
    console.log('\n🎯 Correções aplicadas:');
    console.log('   ✅ Tokens inválidos removidos do localStorage');
    console.log('   ✅ Interceptor de fetch configurado');
    console.log('   ✅ Monitor de localStorage ativo');
    console.log('\n💡 Agora o frontend não deve mais enviar tokens "null"!');
}

// Executar automaticamente se estiver no browser
if (typeof window !== 'undefined') {
    // Aguardar DOM carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTokenFix);
    } else {
        initTokenFix();
    }
}

// Exportar para uso manual
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkAndFixTokens,
        setupFetchInterceptor,
        setupStorageMonitor,
        initTokenFix
    };
}

// Disponibilizar globalmente para debug
window.tokenFix = {
    check: checkAndFixTokens,
    setupInterceptor: setupFetchInterceptor,
    setupMonitor: setupStorageMonitor,
    init: initTokenFix
};

console.log('🔧 Script de correção de tokens carregado!');
console.log('💡 Use tokenFix.check() para verificar tokens manualmente');