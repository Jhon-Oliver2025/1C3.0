import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo1Crypten from '../../assets/members1cT.png'; // Importa o logo da 1crypten
import mainBanner from '../../assets/Bannerprincipal.png'; // Importa o banner principal
import { useCourseAccess } from '../../hooks/useCourseAccess'; // Hook para controle de acesso
import { useAdminCheck } from '../../hooks/useAdminCheck'; // Hook para verificar se é admin
import '../Dashboard/DashboardMobile.css';

import thumb01 from '../../assets/Tamb/01.png';
import thumb02 from '../../assets/Tamb/02.png';
import thumb03 from '../../assets/Tamb/03.png';
import thumb04 from '../../assets/Tamb/04.png';
import thumb05 from '../../assets/Tamb/05.png';
import thumb06 from '../../assets/Tamb/06.png';
import thumb07 from '../../assets/Tamb/07.png';
import thumb08 from '../../assets/Tamb/08.png';
import thumb01M from '../../assets/Tamb/01-M.png';
import CourseShowcase from '../../components/CourseShowcase'; // Importa o novo componente CourseShowcase
import StandardFooter from '../../components/StandardFooter/StandardFooter'; // Importa o novo componente StandardFooter

/**
 * Página Vitrine de Alunos
 * Renderiza a página inicial/vitrine de cursos
 */

