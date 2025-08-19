/**
 * Script para diagnosticar problemas de carregamento de vídeos
 * Execute no console do navegador na página das aulas
 */

// Função para testar carregamento de vídeos
function debugVideoLoading() {
  console.log('🎬 Iniciando diagnóstico de vídeos...');
  
  // Verificar se há elementos de vídeo na página
  const videoElements = document.querySelectorAll('video');
  console.log(`📹 Encontrados ${videoElements.length} elementos de vídeo`);
  
  videoElements.forEach((video, index) => {
    console.log(`\n🎥 Vídeo ${index + 1}:`);
    console.log(`  - Src: ${video.src}`);
    console.log(`  - ReadyState: ${video.readyState}`);
    console.log(`  - NetworkState: ${video.networkState}`);
    console.log(`  - Error: ${video.error ? video.error.message : 'Nenhum'}`);
    
    // Testar se o arquivo existe
    fetch(video.src, { method: 'HEAD' })
      .then(response => {
        console.log(`  - Status HTTP: ${response.status}`);
        console.log(`  - Content-Type: ${response.headers.get('content-type')}`);
        console.log(`  - Content-Length: ${response.headers.get('content-length')}`);
      })
      .catch(error => {
        console.error(`  - Erro ao acessar: ${error.message}`);
      });
  });
  
  // Verificar imports de vídeo
  console.log('\n📁 Verificando imports de vídeo...');
  const videoImports = [
    '/src/assets/vdc/v1.mp4',
    '/src/assets/vdc/v2.mp4',
    '/src/assets/vdc/v3.mp4',
    '/src/assets/vdc/v4.mp4',
    '/src/assets/vdc/v5.mp4',
    '/src/assets/vdc/v6.mp4',
    '/src/assets/vdc/v7.mp4',
    '/src/assets/vdc/v8.mp4'
  ];
  
  videoImports.forEach((videoPath, index) => {
    fetch(videoPath, { method: 'HEAD' })
      .then(response => {
        console.log(`✅ v${index + 1}.mp4: ${response.status} - ${response.headers.get('content-length')} bytes`);
      })
      .catch(error => {
        console.error(`❌ v${index + 1}.mp4: ${error.message}`);
      });
  });
  
  // Verificar localStorage para progresso de vídeos
  console.log('\n💾 Verificando dados do localStorage...');
  const videoProgressData = localStorage.getItem('videoProgressData');
  if (videoProgressData) {
    console.log('Dados de progresso encontrados:', JSON.parse(videoProgressData));
  } else {
    console.log('Nenhum dado de progresso encontrado');
  }
}

// Função para testar carregamento de um vídeo específico
function testVideoLoad(videoNumber) {
  console.log(`🎬 Testando carregamento do vídeo ${videoNumber}...`);
  
  const video = document.createElement('video');
  video.src = `/src/assets/vdc/v${videoNumber}.mp4`;
  video.preload = 'metadata';
  
  video.addEventListener('loadedmetadata', () => {
    console.log(`✅ Vídeo ${videoNumber} carregado com sucesso!`);
    console.log(`  - Duração: ${video.duration}s`);
    console.log(`  - Dimensões: ${video.videoWidth}x${video.videoHeight}`);
  });
  
  video.addEventListener('error', (e) => {
    console.error(`❌ Erro ao carregar vídeo ${videoNumber}:`, e.target.error);
  });
  
  document.body.appendChild(video);
  
  // Remover após teste
  setTimeout(() => {
    document.body.removeChild(video);
  }, 5000);
}

// Função para verificar configuração do Vite
function checkViteConfig() {
  console.log('⚙️ Verificando configuração do ambiente...');
  console.log(`  - Modo: ${import.meta.env.MODE}`);
  console.log(`  - Produção: ${import.meta.env.PROD}`);
  console.log(`  - Base URL: ${import.meta.env.BASE_URL}`);
  console.log(`  - Vite Dev: ${import.meta.env.DEV}`);
}

// Executar diagnóstico completo
console.log('🚀 Executando diagnóstico completo de vídeos...');
debugVideoLoading();
checkViteConfig();

// Testar vídeos individuais
for (let i = 1; i <= 8; i++) {
  setTimeout(() => testVideoLoad(i), i * 1000);
}

console.log('\n📋 Comandos disponíveis:');
console.log('  - debugVideoLoading(): Diagnóstico geral');
console.log('  - testVideoLoad(n): Testar vídeo específico (1-8)');
console.log('  - checkViteConfig(): Verificar configuração do ambiente');