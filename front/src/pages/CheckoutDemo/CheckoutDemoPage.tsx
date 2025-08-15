import React, { useState } from 'react';
import styled from 'styled-components';
import { ShoppingCart, CreditCard, Lock, Star, CheckCircle } from 'lucide-react';
import MercadoPagoCheckout from '../../components/MercadoPagoCheckout/MercadoPagoCheckout';
import StandardFooter from '../../components/StandardFooter/StandardFooter';
import { useCourseAccess } from '../../hooks/useCourseAccess';

// Styled Components
const DemoContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
  padding: 2rem;
`;

const DemoHeader = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    color: #ffffff;
    font-size: 3rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
  }
`;

const CoursesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const CourseCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const CourseHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
  
  h2 {
    color: #ffffff;
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 1rem;
  }
  
  .price {
    font-size: 2rem;
    font-weight: bold;
    background: linear-gradient(135deg, #4caf50, #81c784);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const FeaturesList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  
  li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0.75rem;
    
    svg {
      color: #4caf50;
      flex-shrink: 0;
    }
  }
`;

const StatusBadge = styled.div<{ type: 'demo' | 'production' }>`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 2rem;
  
  ${props => props.type === 'demo' ? `
    background: rgba(255, 193, 7, 0.2);
    border: 1px solid rgba(255, 193, 7, 0.5);
    color: #ffc107;
  ` : `
    background: rgba(76, 175, 80, 0.2);
    border: 1px solid rgba(76, 175, 80, 0.5);
    color: #4caf50;
  `}
`;

const InfoBox = styled.div`
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  
  h3 {
    color: #2196f3;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    margin: 0;
    line-height: 1.6;
  }
`;

/**
 * Página de demonstração do sistema de checkout
 * Mostra os cursos disponíveis e permite testar o fluxo de pagamento
 */
const CheckoutDemoPage: React.FC = () => {
  const { userCourses, availableCourses } = useCourseAccess();
  const [isProduction, setIsProduction] = useState(false);

  // Cursos de demonstração
  const demoCourses = [
    {
      id: 'despertar_crypto',
      name: 'Despertar Crypto - 10 Aulas',
      description: 'Curso completo de introdução às criptomoedas com 10 aulas práticas e objetivas.',
      price: 197.00,
      features: [
        'Acesso vitalício ao curso',
        '10 aulas práticas e objetivas',
        'Suporte direto com especialistas',
        'Certificado de conclusão',
        'Atualizações gratuitas',
        'Garantia de 7 dias'
      ]
    },
    {
      id: 'masterclass',
      name: 'Masterclass - Trading Avançado',
      description: 'Curso avançado de trading e análise técnica para traders experientes.',
      price: 497.00,
      features: [
        'Estratégias avançadas de trading',
        'Análise técnica profissional',
        'Gestão de risco avançada',
        'Acesso a ferramentas premium',
        'Mentoria em grupo',
        'Suporte prioritário'
      ]
    },
    {
      id: 'app_mentoria',
      name: 'App 1Crypten e Mentoria',
      description: 'Acesso completo ao app exclusivo com mentoria personalizada.',
      price: 997.00,
      features: [
        'App 1Crypten completo',
        'Sinais de trading em tempo real',
        'Mentoria personalizada 1:1',
        'Comunidade VIP exclusiva',
        'Suporte 24/7',
        'Atualizações prioritárias'
      ]
    }
  ];

  return (
    <DemoContainer>
      <DemoHeader>
        <h1>🛒 Demo do Sistema de Checkout</h1>
        <p>
          Demonstração do sistema de pagamentos integrado com Mercado Pago.
          Teste o fluxo completo de compra dos nossos cursos.
        </p>
      </DemoHeader>

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <StatusBadge type={isProduction ? 'production' : 'demo'}>
          {isProduction ? (
            <>
              <CheckCircle size={16} />
              Modo Produção (HTTPS)
            </>
          ) : (
            <>
              <Star size={16} />
              Modo Demonstração
            </>
          )}
        </StatusBadge>
      </div>

      <InfoBox>
        <h3>
          <CreditCard size={20} />
          Informações Importantes
        </h3>
        <p>
          <strong>Para testes locais:</strong> O Mercado Pago requer HTTPS para webhooks em produção. 
          Em desenvolvimento, você pode usar cartões de teste, mas para webhooks funcionais, 
          é necessário deploy em servidor com SSL.
        </p>
        <br />
        <p>
          <strong>Cartão de teste (Sandbox):</strong><br />
          Número: 4509 9535 6623 3704<br />
          CVC: 123 | Vencimento: 11/25
        </p>
      </InfoBox>

      <CoursesGrid>
        {demoCourses.map((course) => (
          <CourseCard key={course.id}>
            <CourseHeader>
              <h2>{course.name}</h2>
              <p>{course.description}</p>
              <div className="price">
                R$ {course.price.toFixed(2).replace('.', ',')}
              </div>
            </CourseHeader>

            <FeaturesList>
              {course.features.map((feature, index) => (
                <li key={index}>
                  <CheckCircle size={16} />
                  {feature}
                </li>
              ))}
            </FeaturesList>

            <MercadoPagoCheckout
              courseId={course.id}
              course={{
                name: course.name,
                description: course.description,
                price: course.price
              }}
              onSuccess={(paymentData) => {
                console.log('Pagamento realizado:', paymentData);
                alert('Pagamento realizado com sucesso! (Demo)');
              }}
              onError={(error) => {
                console.error('Erro no pagamento:', error);
                alert(`Erro no pagamento: ${error}`);
              }}
            />
          </CourseCard>
        ))}
      </CoursesGrid>

      <div style={{ 
        textAlign: 'center', 
        marginTop: '3rem', 
        padding: '2rem',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        maxWidth: '800px',
        margin: '3rem auto 0'
      }}>
        <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>
          🚀 Próximos Passos para Produção
        </h3>
        <div style={{ 
          color: 'rgba(255, 255, 255, 0.8)', 
          textAlign: 'left',
          lineHeight: '1.6'
        }}>
          <p><strong>1. Deploy em servidor com SSL (HTTPS)</strong></p>
          <p><strong>2. Configurar credenciais de produção do Mercado Pago</strong></p>
          <p><strong>3. Configurar webhook URL: https://seu-dominio.com/api/payments/webhook</strong></p>
          <p><strong>4. Testar fluxo completo com cartões reais</strong></p>
        </div>
      </div>
      
      {/* Rodapé Padrão */}
      <StandardFooter />
    </DemoContainer>
  );
};

export default CheckoutDemoPage;