const VitrineAlunosPage: React.FC = () => {
  const navigate = useNavigate();
  const { userCourses, hasAccessToCourse, isLoading } = useCourseAccess();
  const { isAdmin } = useAdminCheck(); // Verificar se é admin
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Verificar autenticação
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login', { 
        state: { 
          returnUrl: '/vitrine-alunos',
          message: 'Faça login para acessar a área de membros'
        }
      });
      return;
    }
    setIsAuthenticated(true);
  }, [navigate]);

  // Função para verificar se o usuário tem acesso a um curso específico
  const getUserCourseAccess = (courseFilter: string) => {
    switch (courseFilter) {
      case 'purchased':
        return hasAccessToCourse('despertar_crypto');
      case 'masterclass':
        return hasAccessToCourse('masterclass');
      case 'app_mentoria':
        return hasAccessToCourse('app_mentoria');
      default:
        return false;
    }
  };

  // Mostrar loading enquanto verifica acesso
  if (!isAuthenticated || isLoading) {
    return (
      <div style={{ 
        backgroundColor: '#000000', 
        minHeight: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        color: 'white'
      }}>
        <div>Carregando área de membros...</div>
      </div>
    );
  }

  const vitrineData = {
    sections: [
      {
        type: 'course_list' as const,
        title: 'Despertar Crypto - 10 Aulas',
        filter: 'purchased' as const,
        courses: [
          {
            id: '1',
            title: 'Aula 1 - O PONTO DE PARTIDA',
            description: '"O Jogo do Dinheiro Mudou para Sempre"',
            thumbnail: thumb01,
            progress: '100%',
            link: '/aula/despertar-crypto-01'
          },
          {
            id: '2',
            title: 'Aula 2 - O PONTO DE PARTIDA',
            description: '"Você Precisa ser Rico ou Gênio para Investir?"',
            thumbnail: thumb02,
            progress: '100%',
            link: '/aula/despertar-crypto-02'
          },
          {
            id: '3',
            title: 'Aula 3 - O CAMPO DE JOGO',
            description: '"O Mercado que Nunca Dorme"',
            thumbnail: thumb03,
            progress: '100%',
            link: '/aula/despertar-crypto-03'
          },
          {
            id: '4',
            title: 'Aula 4 - O CAMPO DE JOGO',
            description: '"O Segredo das 21:30: A Hora de Ouro de Hong Kong"',
            thumbnail: thumb04,
            progress: '100%',
            link: '/aula/despertar-crypto-04'
          },
          {
            id: '5',
            title: 'Aula 5 - O CAMPO DE JOGO',
            description: '"A Volatilidade: O Dragão que Você Vai Aprender a Montar"',
            thumbnail: thumb05,
            progress: '100%',
            link: '/aula/despertar-crypto-05'
          },
          {
            id: '6',
            title: 'Aula 6 - A GRANDE OPORTUNIDADE',
            description: '"Por Que Cripto Pode Criar Milionários (A Matemática Simples)"',
            thumbnail: thumb06,
            progress: '100%',
            link: '/aula/despertar-crypto-06'
          },
          {
            id: '7',
            title: 'Aula 7 - A GRANDE OPORTUNIDADE',
            description: '"Você Não Está Atrasado para a Festa"',
            thumbnail: thumb07,
            progress: '100%',
            link: '/aula/despertar-crypto-07'
          },
          {
              id: '8',
              title: 'Aula 8 - A GRANDE OPORTUNIDADE',
              description: '"Recapitulando: A Mentalidade Está Pronta"',
              thumbnail: thumb08,
              progress: '100%',
              link: '/aula/despertar-crypto-08'
            },
            {
              id: '9',
              title: 'Aula 9 - ESTRATÉGIAS AVANÇADAS',
              description: '"Dominando as Técnicas dos Profissionais"',
              thumbnail: thumb01,
              progress: '0%',
              link: '/aula/despertar-crypto-09'
            },
            {
              id: '10',
              title: 'Aula 10 - O FUTURO É AGORA',
              description: '"Construindo Seu Legado Financeiro"',
              thumbnail: thumb02,
              progress: '0%',
              link: '/aula/despertar-crypto-10'
            }
          ]
      },
      {
        type: 'promo_banners' as const,
        banners: [
          {
            text: 'Toda grande jornada financeira começa com um propósito. O seu é a segurança de quem você ama.',
            text_color: '#ffffff',
            background_color: '#0f172a'
          }
        ]
      },
      {
        type: 'course_list' as const,
        title: 'Curso 2 - Masterclass com 10 Aulas',
        filter: 'masterclass' as const,
        courses: [
          {
            id: 'mc1',
            title: 'Aula 1 - Trading Avançado',
            description: 'Estratégias profissionais de trading.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/masterclass-01'
          },
          {
            id: 'mc2',
            title: 'Aula 2 - Análise Fundamentalista',
            description: 'Avaliação profunda de projetos crypto.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/masterclass-02'
          },
          {
            id: 'mc3',
            title: 'Aula 3 - Derivativos Crypto',
            description: 'Futuros, opções e contratos avançados.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/masterclass-03'
          },
          {
            id: 'mc4',
            title: 'Aula 4 - Portfolio Management',
            description: 'Gestão profissional de carteiras crypto.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/masterclass-04'
          }
        ]
      },
      {
        type: 'promo_banners' as const,
        banners: [
          {
            text: 'Nós transformamos a complexidade do mercado em sinais claros. Sua missão é seguir o plano.',
            text_color: '#ffffff',
            background_color: '#0c1426'
          }
        ]
      },
      {
        type: 'course_list' as const,
        title: 'Curso 3 - App 1Crypten e Mentoria',
        filter: 'app_mentoria' as const,
        courses: [
          {
            id: 'app1',
            title: 'Módulo 1 - Configuração do App',
            description: 'Como configurar e usar o app 1Crypten.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/app-01'
          },
          {
            id: 'app2',
            title: 'Módulo 2 - Sinais Automatizados',
            description: 'Receba sinais de trading em tempo real.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/app-02'
          },
          {
            id: 'app3',
            title: 'Módulo 3 - Mentoria Personalizada',
            description: 'Sessões individuais com especialistas.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/app-03'
          },
          {
            id: 'app4',
            title: 'Módulo 4 - Comunidade VIP',
            description: 'Acesso exclusivo à comunidade premium.',
            thumbnail: thumb01M,
            progress: '0%',
            link: '/aula/app-04'
          }
        ]
      },
      {
        type: 'promo_banners' as const,
        banners: [
          {
            text: 'Hoje, você investe em ativos. Amanhã, você colhe um legado. Continue firme.',
            text_color: '#ffffff',
            background_color: '#0a0f1c'
          }
        ]
      },
      {
           type: 'community_text' as const,
           text: 'Seja Bem Vindo ao nosso Ecosistema e a essa revolução Crypto.'
         },


      ]
    };

  // Preparar informações de acesso para o CourseShowcase
  const userAccessInfo = {
    hasDespertarCrypto: hasAccessToCourse('despertar_crypto'),
    hasMasterclass: hasAccessToCourse('masterclass'),
    hasAppMentoria: hasAccessToCourse('app_mentoria')
  };

  // Verificar se o usuário tem acesso a pelo menos um curso
  const hasAnyCourse = userAccessInfo.hasDespertarCrypto || userAccessInfo.hasMasterclass || userAccessInfo.hasAppMentoria;
  
  // Mostrar mensagem se o usuário não tem acesso a nenhum curso (exceto para admins)
  if (!hasAnyCourse && !isAdmin) {
    return (
      <div style={{ 
        backgroundColor: '#000000', 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center',
        color: 'white',
        padding: '20px',
        textAlign: 'center'
      }}>
        <img src={logo1Crypten} alt="Logo 1Crypten" style={{ width: '200px', marginBottom: '30px' }} />
        <h2>Bem-vindo à Área de Membros!</h2>
        <p style={{ fontSize: '1.2em', marginBottom: '30px', maxWidth: '600px' }}>
          Você ainda não possui acesso a nenhum curso. Adquira um de nossos cursos para começar sua jornada no mundo das criptomoedas.
        </p>
      </div>
     );
   }

   // Renderizar a vitrine com os cursos que o usuário tem acesso
   return (
     <div className="vitrine-alunos-page" style={{ backgroundColor: '#000000', padding: '20px' }}>
       {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
       <div className="mobile-motivation-header-container">
         {/* Seção Motivacional */}
         <div className="mobile-motivational">
           <p className="mobile-motivational-text">
             Bem-vindo à 1Crypten! Sua jornada de aprendizado começa aqui.
           </p>
         </div>

         {/* Espaçamento de Segurança (4px) */}
         <div className="mobile-safety-gap"></div>
       </div>
       
       <CourseShowcase data={vitrineData} userAccess={userAccessInfo} isAdmin={isAdmin} />
       <StandardFooter /> {/* Renderiza o componente StandardFooter */}
     </div>
   );
};

export default VitrineAlunosPage;