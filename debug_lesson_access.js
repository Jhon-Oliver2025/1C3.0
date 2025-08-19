/**
 * Script para diagnosticar problemas de acesso às aulas
 * Execute no console do navegador
 */

// Função para testar acesso às aulas
function debugLessonAccess() {
  console.log('🔍 Iniciando diagnóstico de acesso às aulas...');
  
  // Verificar token
  const token = localStorage.getItem('token');
  console.log('🔑 Token encontrado:', !!token);
  if (token) {
    console.log('📝 Token (primeiros 20 chars):', token.substring(0, 20) + '...');
  }
  
  // Verificar dados do usuário
  const user = localStorage.getItem('user');
  console.log('👤 Dados do usuário:', user ? JSON.parse(user) : 'Não encontrado');
  
  // Testar acesso às aulas do Despertar Crypto
  const lessons = [
    'despertar-crypto-01',
    'despertar-crypto-02',
    'despertar-crypto-03',
    'despertar-crypto-04',
    'despertar-crypto-05',
    'despertar-crypto-06',
    'despertar-crypto-07',
    'despertar-crypto-08'
  ];
  
  console.log('\n📚 Testando acesso às aulas...');
  
  lessons.forEach(async (lessonId, index) => {
    try {
      const response = await fetch(`/api/payments/check-lesson-access/${lessonId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`${data.has_access ? '✅' : '❌'} ${lessonId}: ${data.has_access ? 'ACESSO PERMITIDO' : 'ACESSO NEGADO'}`);
        if (!data.has_access && data.message) {
          console.log(`   📝 Motivo: ${data.message}`);
        }
      } else {
        console.log(`❌ ${lessonId}: Erro HTTP ${response.status}`);
        const errorText = await response.text();
        console.log(`   📝 Erro: ${errorText}`);
      }
    } catch (error) {
      console.error(`❌ ${lessonId}: Erro de rede:`, error.message);
    }
  });
}

// Função para testar acesso ao curso
function testCourseAccess() {
  console.log('\n🎓 Testando acesso ao curso Despertar Crypto...');
  
  const token = localStorage.getItem('token');
  if (!token) {
    console.log('❌ Nenhum token encontrado');
    return;
  }
  
  fetch('/api/payments/check-access/despertar_crypto', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  })
  .then(data => {
    console.log(`${data.has_access ? '✅' : '❌'} Curso Despertar Crypto: ${data.has_access ? 'ACESSO PERMITIDO' : 'ACESSO NEGADO'}`);
    if (!data.has_access && data.message) {
      console.log(`📝 Motivo: ${data.message}`);
    }
  })
  .catch(error => {
    console.error('❌ Erro ao verificar acesso ao curso:', error.message);
  });
}

// Função para verificar cursos do usuário
function checkUserCourses() {
  console.log('\n📋 Verificando cursos do usuário...');
  
  const token = localStorage.getItem('token');
  if (!token) {
    console.log('❌ Nenhum token encontrado');
    return;
  }
  
  fetch('/api/payments/user-courses', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  })
  .then(data => {
    console.log('📚 Cursos do usuário:', data.courses);
    if (data.courses && data.courses.length > 0) {
      data.courses.forEach(course => {
        console.log(`  📖 ${course.name} (${course.course_id})`);
        if (course.lessons) {
          console.log(`     🎬 Aulas: ${course.lessons.join(', ')}`);
        }
      });
    } else {
      console.log('❌ Nenhum curso encontrado para este usuário');
    }
  })
  .catch(error => {
    console.error('❌ Erro ao verificar cursos do usuário:', error.message);
  });
}

// Função para simular clique em uma aula
function simulateClickLesson(lessonNumber) {
  console.log(`\n🖱️ Simulando clique na aula ${lessonNumber}...`);
  
  const lessonId = `despertar-crypto-${String(lessonNumber).padStart(2, '0')}`;
  const url = `/aula/${lessonId}`;
  
  console.log(`🔗 URL da aula: ${url}`);
  console.log(`📍 Navegando para: ${window.location.origin}${url}`);
  
  // Simular navegação
  window.history.pushState({}, '', url);
  
  // Verificar se a página carregaria corretamente
  setTimeout(() => {
    console.log(`📍 URL atual: ${window.location.pathname}`);
    if (window.location.pathname === url) {
      console.log('✅ Navegação bem-sucedida');
    } else {
      console.log('❌ Navegação falhou - possível redirecionamento');
    }
  }, 100);
}

// Executar diagnóstico completo
console.log('🚀 Executando diagnóstico completo de acesso às aulas...');
debugLessonAccess();
testCourseAccess();
checkUserCourses();

console.log('\n📋 Comandos disponíveis:');
console.log('  - debugLessonAccess(): Testar acesso a todas as aulas');
console.log('  - testCourseAccess(): Testar acesso ao curso');
console.log('  - checkUserCourses(): Verificar cursos do usuário');
console.log('  - simulateClickLesson(n): Simular clique na aula (1-8)');