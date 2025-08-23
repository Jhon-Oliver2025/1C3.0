/**
 * Script para corrigir configuração de vídeo na página de vendas
 * Execute no console do navegador em http://localhost:3000/sales
 */

// Função para limpar configurações antigas e forçar vsl01.mp4
function fixVideoConfig() {
  console.log('🎬 Corrigindo configuração de vídeo...');
  
  // Verificar configuração atual
  const currentConfig = localStorage.getItem('salesPageConfig');
  if (currentConfig) {
    console.log('📋 Configuração atual encontrada:', JSON.parse(currentConfig));
  }
  
  // Limpar localStorage completamente
  console.log('🧹 Limpando localStorage...');
  localStorage.removeItem('salesPageConfig');
  
  // Criar nova configuração com vídeo correto
  const newConfig = {
    videoConfig: {
      videoUrl: '/vsl01.mp4',
      autoplay: false,
      muted: true,
      showOverlay: true
    },
    timestamp: new Date().toISOString()
  };
  
  // Salvar nova configuração
  localStorage.setItem('salesPageConfig', JSON.stringify(newConfig));
  console.log('✅ Nova configuração salva:', newConfig);
  
  // Recarregar página para aplicar mudanças
  console.log('🔄 Recarregando página...');
  window.location.reload();
}

// Função para verificar se vsl01.mp4 existe
function checkVideoFile() {
  console.log('🔍 Verificando arquivo vsl01.mp4...');
  
  fetch('/vsl01.mp4', { method: 'HEAD' })
    .then(response => {
      if (response.ok) {
        console.log('✅ vsl01.mp4 encontrado!');
        console.log(`📊 Status: ${response.status}`);
        console.log(`📏 Tamanho: ${response.headers.get('content-length')} bytes`);
        console.log(`🎭 Tipo: ${response.headers.get('content-type')}`);
      } else {
        console.error('❌ vsl01.mp4 não encontrado!');
        console.log(`📊 Status: ${response.status}`);
      }
    })
    .catch(error => {
      console.error('❌ Erro ao verificar vsl01.mp4:', error);
    });
}

// Função para verificar todos os vídeos na pasta public
function checkAllVideos() {
  console.log('🎬 Verificando todos os vídeos...');
  
  const videos = [
    '/vsl01.mp4',
    '/BigBuckBunny.mp4',
    '/public/vsl01.mp4',
    '/assets/vsl01.mp4'
  ];
  
  videos.forEach(videoPath => {
    fetch(videoPath, { method: 'HEAD' })
      .then(response => {
        if (response.ok) {
          console.log(`✅ ${videoPath}: ${response.status} - ${response.headers.get('content-length')} bytes`);
        } else {
          console.log(`❌ ${videoPath}: ${response.status}`);
        }
      })
      .catch(error => {
        console.log(`❌ ${videoPath}: ${error.message}`);
      });
  });
}

// Função para verificar elementos de vídeo na página
function checkVideoElements() {
  console.log('🎥 Verificando elementos de vídeo na página...');
  
  const videos = document.querySelectorAll('video');
  console.log(`📹 Encontrados ${videos.length} elementos de vídeo`);
  
  videos.forEach((video, index) => {
    console.log(`\n🎥 Vídeo ${index + 1}:`);
    console.log(`  - Src: ${video.src}`);
    console.log(`  - CurrentSrc: ${video.currentSrc}`);
    console.log(`  - ReadyState: ${video.readyState}`);
    console.log(`  - NetworkState: ${video.networkState}`);
    console.log(`  - Error: ${video.error ? video.error.message : 'Nenhum'}`);
    
    // Tentar forçar o vídeo correto
    if (video.src.includes('BigBuckBunny') || !video.src.includes('vsl01')) {
      console.log(`🔧 Corrigindo src do vídeo ${index + 1}...`);
      video.src = '/vsl01.mp4';
      video.load();
    }
  });
}

// Executar diagnóstico completo
console.log('🚀 Iniciando diagnóstico de vídeo...');
checkVideoFile();
checkAllVideos();
checkVideoElements();

console.log('\n📋 Comandos disponíveis:');
console.log('  - fixVideoConfig(): Corrigir configuração e recarregar');
console.log('  - checkVideoFile(): Verificar se vsl01.mp4 existe');
console.log('  - checkAllVideos(): Verificar todos os vídeos');
console.log('  - checkVideoElements(): Verificar elementos na página');

// Executar correção automaticamente após 3 segundos
setTimeout(() => {
  console.log('\n⏰ Executando correção automática em 3 segundos...');
  console.log('💡 Para cancelar, digite: clearTimeout(autoFix)');
  window.autoFix = setTimeout(fixVideoConfig, 3000);
}, 1000);