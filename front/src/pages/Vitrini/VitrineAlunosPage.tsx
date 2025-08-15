import React from 'react';
import logo1Crypten from '../../assets/members1cT.png'; // Importa o logo da 1crypten
import mainBanner from '../../assets/Bannerprincipal.png'; // Importa o banner principal

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
  const vitrineData = {
    sections: [
      {
        type: 'banner',
        image: mainBanner,
        title: 'Bem-vindo à 1Crypten!',
        subtitle: 'Sua jornada de aprendizado começa aqui.'
      },

      {
        type: 'course_list',
        title: 'Despertar Crypto - 10 Aulas',
        filter: 'purchased',
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
              title: 'Aula 9 - Estratégias Avançadas',
              description: 'Técnicas profissionais de investimento crypto.',
              thumbnail: 'https://via.placeholder.com/200x150/FF6B35/FFFFFF?text=Aula+9',
              progress: '0%',
              link: '/aula/despertar-crypto-09'
            },
            {
              id: '10',
              title: 'Aula 10 - Futuro das Criptomoedas',
              description: 'Tendências e oportunidades futuras no mercado.',
              thumbnail: 'https://via.placeholder.com/200x150/6A4C93/FFFFFF?text=Aula+10',
              progress: '0%',
              link: '/aula/despertar-crypto-10'
            }
          ]
      },
      {
        type: 'promo_banners',
        banners: [
          {
            text: 'Toda grande jornada financeira começa com um propósito. O seu é a segurança de quem você ama.',
            text_color: '#ffffff',
            background_color: '#0f172a'
          }
        ]
      },
      {
        type: 'course_list',
        title: 'Curso 2 - Masterclass com 10 Aulas',
        filter: 'masterclass',
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
        type: 'promo_banners',
        banners: [
          {
            text: 'Nós transformamos a complexidade do mercado em sinais claros. Sua missão é seguir o plano.',
            text_color: '#ffffff',
            background_color: '#0c1426'
          }
        ]
      },
      {
        type: 'course_list',
        title: 'Curso 3 - App 1Crypten e Mentoria',
        filter: 'app_mentoria',
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
        type: 'promo_banners',
        banners: [
          {
            text: 'Hoje, você investe em ativos. Amanhã, você colhe um legado. Continue firme.',
            text_color: '#ffffff',
            background_color: '#0a0f1c'
          }
        ]
      },
      {
           type: 'community_text',
           text: 'Seja Bem Vindo ao nosso Ecosistema e a essa revolução Crypto.'
         },

      {
        type: 'footer_section',
        title: 'Rodapé',
        content: 'Informações adicionais e links importantes.'
      }
      ]
    };

  return (
    <div className="vitrine-alunos-page" style={{ backgroundColor: '#000000', minHeight: '100vh', margin: 0, padding: 0 }}>
      <img src={logo1Crypten} alt="Logo 1Crypten" style={{ position: 'absolute', top: '20px', left: '20px', width: '130px', zIndex: 100 }} />
      <CourseShowcase data={vitrineData} />
      <StandardFooter /> {/* Renderiza o componente StandardFooter */}
    </div>
  );
};

export default VitrineAlunosPage;